#!/usr/bin/env python3
"""Read-only PE/resource analysis. Never runs the selected Windows programs."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import subprocess

import pefile

FEATURE = re.compile(r'booklet|poster|tile.?scale|tile.?overlap|print.*(?:duplex|range|scale)|'
                     r'fit.?to.?page|actual.?size|SearchText|TextSearcher|SelectRangeQuads|'
                     r'BookletSubset|PrintDiag|PageModePosters|PageModeBooklet', re.I)


def dialog(data):
    """Decode standard/extended Win32 dialog control IDs, labels and layout."""
    offset = 0
    def unpack(fmt):
        nonlocal offset
        value = struct.unpack_from('<' + fmt, data, offset)
        offset += struct.calcsize('<' + fmt)
        return value
    def text():
        nonlocal offset
        value = unpack('H')[0]
        if value == 0: return ''
        if value == 0xffff: return {'ordinal': unpack('H')[0]}
        units = [value]
        while True:
            value = unpack('H')[0]
            if not value: break
            units.append(value)
        return struct.pack('<' + 'H' * len(units), *units).decode('utf-16-le', errors='replace')
    extended = data[:4] == b'\x01\x00\xff\xff'
    if extended:
        _, _, _, _, style, count, x, y, w, h = unpack('HHIIIHhhhh')
    else:
        style, _, count, x, y, w, h = unpack('IIHhhhh')
    menu, window_class, title = text(), text(), text()
    if style & 0x40:
        unpack('H')
        if extended: unpack('HBB')
        text()
    controls = []
    for _ in range(count):
        offset = (offset + 3) & ~3
        if extended:
            _, _, _, cx, cy, cw, ch, cid = unpack('IIIhhhhI')
        else:
            _, _, cx, cy, cw, ch, cid = unpack('IIhhhhH')
        klass, label = text(), text()
        extra = unpack('H')[0]
        if extra: offset += extra
        controls.append({'id': cid, 'class': klass, 'text': label, 'dialog_units': [cx, cy, cw, ch]})
    return {'title': title, 'dialog_units': [x, y, w, h], 'controls': controls}


def inspect(path, output):
    raw = path.read_bytes()
    pe = pefile.PE(data=raw, fast_load=True)
    pe.parse_data_directories(directories=[0, 1, 2, 13])
    versions = []
    for group in getattr(pe, 'FileInfo', []):
        for entry in group:
            for table in getattr(entry, 'StringTable', []):
                versions.append({k.decode(errors='replace'): v.decode(errors='replace')
                                 for k, v in table.entries.items()})
    imports = {}
    for directory in ('DIRECTORY_ENTRY_IMPORT', 'DIRECTORY_ENTRY_DELAY_IMPORT'):
        for entry in getattr(pe, directory, []):
            imports.setdefault(entry.dll.decode(errors='replace'), []).extend(
                item.name.decode(errors='replace') if item.name else f'ordinal:{item.ordinal}'
                for item in entry.imports)
    exports = [{'name': item.name.decode(errors='replace') if item.name else None,
                'ordinal': item.ordinal, 'rva': hex(item.address),
                'forwarder': item.forwarder.decode(errors='replace') if item.forwarder else None}
               for item in getattr(getattr(pe, 'DIRECTORY_ENTRY_EXPORT', None), 'symbols', [])]
    strings = []
    for encoding, pattern in [('ascii', rb'[\x20-\x7e]{6,}'), ('utf-16-le', rb'(?:[\x20-\x7e]\x00){6,}')]:
        for match in re.finditer(pattern, raw):
            value = match.group().decode(encoding)
            if FEATURE.search(value) and len(value) <= 1000:
                section = pe.get_section_by_offset(match.start())
                strings.append({'file_offset': hex(match.start()), 'rva': hex(pe.get_rva_from_offset(match.start())),
                                'section': section.Name.rstrip(b'\0').decode(errors='replace') if section else None,
                                'encoding': encoding, 'text': value})
    dialogs, errors, total_dialogs = [], [], 0
    for resource in getattr(getattr(pe, 'DIRECTORY_ENTRY_RESOURCE', None), 'entries', []):
        if resource.id != 5: continue
        for entry in resource.directory.entries:
            for lang in entry.directory.entries:
                total_dialogs += 1
                d = lang.data.struct
                try:
                    parsed = dialog(pe.get_data(d.OffsetToData, d.Size))
                    labels = str(parsed['title']) + ' ' + ' '.join(str(c['text']) for c in parsed['controls'])
                    if re.search(r'booklet|tile scale|page scaling|print range|multiple pages|duplex|overlap', labels, re.I):
                        dialogs.append({'resource_id': entry.id or str(entry.name), 'language_id': lang.id,
                                        'rva': hex(d.OffsetToData), **parsed})
                except (struct.error, IndexError, ValueError) as exc:
                    errors.append({'resource_id': entry.id, 'language_id': lang.id, 'error': str(exc)})
    result = {'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(), 'size': len(raw),
              'machine': hex(pe.FILE_HEADER.Machine), 'image_base': hex(pe.OPTIONAL_HEADER.ImageBase),
              'versions': versions, 'imports': imports, 'exports': exports, 'feature_strings': strings,
              'selected_dialogs': dialogs, 'dialog_count': total_dialogs, 'dialog_parse_errors': errors,
              'limitations': ['Static observations only; no Windows execution or signature validation.',
                              'ASCII/ASCII-range UTF-16 feature strings only; not all languages or compressed resources.',
                              'Names and resources do not establish runtime behavior.']}
    output.mkdir(parents=True, exist_ok=True)
    (output / (path.stem + '-pe.json')).write_text(json.dumps(result, indent=2, ensure_ascii=False) + '\n')
    if path.name == 'FoxitPDFReader.exe':
        controls = {10400: 'Booklet subset', 10399: 'Booklet binding', 10388: 'Poster cut marks',
                    10389: 'Poster labels', 10424: 'Booklet mode', 10427: 'Tile large pages mode',
                    10394: 'Duplex checkbox'}
        messages = []
        for cid, label in controls.items():
            for code in (0, 1, 0x200, 0x300):
                pattern = struct.pack('<IIII', 0x111, code, cid, cid)
                for match in re.finditer(re.escape(pattern), raw):
                    signature, address = struct.unpack_from('<II', raw, match.end())
                    section = pe.get_section_by_rva(address - pe.OPTIONAL_HEADER.ImageBase)
                    if not section or not section.Characteristics & 0x20000000 or signature >= 256:
                        continue
                    messages.append({'control_id': cid, 'label': label, 'wm_command_code': hex(code),
                                     'signature_enum': signature, 'message_map_file_offset': hex(match.start()),
                                     'handler_va': hex(address)})
                    assembly = subprocess.check_output(['objdump', '-d', '--start-address=' + hex(address),
                                                        '--stop-address=' + hex(address + 256), str(path)], text=True)
                    (output / f'foxit-control-{cid}-{hex(code)}.asm.txt').write_text(assembly)
        (output / 'foxit-print-message-map.json').write_text(json.dumps(messages, indent=2) + '\n')
    if path.name == 'UPDFKit.dll':
        selected = ['PDFTextSearcher_FindNext', 'PDFTextSearcher_FindPrev', 'PDFTextSearcher_GetBounds',
                    'PDFTextSearcher_GetCurrentTextPageRotationAndBoundingBox', 'PDFText_SelectAllQuads']
        functions = []
        for item in exports:
            if item['name'] not in selected or item['forwarder']: continue
            address = pe.OPTIONAL_HEADER.ImageBase + int(item['rva'], 16)
            next_addresses = [int(e['rva'], 16) + pe.OPTIONAL_HEADER.ImageBase for e in exports
                              if not e['forwarder'] and int(e['rva'], 16) + pe.OPTIONAL_HEADER.ImageBase > address]
            stop = min(min(next_addresses, default=address + 4096), address + 4096)
            assembly = subprocess.check_output(['objdump', '-d', '--start-address=' + hex(address),
                                               '--stop-address=' + hex(stop), str(path)], text=True)
            (output / (item['name'] + '.asm.txt')).write_text(assembly)
            functions.append({'name': item['name'], 'start_va': hex(address), 'stop_va': hex(stop),
                              'boundary': 'next exported address or 4096-byte cap; not a proved function boundary'})
        (output / 'updf-selected-function-ranges.json').write_text(json.dumps(functions, indent=2) + '\n')
    print(path.name, 'dialogs:', total_dialogs, 'selected:', len(dialogs), 'parse errors:', len(errors),
          'feature strings:', len(strings))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='+', type=Path)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    for path in args.paths: inspect(path, args.output)

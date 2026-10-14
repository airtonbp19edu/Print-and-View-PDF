# Print&View PDF 3.4.0: entrega e validação

A 3.4.0 consolida a base Winux 3.3.11 com a busca progressiva, geometria
CropBox/rotação e apresentação do Print&View. Os formatos são Debian `all`,
Flatpak `x86_64` e instalador Windows com runtime `x64`. Não há sufixo de teste.

## Mudanças

Recuperados da 3.3.11: controle de aparência/GSettings e CSS escuro dedicado,
faces navegáveis do livreto, marcas de encaixe de pôster, JPEG de tela,
cancelamento do Poppler, limites de recursos e validações CUPS. O seletor de
tema corrige a reentrada das notificações GTK e migra a preferência Winux.

Busca combina os trechos/painel/rolagem com extração progressiva por página,
cache limitado, acentos e hifenização. Os realces continuam por retângulos de
palavra, sem geometria exata de caracteres inclinados ou OCR. O painel exibe
até 350 resultados; a navegação mantém até 5.000.

Apresentação oferece página inteira, preencher e leitura 250%/topo. Mantém
imagem anterior durante carregamento e informa falhas. A renderização normal
não cancela pedidos idênticos em andamento; a correção evita a interrupção
contínua causada por notificações de tamanho sem mudança efetiva.

O pypdf embutido passou a 6.20.1, com artefato fixado e SHA-256 conferido com
PyPI. Foram restaurados os hooks Debian e registros de licença. Isso não
constitui certificação de segurança de todo o aplicativo.

## Formatos e compilação

| Formato | Implementação |
|---|---|
| `.deb` | Fontes Python e ícones; dependências GTK/Poppler/CUPS fornecidas pela distribuição; hooks de desktop/ícones/bytecode |
| `.flatpak` | Repositório OSTree/bundle real, com Python 3.13 e runtime GTK/Poppler/CUPS do Debian 13; loader/libc pareados, base Freedesktop 25.08 |
| `.exe` | Instalador NSIS por usuário, Python 3.14.0, GTK 3/Gvsbuild e Poppler Windows; lança a mesma interface e usa impressão nativa |

O Flatpak é um bundle para instalação local, não uma submissão ao Flathub.
O instalador NSIS tem stub PE de 32 bits e instala executáveis/dependências
**x64**, para Windows 10/11 x64. Não possui assinatura Authenticode.

Com as ferramentas e bibliotecas exigidas instaladas:

```bash
/usr/bin/python3 scripts/build_deb.py
python3 scripts/build_flatpak.py --extra-runtime /caminho/runtime-overlay
python3 scripts/build_windows.py --downloads /caminho/downloads --makensis makensis
```

O builder Flatpak é específico do ambiente Debian 13: copia os executáveis
ELF reais de `/usr/bin`, bibliotecas e bindings GI/Cairo compatíveis. O overlay
precisa de `gi-cairo/` se o adaptador não estiver instalado no sistema, e de
`usr/bin/lp`, `lpstat`, `lpoptions` se CUPS client não estiver instalado.
Uma pasta de stage existente é preservada; use outra pasta para uma nova
compilação. NSIS em instalação local pode precisar de `NSISDIR`.

Artefatos Windows têm URLs e SHA-256 fixados em
[windows-artifacts.json](../packaging/windows-artifacts.json). Os ZIPs GTK e
Poppler foram comparados aos digests publicados nos releases GitHub; wheels
Python foram comparados aos hashes PyPI. O pacote CPython NuGet foi obtido por
HTTPS e seu hash foi fixado para reprodução; não se afirma verificação da
assinatura NuGet/Authenticode. GTK, Python, Poppler e dependências mantêm seus
avisos/licenças, separados da licença MIT da aplicação.

## Verificações e limites

- **27 testes** no código final: passaram, sem ignorados, com GTK/Poppler reais.
- **27 testes no conteúdo extraído do `.deb`**: passaram, sem ignorados,
  usando `PRINT_VIEW_TEST_APP` apontando para a extração.
- **27 testes no runtime do Flatpak**: passaram, executados com seu Python/GTK incluído,
  fora do sandbox; não equivale a instalação e execução pelo `flatpak run`.
- Windows/Wine: abertura de PDF de quatro páginas, renderização, busca com
  quatro ocorrências e painel, geração de livreto; resultados em
  [windows-smoke-3.4.0.json](windows-smoke-3.4.0.json).
- Hooks/controle Debian, estrutura OSTree e inventário NSIS inspecionados.

A política de rede bloqueou o download do runtime Freedesktop do Flathub
neste ambiente. O bundle foi gerado, mas sua instalação/execução no sandbox
não foi validada. Impressão física, propriedades de todos os drivers, Windows
nativo e desempenho em PDFs pesados permanecem sem validação nesta entrega.

Os limites POSIX de CPU/memória usam `resource`/`prlimit` quando disponíveis
no Linux; o Windows usa timeout e cancelamento do processo Poppler, sem aplicar
esses mesmos limites POSIX. A impressão Windows rasteriza as páginas a 180 dpi
no diálogo nativo; não promete preservar vetores no spooler como a saída CUPS.

## Origem e histórico

A revisão anterior descreve o estado **antes** da consolidação. Seus testes
sobre o Winux 3.3.11 original permanecem úteis: reproduzem o defeito original
do tema automático, enquanto a suíte atual verifica sua correção. Os pacotes
antigos `~test` são históricos. Consulte [PROVENIENCIA](PROVENIENCIA.md),
[REVISAO-HISTORICO-WINUX](REVISAO-HISTORICO-WINUX.md) e
[engenharia reversa](ENGENHARIA-REVERSA-FOXIT-UPDF.md).

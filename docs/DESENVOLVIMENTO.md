# Desenvolvimento

## Ambiente Linux

O aplicativo usa Python, GTK 3, GI/Cairo, Pillow, cryptography, Poppler e CUPS.
O pypdf está incluído em app/vendor; não é necessário instalá-lo por pip.

```bash
sudo apt update
sudo apt install python3 python3-gi python3-gi-cairo python3-cairo gir1.2-gtk-3.0 python3-pil python3-cryptography poppler-utils cups-client fonts-dejavu-core adwaita-icon-theme librsvg2-common
git clone https://github.com/airtonbp19edu/Print-and-View-PDF.git
cd Print-and-View-PDF
bash scripts/run.sh /caminho/documento.pdf
```

Para abrir a prévia das preferências com um perfil separado:

```bash
python3 scripts/preview_preferences.py
```

## Testes

Em uma sessão gráfica:

```bash
/usr/bin/python3 -m unittest discover -s tests -v
```

Em ambiente sem desktop, use Xvfb:

```bash
sudo apt install xvfb xauth dbus-x11
GSETTINGS_BACKEND=memory xvfb-run -a dbus-run-session -- /usr/bin/python3 -m unittest discover -s tests -v
```

O workflow Linux executa essa suíte em pushes para main e pull requests. A
validação do pacote Flatpak exige também instalar o bundle e testar dentro do
sandbox; o workflow da fonte não a substitui. As evidências da release estão
em [validation/3.4.1](validation/3.4.1/README.md).

## Pacote Debian

```bash
/usr/bin/python3 scripts/build_deb.py
```

O arquivo é escrito em dist/. A instalação pode ser conferida em um ambiente
de teste com apt, sem substituir a instalação de trabalho.

## Bundle Flatpak

O empacotador atual requer **Debian 13 x86_64 com Python 3.13**. Ele inclui o
runtime Python/GTK do sistema e usa org.freedesktop.Platform/x86_64/25.08.

```bash
sudo apt install flatpak python3-cffi libgdk-pixbuf2.0-bin librsvg2-common
mkdir -p .runtime/overlay/gi-cairo/usr/lib/python3/dist-packages/gi
cp /usr/lib/python3/dist-packages/gi/_gi_cairo*.so .runtime/overlay/gi-cairo/usr/lib/python3/dist-packages/gi/
python3 scripts/build_flatpak.py --extra-runtime .runtime/overlay
```

O diretório de staging deve estar vazio. Para novas construções, informe
--stage e --repo com outros caminhos; o script preserva diretórios existentes.
As bibliotecas privadas, o carregador ELF, o wrapper Python e o provedor
OpenSSL precisam permanecer juntos.

## Prévia Windows

Use uma instalação PrintViewPDF que contenha python/, gtk/ e poppler/. Se ela
não estiver em LocalAppData/Programs/PrintViewPDF, defina PRINT_VIEW_RUNTIME.

```powershell
$env:PRINT_VIEW_RUNTIME = 'C:\caminho\PrintViewPDF'
.\scripts\preview-preferences.cmd
```

A prévia usa um perfil separado em .runtime/preferences-preview. O executável
Windows publicado permanece na versão 3.4.0; gerar um novo instalador requer
uma rodada Windows própria. O histórico da prévia e de seus limites está no
[guia de preferências](PREFERENCIAS-PRIMEIRA-IMPLEMENTACAO.md).

## Publicar versões

Atualize app/version.py, metainfo, CHANGELOG e notas de entrega. Construa e
valide os artefatos; publique-os como assets de uma GitHub Release com um
SHA256SUMS específico da versão. Os novos instaladores não são adicionados ao
histórico Git. Os artefatos antigos já rastreados são preservados em packages/.

Configurações pessoais de agentes, ambientes temporários, chaves, caches e
registros de migração local ficam fora do repositório publicado.

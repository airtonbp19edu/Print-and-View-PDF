# Print&View PDF

Print&View PDF é a continuação do Winux PDF: um leitor com busca progressiva,
apresentação e preparação de impressão em livreto, pôster e várias páginas
por folha. A versão **3.4.0** consolida os recursos da Winux **3.3.11** com as
melhorias do Print&View, sem sufixo de teste.

## Downloads

| Sistema | Pacote |
|---|---|
| Debian/Ubuntu | [print-view-pdf_3.4.0_all.deb](packages/print-view-pdf_3.4.0_all.deb) |
| Linux com Flatpak, x86_64 | [PrintViewPDF-3.4.0-x86_64.flatpak](packages/PrintViewPDF-3.4.0-x86_64.flatpak) |
| Windows 10/11, x64 | [PrintViewPDF-3.4.0-Setup-x64.exe](packages/PrintViewPDF-3.4.0-Setup-x64.exe) |

Confira a integridade em [SHA256SUMS](packages/SHA256SUMS). Os pacotes antigos
com `~test` permanecem como histórico; use os arquivos **3.4.0** acima.

## Recursos

- Busca com painel de resultados, trechos de contexto, navegação e rolagem até
  a ocorrência; opções de caso, palavra inteira, acentos e hifenização.
- Temas claro, escuro e automático, com preferência persistida e migração da
  escolha antiga do Winux. O ciclo de notificações do tema automático foi corrigido.
- Apresentação com página inteira, preenchimento centralizado acima dos controles
  e opção de leitura a 250% começando no topo; zoom, pan e laser.
- Renderização JPEG para a tela, cache de vizinhos e cancelamento ativo de pedidos
  obsoletos. Pedidos idênticos em andamento não são reiniciados por notificações
  repetidas de tamanho. A apresentação mantém a imagem anterior e mostra falhas.
- Seleção e cópia por palavras, miniaturas, marcadores, comentários e consulta
  de camadas; exportação de PNG e salvamento de PDF preparado.
- Impressão em tamanho, N-up, livreto e pôster. A prévia do livreto permite
  navegar por todas as faces, respeitando frente/verso e encadernação.

No Linux, a impressão usa CUPS. No Windows, o documento preparado é enviado
pelo diálogo nativo de impressão; propriedades avançadas dependem do driver.
O tema escuro afeta a interface, sem inverter as cores das páginas.

## Instalar

Debian/Ubuntu:

```bash
sudo apt install ./packages/print-view-pdf_3.4.0_all.deb
```

O pacote substitui `winux-pdf` e instala as dependências do leitor. A associação
padrão de arquivos PDF não é alterada automaticamente.

Flatpak:

```bash
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user flathub org.freedesktop.Platform//25.08
flatpak install --user ./packages/PrintViewPDF-3.4.0-x86_64.flatpak
flatpak run io.github.airtonbp19edu.PrintViewPDF
```

O bundle inclui Python, GTK e ferramentas PDF; o runtime base do Freedesktop
é instalado pelo Flatpak. Ele acessa a pasta pessoal para abrir/salvar PDFs,
o display e o CUPS/rede para impressão. Isso não é publicação no Flathub.

No Windows, execute o instalador `.exe`. Python, GTK e Poppler estão incluídos;
a instalação é por usuário, sem exigir privilégios de administrador. O
instalador não possui assinatura Authenticode.

## Desenvolvimento

No Debian/Ubuntu, instale Python do sistema, GTK 3, GI/Cairo, Pillow,
cryptography, Poppler e CUPS client, então execute:

```bash
bash scripts/run.sh /caminho/documento.pdf
/usr/bin/python3 -m unittest discover -s tests -v
/usr/bin/python3 scripts/build_deb.py
```

Os testes gráficos exigem `DISPLAY`. O pypdf **6.20.1** está fixado em
`app/vendor` com sua licença preservada. Outros formatos são gerados por
[scripts/build_flatpak.py](scripts/build_flatpak.py) e
[scripts/build_windows.py](scripts/build_windows.py); consulte
[empacotamento e validação](docs/ENTREGA-3.4.0.md).

As verificações automatizadas não substituem impressão física nem validação
com documentos grandes. O conteúdo do Flatpak foi exercitado fora do sandbox;
a instalação no sandbox requer validação na distribuição de destino. O
runtime Windows foi exercitado no Wine, sem certificar comportamento em todo
Windows/driver. Veja os resultados e limites em [ENTREGA-3.4.0](docs/ENTREGA-3.4.0.md).

A referência é o desenvolvimento próprio do Winux. A
[análise estática do Foxit e UPDF](docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md) é parcial;
não há alegação de equivalência completa nem código ou recursos desses leitores
incorporados à aplicação. A [revisão histórica](docs/REVISAO-HISTORICO-WINUX.md)
registra a evolução dos 18 pacotes e a origem dos recursos.

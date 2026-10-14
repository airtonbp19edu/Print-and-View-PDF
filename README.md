# Print-and-View-PDF
Print&View PDF é a continuação do Winux PDF para Linux, com interface GTK 3,
renderização Poppler e impressão pelo CUPS. A base recuperada é a **3.3.5**;
esta versão para teste é a **3.3.7~test1**, sem incorporar a 3.3.10 mencionada
no histórico, cujo código não foi fornecido.

## Executar em Debian/Ubuntu

```bash
sudo apt-get install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
  python3-cairo python3-cryptography python3-pil poppler-utils cups-client
bash scripts/run.sh /caminho/documento.pdf
```

Use o Python do sistema (`/usr/bin/python3`) para carregar os bindings GTK.
É necessária uma sessão gráfica para a aplicação. O pypdf 6.10.0 original
está preservado em `app/vendor`, com sua licença em `docs/pypdf-LICENSE.txt`.

## Testar e empacotar

```bash
/usr/bin/python3 -m unittest discover -s tests -v
/usr/bin/python3 scripts/build_deb.py
```

Os dois testes GTK exigem `DISPLAY`; sem sessão gráfica, são explicitamente
ignorados. Os demais exercitam geração de PDFs e renderização real com Poppler.
O pacote é gerado em `dist/print-view-pdf_3.3.7~test1_all.deb`.
Uma cópia para download acompanha o código em `packages/`. Para instalar:

```bash
sudo apt install ./packages/print-view-pdf_3.3.7~test1_all.deb
```

O novo pacote substitui `winux-pdf` (não deve coexistir com ele). A associação
de PDFs como aplicativo padrão não é alterada automaticamente. Os logs novos
usam `~/.cache/print-view-pdf`, preservando os antigos do Winux.

## Mudanças desta etapa

- Identidade Print&View PDF no aplicativo, launcher, pacote e menu do sistema.
- Cache de imagens distingue caminho e metadados do arquivo de origem.
- Busca retorna coordenadas por ocorrência, com realces e navegação individual.
- Busca por página com resultados progressivos, descarte de pesquisas substituídas
  e cache limitado a 64 mapas de página por documento.
- Controles de maiúsculas/minúsculas, palavra inteira, ignorar acentos e unir
  palavras hifenizadas entre linhas do mesmo bloco.
- Seleção concluída realça as palavras e respeita linhas/blocos do Poppler ao copiar.
- CropBox e rotação interna do PDF são considerados nas dimensões de leitura.
- Livreto compartilha seleção de frente/verso e encadernação entre motor e prévia.
- Impressão de apenas frente ou verso usa passagem manual sem duplex automático.
- A entrada N-up fracionária é rejeitada também pela API de preparação.

Consulte [o roteiro de teste](docs/TESTAR-3.3.7.md),
[a análise e as limitações](docs/ANALISE.md) e
[a proveniência da base](docs/PROVENIENCIA.md). Não há alegação de equivalência
com Foxit ou UPDF: a análise estática dos aplicativos completos está registrada
em [engenharia reversa](docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md), mas a comparação
dinâmica no Windows ainda está pendente.

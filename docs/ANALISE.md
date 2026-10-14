# Print&View PDF: análise da base e referências

**Entrega atual:** a 3.4.0 consolida Winux 3.3.11; consulte
[ENTREGA-3.4.0](ENTREGA-3.4.0.md). A análise da base 3.3.5 abaixo é histórica.

**Atualização:** os leitores completos agora estão acessíveis e foram analisados
estaticamente. Consulte [a análise atual de Foxit e UPDF](ENGENHARIA-REVERSA-FOXIT-UPDF.md).
As limitações de acesso descritas abaixo registram a primeira etapa; não são
mais o estado atual dos ZIPs do Google Drive.

## Resultado da primeira etapa

Foi recuperado o código real do Winux PDF **3.3.5** e criada sua continuação
Print&View PDF **3.3.6**. A engenharia reversa dos dois leitores Windows
**não está concluída**. Do UPDF foi possível examinar somente um instalador
online; o Foxit ainda não pôde ser transferido. Não se infere funcionamento
de um leitor a partir do funcionamento de seu instalador.

## Arquitetura recuperada

| Componente | Responsabilidade observada |
|---|---|
| `app/main.py` | Janela GTK 3, navegação, ferramentas, busca, seleção e coordenação da impressão |
| `app/async_core.py` | Pool de threads e descarte de callbacks obsoletos por canal |
| `app/rendering.py` | Poppler via `pdftocairo` e `pdftotext`; metadados com pypdf |
| `app/print_window.py` | Controles e desenho da prévia de tamanho, N-up, livreto e pôster |
| `app/imposition.py` | Composição vetorial e exportação do PDF preparado |
| `app/worker_cli.py` | Preparação em subprocesso e impressão raster página a página |
| `app/cups_backend.py` | Impressoras, capacidades/PPD e envio com `lp` |
| `app/presentation.py` | Apresentação, cache e pré-carregamento de páginas vizinhas |
| `app/pdf_panels.py` | Extração de marcadores, comentários e nomes de camadas |

O desenho do Winux é adequado como ponto de partida: interface e trabalho
pesado separados, impressão própria sobre CUPS e imposição vetorial. Ainda
há duplicação de geometria entre o desenho de algumas prévias e o PDF real.

## Falhas reproduzidas e mudanças

| Evidência na base 3.3.5 | Efeito | Correção e validação |
|---|---|---|
| Cache identificado apenas por chave/página/largura | Abrir outro documento com a mesma página e zoom pode retornar a imagem do primeiro | Caminho e identidade/metadados do arquivo participam da chave; teste com PDFs diferentes |
| `search_text` retorna somente índices de página | Ocorrências na mesma página não têm localização nem realce individual | Busca sobre palavras/bounding boxes do Poppler; teste de coordenadas distintas, acentos, Unicode e navegação GTK |
| Seleção agrupa linhas pela diferença de Y e desenha um retângulo único | Cópia e aparência não respeitam necessariamente os blocos reais | Uso de identificadores de linha/bloco e realce das palavras concluídas; teste GTK de seleção |
| Prévia e miniaturas de livreto usam sempre `booklet_pairs(...)[0]` | Selecionar verso não troca as páginas mostradas, embora o PDF preparado filtre versos | Uma seleção compartilhada atende motor, prévia e miniaturas; teste de ambos os lados e encadernação direita |
| Auto-duplex sobrepõe `sides` mesmo com somente verso/frente | Passagem manual pode ser enviada como duplex | Passagens filtradas usam `one-sided`; teste do comando CUPS com subprocesso simulado |
| Dimensões do leitor ignoram rotação interna e render não pede CropBox | Proporções/coordenadas divergem em PDFs recortados ou rotacionados | Renderização CropBox e dimensões orientadas; teste real de PDF recortado e rotação de 90° |
| Dispatcher converte N-up em inteiro antes da validação | `4.9` é silenciosamente convertido em `4` | Valor original chega ao validador; teste de rejeição |

Busca ainda é **textual, sem OCR**. É limitada a 5.000 ocorrências e respeita
blocos de texto do Poppler para evitar unir colunas ou parágrafos distintos.
Realça palavras inteiras que contêm a ocorrência; não oferece ainda seleção
por caracteres, deshifenização, expressões regulares ou índice incremental.
Não se declara equivalência com a busca do Foxit.

## UPDF: observações confirmadas

- O arquivo enviado é um PE x86 com contêiner NSIS, não o leitor `UPDF.exe`.
- O executável de downloader extraído tem dependências Qt 6 Core/Gui/Widgets/
  Network, além de bibliotecas de transporte. Isso descreve **o instalador**;
  não estabelece que o leitor completo use essa mesma arquitetura.
- Há strings com URLs de pacotes completos em `download.updf.com`,
  `download.superace.com` e `download.updf.cn`. São possíveis próximos
  artefatos de análise; o nome/versão do arquivo recebido não garante que
  essas URLs estáticas correspondam exatamente à mesma versão do leitor.
- Os recursos observados são de instalação, download, idioma, inicialização
  e associação de arquivos. Não foram encontrados os componentes necessários
  para validar leitura, seleção, pesquisa ou impressão do aplicativo completo.
- Foi obtida Evidence do REA para o instalador, sem execução. Inventário de
  diretório por essa rota do REA foi rejeitado; a lista dos 83 arquivos vem
  da extração/listagem do 7-Zip, não de uma análise de diretório bem-sucedida.

## Comparação funcional pendente

| Fluxo desejado | Print&View atual | Foxit / UPDF |
|---|---|---|
| Leitura, zoom, rotação e ferramentas | Base recuperada e abertura/renderização exercitadas | Aplicativos completos ainda não disponíveis |
| Busca/seleção com realces precisos | Primeira correção validada com PDFs de teste | Comparação de interação/ordem de leitura pendente |
| Livreto frente/verso | Motor e seleção da prévia validados | Comportamento de passagem manual pendente |
| N-up e pôster | PDFs reais gerados e contagens verificadas | Regras/limites/margens de referência pendentes |
| Impressão física | Integração CUPS preservada; comando duplex testado por mock | Sem impressora nem sessão Windows |
| Camadas | Listadas, sem alterar visibilidade | Não comparado |
| Temas e múltiplos documentos | Não validados integralmente; uma única instância de documento no código | Não comparado |

## Validação executada

Dez testes passaram, **sem skips**, em Python do sistema, GTK 3 e display Xorg
dummy. O adaptador GI/Cairo que faltava ao ambiente foi preparado localmente.
Os testes gráficos abrem PDFs e exercitam busca/seleção, desenho da prévia,
miniaturas e envio dos parâmetros do livreto. Os testes de motor criam e
reabrem PDFs para conferir ordenação, lados, encadernação e quantidade de
folhas N-up/pôster, além de renderizar CropBox com Poppler.

Na base original, a primeira suíte reproduziu dois failures (cache e duplex)
e um erro de contrato (busca sem coordenadas); livreto gerado e contagens de
N-up/pôster já passavam. A prévia foi diagnosticada pelo código e exercitada
em GTK após a correção. Os testes não medem latência com PDFs grandes e não
substituem validação em impressora física ou no Windows.

## Continuidade prioritária

1. Obter Foxit e a instalação completa do UPDF; registrar versões, hashes,
   arquivos, imports e recursos antes de decompilar módulos relacionados a
   leitura e impressão. Nenhum binário deve entrar no produto Linux.
2. Reproduzir em sessão Windows os mesmos PDFs e ações: seleção, busca com
   múltiplas colunas, navegação rápida, livreto/manual-duplex, pôster e N-up.
   Guardar entradas, saídas, screenshots e configurações do trabalho.
3. Comparar geometria do preview com o **PDF preparado**. Expandir primeiro
   N-up em todas as ordens e tamanho real; atualmente há desenhos separados
   que não garantem correspondência geométrica exata. O livreto ainda mostra
   apenas a primeira face selecionada, sem navegação de todas as folhas.
4. Medir cache e fila de renderização com PDFs reais. A fila do executor
   ainda não é limitada e descartar callbacks não cancela trabalho em execução.
   Cache em disco ainda não tem orçamento global; não há benchmark que prove
   navegação equivalente ao Windows.
5. Validar temas, carregamento de várias abas reais, camadas, seleção por
   caracteres e PDFs sem texto antes de expor novos controles.
6. Auditar limites de recursos, arquivos malformados, cancelamento e limpeza
   de processos. Não foi feita uma auditoria completa de segurança.

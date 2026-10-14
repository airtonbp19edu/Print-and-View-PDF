# Engenharia reversa estática: Foxit e UPDF

## Resultado e alcance

Agora foi possível acessar os **leitores completos** fornecidos na pasta do
Google Drive. Foram examinados os executáveis, imports/exports, recursos de
diálogos, strings com endereços e trechos de assembly relacionados a busca e
impressão. Esta análise supera a etapa anterior, limitada ao instalador UPDF.

É uma análise **parcial e estática**, não uma reconstrução integral dos produtos.
Nenhum programa Windows foi executado. Não foi recuperado código-fonte original,
e não foram medidos desempenho, latência, fidelidade visual ou impressão física.
O código da aplicação Print&View não foi alterado nesta rodada: foram adicionadas
evidências e uma ferramenta de análise reproduzível.

## Artefatos observados

| Arquivo | Versão nos recursos PE | Arquitetura | SHA-256 |
|---|---|---|---|
| FoxitPDFReader.exe | 2025.2.0.33046 | x86 | `90208c9e8da92c8e546b76c8f4a2f8fb999105d124e663bbea6744fb6bb6b3a6` |
| UPDF.exe | 2.5.10.0 | x64 | `c801ae470d42d8aecb0069a3dafe2e9df6c0dbb59c4c843c35f55fc13c64adc0` |
| UPDFKit.dll | 1.0.0.575 | x64 | `6c06354f9307606db5f77be8e0e4d25cfc0c096894cc0545f34e0b255e2783d5` |

São versões **declaradas pelos arquivos**, não autenticação da origem. A tabela
de versão do Foxit também contém a versão de um componente de correção
ortográfica; ela não deve ser confundida com a versão do leitor.

Os ZIPs baixados anteriormente passaram em `ZipFile.testzip()` e contêm:

- Foxit: 3.539 entradas, 3.276 arquivos; ZIP SHA-256
  `51b6e7b68866aa03f588127f8f9fbcb0b2c91e00ae2d0900c0ce182d293a1bdf`.
- UPDF: 694 entradas, 653 arquivos; ZIP SHA-256
  `0d225d73f0c9ca0f50a81fc5440c8226090073a8ff38f9be2a0f14b61e2bf85d`.

A pasta foi consultada novamente com HTTP 200 e agora também lista diretórios
extraídos e executáveis avulsos. Nesta rodada foram usados os ZIPs já baixados,
com hashes conhecidos; não se afirma que os arquivos avulsos ou as novas pastas
sejam byte a byte iguais. A extração foi realizada fora do checkout, verificando
que os caminhos de cada entrada permaneciam dentro do destino.

## Foxit: impressão rastreada do controle ao código

O executável utiliza recursos de janela Win32 e estruturas compatíveis com
message maps do MFC. A referência de layout é nativa de Windows; não se trata
de um aplicativo Electron que possa ser copiado ou executado diretamente no Linux.

Foram decodificados **405 recursos de diálogo, sem erro de parsing** nessa
amostra. Seis foram selecionados por termos relacionados a impressão. Coordenadas
extraídas estão em *dialog units* do Windows, não pixels nem medidas de papel.

| Recurso | Observação confirmada |
|---|---|
| Diálogo 7792, `Print` | 65 controles, quatro modos: Scale, Tile Large Pages, Multiple Pages Per Sheet e Booklet; duplex separado com borda longa/curta; auto-rotação e auto-centralização |
| Diálogo 7786 | Controles de binding, booklet subset e margens do livreto |
| Diálogo 7790 | Zoom da página, overlap, unidade, cut marks e labels do mosaico |
| Diálogo 7794, `Batch Print` | Lista de documentos, ordenação, modos de impressão e opções de duplex |

Isso confirma a organização dos controles da versão fornecida. Não prova,
isoladamente, que todos funcionem corretamente ou quais sejam os valores padrão.

### Seletor de lados do livreto

O controle **10400** do diálogo 7786 foi ligado a uma entrada de message map:

- Offset de arquivo da entrada: `0x4fdb798`.
- Mensagem `WM_COMMAND = 0x111`, notificação `CBN_SELCHANGE = 1`.
- Endereço virtual do handler: **`0x016dfb10`**.
- O handler chama o import `USER32!SendMessageW`, com `CB_GETCURSEL = 0x147`.
- Se o retorno for 0, 1 ou 2, grava esse mesmo valor no campo `+0xcc` de um
  objeto referenciado pelo diálogo. Não se atribui significado a cada número
  sem conferir os itens da combo e o consumidor da configuração.
- Depois passa por conversões de tipo compatíveis com `CReader_DlgPrinter` e
  `CReader_DlgBatchPrint` (nomes confirmados em RTTI) e chama rotinas de
  atualização em `0x016772e0` e `0x0168fbd0`, conforme o tipo disponível.

Portanto, **a seleção atualiza um estado compartilhado e notifica a janela
de impressão**. A interpretação de que todas as folhas da prévia são recalculadas
precisa de análise adicional das rotinas chamadas ou de teste no Windows.

O controle **10399** de binding aponta para `0x016dfa50`. Seu handler mapeia
índice 0 para valor 1 e índice 1 para valor 0 no campo `+0xd0`, limpa outros
dois campos (`+0xdc` e `+0xe4`) e segue rotas de atualização semelhantes.
Não se presume qual valor corresponde a esquerda/direita somente pelo número.

Também foram rastreados controles de marcas de corte, etiquetas, seleção de
modo livreto, modo mosaico e checkbox duplex. No handler de marcas de corte
`0x016dc5f0`, há cópia de estado para o campo `+0x84` de um objeto de opções
e uma chamada virtual após obter a janela de impressão. O handler de etiquetas
usa o campo adjacente `+0x88`. Isso demonstra fluxo de estado; ainda não reconstrói
a geometria dos desenhos ou a geração do trabalho de impressão.

**Aplicação ao Print&View:** reforça a correção já feita para compartilhar
a seleção de lados entre motor e prévia. A próxima melhoria é permitir navegar
por todas as faces do PDF preparado e usar a mesma geometria para prévia e saída,
em vez de apenas desenhar a primeira face selecionada.

## UPDF: separação entre interface e biblioteca PDF

No **leitor completo**, e não apenas no downloader, foram confirmados imports
de `Qt6Widgets`, `Qt6Gui`, `Qt6PrintSupport`, `UPDFKit.dll` e bibliotecas
auxiliares. Há imports atrasados adicionais registrados no JSON. A presença
de uma biblioteca na pasta não significa que ela seja usada pelo caminho examinado.

`UPDFKit.dll` exporta **1.315 entradas**. O executável importa, entre outras:

- Busca: `PDFPage_LoadTextSearcher`, `PDFTextSearcher_FindNext`,
  `PDFTextSearcher_GetBounds`, `PDFTextSearcher_GetCurrentTextBounds` e funções
  para obter texto por palavras.
- Seleção: `PDFText_GetQuads`, `PDFText_SelectRangeQuads` e
  `PDFText_GetBlockQuadPoints`.
- Renderização: `PDF_RenderPageBitmap`, `PDF_RenderPageHDC`,
  `PDF_RenderPageRectToBitmap_Start`, `PDF_RenderPage_Continue` e
  `PDF_RenderPage_Close`.
- Impressão Qt: seleção da impressora, formatos de papel suportados,
  `QPrinter::setDuplex`, número de cópias, agrupamento e modo de cor.

Esses imports confirmam interfaces disponíveis à aplicação. A frequência,
ordem e condição de chamada ainda não foram observadas dinamicamente. Não se
atribui a marca de um motor PDF de terceiros apenas pelos nomes dessas APIs.

### Rotinas de busca examinadas em assembly

| Export da UPDFKit | Endereço virtual | Observação de código |
|---|---|---|
| `PDFTextSearcher_FindNext` | `0x180220b60` | Valida referências; chama busca interna; quando necessário incrementa um índice do objeto e compara com um limite antes de continuar |
| `PDFTextSearcher_FindPrev` | `0x180220be0` | Rotina correspondente de navegação reversa, salva para análise comparativa |
| `PDFTextSearcher_GetBounds` | `0x180220c60` | Calcula quantidade de elementos a partir de um intervalo de memória, com passo de 32 bytes; limita a cópia à capacidade recebida quando há buffer |
| `PDFTextSearcher_GetCurrentTextPageRotationAndBoundingBox` | `0x180221300` | Valida ponteiros, obtém um valor de rotação e grava também dados de bounding box nos parâmetros de saída |
| `PDFText_SelectAllQuads` | `0x180238da0` | Obtém intervalo de texto, constrói dados geométricos e passa um buffer/contagem a um callback |

Os offsets do objeto são observados; chamar o índice de `FindNext` de
"página atual" é uma inferência apoiada nos nomes das APIs adjacentes, não um
tipo de dados recuperado. O passo de 32 bytes não estabelece sozinho se os
elementos usam floats, doubles, retângulos ou outra estrutura. Não foram
reconstruídos os detalhes do algoritmo interno de busca, normalização ou cache.

**Aplicação ao Print&View:** a busca deve conservar posição por ocorrência,
identidade da página, rotação e geometria; seleção deve ter geometria por
trecho/quadrilátero, sobretudo para texto inclinado. Os retângulos por palavra
implementados na primeira etapa são uma melhoria inicial, não equivalência
com essa interface de seleção.

### Modelo de opções de impressão

Uma região de strings no arquivo, próxima ao offset **`0x14af400`**, contém:
`PaperSize`, `AutoRotate`, `AutoCenter`, `CopyCount`, `Collate`, `AsImage`,
`Colorgray`, `Reverseprint`, `PrintMode`, `SizeScale`, `SizeChoosePaper`,
`PosterScale`, `PosterOverlap`, `PosterLabels`, `PosterMarks`, `MultLCount`,
`MultRCount`, `MultOrder`, `MultPrintBorder`, `MultPrintCropLine`,
`BookletOrder`, `BookletBinding` e `BothSide`.

Esses nomes sugerem um modelo persistido de opções, incluindo linhas/colunas
N-up e presets. A persistência e todos os valores de enum não foram rastreados.
Também há strings de diagnóstico de `DEVMODE`, incluindo papel, orientação,
escala, resolução, cor, cópias e duplex. Isso evidencia uma fronteira de
configuração Windows; para Linux ela deve ser substituída por capacidades
CUPS/IPP, não transposta literalmente.

## Prioridades concretas para a continuação Linux

| Prioridade | Trabalho independente no Print&View | Evidência que o orienta |
|---|---|---|
| 1 | Um objeto de configuração normalizado compartilhado por controles, motor e prévia; navegação de todas as folhas/faces preparadas | Handlers Foxit, controles de prévia e conjunto de opções UPDF |
| 2 | Seleção de texto por faixa e geometria precisa, com transformação explícita de página/zoom/rotação | Imports e assembly das APIs de texto UPDFKit |
| 3 | Busca incremental por página, cancelável, conservando ocorrência e geometria | Navegação e objetos de busca UPDF; desempenho ainda deve ser medido |
| 4 | Melhorar auto-rotação, centralização, presets e ordenação N-up; verificar preview contra PDF exportado | Diálogos Foxit e strings de opções UPDF |
| 5 | Separar duplex automático de passagens manuais e refletir capacidades reais da impressora | Controles Foxit e imports QPrinter; Winux/CUPS usa outra plataforma |
| 6 | Renderização por regiões e orçamento de cache/fila medidos em PDFs pesados | APIs progressivas UPDF; sua utilização efetiva ainda precisa de rastreamento |

Não é necessário substituir a estrutura Winux pelo código dos programas Windows.
As implementações Linux devem usar a base própria e bibliotecas permitidas,
com equivalência demonstrada por entradas e saídas, sem incorporar binários,
ícones ou implementação proprietária ao aplicativo.

## Evidências, reprodução e limitações

As evidências estão em `docs/windows-evidence/`: metadados/imports/exports PE,
recursos de diálogo selecionados, strings com offset/RVA, message maps e
assembly dos pontos examinados. `pefile 2024.8.26` foi instalado em um diretório
de ferramentas fora da aplicação. Os assemblies foram obtidos com GNU objdump;
limites de 256 bytes para handlers Foxit podem incluir partes de funções vizinhas.
Para exports UPDF, o limite é o próximo endereço exportado ou 4.096 bytes;
isso também não é uma prova formal de fronteira de função.

O comando `inspect-with-objdump` descrito na documentação do checkout REA
**não está disponível** na CLI 6.4.0 instalada. Ele foi tentado e retornou
`COMMAND_NOT_FOUND`; não é contado como análise bem-sucedida. O fallback foi
objdump diretamente. `rea inspect-artifact` foi executado separadamente
nos executáveis para registrar Evidence de inventário/identidade do artefato.

Para repetir a leitura PE, na máquina preparada:

```bash
cd /workspace/Print-and-View-PDF
PYTHONPATH=/workspace/.pdf-analysis-python python3 scripts/analyze_windows_readers.py \
  '/workspace/pdf-reference-analysis/foxit/Foxit PDF Reader/FoxitPDFReader.exe' \
  /workspace/pdf-reference-analysis/updf/UPDF/UPDF.exe \
  /workspace/pdf-reference-analysis/updf/UPDF/UPDFKit.dll \
  --output docs/windows-evidence
```

Ainda são necessários testes Windows com os mesmos PDFs e configurações usados
no Linux, análise dos consumidores da imposição, benchmarks de navegação e
comparação dos trabalhos de impressão. Não se declara engenharia reversa
integral, compatibilidade binária, assinatura validada ou comportamento idêntico.

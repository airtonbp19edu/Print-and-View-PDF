# Print&View PDF 3.3.7~test1: versão de teste

Esta versão continua a base Winux 3.3.5 fornecida pelo autor. A 3.3.10 mencionada
no histórico não foi incorporada. Busca e impressão mantêm implementação própria
em Python/GTK/Poppler/pypdf/CUPS; não incluem o código dos leitores Windows.

## Instalar

Baixe `packages/print-view-pdf_3.3.7~test1_all.deb` do repositório. No diretório
do download, execute:

```bash
sudo apt install './print-view-pdf_3.3.7~test1_all.deb'
print-view-pdf '/caminho/seu-documento.pdf'
```

O APT resolve as dependências declaradas. O pacote substitui `winux-pdf`;
não deve coexistir com ele. A associação padrão de PDF não é alterada
automaticamente. Para voltar, é necessário reinstalar seu pacote Winux original.

## Busca: verificar com seus PDFs

1. Abra um documento com texto e pressione **Ctrl+F**. Busque uma palavra que
   apareça mais de uma vez na mesma página. Confira os realces, o contador e
   os botões Anterior/Próximo.
2. Ative **Palavra inteira**: por exemplo, `agir` deve excluir `reagir`.
3. Ative **Maiúsc./minúsc.**: `AÇÃO` e `ação` passam a ser consultas distintas.
4. Ative **Ignorar acentos**: `acao` deve localizar `ação`. Sem essa opção,
   a busca mantém os acentos. Não existe OCR nesta versão.
5. Ative **Unir hifenização** para buscar uma palavra dividida por hífen no
   final da linha. A união ocorre apenas dentro do mesmo bloco do Poppler.
   Ela pode unir um composto legítimo; por isso é uma opção desligada inicialmente.
6. Em um PDF grande, observe resultados surgindo antes da conclusão e o
   contador de páginas examinadas. Mude o termo durante a pesquisa e confira
   que resultados antigos não reaparecem.
7. Confira a posição do realce em zooms diferentes, rotação e PDFs com CropBox.
   Teste também duas colunas e seleção/cópia de texto.

Um máximo de 5.000 resultados é exibido, com indicação do limite. O cache
retém até 64 mapas de página. Consultas repetidas reutilizam os mapas presentes;
documentos maiores podem exigir nova extração de páginas que saíram do cache.
O cancelamento interrompe a busca entre páginas; um subprocesso Poppler já
iniciado termina a extração daquela página antes de parar. Não há benchmark
que demonstre desempenho equivalente ao Foxit/UPDF.

Os realces ainda são retângulos das palavras participantes, inclusive quando
a consulta é parte de uma palavra. Texto inclinado, ordem de leitura em PDFs
complexos, ligaduras e seleções por caractere precisam de validação adicional.

## Impressão

Teste primeiro **Salvar como PDF**, antes de usar papel:

- Livreto de 8 páginas, somente frente, somente verso e ambos os lados;
  confira que a prévia troca as páginas e que os PDFs preparados têm lados distintos.
- Encadernação esquerda/direita, N-up e pôster com sobreposição.
- Passagens manuais de frente/verso não devem usar duplex automático.

A prévia de livreto ainda exibe somente a primeira face selecionada. O motor
gera as faces restantes. A impressão física não foi validada neste ambiente.

## Registrar um problema

Informe distribuição Linux, versão do pacote, termo pesquisado, opções
marcadas, página, zoom e rotação. Envie um PDF de exemplo que possa compartilhar
e uma captura do resultado esperado/obtido. O log fica em
`~/.cache/print-view-pdf/diagnostics.log`.

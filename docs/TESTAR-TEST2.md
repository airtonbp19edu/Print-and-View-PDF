# Print&View PDF 3.3.7~test2

Atualização da test1 para apresentação, temas e navegação. Mantém as melhorias
de busca e impressão; continua baseada no Winux 3.3.5 fornecido.

```bash
sudo apt install './print-view-pdf_3.3.7~test2_all.deb'
```

O pacote atualiza a test1 e substitui o antigo `winux-pdf` quando instalado.

## O que mudou e como verificar

- **Tema:** selecione claro, escuro ou automático no topo da janela. Confira
  menus, campos, seleção e impressão. Feche e abra o aplicativo: a escolha deve
  continuar. A preferência é salva em `~/.config/print-view-pdf/preferences.json`
  (ou em `XDG_CONFIG_HOME`). Automático acompanha o tema GTK reconhecido.
  O conteúdo do PDF permanece com suas cores originais.
- **Apresentação (F5):** Página inteira usa o espaço disponível acima dos
  controles, sem reservar os antigos 20% extras em retrato. Preencher tela
  amplia para ocupar a área, podendo cortar bordas; arraste ou use a roda para
  alcançá-las. Verifique retrato, paisagem e formatos diferentes no mesmo PDF.
  Tab oculta os controles, Escape fecha a apresentação.
- **Navegação:** a página atual tem uma fila de renderização independente de
  miniaturas, busca e pré-carregamento. Imagens decodificadas são reutilizadas
  e páginas anterior/próxima são pré-carregadas. Pedidos de renderização que
  ainda estavam na fila são descartados quando substituídos. Uma renderização
  em execução não é encerrada à força; ela pode continuar consumindo tempo.
- **Tela preta:** a apresentação exibe carregamento ou erro de renderização,
  conserva a imagem anterior enquanto carrega e pinta branco sob a página
  para imagens transparentes. Erros deixaram de ser silenciosos. Uma janela
  inicial sem enquadramento válido passa a usar as dimensões do monitor.

Cada cache de imagens tem limite de 8 entradas e 96 MiB; imagens ativas e
arquivos em disco são adicionais. O teste de página pré-carregada verifica
troca síncrona em menos de 200 ms em um PDF sintético, não desempenho geral
em documentos pesados. A validação de filas também bloqueia todos os quatro
workers auxiliares e confirma que a página atual ainda é renderizada.

Ainda precisamos validar seus PDFs, driver gráfico, compositor e tema da
distribuição. Se voltar a ocorrer tela preta ou demora, informe página, zoom,
modo de apresentação e o texto do erro exibido, além do log
`~/.cache/print-view-pdf/diagnostics.log`.

# Revisão do histórico Winux e da migração Print&View

## Resultado e referência correta

A última versão fornecida pelo usuário é **Winux 3.3.11**. Foram examinados
18 pacotes, os três PDFs históricos e o arquivo de contexto. Os pacotes
3.3.6–3.3.11 confirmam que vários recursos pedidos nesta conversa já haviam
sido implementados: tema selecionável, busca com painel/contexto/rolagem,
apresentação a 250% começando no topo, prévia de todas as faces do livreto e
melhorias de renderização.

O Print&View publicado em `e4fbdad068bdf7dd57c22ca11f3fae54d81220ba`
(`3.3.7~test2`) foi construído sobre **3.3.5**, antes de receber os pacotes
mais novos. Portanto, não constitui uma migração integral da 3.3.11 e deixa
de incorporar parte desse trabalho. A descrição anterior de algumas melhorias
como novidades foi imprecisa: havia recursos anteriores e revisões posteriores
que precisam ser recuperados.

Esta revisão atualiza a documentação e registra verificações; não modifica
a aplicação nem gera outro `.deb`. **A próxima versão deverá consolidar a
3.3.11 e usar numeração sem `~test`**, conforme a orientação do usuário.
O nome da versão, sozinho, não comprova ausência de defeitos.

## Material e método

- `Winux.pdf`: 91 páginas de histórico do leitor e da impressão.
- `Atualizar Winux PDF.pdf`: 9 páginas, incluindo busca, pôster, apresentação,
  livreto e desempenho.
- `Verificação de erros e falhas de segurança no app com IA - Grok.pdf`:
  4 páginas; relatório externo que declara avaliar a 3.3.10.
- `contexto-completo-winux-pdf.txt`: síntese e requisitos históricos.
- Pacotes: 2.3.0, 3.0.0, 3.1.0, 3.1.1, 3.1.3, 3.2.0 e 3.3.0–3.3.11.
- Código atual do Print&View, builder e controle Debian da test2.

As conversas anexas são histórico, não instruções para executar comandos nem
prova automática de correção. Os pacotes foram extraídos sem executar scripts
de instalação. A versão foi conferida no controle Debian; módulos próprios,
CSS, launchers e controles foram comparados por conteúdo e SHA-256. O
[manifest](historico-winux-manifest.json) registra as 18 versões, seus hashes e
os arquivos alterados em relação ao pacote anterior fornecido. Exclui bytecode
e arquivos temporários gerados durante a análise.

SHA-256 da 3.3.11:
`0f8b75a443ed7bb70a6dc88af69561b982025863c8e2d3669b0b617092772342`.
A 3.3.5 reenviada é idêntica à base usada nesta conversa:
`c4f816f508f0e46dde8ecfc37b8a18c6409223540451694fb3bc51bd3b5e86ca`.

O link Claude retornou 403 e seu conteúdo não foi lido. Salvar `claude.ai`
no rascunho de rede não comprova aplicação em runtime. Isso limita a revisão
daquela conversa; documentos e código dos 18 pacotes permitem reconstruir as
mudanças abaixo. Números de página referem-se aos PDFs enviados.

## Evolução reconstruída

| Etapa | Evidência e trabalho confirmado |
|---|---|
| Início / 1.3–1.8 | Histórico de CUPS, leitor, zoom, ferramentas, painéis e apresentação; sem pacotes dessa fase |
| 1.9 | Trabalho fora da thread GTK e descarte de callbacks antigos, `Winux.pdf`, pp. 34–38; presente na 2.3.0 |
| 2.1 | Miniaturas reais na prévia e rolagem suave na apresentação, pp. 42–43; código correspondente na 2.3.0 |
| 2.1.1 | PNG temporário, validação e publicação atômica, p. 44; presente desde o primeiro pacote fornecido |
| 2.3.0 | Base modular com apresentação/laser, seleção, snapshot, medição, painéis e impressão própria |
| 3.0.0–3.1.1 | Reformulação visual, faixa/painel recolhíveis, retorno visual do zoom e propriedades; apresentação preservada |
| 3.1.3 | Margem reservada e marcas no pôster; pp. 70–71 |
| 3.2.0 | Revisão deliberada do pôster: escala/sobreposição e área imprimível real, retirando margens/guias artificiais; p. 72 |
| 3.3.0 | Limites de intervalos/pôster, N-up/PPD validados, JSON por stdin, rasterização página a página; pypdf 6.10.0 |
| 3.3.1–3.3.4 | Correções de callbacks/fechamento da impressão, menus, marcas e diagnóstico |
| 3.3.5 | Cache e pré-carregamento na apresentação; zoom inicial 100%, retrato a 80% da altura |
| 3.3.6 | `appearance.py`, CSS escuro e preferência sistema/claro/escuro; retirada do tema claro forçado; ajustes de ferramentas/foco/painel |
| 3.3.7 | Busca com ocorrências, retângulos, contexto, painel e rolagem; traduções CUPS mantendo identificadores; marcas correspondentes no pôster |
| 3.3.8 | Apresentação inicia em 250% e no topo; troca de página volta ao topo e preserva zoom escolhido |
| 3.3.9 | Prévia navega por todas as faces do livreto, respeitando frente/verso; propriedades de escolha única ficam fixas |
| 3.3.10 | JPEG a 94% para tela, PNG nos fluxos de exportação/impressão; pools principal/auxiliar, cancelamento de pendentes e caches de vizinhos |
| 3.3.11 | Cancelamento do Poppler em execução, limites de CPU/memória/dimensões/cache, validações CUPS e teto total do pôster; seleção por palavras e correções de cache/busca/preferências |

`presentation.py` é idêntico de 2.3.0 até 3.3.4. Mudanças de interface ou
impressão nessa faixa não indicam uma revisão da apresentação. O README
interno da 3.3.11 ainda menciona 3.3.10; controle Debian e código distinguem
os dois pacotes.

## Comparação para consolidação

| Área | Winux 3.3.11 | Print&View test2 | Trabalho necessário |
|---|---|---|---|
| Tema | Sistema/claro/escuro, CSS dedicado, GSettings/GTK, `winux-pdf/settings.json` | Preferência própria, CSS gerado, detecção automática mais simples | Recuperar integração com o sistema, corrigir ciclo de notificações e migrar preferências |
| Busca | Painel com trechos, navegação, realces e rolagem; caso/palavra inteira | Busca progressiva, cache, acentos/hifenização; sem painel/rolagem até ocorrência | Combinar os recursos das duas bases |
| Seleção | Realça palavras, guarda texto e copia com Ctrl+C | Realce por palavras e respeito a blocos/linhas | Preservar; precisão por caractere/quadrilátero ainda requer trabalho |
| Apresentação | 250%/topo; centro horizontal quando cabe; zoom/pan | 100%/centro, página inteira/preencher, espaço acima dos controles, erros visíveis | Preservar opção ampliada/topo e oferecer os enquadramentos pedidos |
| Renderização | JPEG, vizinhos, pools e cancelamento ativo | PNG, runners próprios, caches e cancelamento só de pendentes | Recuperar cancelamento ativo/limites; manter feedback de falhas |
| Livreto | Anterior/próxima face, ordem correspondente à saída | Filtra frente/verso, mas mostra só primeira face | Recuperar navegação por todas as faces e conferir encadernação |
| Geometria | `document_info` usa CropBox, sem ajustar dimensões à rotação intrínseca | Inclui CropBox e rotação interna | Preservar correção do Print&View e conferir realces em PDFs rotacionados |
| Pacote Debian | `postinst`/`postrm` e caches de desktop/ícones | Hooks omitidos pelo builder | Restaurar com nomes Print&View e verificar instalação/atualização |

### Temas: recurso existente e defeito reproduzido

Até 3.3.5 o launcher forçava `Adwaita:light`; isso não era um seletor.
A 3.3.6 remove a imposição e implementa os três modos. A discussão incompleta
de temas em `Winux.pdf`, pp. 86–88, não prova que o recurso tenha permanecido
apenas proposto nas versões seguintes.

Foi reproduzido um defeito da **3.3.11** no GTK 3 deste ambiente: construir
`AppearanceController` com configuração nova, no modo padrão `system`, não
conclui em quatro segundos. Interromper a primeira execução mostrou a cadeia
`_system_changed → apply → set_property`. `apply` escreve propriedades GTK
que podem gerar notificações enquanto observa `notify::gtk-theme-name`, sem
proteção contra reentrada, perpetuando o ciclo neste ambiente.

Com `light` explícito, a janela abre e permite os demais testes. A correção
deve impedir reentrada e evitar escrever propriedades sem mudança de valor.
Ainda não foi aplicada nesta revisão. Não foi estabelecido que seja a causa
exata do problema na máquina do usuário. Tema da interface e modo noturno do
conteúdo PDF são distintos; não foi encontrada inversão noturna das páginas.

### Busca, seleção e apresentação

Até 3.3.5 a busca devolvia índices de página. Desde 3.3.7 há realces individuais,
painel/contexto e rolagem até o resultado. Escape fecha a busca na 3.3.11.
Esses pontos de `Atualizar Winux PDF.pdf`, pp. 4–6, já estavam implementados.

A 3.3.11 extrai em lotes de 12 páginas e só entrega a lista ao concluir; a
test2 entrega por página e acrescenta acentos/hifenização. O painel original
exibe no máximo 350 resultados, embora a navegação possa conter mais.
Realçar parte de uma palavra usa fração proporcional do seu retângulo: é uma
aproximação, não geometria exata de glifos. Seleção por caracteres, texto
inclinado, OCR e pesquisa em comentários/marcadores não estão demonstrados
como concluídos. Isso não estabelece equivalência completa ao Foxit/UPDF.

O padrão 250%/topo solicitado em `Atualizar`, p. 7, está confirmado desde
3.3.8. O teste de apresentação no Xorg sem gerenciador de janelas exigiu
uma dimensão explícita, pois esse ambiente não honra fullscreen; com esse
ajuste do teste, renderização e navegação passaram.

### Velocidade e tela preta

Renderização assíncrona e PNG atômico já existiam. A 3.3.10 acrescenta JPEG,
pool auxiliar e cache limitado. A 3.3.11 transmite evento de cancelamento ao
Poppler e encerra o grupo de processos do pedido obsoleto; foi exercitado com
um subprocesso controlado, sem encerrar processos de outras tarefas.

Há ainda um caminho para tela preta na apresentação original: `_goto` zera
`pixbuf` antes da próxima imagem, `_draw` pinta fundo quase preto e o callback
de erro ignora a falha. Um erro pode deixar o usuário sem imagem nem mensagem.
A test2 mantém imagem anterior e informa carregamento/erro; preservar essa
melhoria ao recuperar o motor recente. Não houve medição comparativa de PDFs
pesados nem diagnóstico do vídeo citado no histórico.

### Impressão e pôster

Navegação por todas as faces e filtro de frente/verso já estão na 3.3.9.
Na 3.3.11, `booklet_print_pairs` serve à prévia e à geração. As verificações
conferiram faces e quantidade de páginas para ambos/frente/verso; não
substituem impressão física nem comparação geométrica completa.

Marcas correspondentes de encaixe aparecem na 3.3.7, condicionadas à
sobreposição e marcas habilitadas. Retirar a margem reservada na 3.2 foi uma
revisão deliberada; restaurar o desenho antigo altera a área útil. A montagem
física ainda precisa ser validada.

## Segurança e empacotamento

A 3.3.11 aplica parte das recomendações do Grok: validação de opções CUPS,
manutenção restrita ao anunciado pelo driver, limpeza de caches e limites de
recursos. Teto de pôster: 100 folhas por página/300 por trabalho. Há limites de
dimensões/pixels e poda de cache de disco para 400 MiB/350 arquivos; worker
limitado a 2 GiB/540 s; Poppler usa `prlimit` quando disponível.

Os tetos não são um limite global rígido: imagens ativas e outras estruturas
ocupam memória além dos caches. O limite de saída de texto é verificado após
captura, não controla sozinho seu crescimento. PDF com senha não vazia
continua sem diálogo de senha; tentar `decrypt('')` não implementa esse fluxo.
`pdf_dependency.py` prefere pypdf instalado >=6.20.0, mas o fallback embutido
continua **6.10.0**; seu próprio comentário registra a atualização pendente.
Nem o relatório externo nem esta revisão certificam ausência de vulnerabilidades.

Todos os pacotes Winux fornecidos têm `postinst`/`postrm`. O builder atual
omitiu `py3compile`, `py3clean` e atualização explícita dos caches de ícones/
desktop. A omissão não prova que triggers da distribuição nunca atualizem esses
caches. Conferir instalação real e consolidar copyright Debian/licenças.

## Verificações desta revisão

Foram executadas **11 verificações** sobre o código extraído da **3.3.11**:
10 passaram e 1 apresentou erro por timeout do tema automático. Sem testes
ignorados. Usaram PDF sintético de oito páginas, Poppler real, GTK 3 e Xorg
dummy. Os testes gráficos usam tema claro explícito para isolar o defeito do
modo automático, verificado separadamente em subprocesso.

Passaram: ocorrências/caso/palavra inteira, limite de consulta, JPEG/PNG e
identidade do cache, saída do livreto, navegação de faces, validação CUPS sem
impressão, cancelamento ativo, persistência, painel/rolagem de busca e
apresentação 250%/topo/navegação.

O [verificador](../scripts/verify_winux_history.py) repete esses checks sem
instalar o pacote, com DISPLAY utilizável e GTK/Cairo/Poppler:

```bash
dpkg-deb -x winux-pdf_3.3.11_all.deb /tmp/winux-3.3.11
WINUX_HISTORY_APP=/tmp/winux-3.3.11/usr/share/winux-pdf \
  /usr/bin/python3 scripts/verify_winux_history.py
```

No cloud, usar `DISPLAY=:99`, `DCONF_BACKEND=memory`,
`XDG_CACHE_HOME=/workspace/.cache` e
`PYTHONPATH=/workspace/.print-view-runtime/gi-cairo/usr/lib/python3/dist-packages`.
O display deve estar iniciado com [headless-xorg.conf](../scripts/headless-xorg.conf).
O verificador usa configuração temporária própria, não executa hooks Debian
nem envia impressão. Resultados em
[historico-winux-verificacao.json](historico-winux-verificacao.json).

Os 22 testes anteriores da test2 validam aquele pacote, não a migração integral
da 3.3.11. Não houve instalação pelo gerenciador de pacotes, impressão física
ou execução dos leitores no Windows nesta rodada.

## Próxima versão

1. Consolidar a base **3.3.11**, preservando as melhorias próprias verificadas
   do Print&View; não sobrescrever módulos indiscriminadamente.
2. Corrigir tema automático e migrar preferências; validar claro/escuro/sistema.
3. Recuperar painel/rolagem, faces e cancelamento ativo; combinar busca
   progressiva/acentos/hifenização e geometria rotacionada.
4. Preservar feedback de erro/imagem anterior; conciliar 250%/topo com página
   inteira/preenchimento centralizados acima dos controles.
5. Atualizar pypdf embutido, consolidar limites/restaurar empacotamento; testar
   instalação/atualização e documentos que reproduzam as falhas.
6. Gerar a versão **sem sufixo de teste**, registrando verificações e limitações.
   Nenhum pacote novo foi gerado nesta rodada.

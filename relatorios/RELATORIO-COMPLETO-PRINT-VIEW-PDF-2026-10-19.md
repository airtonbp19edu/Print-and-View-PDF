# Relatório completo do Print and View PDF

**Situação do desenvolvimento, trabalhos concluídos, pendências e caminho até a próxima recompilação**

Data de referência: **19 de outubro de 2026**, fuso America/Sao_Paulo. Destinatário: Airton. Versão examinada: **3.4.0**, commit `e01c947e63a34887094a1ef7a3f877309a580bdb`, branch local `main`. Repositório: `https://github.com/airtonbp19edu/Print-and-View-PDF`.

## 1 O que já está entregue e por que ainda há pendências

A versão 3.4.0 já foi empacotada. Existem no repositório um pacote Debian, um bundle Flatpak, um instalador Windows e um arquivo de fontes. Portanto, já passamos por uma geração de pacotes. A próxima recompilação não depende de terminar toda a lista de melhorias deste relatório: depende de definir o resultado esperado da próxima entrega, preparar o ambiente de construção correspondente e, quando houver mudanças, validar essas mudanças antes de gerar os novos arquivos.

Ao mesmo tempo, os pacotes existentes não demonstram que todos os cenários de uso tenham sido concluídos. Os testes registrados cobrem partes importantes do leitor e da impressão, mas não incluem impressão em papel, instalação completa em Windows nativo, execução do Flatpak dentro do sandbox nem desempenho geral em PDFs grandes. Há recursos que realmente ainda não foram implementados, como OCR e seleção precisa de caracteres. Há outros já implementados que precisam de validação adicional. Essas situações têm consequências diferentes e serão tratadas separadamente.

A demora não pode ser atribuída apenas a uma compilação lenta. O histórico documenta recuperação de código, adoção inicial de uma base anterior à última versão Winux disponível, posterior consolidação de versões, dificuldades de acesso a materiais, preparação de runtimes e ampliação do empacotamento para três plataformas. Além disso, neste chat, depois da clonagem, houve uma consulta de progresso e agora a solicitação deste relatório. Não há implementação adicional registrada entre essas solicitações. O tempo de calendário decorrido não corresponde a horas contínuas de desenvolvimento.

Este documento preserva o detalhamento por área, descreve cada teste existente, relaciona as pendências com critérios de conclusão e inclui anexos com os documentos históricos completos, registros de validação, inventário de arquivos e procedimentos de construção. As conclusões sobre execução anterior estão identificadas como registros anteriores; as conferências realizadas em 19/10/2026 estão identificadas como verificações atuais.

## 2 Como interpretar os estados

| Estado | Significado neste relatório | O que não comprova sozinho |
|---|---|---|
| Implementado | Existe um caminho funcional no código examinado | Que foi exercitado em todas as plataformas, documentos ou impressoras |
| Validado em teste delimitado | Há teste ou execução documentada para condições específicas | Equivalência completa com Foxit ou UPDF, ou cobertura integral |
| Parcial | Parte da funcionalidade existe ou foi testada, mas permanece uma lacuna identificada | Que tudo precise ser refeito |
| Pendente de implementação | O comportamento solicitado não está demonstrado como implementado | Que seja obrigatoriamente necessário para empacotar o código atual |
| Pendente de validação | Há código ou pacote, mas falta comprovação no cenário alvo | Que exista um defeito já reproduzido |
| Histórico superado | Foi verdadeiro em uma etapa anterior e foi tratado depois | Que continue bloqueando a versão 3.4.0 |
| Proposta de continuidade | Trabalho recomendado para fechar uma lacuna | Que tenha sido executado, autorizado como implementação nesta consulta ou estimado em horas |

Não há uma lista original única de requisitos com pesos e critérios de aceite para calcular uma porcentagem geral confiável. Contar arquivos, testes ou linhas não mede percentagem de produto concluído. Por isso, não são atribuídos números como 80% ou 95% de conclusão.

## 3 Conferência atual da cópia local

### 3.1 Estado do Git e alcance da consulta

No início desta elaboração, `git status --short --branch` mostrou `main...origin/main`, sem arquivos modificados. O HEAD continua no commit da entrega 3.4.0. Esse alinhamento se refere às referências locais disponíveis; não foi feito `fetch` do GitHub nesta consulta. Não se afirma que nenhuma outra máquina ou outro chat possua trabalho ainda não incorporado a este checkout.

Foram examinados os cinco commits existentes na história local, todos os documentos de progresso presentes, os cinco arquivos de teste, os scripts de empacotamento, os módulos próprios da aplicação e os registros estruturados de validação. O inventário do Git contém 156 arquivos rastreados. Os 19 módulos Python próprios diretamente em `app/` totalizam 6.028 linhas; a biblioteca de terceiros em `app/vendor/pypdf` não foi contada como desenvolvimento próprio.

Nesta solicitação foi produzido um relatório. Não foram instalados pacotes do aplicativo, enviados trabalhos a impressoras, executadas as 27 verificações funcionais, executados leitores de referência ou gerados novos instaladores. As conferências atuais foram de histórico, conteúdo, sintaxe para inventário e integridade dos artefatos.

### 3.2 Integridade verificada agora

Os seis artefatos listados em `packages/SHA256SUMS` foram lidos e seus SHA-256 recalculados. Todos coincidem com o arquivo de checksums. Isso comprova correspondência com o inventário presente no repositório; não é verificação independente de assinatura digital ou autenticidade de fornecedores.

Os 19 módulos próprios coincidem com os hashes do registro `docs/validacao-3.4.0.json` quando normalizadas as quebras de linha Windows CRLF para LF. A comparação binária direta difere por essa conversão de texto feita no checkout. Essa diferença não foi tratada como alteração funcional ou adulteração.

Também foram abertos em memória o pacote Debian 3.4.0 e o arquivo de fontes 3.4.0. Em cada um foram comparados 81 arquivos de `app/` que existem nesta cópia. Após normalizar CRLF/LF, não apareceu diferença de conteúdo nesses 81 arquivos. Não foram executados os scripts de instalação do Debian para realizar essa comparação. Os conteúdos do `.exe` e do `.flatpak` não foram extraídos e comparados arquivo a arquivo nesta consulta; seus arquivos completos tiveram os hashes conferidos.

Essa conferência é relevante para a pergunta sobre recompilação: a aplicação desta cópia corresponde, nas comparações acima, à base que já possui pacotes. Não foi encontrada aqui uma nova rodada de alterações de código aguardando seu primeiro empacotamento.

## 4 Linha do tempo documentada

### 4.1 Evolução anterior do Winux

O histórico consolidado no repositório descreve estas etapas. As fases iniciais sem pacotes são evidência documental histórica; as versões a partir de 2.3.0 foram comparadas nos 18 pacotes fornecidos naquela análise.

| Fase | Trabalho registrado | Consequência para a versão atual |
|---|---|---|
| Winux 1.3 a 1.8 | Leitor, zoom, ferramentas, CUPS, painéis e apresentação | Antecedentes descritos em histórico, sem pacotes dessa fase no conjunto auditado |
| Winux 1.9 | Trabalho pesado fora da thread GTK e descarte de callbacks antigos | A arquitetura assíncrona não começou no Print&View |
| Winux 2.1 | Miniaturas reais na prévia e rolagem suave na apresentação | Recursos anteriores que devem ser preservados |
| Winux 2.1.1 | PNG temporário, validação e publicação atômica | Proteção contra imagens incompletas já existente |
| Winux 2.3.0 | Base modular, apresentação com laser, seleção, snapshot, medição, painéis e impressão própria | Primeiro pacote do inventário histórico |
| Winux 3.0.0 a 3.1.1 | Reformulação visual, faixa e painel recolhíveis, retorno do zoom e propriedades | Mudanças de interface não significam reconstrução de todo o motor |
| Winux 3.1.3 | Margem reservada e marcas de pôster | Etapa posteriormente revista |
| Winux 3.2.0 | Área imprimível real, escala e sobreposição; retirada de margens e guias artificiais | Restaurar o desenho antigo indiscriminadamente poderia mudar a área útil |
| Winux 3.3.0 | Limites de intervalos e pôster, validação N-up/PPD, opções JSON por stdin, rasterização página a página | Parte das proteções e do fluxo de impressão já existia |
| Winux 3.3.1 a 3.3.4 | Callbacks, fechamento da impressão, menus, marcas e diagnóstico | Correções incrementais preservadas na base |
| Winux 3.3.5 | Cache e pré-carregamento da apresentação, 100% inicial e retrato a 80% da altura | Base inicialmente recuperada para o Print&View |
| Winux 3.3.6 | Aparência sistema/claro/escuro, CSS escuro, preferências, foco e ferramentas | O seletor de tema antecede a consolidação atual |
| Winux 3.3.7 | Busca com ocorrências, retângulos, contexto, painel e rolagem; traduções CUPS e marcas de encaixe | Parte dos itens apresentados antes como novos já existia no Winux |
| Winux 3.3.8 | Apresentação a 250% iniciando no topo, preservação do zoom ao trocar páginas | Comportamento recuperado como opção de leitura |
| Winux 3.3.9 | Navegação por todas as faces do livreto; frente/verso; opções únicas fixas | A prévia completa do livreto não era uma ideia ainda sem implementação |
| Winux 3.3.10 | JPEG a 94% para tela, pools e cache de vizinhos, cancelamento de pendentes | Base para reduzir o custo de navegação |
| Winux 3.3.11 | Cancelamento de Poppler em execução, limites, validações CUPS, teto total de pôster e correções de seleção/cache/preferências | Última base Winux consolidada na 3.4.0 |

### 4.2 Commits do Print and View

Os horários abaixo foram convertidos para America/Sao_Paulo a partir dos registros do Git. Um horário de commit indica registro de alterações; não mede quanto tempo elas levaram para ser desenvolvidas.

| Data e hora local | Commit | Resultado registrado |
|---|---|---|
| 13/10/2026 19:44:46 | `f765341` | Início do repositório com licença e README |
| 13/10/2026 21:37:46 | `15260c2` | Recuperação da base Winux 3.3.5, correções iniciais, busca por ocorrências, testes, test1 e evidências estáticas dos leitores de referência |
| 13/10/2026 22:06:53 | `e4fbdad` | Test2 com enquadramento de apresentação, temas, navegação e cache |
| 13/10/2026 23:33:32 | `597df84` | Auditoria histórica até Winux 3.3.11, diferenças de migração e verificador |
| 14/10/2026 00:22:20 | `e01c947` | Consolidação 3.4.0 e geração dos pacotes Debian, Flatpak, Windows e fontes |

### 4.3 O que aconteceu neste chat

Em 16/10/2026, foi solicitado apenas copiar o repositório. A clonagem inicial encontrou `getaddrinfo() thread failed to start`; a repetição com acesso de rede autorizado terminou com os 156 arquivos extraídos e o Git limpo. Nenhuma alteração de código foi feita nessa tarefa.

Em 17/10/2026, foi solicitada a listagem das etapas e da progressão. Foram consultados os documentos, o histórico e os arquivos de validação, e foi apresentado um panorama em dez etapas. Os testes não foram executados novamente.

Em 19/10/2026, foi solicitado este relatório completo. O estado inicial do código ainda era o mesmo commit 3.4.0. Esse intervalo não contém, neste chat, uma solicitação anterior de implementar todas as lacunas, uma recompilação em execução ou um processo de desenvolvimento contínuo documentado. Isso explica por que a passagem dos dias não produziu uma nova versão nesta cópia.

## 5 Trabalho concluído em detalhe

### 5.1 Recuperação e proveniência

Foi extraído o pacote Winux 3.3.5 com `dpkg-deb -x`, sem executar hooks do pacote. O código original veio de `/usr/share/winux-pdf/`; os ícones vieram da árvore hicolor. O hash do pacote de origem e os hashes dos arquivos anteriores às modificações foram registrados. A documentação declara a autorização da equipe autora para continuar o Winux com o nome Print&View.

Foi preservada a licença MIT presente no repositório e a licença BSD do pypdf. As evidências sobre Foxit e UPDF permanecem separadas da aplicação: não há declaração de licença MIT para seus componentes, nem incorporação de seus executáveis ou ícones no produto. A leitura de metadados desses binários foi usada como referência de comportamento e arquitetura.

Posteriormente foram comparados 18 pacotes Winux, os três PDFs históricos e um arquivo de contexto. O manifest registra versões, hashes, módulos próprios, controles Debian e diferenças entre os pacotes fornecidos. Os três PDFs e os pacotes Winux originais não fazem parte dos 156 arquivos desta cópia; aqui existem os resultados e evidências produzidos a partir deles.

### 5.2 Estrutura do leitor e interface

O leitor usa Python e GTK 3. `app/main.py` constrói a janela, a faixa de ferramentas, a barra visual de documento, a barra de pesquisa, os painéis laterais, o canvas, o status e os atalhos. Há abertura de PDF, fechamento do documento, navegação por página, zoom, ajuste de página, ajuste à largura e rotação. O carregamento de informações e a preparação de impressão passam por subprocessos ou tarefas auxiliares para não concentrar todo o trabalho na thread GTK.

Há miniaturas reais com carregamento em lotes e pedidos próximos à região visível. Há leitura de metadados, propriedades do documento, cópia de arquivo, cópia de texto da página e exportação de PNG. São ferramentas existentes no código; nem todas têm um teste próprio e independente no conjunto de 27 casos. A ausência de teste individual deve ser distinguida de ausência de implementação.

A barra visual de documento não é um gerenciador de vários documentos simultâneos. O estado principal mantém um `filepath`, um conjunto de páginas e um documento ativo por janela. A palavra “aba” na interface não comprova suporte a múltiplos PDFs com estados independentes.

### 5.3 Geometria de página e renderização

`app/rendering.py` obtém informações com pypdf e usa Poppler pelos programas `pdfinfo`, `pdftocairo` e `pdftotext`. A versão atual considera CropBox e rotação intrínseca para as dimensões e para a extração usada por busca e seleção. A renderização inclui `-cropbox`. O teste de regressão cria um PDF com recorte e rotação de 90 graus e compara dimensões de texto, metadados e imagem.

Os arquivos de cache incluem identidade do documento, metadados do arquivo, página, formato, largura e canal. Isso trata o defeito em que dois documentos podiam compartilhar indevidamente uma imagem por terem a mesma página e zoom. A imagem é gerada em destino temporário, verificada e publicada por substituição atômica. PNG verifica assinatura e finalização; JPEG verifica marcadores de início e fim. Essa verificação é delimitada e não equivale a decodificar e auditar todo possível arquivo malformado.

Na tela são usados JPEGs com qualidade 94; exportação e fluxos de impressão preservam PNG quando rasterizam. Há cache de imagens decodificadas, pré-carregamento de vizinhas e separação entre pedidos interativos e tarefas auxiliares. A aplicação evita reiniciar um pedido idêntico que ainda está sendo renderizado por notificações repetidas de tamanho.

O código limita a largura solicitada de tela a 5.200 pixels e reduz adicionalmente dimensões para respeitar 9.000 pixels de altura e cerca de 40 milhões de pixels. Exportação/rasterização possui limite de 45 milhões de pixels por página e faixa de 72 a 600 dpi. Esses limites protegem caminhos específicos, não definem um teto global de memória para toda a aplicação.

### 5.4 Trabalho assíncrono e cancelamento

`app/async_core.py` controla sequências por canal, futures e eventos de cancelamento. Quando um pedido substitui outro, o resultado antigo é invalidado e o evento anterior é sinalizado. O retorno à interface usa `GLib.idle_add`. O runner mantém pools para trabalho principal e de fundo; há runners utilizados para a navegação interativa e para trabalhos auxiliares.

`app/cancel_state.py` transmite o evento para o trabalho da thread. O wrapper de subprocessos em `rendering.py` verifica cancelamento e timeout; no Linux encerra o grupo de processos do pedido, e no Windows mata o processo correspondente. O cancelamento efetivo existe no caminho que usa esse wrapper; não se deve supor que todos os usos de `subprocess.run` em todo o projeto tenham automaticamente o mesmo comportamento.

Foram registrados testes para cancelamento ativo, descarte de fila obsoleta, isolamento da renderização de página diante de workers auxiliares ocupados, preservação do resultado correto quando uma renderização antiga termina e proteção contra cancelar repetidamente o mesmo pedido válido.

### 5.5 Busca textual

`app/search_engine.py` contém normalização Unicode, `casefold`, opção de ignorar acentos, palavra inteira e união de hifenização. A busca guarda posição por ocorrência, página, dimensões, retângulos de palavras e trecho de contexto. A pesquisa trabalha por blocos do Poppler, preservando a separação entre blocos para não unir diretamente colunas diferentes.

O índice extrai texto por página e comunica progresso antes de terminar todo o documento. Há cache LRU de até 64 mapas de página por índice, detecção de alteração do arquivo durante a pesquisa e cancelamento entre extrações. Consultas têm limite de 256 caracteres. A navegação mantém até 5.000 ocorrências; o painel mostra até 350 linhas. Esses dois limites atendem objetos diferentes e não devem ser confundidos.

A interface oferece pesquisa com anterior/próximo, contador, realces, lista com contexto e rolagem até a ocorrência. Mudar termo ou opções cancela a consulta antiga e evita que resultados atrasados reapareçam. O conjunto de testes verifica acentos, caso, palavra inteira, `Straße`/`STRASSE`, frases, hifenização, separação de blocos, reaproveitamento/expulsão de cache, modificação do arquivo e resultados progressivos.

O caminho atual usa busca literal normalizada. A existência de um helper antigo com padrão de busca em `rendering.py` não significa que exista opção de expressões regulares na interface. Não há OCR, pesquisa em comentários/marcadores nem geometria exata por glifo demonstrados como recursos concluídos.

### 5.6 Seleção e ferramentas de leitura

A seleção transforma o retângulo de tela em coordenadas PDF, seleciona palavras que intersectam a região, agrupa texto por bloco/linha e copia o resultado para a área de transferência. Os realces acompanham os retângulos de palavra. Há funções de ida e volta entre geometria PDF e tela com rotações de 0, 90, 180 e 270 graus; o teste gráfico verifica essas transformações.

Também existem ferramenta de mão, snapshot de região, lupa e medição. O snapshot recorta a imagem atual e copia a imagem; isso não é OCR. A medição usa geometria da página e não constitui calibração certificada para desenho técnico. Esses caminhos precisam de caracterização manual adicional para ampliar a confiança nos documentos reais do usuário.

### 5.7 Aparência e preferências

Foram consolidados `appearance.py`, `themes.py`, CSS base e CSS escuro. Existem modos sistema, claro e escuro, leitura e salvamento de preferências, migração de `winux-pdf/settings.json`, escrita temporária seguida de substituição e preservação de outros campos do arquivo de configuração.

O defeito de reentrada do tema automático foi reproduzido no Winux 3.3.11 original. Na versão atual há guarda `_applying`, verificação antes de escrever propriedades GTK e proteção no carregamento do tema. O registro da entrega afirma correção e os testes atuais incluem inicialização do modo sistema e migração. O erro histórico de timeout não deve ser contabilizado como falha atual sem nova reprodução.

O tema escuro modifica a interface. Não há inversão das cores das páginas PDF. O modo automático usa informações de GSettings quando disponíveis e fallback do tema GTK; a correspondência com cada ambiente de desktop ainda precisa ser validada.

### 5.8 Apresentação

`presentation.py` fornece página inteira, preenchimento da área disponível e leitura a 250% começando no topo. Considera o espaço acima dos controles; permite ocultá-los, navegar, ajustar zoom, arrastar/rolar a página e usar laser com seleção de cor. A opção de leitura preserva o zoom escolhido e retorna ao topo ao mudar de página.

A imagem anterior permanece enquanto a nova é carregada. Falhas deixam de ser silenciosas: há estado de carregamento/erro. O desenho pinta branco sob o conteúdo para páginas transparentes. Há cache e pré-carregamento, correção para janelas iniciais sem enquadramento válido e descarte de callbacks obsoletos.

Os testes registrados cobrem retrato e paisagem, página inteira, preencher, alinhamento, 250%/topo, preservação da imagem diante de erro e prevenção de substituição por resultado antigo. Não demonstram que todo episódio de tela preta citado anteriormente tenha a mesma causa; o vídeo mencionado no histórico não foi analisado.

### 5.9 Painéis de marcadores, comentários e camadas

`pdf_panels.py` inspeciona marcadores, comentários existentes e nomes de camadas opcionais. `main.py` preenche os painéis e permite ativar entradas para navegação. Isso não é um editor completo de comentários ou de estrutura PDF.

As camadas são listadas. A interface informa que a visibilidade continua definida pelo próprio PDF. Alterar a visibilidade de grupos opcionais não está demonstrado como implementado. OCR, edição de anotações e pesquisa nesses painéis também não são recursos concluídos por consequência da simples existência das listas.

### 5.10 Preparação de impressão

`imposition.py` implementa seleção de intervalos, pares/ímpares, ordem reversa, tamanhos de papel, orientação e composição. O fluxo `size` cria saída em tamanho real ou ajustado. Há papéis ISO, Letter, Legal, Tabloid e tamanhos fotográficos conhecidos; o fallback para nomes não reconhecidos deve ser caracterizado com o driver escolhido.

N-up admite 1, 2, 4, 6, 9 e 16 páginas por folha, ordens de colocação e margem. O validador rejeita contagens fracionárias como 4,9 em vez de convertê-las silenciosamente em 4. O worker recebe o valor original para que essa validação tenha efeito.

Livreto calcula pares, insere espaços quando necessário, permite frente, verso ou ambos, encadernação esquerda/direita, margens de segurança e gutter. A mesma seleção de faces alimenta o motor e a prévia. A navegação de todas as faces, que faltava na test2, está recuperada na 3.4.0. Os testes conferem ordem e quantidade, mas não equivalem a dobrar e encadernar um trabalho físico.

Pôster calcula grade com escala, sobreposição e área imprimível; produz marcas de encaixe/corte e rótulos quando habilitados. Há teto de 100 folhas por página original e 300 por trabalho. O desenho antigo de margem artificial foi revisto no histórico e não deve ser restaurado por engano como se fosse uma pendência inequívoca.

`print_window.py` reúne destino, salvar como PDF, cópias, agrupamento, cinza, intervalo, orientação, modos, prévia, propriedades e opções do driver. O dicionário enviado ao worker contém os parâmetros escolhidos. A existência desse dicionário compartilhado não prova que toda geometria da prévia seja a mesma implementação usada na geração vetorial; há desenhos específicos que ainda exigem comparação sistemática.

### 5.11 CUPS e opções da impressora

`cups_backend.py` consulta impressoras, padrão, URI, status, opções PPD e geometria do papel/área imprimível. Há tratamento de duplicatas de descoberta, nomes e traduções visuais que preservam identificadores técnicos. Existem propriedades e ações de manutenção limitadas ao que a impressora anuncia, além de página de teste e tentativa de abrir utilitário do fabricante.

O envio usa `lp` com validação de opções e limites de timeout. Passagens manuais de livreto frente/verso são enviadas como simplex; o duplex automático fica separado. O teste correspondente simula a execução do comando e verifica `sides=one-sided`. Não envia papel nem comprova a orientação física em cada equipamento.

O código de manutenção e página de teste existe, mas não foi exercitado nesta consulta e não possui cobertura física registrada na entrega. O funcionamento depende do driver, da fila, do equipamento e das opções efetivamente anunciadas.

### 5.12 Caminho Windows

`windows_bootstrap.py` prepara caminhos de GTK/Poppler, tipotecas GI, schemas, diretórios de configuração/cache, DLLs e log. `platform_runtime.py` escolhe o Python do worker e opções para não exibir janelas de console desnecessárias. `windows_print.py` enumera impressoras e chama propriedades e diálogo nativo via GTK/Win32.

O documento já imposto é rasterizado a 180 dpi para o diálogo Windows. Isso é uma diferença real em relação à saída CUPS vetorial e precisa entrar nos critérios de qualidade. Não há promessa de preservar todos os vetores no spooler Windows.

O instalador NSIS é por usuário, registra desinstalação, atalhos e suporte a abertura de PDF. O stub do instalador é PE de 32 bits, mas o runtime instalado é x64; o alvo documentado é Windows 10/11 x64. Python, GTK e Poppler estão incluídos. Não há assinatura Authenticode do instalador. O teste de Wine não executou o instalador em ambiente Wine32 nem comprova o ciclo completo de instalação no Windows nativo.

### 5.13 Proteções e limites implementados

Há leitura de opções via JSON por stdin, limites de intervalos antes de construir ranges grandes, limites de N-up, teto de mosaico, validação de dimensões e pixels, publicação atômica de cache, timeout de subprocessos, cancelamento e limpeza de temporários. O cache decodificado limita cada instância a 8 entradas/96 MiB; o cache de imagens em disco tenta podar para 400 MiB/350 arquivos.

No Linux, o worker tenta limitar espaço de endereçamento a 2 GiB e CPU a 540 segundos. O wrapper Poppler usa `prlimit` quando disponível, com espaço de endereçamento de 1,5 GiB e CPU ligada ao timeout. No Windows esses mesmos limites POSIX não são aplicados; permanecem timeout, cancelamento e os limites funcionais implementados em Python.

Esses mecanismos não constituem auditoria completa. A memória de imagens ativas e outras estruturas soma-se aos caches; a saída de texto é capturada antes de determinadas verificações de tamanho. PDFs com senha não vazia não têm fluxo de diálogo completo: tentar senha vazia não resolve o problema. Cada uma dessas limitações aparece na lista de continuidade adiante.

### 5.14 Dependências e construção

O pypdf embutido foi atualizado de 6.10.0 para 6.20.1 na consolidação. A configuração atual prefere a cópia fixada em `app/vendor` em todas as plataformas, em vez da política antiga de preferir uma versão do sistema. O artefato de referência e a licença foram registrados.

O Debian restaura `postinst`/`postrm`, bytecode, caches de ícones e desktop e registros de copyright. O Flatpak cria repositório OSTree e bundle real com runtime copiado de Debian 13 e base Freedesktop 25.08. O Windows baixa dependências fixadas por URL/SHA-256, monta runtime e compila launcher e instalador com NSIS.

Os scripts de construção existem e os artefatos foram gerados anteriormente. Isso é um marco concluído. Repetir a geração em outra máquina exige preparar as ferramentas e os arquivos que não estão dentro do checkout, especialmente o overlay Linux e os downloads de runtime Windows.

## 6 Análise de Foxit e UPDF com alcance exato

### 6.1 O que foi feito

Foi inicialmente inspecionado apenas um instalador/downloader UPDF, de 22.901.424 bytes, extraído em 83 arquivos. A documentação distingue esse instalador do leitor. Mais tarde foram obtidos os ZIPs dos leitores completos e inspecionados FoxitPDFReader.exe, UPDF.exe e UPDFKit.dll.

Foram registrados versões declaradas em recursos PE, arquitetura, hashes, imports, exports, recursos, strings, handlers e trechos de assembly. Para Foxit foram decodificados 405 diálogos sem erro de parsing nessa amostra, com seis selecionados por termos de impressão. Foram identificados modos Scale, Tile Large Pages, Multiple Pages Per Sheet, Booklet e Batch Print, além de controles de duplex, binding, margens, marcas e etiquetas.

Foram rastreados message maps e handlers de seleção de lados do livreto, binding, corte, etiquetas e duplex. A evidência comprova atualização de campos e chamadas de atualização; não reconstrói toda a geração do trabalho nem demonstra automaticamente todos os valores padrão.

Para UPDFKit foram inventariadas 1.315 entradas exportadas e interfaces de busca, seleção por quadriláteros, renderização e impressão. Foram examinadas rotinas FindNext, FindPrev, GetBounds, obtenção de rotação/bounding box e SelectAllQuads. Strings de opções indicam papéis, cópias, ordenação, mosaico, N-up e livreto. Nomes e imports não provam a sequência real de uso de cada API.

O comando REA `inspect-with-objdump` não existia na CLI 6.4.0 usada; houve fallback para GNU objdump. `inspect-artifact` foi usado separadamente. Essa tentativa malsucedida não foi registrada como análise de código bem-sucedida.

### 6.2 O que permanece parcial

Não houve execução dinâmica dos leitores de referência, comparação lado a lado com os mesmos documentos, medição de latência nem impressão física de referência. Não foi recuperado seu código-fonte original, reconstruído seu motor PDF ou comprovada equivalência integral de comportamento.

Para avançar nessa frente, será preciso escolher operações concretas, preparar entradas idênticas, registrar configurações e observar saídas. Investigar integralmente dois produtos comerciais é um escopo muito maior do que corrigir e empacotar este leitor. A entrega de uma próxima versão pode usar critérios próprios e delimitados sem esperar engenharia reversa integral.

As prioridades derivadas dessa análise têm estados distintos: busca incremental e navegação de faces foram implementadas; seleção precisa por faixa/quadrilátero continua aberta; geometria única entre prévia e exportação não foi demonstrada integralmente; renderização por regiões e orçamento global medido continuam trabalhos de evolução.

## 7 Tudo que está parcialmente feito e o que falta em cada área

### 7.1 Busca e seleção

**Já existe:** pesquisa literal progressiva, contexto, realces por palavras, transformações para zoom/rotação, opções de normalização e navegação. **Limite:** retângulos de palavra não fornecem contorno exato de cada caractere, especialmente em texto inclinado, ligaduras e ordem de leitura complexa.

**Falta para concluir precisão avançada:** escolher representação de trechos/glifos, definir a transformação geométrica única, lidar com inclinação, recortes e rotação, testar cópia/ordem de leitura em múltiplas colunas, estabelecer tolerância visual e comparar resultados em documentos reais. Critério de aceite proposto: seleção e realce coincidirem com trechos esperados em uma coleção aprovada, com conteúdo copiado e geometria conferidos. Essa evolução é independente da capacidade de reconstruir o pacote 3.4.0.

**Falta para OCR:** escolher e integrar um motor, definir idiomas, instalação e licenças, progresso e cancelamento, limites de recursos e maneira de apresentar/salvar o texto. Não existe evidência de início dessa implementação. Pesquisar um PDF escaneado sem camada textual continuará sem localizar palavras enquanto isso não for feito.

**Outras evoluções não concluídas:** expressões regulares, pesquisa em comentários/marcadores e indexação persistente do documento. O índice atual é um cache de páginas em memória; não é uma base de busca persistente. Tais itens devem entrar em uma entrega somente quando estiverem no escopo escolhido.

### 7.2 Geometria da prévia e saída

**Já existe:** geração dos quatro modos, seleção compartilhada de faces do livreto e prévia navegável. **Limite:** quantidade/ordem de páginas corretas não comprova posição, corte e escala exatos em toda combinação. Existem desenho de prévia e composição de saída com responsabilidades diferentes.

**Falta:** montar uma matriz por modo, papel, orientação, rotação, CropBox, margem, ordem e encadernação; exportar o PDF preparado; comparar geometria, conteúdo e áreas cortadas; corrigir divergências reproduzidas. Critério proposto: cada combinação aceita deve ter saída esperada verificável e correspondência visual/dimensional da prévia dentro de tolerância definida.

### 7.3 Impressão física

**Já existe:** integração CUPS e diálogo Windows, geração de documentos preparados e separação entre duplex automático e passagens manuais. **Limite:** nenhuma folha impressa foi validada no registro de entrega.

**Falta:** escolher impressoras/drivers alvo; registrar papel, margem e orientação; imprimir tamanho real e ajustado; N-up; livreto frente, verso e ambos; conferir borda de virada; montar e dobrar; testar escala de cinza/cópias/agrupamento; cancelar; verificar estado da fila e erros. Pôster exige medir sobreposição e montar as folhas para confirmar encaixe. Critério proposto: checklist assinado com exemplos de saída e configurações, sem declarar compatibilidade com todos os drivers.

### 7.4 Instalação Debian e atualização

**Já existe:** `.deb`, dependências declaradas, conflitos/substituição de Winux e hooks restaurados. Os 27 testes registrados rodaram no conteúdo extraído do pacote. **Limite:** extrair o pacote não executa o gerenciador de pacotes, migração completa, caches do desktop ou desinstalação.

**Falta:** instalação limpa numa distribuição alvo, atualização a partir do Winux e das test1/test2 quando aplicável, abertura pelo menu e por arquivo, persistência/migração de preferências, convivência com dependências da distribuição e desinstalação. Critério: ciclos completos documentados e nenhuma perda de documentos do usuário.

### 7.5 Flatpak

**Já existe:** bundle real, estrutura OSTree e conteúdo testado com o runtime incluído fora do sandbox. **Limite:** acesso ao runtime Freedesktop no ambiente anterior foi bloqueado, e não houve validação por `flatpak run`.

**Falta:** disponibilizar runtime 25.08, instalar o bundle numa máquina alvo, abrir e salvar em pastas permitidas, testar fontes, GTK/tema/display, CUPS e rede, portal e preferências dentro do ambiente real. Avaliar permissões efetivamente necessárias com os fluxos em funcionamento. Publicação no Flathub não foi feita e é uma entrega separada de distribuir o bundle local.

### 7.6 Windows

**Já existe:** instalador x64, runtime, bootstrap, leitor exercitado no Wine e impressão nativa implementada. **Limite:** não há resultado de instalação/desinstalação nem impressão em Windows nativo. O instalador não tem Authenticode.

**Falta:** testar instalação por usuário, atalhos, abertura com argumentos, caminhos com espaços/acentos, atualização, desinstalação, fontes, DPI de tela, mudanças de tema, impressoras, propriedades e cancelamento. Conferir a qualidade de impressão a 180 dpi e decidir se atende ao alvo ou requer outra estratégia. Assinar o instalador, se for um requisito de distribuição, requer certificado e procedimento próprios; não é requisito técnico para compilar NSIS.

### 7.7 Desempenho

**Já existe:** JPEG, caches, vizinhas, pools, cancelamento e um teste delimitado de troca de página previamente carregada em menos de 200 ms. **Limite:** isso não mede a navegação geral de um PDF pesado nem estabelece equivalência com outros leitores.

**Falta:** coleção real com PDFs vetoriais complexos, muitas páginas, imagens grandes, escaneados e mistos; medidas de abertura, primeira página, navegação fria/quente, zoom, primeira ocorrência/tempo total de busca, CPU, memória e disco; repetir com hardware e resolução definidos. Definir metas antes de otimizar. Só então selecionar gargalos, por exemplo renderização por regiões ou orçamento global de fila/cache, e medir novamente.

### 7.8 Robustez e documentos difíceis

**Já existe:** limites e timeouts descritos na seção 5.13. **Limite:** não há auditoria completa, fuzzing ou matriz extensa de documentos malformados. Saídas de subprocessos podem crescer antes de algumas verificações, e os limites são diferentes entre plataformas.

**Falta:** testar PDFs corrompidos, páginas extremas, fluxos de texto muito grandes, tempo excedido, cancelamento durante preparação, falha de disco, diretório inacessível e limpeza após erro/fechamento. Rever captura de saída se houver caso reproduzido de crescimento excessivo. Critério: falhas retornam mensagem utilizável, encerram o trabalho correspondente e não comprometem documentos ou deixam processos persistentes. Nenhum defeito adicional foi inventado a partir da simples existência de `try/except`.

### 7.9 PDF protegido por senha

**Já existe:** detecção/tentativa de senha vazia e erros em determinados caminhos. **Falta:** um diálogo de senha e propagação coerente da credencial ao leitor, extração, busca, renderização e preparação; tratamento de senha incorreta/cancelamento e decisão de persistência. Não armazenar senha não foi implementado como regra nova neste relatório; a questão deve ser projetada na implementação. Critério proposto: abrir, pesquisar e imprimir documentos autorizados com senha sem expor a senha em logs ou comandos desnecessariamente.

### 7.10 Múltiplos documentos e camadas

**Já existe:** um documento ativo e sua barra visual; listagem de camadas. **Falta para múltiplos documentos:** estados independentes por documento, troca/fechamento, caches, buscas e impressão associados ao documento correto, orçamento compartilhado e testes de isolamento. **Falta para camadas:** controle real de visibilidade refletido na renderização e definição de como isso afeta impressão/exportação. Esses dois recursos não são requisitos para apenas repetir o empacotamento atual.

### 7.11 Documentação e comprovação

**Já existe:** relatórios de origem, análise, história, entrega e testes. **Limite:** os arquivos históricos contêm pendências que a 3.4.0 já resolveu. As notas iniciais desses arquivos avisam isso, mas uma leitura isolada pode dar impressão de repetição ou regressão.

**Falta como melhoria de acompanhamento:** um registro ativo por item com requisito, estado, versão, evidência, validação ainda necessária e critério de aceite. Este relatório oferece essa estrutura, mas a manutenção futura depende de atualizar o registro quando o código e os testes mudarem. A ausência de uma porcentagem inventada é intencional: não existe base de aceitação para somar todas as melhorias como se tivessem o mesmo peso.

## 8 Testes existentes e o que seus resultados significam

### 8.1 Resultado registrado para a versão atual

`docs/validacao-3.4.0.json` registra 27 testes executados, 27 aprovados e zero ignorados no código final; os mesmos números no conteúdo extraído do `.deb`; e os mesmos números no runtime do Flatpak fora do sandbox. São três execuções do conjunto de 27 casos, e não 81 requisitos independentes de produto.

O teste Windows/Wine registra PDF sintético de quatro páginas, quatro ocorrências, quatro linhas no painel, uma página de saída de livreto no recorte exercitado e imagem de 884 por 1.253 pixels. O ambiente declarado é Wine 10.0 sobre Debian 13 com backend GTK Win32 e Python 3.14.0. O resultado positivo não inclui impressão física, Windows nativo ou execução do instalador sob Wine32.

### 8.2 Registro do Winux original

O verificador histórico da 3.3.11 original executou 11 casos: 10 passaram e um terminou em erro de timeout do tema automático. Não houve falha de asserção nem teste ignorado nessa execução. O erro foi um achado da base antiga e motivou a correção consolidada; misturá-lo com os 27 casos atuais produziria um retrato incorreto.

Na etapa inicial da base 3.3.5, a documentação registra dois failures e um erro de contrato na primeira suíte, depois dez testes aprovados. A test2 ampliou a cobertura registrada para 22. A entrega final chegou a 27. Esses números pertencem a momentos e alvos diferentes.

### 8.3 Cobertura que ainda não existe como comprovação de entrega

Não há evidência de suíte de aceitação cobrindo instalação nos três formatos, todos os drivers, impressão física, documentos grandes, todas as geometrias de prévia/saída, seleção por caracteres, OCR, múltiplos documentos, visibilidade de camadas ou fluxo de senha. Alguns desses comportamentos não existem, enquanto outros existem e carecem de validação. O catálogo individual dos 27 casos e seus códigos completos estão nos anexos para permitir verificar exatamente o alcance das asserções.

## 9 Por que houve demora e o que pode reduzir o trabalho restante

### 9.1 Base inicial anterior e consolidação posterior

A test1 e a test2 partiram da 3.3.5. Depois foram disponibilizados materiais até a 3.3.11, onde vários recursos já existiam. Foi necessário comparar versões, identificar o que havia sido perdido ou descrito imprecisamente como novidade, combinar busca progressiva com painel/rolagem, preservar geometrias, recuperar navegação de faces e cancelamento e corrigir tema automático. Esse retrabalho está documentado; não é apenas uma hipótese para explicar a demora.

O documento de revisão reconhece expressamente a imprecisão de algumas descrições anteriores. A 3.4.0 trata a consolidação. Não seria correto afirmar hoje que a migração ainda está inteiramente por fazer só porque o relatório histórico tem uma seção “Próxima versão”.

### 9.2 Escopo com três sistemas de distribuição

O leitor continuou uma base Linux, mas a entrega passou a incluir `.deb`, Flatpak e instalador Windows. Além de copiar o Python, foi necessário organizar GTK, bindings, Cairo, Poppler, fontes, loaders, licenças, launcher e formas diferentes de impressão. Cada plataforma multiplica cenários de instalação e validação. Isso explica trabalho adicional, mas não permite estimar duração sem dados de execução.

### 9.3 Acesso a referências e tentativas que não entregaram material

O histórico registra rejeição de arquivos acima de 32 MiB, respostas 403 do proxy/links e 401 na API de compartilhamento, além de bloqueio do download completo do UPDF por uma rota. Foi possível trabalhar inicialmente só com o instalador e depois obter os leitores completos por outros materiais. Essas barreiras atrasaram a análise de referência naquela etapa; não devem continuar sendo tratadas como bloqueio atual de acesso a leitores já analisados estaticamente.

O link Claude retornou 403 e não foi lido. O vídeo citado não foi analisado. Portanto, não há base para prometer que todos os detalhes dessas fontes foram incorporados. O código e os documentos disponíveis permitiram avançar, mas não substituem um caso reproduzível do problema visual do usuário.

### 9.4 Preparação do ambiente e limites da plataforma de teste

Houve preparação de GI/Cairo em overlay local, adaptação de ambiente gráfico Xorg sem gerenciador de janelas e fallback de ferramenta de análise. A instalação do runtime Freedesktop do Flathub foi bloqueada no ambiente anterior. Por isso, o Flatpak foi construído e testado fora do sandbox, mas não validado na forma final de execução.

A máquina atual do chat é Windows. Na consulta ao PATH desta sessão não foram encontrados `dpkg-deb`, `flatpak` ou `makensis`. Isso não comprova que não estejam instalados em nenhuma pasta, VM ou distribuição WSL; comprova que a recompilação não deve ser prometida com um único comando neste shell sem preparar e verificar o ambiente adequado. A existência de `wsl.exe` no PATH também não comprova uma distribuição Linux configurada.

### 9.5 Falta de validação de campo

Sem execução registrada em Windows nativo, sandbox Flatpak e impressora física, não é possível encerrar honestamente esses itens. Criar mais um instalador não resolve automaticamente esse tipo de lacuna. O próximo avanço útil é executar os cenários que faltam e corrigir os defeitos concretos encontrados, em vez de repetir apenas a geração dos pacotes.

### 9.6 Fronteira de conclusão pouco clara

“Concluir” pode significar reconstruir a 3.4.0, corrigir os problemas atuais do usuário, validar a distribuição ou atingir paridade ampla com Foxit e UPDF. São metas de tamanhos diferentes. A lista anterior juntou melhorias opcionais e validações com a etapa de recompilar; isso pode ter passado a impressão de que OCR ou engenharia reversa integral seriam obrigatórios antes de gerar qualquer pacote. Não são.

Uma definição objetiva de entrega deve dizer quais funções entram, em quais sistemas e com quais casos de aceite. Os itens fora desse recorte continuam visíveis no backlog sem impedir indefinidamente uma entrega delimitada. Essa é uma proposta de organização, não uma redução silenciosa de escopo já contratado.

### 9.7 O que o histórico não permite afirmar

Não há apontamento de horas, duração de cada build, diário contínuo de execução ou estimativa medida de trabalho restante. Não é possível repartir o atraso em percentagens por causa, afirmar quantas horas foram desperdiçadas ou marcar uma data final confiável a partir dos cinco commits. Datas próximas no Git também não provam que todo o projeto foi desenvolvido dentro daquele intervalo.

Nesta cópia, o período posterior à clonagem não contém novos commits de implementação. Não existia aqui uma compilação demorando dias. O trabalho solicitado e realizado nesse intervalo foi copiar e consultar o estado. Para mudar essa situação, a próxima tarefa de execução precisa partir de uma lista concreta de correções ou validações; este relatório organiza essa lista.

## 10 Caminho completo até a próxima recompilação

### 10.1 Três resultados possíveis

| Resultado pretendido | Pré-requisitos reais | Não precisa esperar |
|---|---|---|
| Reconstruir a base 3.4.0 sem mudar comportamento | Fonte identificada, ferramentas/runtime corretos, dependências fixadas, diretório de stage novo e espaço de trabalho | OCR, múltiplos documentos, auditoria integral ou paridade completa com leitores de referência |
| Entregar uma versão com correções escolhidas | Reproduzir defeitos, implementar correções, testar as áreas alteradas, identificar versão e gerar pacotes | Toda melhoria futura que estiver fora dos critérios dessa versão |
| Declarar a versão validada para uso nos ambientes alvo | Além dos pacotes, instalação real, execução, regressão e impressão conforme matriz acordada | Certificação para todos os documentos e todos os drivers existentes |

### 10.2 Etapa A Fixar o ponto de partida

Registrar commit, versão, estado do Git, plataforma alvo e lista de artefatos. Preservar a base atual para comparação. O HEAD já foi identificado neste relatório. Se houver trabalho em outra cópia, ele precisa ser examinado e incorporado conscientemente antes de prometer que o pacote o contém. Não foi feita sincronização remota nesta consulta.

Critério de conclusão: fonte da próxima construção sem ambiguidade e alterações locais entendidas. Dependência: nenhuma. Estado: identificação local feita; nenhuma nova fonte escolhida além da 3.4.0.

### 10.3 Etapa B Definir o que a próxima versão deve resolver

Transformar cada problema real em entrada, ação, resultado esperado e resultado observado. Para atraso/tela preta, registrar documento, página, zoom, modo, máquina e diagnóstico. Para impressão, registrar driver, papel e opções. Separar correções obrigatórias, validação do que já existe e evolução funcional. OCR, senha, abas e camadas exigem decisão de escopo se forem desejados nessa entrega.

Critério: lista de aceite finita e testável, com cada item associado a uma plataforma. Dependência: A. Estado: lacunas inventariadas, escopo de uma nova implementação ainda não definido neste chat.

### 10.4 Etapa C Preparar ambiente de teste e construção

Para Debian e Flatpak, preparar um Linux compatível e os programas reais exigidos. Para testes gráficos, preparar GTK/GI/Cairo, Poppler e display utilizável. Para Flatpak, o builder atual assume Debian 13, Python 3.13 e diretórios x86_64 específicos; uma distribuição diferente requer avaliar adaptação. Para Windows, disponibilizar NSIS e os downloads fixados e usar stage novo.

Critério: ferramentas e bibliotecas encontradas com versões registradas, importação e programas mínimos verificados no ambiente selecionado. Dependência: A e formato alvo. Estado: scripts e manifestos disponíveis; o ambiente de construção não foi preparado nesta solicitação.

### 10.5 Etapa D Executar a base de regressão e reproduzir problemas

Rodar a suíte existente em ambiente GTK real, verificar se os 27 casos executam sem skips e guardar resultado, fonte e ambiente. Nos defeitos escolhidos, confirmar reprodução antes da correção. Repetir uma suíte sem as dependências gráficas pode nem importar os módulos; definir `DISPLAY` sozinho não cria um display utilizável.

Critério: baseline conhecido e reproduções anexadas. Dependência: B/C. Estado: existe registro histórico aprovado; não há nova execução desta consulta.

### 10.6 Etapa E Implementar apenas os itens aceitos e conferir regressões

Cada correção deve fechar um comportamento observado e preservar recursos recuperados da 3.3.11. Mudanças em busca afetam ocorrência, geometria e estado assíncrono; mudanças em apresentação afetam enquadramento/cache; mudanças em impressão afetam prévia e PDF preparado. Recursos novos, caso incluídos, precisam do trabalho descrito na seção 7.

Critério: casos de aceite passam e regressão apropriada passa. Dependência: B/D. Estado: não há novas alterações de código solicitadas ou realizadas durante esta elaboração; não há como declarar essa etapa concluída para uma versão ainda não definida.

### 10.7 Etapa F Identificar a versão e conferir materiais de distribuição

Para reconstrução sem mudanças, manter identificação coerente da 3.4.0 e registrar que é uma reconstrução. Para mudanças de comportamento, escolher uma versão coerente e atualizar os lugares pertinentes, como `app/version.py`, notas de entrega, metainfo e referências aos novos artefatos. Não basta renomear o instalador. Preservar licenças, dependências fixadas e instruções de instalação.

Critério: fonte, versão, notas e nomes dos artefatos concordam. Dependência: E, ou A/C se apenas reconstruir. Estado: 3.4.0 consistente como base histórica; nenhuma nova numeração foi atribuída neste relatório.

### 10.8 Etapa G Gerar Debian

No Linux preparado, o comando do projeto é:

```bash
/usr/bin/python3 scripts/build_deb.py
```

O script copia a aplicação, ícones e documentos, gera o launcher, controle e hooks, ajusta permissões e chama `dpkg-deb --root-owner-group --build`. A saída vai para `dist/print-view-pdf_<VERSAO>_all.deb`. O builder não copia automaticamente esse arquivo para `packages/` nem atualiza `SHA256SUMS`.

Critério: processo retorna sucesso, pacote contém a versão e fontes esperadas, controle/hooks/licenças conferidos. Dependência: C/F. Estado: caminho implementado e artefato 3.4.0 existente; nenhuma nova execução agora.

### 10.9 Etapa H Gerar Flatpak

No Linux Debian 13 preparado, substituir os caminhos de exemplo por locais reais e novos:

```bash
python3 scripts/build_flatpak.py --extra-runtime /caminho/runtime-overlay --stage /caminho/stage-novo --repo /caminho/repositorio-ostree
```

`--extra-runtime` é obrigatório. O builder procura adaptador GI/Cairo e programas CUPS ausentes no sistema no overlay. Exige executáveis ELF reais, copia bibliotecas pareadas ao loader/libc, tipotecas, fontes, schemas, ícones e licenças. Cria wrappers e metadata; chama `flatpak build-export` e `flatpak build-bundle`. Stage existente é recusado para preservar seu conteúdo. Não é necessário apagar recursivamente um diretório antigo: pode-se escolher outro caminho.

Critério: bundle criado, ID/runtime/permissões corretos e conteúdo identificado. A validação de entrega exige instalar e executar no sandbox depois. Dependência: C/F e runtime apropriado. Estado: bundle 3.4.0 existe; sandbox ainda sem validação registrada.

### 10.10 Etapa I Gerar Windows

Com Python e NSIS disponíveis em Linux ou Windows, substituir os caminhos pelos reais:

```text
python scripts/build_windows.py --downloads CAMINHO_DOS_DOWNLOADS --makensis CAMINHO_DO_MAKENSIS --stage CAMINHO_DE_STAGE_NOVO
```

O builder baixa os sete artefatos do manifesto quando faltam, confere SHA-256, extrai Python/GTK/Poppler e wheels selecionadas, copia aplicação e licenças, compila launcher e instalador NSIS. O stage precisa ser novo. Instalações locais de NSIS podem exigir `NSISDIR`. A saída vai para `dist/PrintViewPDF-<VERSAO>-Setup-x64.exe`.

Critério de construção: instalador gerado com runtime e versão corretos. Critério de entrega: ciclo de instalação/execução/atualização/desinstalação em Windows nativo. Dependência: C/F e downloads disponíveis. Estado: instalador 3.4.0 existe; ciclo nativo não validado no registro.

### 10.11 Etapa J Verificar os artefatos gerados

Conferir conteúdo e inventários dos pacotes, executar testes no conteúdo empacotado, abrir um PDF real, pesquisar, navegar, exportar e preparar saída. Comparar fonte e aplicativo incluído, conferir licenças e nomes. Os resultados devem ser registrados com o commit e a plataforma. Assinatura, quando exigida, ocorre no processo definido para distribuição e não deve ser confundida com checksum.

Critério: os arquivos a distribuir correspondem ao código testado. Dependência: G/H/I conforme alvos. Estado: há registros históricos e novas conferências de integridade; falta a validação de campo listada.

### 10.12 Etapa K Instalar e validar nos ambientes alvo

Executar os ciclos de Debian, Flatpak e Windows descritos na seção 7, incluindo impressoras realmente escolhidas. Separar defeito do aplicativo, limitação do driver e diferença esperada de rasterização. Se uma plataforma não for alvo da próxima entrega, não declarar aprovação nela por herança do teste em outra.

Critério: matriz de aceite preenchida com resultados e falhas restantes explicitadas. Dependência: J e acesso aos ambientes/equipamentos. Estado: parcial na entrega atual.

### 10.13 Etapa L Preparar a distribuição e encerrar o marco

Copiar somente os artefatos aprovados para a pasta de distribuição escolhida, gerar checksums a partir desses arquivos finais, preparar fonte correspondente e notas com limites conhecidos. O repositório não tem, entre os arquivos rastreados, um script específico para reproduzir o tarball de fontes e atualizar todos os checksums de release numa única etapa; isso precisa ser realizado e registrado no procedimento da nova entrega.

Publicar ou enviar uma release é uma ação posterior à produção dos arquivos. Não foi solicitada nesta consulta. Critério: artefatos, fonte, checksums, instruções e resultados rastreáveis, com o próximo backlog separado do marco encerrado. Dependência: J/K e escopo da distribuição. Estado: artefatos atuais presentes no repositório; nenhuma nova distribuição preparada por este relatório.

## 11 Lista integral de continuidade organizada para execução

Os códigos abaixo são identificadores criados para acompanhar os trabalhos deste relatório. A coluna “relação com recompilação” evita transformar toda evolução futura em pré-requisito obrigatório de build.

| ID | Trabalho a fazer | Estado de partida | Critério de conclusão | Relação com recompilação |
|---|---|---|---|---|
| R01 | Fixar fonte/commit da próxima entrega | Base local identificada | Fonte e alterações de origem conhecidas | Antes de qualquer nova construção |
| R02 | Definir sistemas e artefatos alvo | Há três formatos existentes | Lista explícita de alvos da entrega | Antes de planejar a construção |
| R03 | Definir bugs/requisitos obrigatórios | Inventário disponível | Casos finitos com esperado/observado | Antes de alterar comportamento |
| R04 | Recuperar materiais adicionais necessários aos bugs | Vídeo/link anterior não analisados | Caso reproduzível suficiente por problema | Quando o problema depender deles |
| R05 | Preparar Linux de teste/construção | Scripts existem | GTK/Cairo/Poppler/display e ferramentas funcionam | Para Debian/Flatpak e suíte Linux |
| R06 | Preparar runtime/overlay Flatpak | Builder depende do ambiente | Python 3.13, ELF, GI/Cairo e CUPS corretos | Para novo Flatpak |
| R07 | Disponibilizar runtime Freedesktop 25.08 | Bloqueado no ambiente anterior | Runtime acessível no alvo | Para execução do Flatpak no sandbox |
| R08 | Preparar downloads Windows e NSIS | Manifesto fixado | Arquivos conferidos e compilador disponível | Para novo instalador Windows |
| R09 | Reexecutar regressão da base escolhida | 27/27 registrados anteriormente | Novo resultado com fonte/ambiente e skips conhecidos | Antes de declarar nova validação |
| R10 | Reproduzir e corrigir bugs aceitos | Não há nova lista de bugs reproduzidos | Casos aceitos passam após mudança | Se a entrega incluir correções |
| R11 | Conferir seleção/cópia em PDFs reais complexos | Palavras e rotação implementadas | Texto e regiões esperados conferidos | Validação funcional |
| R12 | Implementar seleção por caracteres/quadriláteros | Ausente como recurso completo | Geometria e cópia precisas na coleção alvo | Evolução, se incluída no escopo |
| R13 | Implementar OCR | Ausente | Escaneados pesquisáveis com limites/idiomas definidos | Evolução, se incluída |
| R14 | Adicionar regex | Ausente na interface | Semântica, erros e limites testados | Evolução, se incluída |
| R15 | Pesquisa em comentários/marcadores | Ausente como pesquisa integrada | Resultados distinguem origens e navegam | Evolução, se incluída |
| R16 | Índice persistente | Cache atual é em memória | Identidade/invalidação/disco definidos e testados | Evolução, se necessária |
| R17 | Fluxo de senha | Tentativa de senha vazia | Senha fornecida vale nos caminhos necessários | Evolução/correção conforme alvo |
| R18 | Múltiplos documentos reais | Um estado ativo por janela | Estados, buscas/caches e fechamento isolados | Evolução, se incluída |
| R19 | Visibilidade de camadas | Somente listagem | Render e saída respeitam opção definida | Evolução, se incluída |
| R20 | Caracterizar snapshot/lupa/medição/exportação | Caminhos de código presentes | Casos manuais registrados e falhas tratadas | Validação de ferramentas existentes |
| R21 | Validar temas nos desktops alvo | Testes delimitados passam no registro | Modo sistema/claro/escuro e migração conferidos | Validação de ambiente |
| R22 | Validar apresentação em ambientes reais | Testes sintéticos registrados | Retrato/paisagem/zoom/display estáveis | Validação de ambiente |
| R23 | Reproduzir tela preta/demora com documentos alvo | Há correções gerais; vídeo não analisado | Problema reproduzido/resolvido ou causa delimitada | Correção quando houver caso |
| R24 | Comparar prévia e saída em tamanho/ajuste | Implementado sem matriz completa | Escala/posição/corte conferidos | Validação de impressão |
| R25 | Comparar N-up em todas as ordens aceitas | Geração e teste básico existem | Conteúdo e geometria corretos na matriz | Validação de impressão |
| R26 | Comparar livreto em todas as faces/opções alvo | Navegação e ordem testadas | Prévia/arquivo/dobra concordam | Validação de impressão |
| R27 | Comparar pôster em área imprimível/escala | Geração/marcas existem | Sobreposição e encaixe medidos | Validação de impressão |
| R28 | Unificar geometria onde houver divergência | Compartilhamento parcial | Um resultado coerente para controles/prévia/saída | Implementação condicionada aos achados |
| R29 | Validar CUPS com drivers alvo | Comandos/opções implementados | Capacidades e trabalhos corretos nos equipamentos | Validação de campo |
| R30 | Validar simplex/duplex e passagens manuais | Teste de comando simulado | Bordas e reinserção corretas em papel | Validação de campo |
| R31 | Validar manutenção e propriedades | Caminhos existentes | Ações anunciadas e retorno corretos | Validação por equipamento |
| R32 | Validar impressão Windows a 180 dpi | Raster implementado | Qualidade/escala aceitas no alvo | Validação/correção conforme resultado |
| R33 | Instalação Debian limpa | Pacote e hooks existentes | Menu/arquivo/dependências funcionam | Depois de gerar o pacote |
| R34 | Atualização Debian de bases escolhidas | Substituição/migração parcial testada | Pacote/preferências atualizam corretamente | Depois de gerar o pacote |
| R35 | Remoção Debian | Hook presente | Remoção consistente sem afetar PDFs | Depois de gerar o pacote |
| R36 | Instalar/executar Flatpak no sandbox | Ainda não validado | Leitura/salvar/display/fontes/impressão passam | Depois de gerar bundle |
| R37 | Revisar permissões Flatpak com fluxos reais | Metadata existente | Permissões justificadas pelos fluxos alvo | Validação de distribuição |
| R38 | Instalar/atualizar/remover Windows nativo | Wine cobre só runtime | Ciclo completo registrado | Depois de gerar instalador |
| R39 | Testar DPI/caminhos/tema/fontes no Windows | Sem matriz nativa | Casos escolhidos aprovados | Validação de distribuição |
| R40 | Assinar instalador se exigido | Não assinado | Assinatura verificável no artefato final | Distribuição, não compilação básica |
| R41 | Definir coleção e metas de desempenho | Testes sintéticos existentes | Entradas, hardware e metas registradas | Antes de otimizar |
| R42 | Medir abertura/navegação/zoom/busca | Sem benchmark geral | Medições repetíveis frias/quentes | Validação de desempenho |
| R43 | Medir memória/CPU/cache/fila | Limites locais existentes | Orçamento observado por cenário | Validação de desempenho |
| R44 | Implementar regiões/orçamento global se necessário | Não demonstrado integralmente | Metas alcançadas sem regressão | Evolução condicionada à medição |
| R45 | Ensaiar PDFs malformados e extremos | Proteções parciais | Erros/limites/limpeza e recuperação verificados | Robustez conforme escopo |
| R46 | Rever captura de saída e memória em casos extremos | Limite não é global | Consumo e cancelamento dentro de meta | Correção se reprodução exigir |
| R47 | Comparar Foxit/UPDF dinamicamente | Apenas estática | Mesmas entradas/opções e saídas documentadas | Pesquisa de referência, não build básico |
| R48 | Aprofundar consumidores/algoritmos de referência | Assembly parcial | Hipóteses verificadas com alcance definido | Pesquisa opcional para requisitos concretos |
| R49 | Atualizar versão/notas/metainfo | Atual é 3.4.0 | Identificações coerentes com mudanças | Antes da nova release |
| R50 | Construir Debian | Script e pacote existentes | Novo `.deb` corresponde à fonte escolhida | Recompilação do alvo |
| R51 | Construir Flatpak | Script e bundle existentes | Novo bundle corresponde à fonte escolhida | Recompilação do alvo |
| R52 | Construir Windows | Script e instalador existentes | Novo `.exe` corresponde à fonte escolhida | Recompilação do alvo |
| R53 | Testar o conteúdo empacotado | Há registro da 3.4.0 | Novo conteúdo testado com origem registrada | Depois da construção |
| R54 | Preparar fonte da nova entrega | Tarball atual presente | Arquivo corresponde à fonte distribuída | Distribuição/reprodutibilidade |
| R55 | Gerar checksums finais | Arquivo atual conferido | Inventário calculado dos novos arquivos | Depois de finalizar artefatos |
| R56 | Manter registro ativo e fechar marco | Relatório atual fornece baseline | Cada item tem resultado/evidência/limites | Acompanhamento e encerramento |
| R57 | Publicar/distribuir quando solicitado | Pacotes atuais no repositório | Destino, versão e arquivos aprovados identificados | Ação posterior à produção |

Não há evidência de que os 57 itens tenham sido iniciados simultaneamente. Esta lista transforma lacunas e passos de entrega em tarefas rastreáveis. Os itens de evolução só se tornam obrigatórios para uma versão quando entram no seu escopo; itens de validação devem ser exigidos para as afirmações que se pretende fazer sobre essa versão.

## 12 Critérios objetivos para encerrar cada tipo de entrega

### 12.1 Recompilação concluída

- Fonte e versão identificadas.
- Ambiente e dependências registrados.
- Processo de construção termina com sucesso.
- Artefatos esperados existem, são íntegros e contêm a aplicação correta.
- Checksum calculado dos arquivos finais.
- Nenhuma alegação adicional de impressão ou compatibilidade baseada apenas na existência do arquivo.

### 12.2 Correção funcional concluída

- Defeito reproduzido com entrada/ações conhecidas.
- Mudança implementada e caso original resolvido.
- Testes/regressões pertinentes aprovados.
- Pacote gerado contém a correção.
- Resultado confirmado no ambiente onde o problema ocorria, quando o defeito depende dele.

### 12.3 Entrega validada para o usuário

- Alvos e equipamentos escolhidos são explícitos.
- Instalação, atualização e execução aprovadas nesses alvos.
- Fluxos críticos de leitura, busca, apresentação, exportação e impressão aprovados.
- Limites e pendências remanescentes documentados.
- Fonte, pacotes, instruções e resultados associados à mesma versão.
- Melhorias futuras separadas da lista finita que encerra o marco.

## 13 Fontes e limites da prestação de contas

As fontes primárias desta prestação de contas são os arquivos e o histórico do checkout identificado. Os documentos anteriores foram lidos como registros de trabalho; os scripts e testes foram lidos para delimitar implementação e cobertura. O histórico desta conversa e sua recapitulação local foram usados para distinguir clonagem, consulta de estado e implementação.

Não foi feita auditoria de todo histórico externo de conversas, nem leitura dos PDFs/ZIPs originais que ficaram fora do repositório. Não foram consultadas alterações remotas posteriores ao clone. “Tudo” neste arquivo significa todos os trabalhos, limites, pendências e evidências identificáveis no material examinado, com inventário integral dos arquivos rastreados, sem inventar tarefas executadas em fontes que não foram acessadas.

Os anexos seguintes preservam integralmente os documentos narrativos presentes no repositório, os registros técnicos selecionados, os casos de teste, os procedimentos de construção e o inventário. Os documentos históricos estão identificados por sua origem: textos como “ainda não foi corrigido” neles devem ser interpretados segundo a data/etapa e a consolidação explicada no corpo do relatório.


## Anexo A Catálogo completo dos 27 testes atuais

Os nomes, arquivos e linhas foram extraídos do código desta cópia. As explicações descrevem as asserções; o estado aprovado decorre dos registros anteriores, não de execução nesta elaboração.


### A01 Inicialização de tema sistema e migração

Local: `tests/test_consolidation.py:17`. Caso: `ConsolidationTests.test_fresh_system_theme_initializes_and_migrates_legacy`.

**O que confere:** Executa controlador em subprocesso com configuração nova, exige conclusão em até 5 segundos; grava preferência Winux dark e verifica migração para o arquivo novo.

**Limite:** Depende de DISPLAY/GTK; não cobre todos os desktops.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A02 Cancelamento de processo ativo

Local: `tests/test_consolidation.py:31`. Caso: `ConsolidationTests.test_active_process_cancellation`.

**O que confere:** Sinaliza evento depois de 0,2 s, espera erro de cancelamento no wrapper de subprocesso e término em menos de 2 s de um processo que dormiria 10 s.

**Limite:** Usa processo controlado, não PDF pesado nem todos os caminhos de subprocesso.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A03 Ocorrências, seleção e rotação na interface

Local: `tests/test_gui.py:53`. Caso: `GUIRegressionTests.test_search_navigation_selection_and_rotation`.

**O que confere:** Busca duas ocorrências, navega anterior/próximo, verifica transformações de ida e volta nas quatro rotações, seleciona palavra e limpa pesquisa.

**Limite:** PDF sintético; não valida seleção por glifo ou texto inclinado.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A04 Painel, rolagem e faces do livreto

Local: `tests/test_gui.py:75`. Caso: `GUIRegressionTests.test_search_sidebar_scroll_and_all_booklet_faces`.

**O que confere:** Exige sete resultados no painel e navegação até página alvo; percorre 4 faces para ambos, 2 para frente e 2 para verso em livreto de 8 páginas.

**Limite:** Não mede a geometria de todas as faces nem impressão física.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A05 Prévia e envio das opções de livreto

Local: `tests/test_gui.py:97`. Caso: `GUIRegressionTests.test_booklet_preview_sides_binding_and_submit`.

**O que confere:** Confere miniaturas de frente/verso, binding à direita, duplex desabilitado para passagem filtrada, desenho Cairo e parâmetros enviados ao callback.

**Limite:** Fila TestPrinter e callback local; nenhum trabalho físico.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A06 Resultados progressivos e descarte da busca antiga

Local: `tests/test_gui.py:122`. Caso: `GUIRegressionTests.test_search_results_arrive_before_end_and_options_cancel_old_query`.

**O que confere:** Bloqueia página posterior, confirma resultados antes do fim, troca consulta/opções, confere evento antigo cancelado e opção de acentos.

**Limite:** Sincronização controlada, não benchmark geral.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A07 Identidade do cache entre documentos

Local: `tests/test_regressions.py:43`. Caso: `CoreRegressionTests.test_cache_distinguishes_documents`.

**O que confere:** Renderiza dois PDFs distintos com mesma configuração e compara hashes das imagens para exigir saídas diferentes.

**Limite:** Dois PDFs sintéticos; não cobre toda substituição concorrente de arquivo.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A08 Ordem e contagem de páginas no livreto gerado

Local: `tests/test_regressions.py:51`. Caso: `CoreRegressionTests.test_booklet_generated_sides_and_binding`.

**O que confere:** Confere ambos/frente/verso e texto inicial nas faces; também confere encadernação direita no PDF de saída.

**Limite:** Não verifica escala, margens em todas as combinações ou dobra em papel.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A09 Geometria individual das ocorrências

Local: `tests/test_regressions.py:65`. Caso: `CoreRegressionTests.test_search_has_individual_occurrence_coordinates`.

**O que confere:** Espera páginas 0,0,1 para três ocorrências, retângulos diferentes na mesma página e dimensões positivas.

**Limite:** Retângulos de palavras, sem precisão por caractere.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A10 Separação de passagem manual e duplex

Local: `tests/test_regressions.py:72`. Caso: `CoreRegressionTests.test_manual_booklet_sides_are_not_duplex`.

**O que confere:** Simula comando CUPS para livreto somente verso; exige sides=one-sided e ausência de imposição de two-sided-short-edge.

**Limite:** Execução de lp simulada por mock.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A11 Worker para N-up e pôster

Local: `tests/test_regressions.py:84`. Caso: `CoreRegressionTests.test_worker_prepares_nup_and_poster`.

**O que confere:** Executa subprocesso real do worker com JSON e exige 2 páginas em N-up 4 e 32 folhas no cenário de pôster definido.

**Limite:** Confere quantidade nesse cenário; não todas as ordens/geometrias.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A12 CropBox e rotação intrínseca

Local: `tests/test_regressions.py:94`. Caso: `CoreRegressionTests.test_intrinsic_rotation_and_cropbox_match_text_geometry`.

**O que confere:** Cria recorte rotacionado 90 graus, exige dimensão 540 por 380 no mapa, metadados e render e palavras dentro da largura.

**Limite:** Um caso sintético específico, não toda combinação de caixas PDF.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A13 Unicode e busca de frase

Local: `tests/test_regressions.py:112`. Caso: `CoreRegressionTests.test_search_phrases_and_casefold_expansion`.

**O que confere:** Confere duas ocorrências de STRASSE, frase em duas linhas com dois retângulos e nenhuma ocorrência para termo ausente ou vazio.

**Limite:** Não inclui OCR ou semântica de regex.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A14 Validação N-up sem truncamento

Local: `tests/test_regressions.py:121`. Caso: `CoreRegressionTests.test_nup_worker_rejects_fractional_count`.

**O que confere:** Exige ValueError para 4,9 páginas por folha no dispatcher de preparação.

**Limite:** Um valor inválido representativo; não auditoria de todas as entradas.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A15 Opções de pesquisa

Local: `tests/test_search.py:14`. Caso: `SearchTests.test_options_and_real_pdf`.

**O que confere:** Verifica caso, acentos, palavra inteira e expansão Unicode no índice usando PDF gerado e extração real.

**Limite:** Documentos sintéticos com strings conhecidas.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A16 Reuso e cancelamento do índice

Local: `tests/test_search.py:25`. Caso: `SearchTests.test_cache_reuse_and_cancellation_progress`.

**O que confere:** Confere 8 extrações para duas consultas no mesmo documento, interrompe após página 2 e verifica progresso e evento pré-cancelado.

**Limite:** Cancelamento entre páginas; não mede latência de todos os subprocessos.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A17 Hifenização e separação de blocos

Local: `tests/test_search.py:39`. Caso: `SearchTests.test_hyphenation_does_not_join_columns`.

**O que confere:** Mapa de palavras controlado só une impres-/são quando opção está ativa e não une texto do bloco seguinte.

**Limite:** Mapa construído em memória, não valida todos os layouts de Poppler.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A18 Expulsão de cache e alteração de PDF

Local: `tests/test_search.py:49`. Caso: `SearchTests.test_cache_eviction_and_changed_file`.

**O que confere:** Limita cache a 2 páginas e exige erro ao pesquisar depois de substituir o documento.

**Limite:** Não cobre toda corrida de sistema de arquivos ou armazenamento remoto.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A19 Persistência e contraste de temas

Local: `tests/test_viewer.py:36`. Caso: `ViewerTests.test_theme_persistence_and_contrast`.

**O que confere:** Seleciona dark/light, confere arquivo, propriedade GTK e limiares do texto do status.

**Limite:** Amostra de estilos/GTK do ambiente de teste.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A20 Render válido não reiniciado por notificações repetidas

Local: `tests/test_viewer.py:49`. Caso: `ViewerTests.test_repeated_requests_do_not_cancel_same_running_render`.

**O que confere:** Bloqueia carregamento, dispara 20 solicitações iguais e confirma evento não cancelado e página exibida ao liberar.

**Limite:** Simulação delimitada de repetição, não avaliação em todo compositor.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A21 Leitura a 250 por cento no topo

Local: `tests/test_viewer.py:69`. Caso: `ViewerTests.test_historical_reading_mode_keeps_top_at_250_percent`.

**O que confere:** Seleciona reading, exige zoom renderizado 250, âncora superior e topo mantido após troca de página.

**Limite:** Janela de teste e PDF sintético.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A22 Página vizinha em cache

Local: `tests/test_viewer.py:84`. Caso: `ViewerTests.test_prefetched_reader_page_is_immediate`.

**O que confere:** Espera vizinha pré-carregada, navega sincronamente em menos de 0,2 s e confere orçamento do cache.

**Limite:** Não mede página fria, abertura ou PDF pesado.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A23 Enquadramento e erro na apresentação

Local: `tests/test_viewer.py:91`. Caso: `ViewerTests.test_presentation_fit_fill_center_and_error`.

**O que confere:** Confere área útil e centralização, preencher, preservação de imagem ao simular falha e fundo branco de imagem transparente.

**Limite:** Erro injetado; não reproduz automaticamente o vídeo histórico.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A24 Resultado antigo não substitui página atual em cache

Local: `tests/test_viewer.py:123`. Caso: `ViewerTests.test_cached_presentation_page_invalidates_old_render`.

**O que confere:** Inicia render lento de outra página, volta à imagem em cache, libera tarefa antiga e exige preservação da página/imagem atual.

**Limite:** Concorrência controlada por eventos.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A25 Prioridade de navegação

Local: `tests/test_viewer.py:149`. Caso: `ViewerTests.test_render_is_not_blocked_by_auxiliary_workers`.

**O que confere:** Ocupa quatro trabalhos auxiliares e exige que outra página do leitor renderize antes da liberação deles.

**Limite:** Valida isolamento no caso controlado, não teto universal de fila.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A26 Descarte de tarefa pendente obsoleta

Local: `tests/test_viewer.py:163`. Caso: `ViewerTests.test_latest_renderer_skips_obsolete_queue_entries`.

**O que confere:** Com runner de um worker, mantém tarefa ocupada e substitui entrada page; exige cancelamento da anterior e execução somente da nova.

**Limite:** Fila artificial por canal; não prova orçamento global em bytes.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


### A27 Apresentação com formatos mistos

Local: `tests/test_viewer.py:176`. Caso: `ViewerTests.test_presentation_handles_portrait_and_landscape`.

**O que confere:** Cria PDF com página rotacionada, navega e confere paisagem dentro da área útil e enquadramento/centro.

**Limite:** Duas geometrias sintéticas.

**Resultado conhecido:** integra a suíte de 27 casos com aprovação registrada na entrega 3.4.0. Não foi reexecutado agora.


## Anexo B Mapa completo dos módulos próprios e símbolos

A presença de um símbolo é inventário de código, não declaração de cobertura integral. São listadas funções e classes de primeiro nível e métodos diretamente declarados nas classes; closures internos não são enumerados individualmente. As linhas são as da cópia examinada.


| Módulo | Linhas | Responsabilidade |
| --- | --- | --- |
| app/appearance.py | 158 | Preferências, migração Winux, integração GTK/GSettings, CSS e proteção de reentrada. |
| app/async_core.py | 108 | Pools de execução, canais, callbacks, sequências e eventos de cancelamento. |
| app/cancel_state.py | 12 | Evento de cancelamento local da thread para o wrapper de processos. |
| app/cups_backend.py | 450 | Descoberta de filas, PPD, mídia, propriedades, manutenção e envio CUPS. |
| app/imposition.py | 612 | Intervalos, papel, tamanho, N-up, livreto, pôster e dispatcher da preparação. |
| app/main.py | 1647 | Janela principal, ferramentas, busca, geometria de interação, painéis e coordenação da impressão. |
| app/page_cache.py | 32 | Cache LRU de imagens decodificadas com orçamento por quantidade e bytes. |
| app/pdf_dependency.py | 9 | Seleção da cópia de pypdf embutida para todas as plataformas. |
| app/pdf_panels.py | 106 | Inspeção de marcadores, comentários existentes e nomes de camadas. |
| app/platform_runtime.py | 18 | Python do worker e opções de subprocesso por sistema. |
| app/presentation.py | 562 | Apresentação, modos de enquadramento, zoom, pan, cache, laser e feedback de erros. |
| app/print_window.py | 1525 | Controles de impressão, propriedades, traduções de opções, prévia e construção do job. |
| app/rendering.py | 378 | Metadados, wrappers de Poppler, limites, caches de imagem, extração e geometria de palavras. |
| app/search_engine.py | 115 | Normalização de texto, ocorrências, cache de páginas e pesquisa incremental. |
| app/themes.py | 48 | API de compatibilidade de tema e carregamento do controlador consolidado. |
| app/version.py | 1 | Identificação 3.4.0 da aplicação. |
| app/windows_bootstrap.py | 43 | Realocação de DLLs, schemas, loaders, caminhos, configurações e log Windows. |
| app/windows_print.py | 97 | Impressoras Win32, propriedades e diálogo de impressão raster do documento preparado. |
| app/worker_cli.py | 107 | Subprocesso info/panels/prepare, limites POSIX e rasterização página a página. |


### app/appearance.py

Linhas: 158. Imports declarados: `gi`, `gi.repository`, `json`, `os`, `pathlib`, `tempfile`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| config_file | 14 | FunctionDef |
| read_mode | 19 | FunctionDef |
| save_mode | 39 | FunctionDef |
| AppearanceController | 65 | ClassDef |
| AppearanceController.__init__ | 66 | FunctionDef |
| AppearanceController._system_dark | 90 | FunctionDef |
| AppearanceController._system_changed | 106 | FunctionDef |
| AppearanceController.apply | 110 | FunctionDef |
| AppearanceController._apply | 119 | FunctionDef |
| AppearanceController.set_mode | 145 | FunctionDef |
| AppearanceController.close | 152 | FunctionDef |


### app/async_core.py

Linhas: 108. Imports declarados: `cancel_state`, `concurrent.futures`, `gi`, `gi.repository`, `threading`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| BackgroundRunner | 10 | ClassDef |
| BackgroundRunner.__init__ | 13 | FunctionDef |
| BackgroundRunner.invalidate | 22 | FunctionDef |
| BackgroundRunner.submit | 34 | FunctionDef |
| BackgroundRunner.shutdown | 94 | FunctionDef |


### app/cancel_state.py

Linhas: 12. Imports declarados: `threading`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| get_event | 7 | FunctionDef |
| set_event | 11 | FunctionDef |


### app/cups_backend.py

Linhas: 450. Imports declarados: `functools`, `os`, `re`, `shutil`, `subprocess`, `tempfile`, `urllib.parse`, `windows_print`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| _run | 10 | FunctionDef |
| available | 18 | FunctionDef |
| get_default_printer | 24 | FunctionDef |
| _device_uris | 37 | FunctionDef |
| _uri_identity | 51 | FunctionDef |
| list_printers | 77 | FunctionDef |
| get_ppd_options | 140 | FunctionDef |
| get_printer_details | 176 | FunctionDef |
| _ppd_path | 190 | FunctionDef |
| _fallback_media_size_points | 201 | FunctionDef |
| get_media_geometry | 231 | FunctionDef |
| get_maintenance_commands | 326 | FunctionDef |
| send_maintenance_command | 344 | FunctionDef |
| print_test_page | 366 | FunctionDef |
| launch_vendor_utility | 377 | FunctionDef |
| supports_duplex | 388 | FunctionDef |
| print_file | 397 | FunctionDef |


### app/imposition.py

Linhas: 612. Imports declarados: `cairo`, `copy`, `math`, `os`, `pathlib`, `pdf_dependency`, `pypdf`, `pypdf._page`, `re`, `sys`, `tempfile`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| paper_size_points | 36 | FunctionDef |
| oriented_paper | 63 | FunctionDef |
| parse_page_range | 72 | FunctionDef |
| select_page_indices | 109 | FunctionDef |
| _reader | 120 | FunctionDef |
| _normalized_page | 130 | FunctionDef |
| _place | 140 | FunctionDef |
| _blank | 155 | FunctionDef |
| _write | 159 | FunctionDef |
| create_sized | 166 | FunctionDef |
| _grid_for_nup | 179 | FunctionDef |
| _cell_order | 183 | FunctionDef |
| create_nup | 193 | FunctionDef |
| booklet_pairs | 227 | FunctionDef |
| booklet_print_pairs | 241 | FunctionDef |
| create_booklet | 255 | FunctionDef |
| _poster_geometry | 286 | FunctionDef |
| _merge_poster_marks | 307 | FunctionDef |
| poster_grid_for_size | 473 | FunctionDef |
| create_poster | 503 | FunctionDef |
| prepare_output | 574 | FunctionDef |
| selected_booklet_pairs | 611 | FunctionDef |


### app/main.py

Linhas: 1647. Imports declarados: `async_core`, `cups_backend`, `faulthandler`, `gi`, `gi.repository`, `json`, `math`, `os`, `page_cache`, `pathlib`, `pdf_panels`, `platform_runtime`, `presentation`, `print_window`, `rendering`, `search_engine`, `shutil`, `subprocess`, `sys`, `tempfile`, `themes`, `threading`, `time`, `traceback`, `windows_print`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| load_css | 42 | FunctionDef |
| PDFWindow | 46 | ClassDef |
| PDFWindow.__init__ | 47 | FunctionDef |
| PDFWindow._command_button | 136 | FunctionDef |
| PDFWindow._command_toggle | 153 | FunctionDef |
| PDFWindow._ribbon_group | 169 | FunctionDef |
| PDFWindow._ribbon_page | 182 | FunctionDef |
| PDFWindow._select_ribbon_tab | 196 | FunctionDef |
| PDFWindow._activate_ribbon_tab | 207 | FunctionDef |
| PDFWindow._build_ribbon | 212 | FunctionDef |
| PDFWindow._build_document_tabs | 407 | FunctionDef |
| PDFWindow._build_findbar | 431 | FunctionDef |
| PDFWindow._toggle_ribbon_stack | 472 | FunctionDef |
| PDFWindow._sidebar_rail_button | 484 | FunctionDef |
| PDFWindow._set_sidebar_visible | 494 | FunctionDef |
| PDFWindow._show_side_panel | 528 | FunctionDef |
| PDFWindow._build_body | 540 | FunctionDef |
| PDFWindow._build_status | 622 | FunctionDef |
| PDFWindow._status_page_activate | 645 | FunctionDef |
| PDFWindow._status_zoom_changed | 651 | FunctionDef |
| PDFWindow._apply_status_zoom | 662 | FunctionDef |
| PDFWindow._choose_open | 668 | FunctionDef |
| PDFWindow.open_document | 676 | FunctionDef |
| PDFWindow._load_failed | 708 | FunctionDef |
| PDFWindow._clear_document_state | 712 | FunctionDef |
| PDFWindow._close_document | 738 | FunctionDef |
| PDFWindow._set_actions_enabled | 741 | FunctionDef |
| PDFWindow._page_dimensions_rotated | 754 | FunctionDef |
| PDFWindow._target_final_width | 759 | FunctionDef |
| PDFWindow._render_width_for_poppler | 769 | FunctionDef |
| PDFWindow.request_render | 775 | FunctionDef |
| PDFWindow._reader_pixbuf | 815 | FunctionDef |
| PDFWindow._prefetch_reader_pages | 823 | FunctionDef |
| PDFWindow._theme_changed | 850 | FunctionDef |
| PDFWindow._system_theme_changed | 856 | FunctionDef |
| PDFWindow._display_pixbuf | 859 | FunctionDef |
| PDFWindow._apply_zoom_preview | 878 | FunctionDef |
| PDFWindow._viewer_scroll_event | 895 | FunctionDef |
| PDFWindow.goto_page | 915 | FunctionDef |
| PDFWindow._page_entry_activate | 928 | FunctionDef |
| PDFWindow._zoom_delta | 932 | FunctionDef |
| PDFWindow._zoom_100 | 951 | FunctionDef |
| PDFWindow._fit_page | 956 | FunctionDef |
| PDFWindow._fit_width | 960 | FunctionDef |
| PDFWindow._rotate | 964 | FunctionDef |
| PDFWindow._update_zoom_labels | 968 | FunctionDef |
| PDFWindow._on_resize | 978 | FunctionDef |
| PDFWindow._resize_render | 991 | FunctionDef |
| PDFWindow._clear_thumbnails | 995 | FunctionDef |
| PDFWindow._start_thumb_build | 999 | FunctionDef |
| PDFWindow._build_thumb_batch | 1002 | FunctionDef |
| PDFWindow._request_nearby_thumbnails | 1014 | FunctionDef |
| PDFWindow._thumb_selected | 1027 | FunctionDef |
| PDFWindow._select_thumb_row | 1030 | FunctionDef |
| PDFWindow._toggle_sidebar | 1035 | FunctionDef |
| PDFWindow._clear_listbox | 1045 | FunctionDef |
| PDFWindow._clear_side_panels | 1051 | FunctionDef |
| PDFWindow._info_row | 1057 | FunctionDef |
| PDFWindow._load_side_panels | 1065 | FunctionDef |
| PDFWindow._populate_side_panels | 1080 | FunctionDef |
| PDFWindow._bookmark_activated | 1120 | FunctionDef |
| PDFWindow._comment_activated | 1124 | FunctionDef |
| PDFWindow._tool_toggled | 1129 | FunctionDef |
| PDFWindow._update_tool_cursor | 1146 | FunctionDef |
| PDFWindow._norm_rect | 1154 | FunctionDef |
| PDFWindow._interaction_press | 1158 | FunctionDef |
| PDFWindow._interaction_motion | 1176 | FunctionDef |
| PDFWindow._interaction_release | 1189 | FunctionDef |
| PDFWindow._interaction_leave | 1203 | FunctionDef |
| PDFWindow._interaction_draw | 1207 | FunctionDef |
| PDFWindow._finish_snapshot | 1242 | FunctionDef |
| PDFWindow._display_rect_to_pdf | 1251 | FunctionDef |
| PDFWindow._pdf_rect_to_display | 1265 | FunctionDef |
| PDFWindow._finish_text_selection | 1280 | FunctionDef |
| PDFWindow._finish_measure | 1304 | FunctionDef |
| PDFWindow._find_result_activated | 1309 | FunctionDef |
| PDFWindow._find_update_results | 1314 | FunctionDef |
| PDFWindow._hide_find | 1335 | FunctionDef |
| PDFWindow._select_search_hit | 1349 | FunctionDef |
| PDFWindow._scroll_to_search_hit | 1366 | FunctionDef |
| PDFWindow._show_find | 1383 | FunctionDef |
| PDFWindow._find_changed | 1387 | FunctionDef |
| PDFWindow._start_search | 1400 | FunctionDef |
| PDFWindow._update_find_status | 1439 | FunctionDef |
| PDFWindow._find_next | 1448 | FunctionDef |
| PDFWindow._find_prev | 1452 | FunctionDef |
| PDFWindow._save_copy | 1457 | FunctionDef |
| PDFWindow._copy_page_text | 1468 | FunctionDef |
| PDFWindow._export_png | 1476 | FunctionDef |
| PDFWindow._properties | 1484 | FunctionDef |
| PDFWindow._present | 1495 | FunctionDef |
| PDFWindow._fullscreen_toggle | 1500 | FunctionDef |
| PDFWindow._reading_mode_toggle | 1505 | FunctionDef |
| PDFWindow._print | 1518 | FunctionDef |
| PDFWindow._submit_print_job | 1523 | FunctionDef |
| PDFWindow._on_key | 1551 | FunctionDef |
| PDFWindow._error | 1573 | FunctionDef |
| PDFWindow._on_destroy | 1577 | FunctionDef |
| _cleanup_stale_render_caches | 1586 | FunctionDef |
| _install_diagnostics | 1602 | FunctionDef |
| main | 1638 | FunctionDef |


### app/page_cache.py

Linhas: 32. Imports declarados: `collections`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| PageCache | 4 | ClassDef |
| PageCache.__init__ | 6 | FunctionDef |
| PageCache.get | 12 | FunctionDef |
| PageCache.put | 18 | FunctionDef |
| PageCache.clear | 31 | FunctionDef |


### app/pdf_dependency.py

Linhas: 9. Imports declarados: `pathlib`, `sys`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| configure_pdf_library | 5 | FunctionDef |


### app/pdf_panels.py

Linhas: 106. Imports declarados: `pathlib`, `pypdf`, `sys`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| _obj | 16 | FunctionDef |
| _text | 23 | FunctionDef |
| inspect_document_panels | 32 | FunctionDef |


### app/platform_runtime.py

Linhas: 18. Imports declarados: `os`, `pathlib`, `sys`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| worker_python | 7 | FunctionDef |
| subprocess_options | 17 | FunctionDef |


### app/presentation.py

Linhas: 562. Imports declarados: `async_core`, `gi`, `gi.repository`, `math`, `page_cache`, `rendering`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| PresentationWindow | 24 | ClassDef |
| PresentationWindow.__init__ | 39 | FunctionDef |
| PresentationWindow._destroyed | 121 | FunctionDef |
| PresentationWindow._toolbar | 137 | FunctionDef |
| PresentationWindow._update_labels | 174 | FunctionDef |
| PresentationWindow._goto | 180 | FunctionDef |
| PresentationWindow._set_zoom | 191 | FunctionDef |
| PresentationWindow._canvas_size | 210 | FunctionDef |
| PresentationWindow._base_width_for | 216 | FunctionDef |
| PresentationWindow._controls_height | 227 | FunctionDef |
| PresentationWindow._fit_changed | 230 | FunctionDef |
| PresentationWindow._target_width_for | 238 | FunctionDef |
| PresentationWindow._target_width | 241 | FunctionDef |
| PresentationWindow._cache_get | 244 | FunctionDef |
| PresentationWindow._cache_put | 247 | FunctionDef |
| PresentationWindow._apply_pixbuf | 250 | FunctionDef |
| PresentationWindow._load_page_pixbuf | 262 | FunctionDef |
| PresentationWindow._request_render | 266 | FunctionDef |
| PresentationWindow._prefetch_neighbours | 304 | FunctionDef |
| PresentationWindow._pan_bounds | 339 | FunctionDef |
| PresentationWindow._clamp_target_pan | 352 | FunctionDef |
| PresentationWindow._set_pan_target | 357 | FunctionDef |
| PresentationWindow._pan_by | 370 | FunctionDef |
| PresentationWindow._ensure_animation | 375 | FunctionDef |
| PresentationWindow._animate_pan | 379 | FunctionDef |
| PresentationWindow._size_allocate | 393 | FunctionDef |
| PresentationWindow._draw | 414 | FunctionDef |
| PresentationWindow._motion | 440 | FunctionDef |
| PresentationWindow._button_press | 448 | FunctionDef |
| PresentationWindow._button_release | 455 | FunctionDef |
| PresentationWindow._scroll | 465 | FunctionDef |
| PresentationWindow._laser_toggle | 504 | FunctionDef |
| PresentationWindow._color_changed | 508 | FunctionDef |
| PresentationWindow._key | 514 | FunctionDef |


### app/print_window.py

Linhas: 1525. Imports declarados: `cairo`, `cups_backend`, `gi`, `gi.repository`, `imposition`, `math`, `os`, `pathlib`, `re`, `rendering`, `windows_print`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| _system_language | 20 | FunctionDef |
| _paper_size_display | 105 | FunctionDef |
| _choice_display | 141 | FunctionDef |
| OptionPicker | 221 | ClassDef |
| OptionPicker.__init__ | 222 | FunctionDef |
| OptionPicker._on_choice | 242 | FunctionDef |
| PrinterPropertiesWindow | 247 | ClassDef |
| PrinterPropertiesWindow.__init__ | 248 | FunctionDef |
| PrinterPropertiesWindow._format_cups_date | 273 | FunctionDef |
| PrinterPropertiesWindow._maintenance_summary | 287 | FunctionDef |
| PrinterPropertiesWindow._maintenance_page | 346 | FunctionDef |
| PrinterPropertiesWindow._maintenance_action | 456 | FunctionDef |
| PrinterPropertiesWindow._make_page | 532 | FunctionDef |
| PrinterPropertiesWindow._pick | 562 | FunctionDef |
| PrinterPropertiesWindow.result | 573 | FunctionDef |
| PrintWindow | 577 | ClassDef |
| PrintWindow.__init__ | 578 | FunctionDef |
| PrintWindow._set_workarea_size | 628 | FunctionDef |
| PrintWindow._frame | 637 | FunctionDef |
| PrintWindow._build_destination_bar | 642 | FunctionDef |
| PrintWindow._build_preview | 691 | FunctionDef |
| PrintWindow._build_settings | 718 | FunctionDef |
| PrintWindow._build_range | 727 | FunctionDef |
| PrintWindow._build_handling | 758 | FunctionDef |
| PrintWindow._size_page | 789 | FunctionDef |
| PrintWindow._poster_page | 803 | FunctionDef |
| PrintWindow._poster_overlap_mm | 858 | FunctionDef |
| PrintWindow._multiple_page | 863 | FunctionDef |
| PrintWindow._booklet_page | 888 | FunctionDef |
| PrintWindow._load_printers_async | 923 | FunctionDef |
| PrintWindow._destination_changed | 940 | FunctionDef |
| PrintWindow._open_properties | 951 | FunctionDef |
| PrintWindow._request_preview_image | 986 | FunctionDef |
| PrintWindow._preview_loaded | 993 | FunctionDef |
| PrintWindow._booklet_faces | 1002 | FunctionDef |
| PrintWindow._current_booklet_face | 1008 | FunctionDef |
| PrintWindow._booklet_step | 1013 | FunctionDef |
| PrintWindow._mode_thumbnail_indices | 1020 | FunctionDef |
| PrintWindow._request_mode_thumbnails | 1042 | FunctionDef |
| PrintWindow._draw_pixbuf_in_rect | 1067 | FunctionDef |
| PrintWindow._controls_changed | 1081 | FunctionDef |
| PrintWindow._set_label_text | 1103 | FunctionDef |
| PrintWindow._refresh_preview_labels | 1108 | FunctionDef |
| PrintWindow._close_window | 1177 | FunctionDef |
| PrintWindow._on_destroy | 1186 | FunctionDef |
| PrintWindow._page_range | 1207 | FunctionDef |
| PrintWindow._page_set | 1214 | FunctionDef |
| PrintWindow._selected_indices | 1217 | FunctionDef |
| PrintWindow._paper_name | 1220 | FunctionDef |
| PrintWindow._poster_media_geometry | 1223 | FunctionDef |
| PrintWindow._update_paper_label | 1235 | FunctionDef |
| PrintWindow._draw_dotted | 1242 | FunctionDef |
| PrintWindow._draw_sheet | 1253 | FunctionDef |
| PrintWindow._draw_preview | 1261 | FunctionDef |
| PrintWindow._submit | 1470 | FunctionDef |


### app/rendering.py

Linhas: 378. Imports declarados: `bisect`, `cancel_state`, `hashlib`, `math`, `os`, `pathlib`, `pdf_dependency`, `platform_runtime`, `pypdf`, `re`, `search_engine`, `shutil`, `signal`, `subprocess`, `sys`, `tempfile`, `time`, `unicodedata`, `xml.etree.ElementTree`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| _run | 22 | FunctionDef |
| document_info | 67 | FunctionDef |
| _valid_png | 93 | FunctionDef |
| _valid_jpeg | 111 | FunctionDef |
| render_page | 126 | FunctionDef |
| _prune_image_cache | 216 | FunctionDef |
| _page_limit | 236 | FunctionDef |
| render_page_to_png | 248 | FunctionDef |
| extract_page_text | 265 | FunctionDef |
| _word_match_rectangle | 271 | FunctionDef |
| _parse_search_page | 280 | FunctionDef |
| search_text | 333 | FunctionDef |
| safe_filename_from_pdf | 338 | FunctionDef |
| extract_page_words | 344 | FunctionDef |
| _parse_word_pages | 360 | FunctionDef |


### app/search_engine.py

Linhas: 115. Imports declarados: `collections`, `pathlib`, `rendering`, `threading`, `unicodedata`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| normalized | 10 | FunctionDef |
| page_hits | 20 | FunctionDef |
| TextSearchIndex | 61 | ClassDef |
| TextSearchIndex.__init__ | 63 | FunctionDef |
| TextSearchIndex._identity | 75 | FunctionDef |
| TextSearchIndex.page | 79 | FunctionDef |
| TextSearchIndex.search | 97 | FunctionDef |


### app/themes.py

Linhas: 48. Imports declarados: `appearance`, `gi`, `gi.repository`, `pathlib`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| preferences_path | 15 | FunctionDef |
| read_theme | 19 | FunctionDef |
| save_theme | 24 | FunctionDef |
| load_theme | 28 | FunctionDef |


### app/version.py

Linhas: 1. Imports declarados: .


Não há funções ou classes declaradas de primeiro nível neste arquivo.


### app/windows_bootstrap.py

Linhas: 43. Imports declarados: `main`, `os`, `pathlib`, `sys`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| configure | 12 | FunctionDef |


### app/windows_print.py

Linhas: 97. Imports declarados: `cairo`, `ctypes`, `gi`, `gi.repository`, `os`, `pathlib`, `rendering`, `tempfile`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| show_properties | 7 | FunctionDef |
| list_printers | 21 | FunctionDef |
| print_dialog | 43 | FunctionDef |


### app/worker_cli.py

Linhas: 107. Imports declarados: `PIL`, `imposition`, `json`, `os`, `pathlib`, `pdf_panels`, `rendering`, `resource`, `subprocess`, `sys`, `tempfile`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| _rasterize_pdf_in_place | 17 | FunctionDef |
| main | 69 | FunctionDef |


### scripts/analyze_windows_readers.py

Linhas: 159. Imports declarados: `argparse`, `hashlib`, `json`, `pathlib`, `pefile`, `re`, `struct`, `subprocess`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| dialog | 18 | FunctionDef |
| inspect | 61 | FunctionDef |


### scripts/build_deb.py

Linhas: 61. Imports declarados: `pathlib`, `shutil`, `subprocess`, `sys`, `tempfile`, `version`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| build | 14 | FunctionDef |


### scripts/build_flatpak.py

Linhas: 185. Imports declarados: `argparse`, `os`, `pathlib`, `re`, `shutil`, `subprocess`, `sys`, `version`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| build | 17 | FunctionDef |


### scripts/build_windows.py

Linhas: 97. Imports declarados: `argparse`, `hashlib`, `json`, `pathlib`, `shutil`, `subprocess`, `sys`, `urllib.request`, `version`, `zipfile`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| extract | 18 | FunctionDef |
| build | 24 | FunctionDef |


### scripts/smoke_windows.py

Linhas: 71. Imports declarados: `argparse`, `cairo`, `gi.repository`, `imposition`, `json`, `main`, `pathlib`, `pypdf`, `sys`, `tempfile`, `time`, `windows_bootstrap`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| poll | 44 | FunctionDef |


### scripts/verify_winux_history.py

Linhas: 230. Imports declarados: `appearance`, `atexit`, `cairo`, `cancel_state`, `cups_backend`, `gi`, `gi.repository`, `hashlib`, `imposition`, `json`, `main`, `os`, `pathlib`, `presentation`, `print_window`, `pypdf`, `rendering`, `subprocess`, `sys`, `tempfile`, `threading`, `time`, `unittest`, `unittest.mock`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| make_pdf | 42 | FunctionDef |
| wait_for | 55 | FunctionDef |
| HistoryChecks | 69 | ClassDef |
| HistoryChecks.setUp | 70 | FunctionDef |
| HistoryChecks.tearDown | 79 | FunctionDef |
| HistoryChecks.reader | 85 | FunctionDef |
| HistoryChecks.test_search_occurrences_case_and_whole_words | 98 | FunctionDef |
| HistoryChecks.test_search_query_bound | 105 | FunctionDef |
| HistoryChecks.test_jpeg_png_and_document_cache_identity | 109 | FunctionDef |
| HistoryChecks.test_booklet_output_all_sides | 118 | FunctionDef |
| HistoryChecks.test_running_process_cancellation | 125 | FunctionDef |
| HistoryChecks.test_cups_option_validation_without_printing | 142 | FunctionDef |
| HistoryChecks.test_theme_persistence_preserves_other_settings | 149 | FunctionDef |
| HistoryChecks.test_system_theme_controller_initializes | 159 | FunctionDef |
| HistoryChecks.test_reader_search_sidebar_and_navigation | 169 | FunctionDef |
| HistoryChecks.test_presentation_initial_zoom_top_and_navigation | 178 | FunctionDef |
| HistoryChecks.test_booklet_preview_browses_all_faces | 192 | FunctionDef |


### tests/test_consolidation.py

Linhas: 40. Imports declarados: `cancel_state`, `os`, `pathlib`, `rendering`, `subprocess`, `sys`, `tempfile`, `test_regressions`, `threading`, `time`, `unittest`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| ConsolidationTests | 15 | ClassDef |
| ConsolidationTests.test_fresh_system_theme_initializes_and_migrates_legacy | 17 | FunctionDef |
| ConsolidationTests.test_active_process_cancellation | 31 | FunctionDef |


### tests/test_gui.py

Linhas: 155. Imports declarados: `cairo`, `gi`, `gi.repository`, `main`, `os`, `pathlib`, `print_window`, `search_engine`, `sys`, `tempfile`, `test_regressions`, `threading`, `time`, `unittest`, `unittest.mock`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| wait_for | 18 | FunctionDef |
| GUIRegressionTests | 31 | ClassDef |
| GUIRegressionTests.setUp | 32 | FunctionDef |
| GUIRegressionTests.tearDown | 48 | FunctionDef |
| GUIRegressionTests.test_search_navigation_selection_and_rotation | 53 | FunctionDef |
| GUIRegressionTests.test_search_sidebar_scroll_and_all_booklet_faces | 75 | FunctionDef |
| GUIRegressionTests.test_booklet_preview_sides_binding_and_submit | 97 | FunctionDef |
| GUIRegressionTests.test_search_results_arrive_before_end_and_options_cancel_old_query | 122 | FunctionDef |


### tests/test_regressions.py

Linhas: 128. Imports declarados: `PIL`, `cairo`, `cups_backend`, `imposition`, `json`, `os`, `pathlib`, `pypdf`, `rendering`, `subprocess`, `sys`, `tempfile`, `unittest`, `unittest.mock`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| make_pdf | 20 | FunctionDef |
| CoreRegressionTests | 33 | ClassDef |
| CoreRegressionTests.setUp | 34 | FunctionDef |
| CoreRegressionTests.tearDown | 40 | FunctionDef |
| CoreRegressionTests.test_cache_distinguishes_documents | 43 | FunctionDef |
| CoreRegressionTests.test_booklet_generated_sides_and_binding | 51 | FunctionDef |
| CoreRegressionTests.test_search_has_individual_occurrence_coordinates | 65 | FunctionDef |
| CoreRegressionTests.test_manual_booklet_sides_are_not_duplex | 72 | FunctionDef |
| CoreRegressionTests.test_worker_prepares_nup_and_poster | 84 | FunctionDef |
| CoreRegressionTests.test_intrinsic_rotation_and_cropbox_match_text_geometry | 94 | FunctionDef |
| CoreRegressionTests.test_search_phrases_and_casefold_expansion | 112 | FunctionDef |
| CoreRegressionTests.test_nup_worker_rejects_fractional_count | 121 | FunctionDef |


### tests/test_search.py

Linhas: 56. Imports declarados: `search_engine`, `sys`, `test_regressions`, `threading`, `unittest`, `unittest.mock`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| SearchTests | 11 | ClassDef |
| SearchTests.test_options_and_real_pdf | 14 | FunctionDef |
| SearchTests.test_cache_reuse_and_cancellation_progress | 25 | FunctionDef |
| SearchTests.test_hyphenation_does_not_join_columns | 39 | FunctionDef |
| SearchTests.test_cache_eviction_and_changed_file | 49 | FunctionDef |


### tests/test_viewer.py

Linhas: 194. Imports declarados: `async_core`, `cairo`, `cancel_state`, `main`, `os`, `pathlib`, `presentation`, `pypdf`, `rendering`, `sys`, `test_gui`, `test_regressions`, `themes`, `threading`, `time`, `unittest`, `unittest.mock`.


| Símbolo | Linha | Tipo |
| --- | --- | --- |
| ViewerTests | 21 | ClassDef |
| ViewerTests.setUp | 25 | FunctionDef |
| ViewerTests.tearDown | 33 | FunctionDef |
| ViewerTests.test_theme_persistence_and_contrast | 36 | FunctionDef |
| ViewerTests.test_repeated_requests_do_not_cancel_same_running_render | 49 | FunctionDef |
| ViewerTests.test_historical_reading_mode_keeps_top_at_250_percent | 69 | FunctionDef |
| ViewerTests.test_prefetched_reader_page_is_immediate | 84 | FunctionDef |
| ViewerTests.test_presentation_fit_fill_center_and_error | 91 | FunctionDef |
| ViewerTests.test_cached_presentation_page_invalidates_old_render | 123 | FunctionDef |
| ViewerTests.test_render_is_not_blocked_by_auxiliary_workers | 149 | FunctionDef |
| ViewerTests.test_latest_renderer_skips_obsolete_queue_entries | 163 | FunctionDef |
| ViewerTests.test_presentation_handles_portrait_and_landscape | 176 | FunctionDef |


## Anexo C Todos os pacotes e a conferência de integridade atual


### PrintViewPDF-3.4.0-Setup-x64.exe

Categoria: Entrega 3.4.0. Tamanho: 67,017,156 bytes.

SHA-256 recalculado: `2ee91c8828db0d246c5129bded8a47825fa681daf1b575f80bf4dd99989ab43e`.

Coincide com SHA256SUMS: **sim**.


### PrintViewPDF-3.4.0-x86_64.flatpak

Categoria: Entrega 3.4.0. Tamanho: 43,197,720 bytes.

SHA-256 recalculado: `7f5926f32a5034677d6c26e947029e8359d511f29cdfbacc9afd27d1a38b7b08`.

Coincide com SHA256SUMS: **sim**.


### print-view-pdf_3.3.7~test1_all.deb

Categoria: Histórico de teste. Tamanho: 330,748 bytes.

SHA-256 recalculado: `f12e476cf114eff9588dad3cfb5427376a0a5d06eddc57555472b6cd428c1bab`.

Coincide com SHA256SUMS: **sim**.


### print-view-pdf_3.3.7~test2_all.deb

Categoria: Histórico de teste. Tamanho: 333,884 bytes.

SHA-256 recalculado: `534d7ccf6168c4529cbb4dcead7b4b08aee58a188cca1093e4be0f9eb204abb0`.

Coincide com SHA256SUMS: **sim**.


### print-view-pdf_3.4.0_all.deb

Categoria: Entrega 3.4.0. Tamanho: 389,952 bytes.

SHA-256 recalculado: `229023b13486d51df93170a70623fedbb2dd2ff7fd188044e1bf7224c5c86273`.

Coincide com SHA256SUMS: **sim**.


### print-view-pdf_3.4.0_source.tar.gz

Categoria: Entrega 3.4.0. Tamanho: 684,912 bytes.

SHA-256 recalculado: `5d1858a527d741c303617e391c055d7d224011075cf358fb172c3a5932772fb2`.

Coincide com SHA256SUMS: **sim**.


### Comparação com os hashes de módulos da entrega

A comparação normalizada abaixo usa LF para os finais de linha. O hash original esperado é preservado para reprodução. Não é afirmação de igualdade binária do checkout CRLF.


| Arquivo | Hash esperado do registro | Conteúdo normalizado corresponde |
| --- | --- | --- |
| app/appearance.py | 1f41078231d6a7ab85b817826978591724f1a0dcbe05556acfc23499d4f229ae | sim |
| app/async_core.py | b38ee3f425c924bc9a681a46095f99d0903079caf7d5f125887c61060a990d0f | sim |
| app/cancel_state.py | c56c1cca7cb33f8375bc716ab60751952067f9eb720f48bd3df4746f36d5c820 | sim |
| app/cups_backend.py | cf6732cb028c35c9fc09abd394ed20864d71420e741a6a016f860b8f9508f282 | sim |
| app/imposition.py | 8a19f036dd11e5a6eef38d17f09777e61c9b6c4a3cd21c71b7da1b6b29a1ac37 | sim |
| app/main.py | 5d49481f09f36a7e0b6c30d75a80a587822824135657c9bce57538118fefb949 | sim |
| app/page_cache.py | d339231d4d4dc06cc9c7c08190bdf72874294f7e0e2a609e1a772254c09ae856 | sim |
| app/pdf_dependency.py | b97a5431551b8a1fa5a3f49e27a7791e9753309975b9247baf8d70aac6cca8e5 | sim |
| app/pdf_panels.py | 7390a26fc7015643450afbe562fbddf96a25a3d857a3faf7384ba4fd342878b2 | sim |
| app/platform_runtime.py | 7c6d03d0f6032a4d0888be248e299ea43a009ae563ed89cd18fed85cdbbbfe74 | sim |
| app/presentation.py | 9d0fec9c32ef15a43a56780c2332d6270e4c24527be57e8dd16b1e6d3ad525e5 | sim |
| app/print_window.py | 99421e880dee024a58485a93a51f38332fb7f708a7e114d02deca9669bf83a6e | sim |
| app/rendering.py | 8d519f2129f2061b370b0b9d2eca6ee81f788b6a100c3e3f47c3552063cf08e4 | sim |
| app/search_engine.py | 3a1d4912ffba06374066a17fafe8824fdd37466365586c76cf9e7fd43a459bb8 | sim |
| app/themes.py | c5263f1a61d5e72db45704a597f0214fb48c5e47d79b55492cc30575d2b7edc9 | sim |
| app/version.py | 36f7896ab9f499430c7386716be5f1bbde6780af116c9a49497ec13c45026455 | sim |
| app/windows_bootstrap.py | 537bf137e997dec1e61f19bb9adaa178ad1307118b793583b8c4cf3bc3e894f8 | sim |
| app/windows_print.py | 3c2905d38de3ac9d601071ebd1650c39f264bc8ec50f85cc7e135cf483d26cd4 | sim |
| app/worker_cli.py | aa2f2fa1922e3b58c8131f1b852f246162a01990318053e8c5b03970f05e8fbb | sim |


### Comparação do conteúdo de aplicação dos arquivos Debian e fontes


| Pacote | Arquivos comparados | Diferentes em bytes | Diferentes após normalizar finais de linha |
| --- | --- | --- | --- |
| packages/print-view-pdf_3.4.0_source.tar.gz | 81 | 80 | 0 |
| packages/print-view-pdf_3.4.0_all.deb | 81 | 80 | 0 |


## Anexo D Os 18 pacotes Winux da auditoria histórica

Este inventário reproduz os dados do manifest histórico; os pacotes Winux originais não foram novamente baixados ou executados agora. A coluna de diferenças se refere ao pacote fornecido anteriormente na sequência da auditoria, não a todos os passos de desenvolvimento que possam ter existido.


| Versão | pypdf registrado | SHA-256 do pacote |
| --- | --- | --- |
| 2.3.0 | 5.9.0 | 1320acd4c8ec8fd44569353bdbd8b807e5e2223c03e06cb19eb541c643f064b2 |
| 3.0.0 | 5.9.0 | fbdb4f0c2a3315180145160185dbc7fb33ca5b884d59902d568febe9836c836d |
| 3.1.0 | 5.9.0 | f46fd8dbbf0623dacdcec59fef8b4e4f65dfcba0dd622a7b978329bd388d359c |
| 3.1.1 | 5.9.0 | 1e0854a91c41611fca11b880f05e62e31011119d57cff95cc7b55f91c65fe59e |
| 3.1.3 | 5.9.0 | ed20e15852a73c858a1b4be8a6458a6e68e6b58d41378579ba84bc726aec4eb9 |
| 3.2.0 | 5.9.0 | 0af5adf4b30aac1ef23360e02a59e1d8f24714c1afe12d4f069bc911561eb5d7 |
| 3.3.0 | 6.10.0 | 1a5d72429cafdf4e836708fdf356f665e45bf16b2b9dd88394e9d4b4c9ea336e |
| 3.3.1 | 6.10.0 | 0f5f3882ec48669cf9227be138fe4d8f2da276b9a98e373da0bb1181a064f6c6 |
| 3.3.2 | 6.10.0 | d7271c90412a64b36620b5718d31d61aa09baac8eee4b22c0714b1072a2a7654 |
| 3.3.3 | 6.10.0 | b2cce021bc238fc12fcb51165a9635ad8723c9dbbdaad10b233386db3a586a77 |
| 3.3.4 | 6.10.0 | 8fafdb0b2a82bf6602c04cfd77c2d8a16ef6aed652f23ccf873290146a202107 |
| 3.3.5 | 6.10.0 | c4f816f508f0e46dde8ecfc37b8a18c6409223540451694fb3bc51bd3b5e86ca |
| 3.3.6 | 6.10.0 | ffce05b0c6dac2cddbcfc1c6a7bd7317d8fe48c7f8670022551eb68dccc92b58 |
| 3.3.7 | 6.10.0 | a0e3baab2bb106a67da39de2426b864eb2636c10e086c93391972f3eaf59e9b9 |
| 3.3.8 | 6.10.0 | c495dd35d40fca60d409f3ea359bd1272f9b587c68d3362dd0a15f86433cb8df |
| 3.3.9 | 6.10.0 | ff19a3644a7a987db2371cc5b99de1c1e9b4b08ccb9e0a195ca67af791b6264f |
| 3.3.10 | 6.10.0 | 9045e5d1788e8644be234745d79aa5514e776cf2c81224a7c96ae65df823f907 |
| 3.3.11 | 6.10.0 | 0f8b75a443ed7bb70a6dc88af69561b982025863c8e2d3669b0b617092772342 |


### Winux 2.3.0

Arquivos próprios alterados em relação à versão fornecida anterior: `async_core.py`, `cups_backend.py`, `imposition.py`, `main.py`, `pdf_panels.py`, `presentation.py`, `print_window.py`, `rendering.py`, `style.css`, `worker_cli.py`.


### Winux 3.0.0

Arquivos próprios alterados em relação à versão fornecida anterior: `main.py`, `style.css`.


### Winux 3.1.0

Arquivos próprios alterados em relação à versão fornecida anterior: `main.py`, `style.css`.


### Winux 3.1.1

Arquivos próprios alterados em relação à versão fornecida anterior: `main.py`, `print_window.py`.


### Winux 3.1.3

Arquivos próprios alterados em relação à versão fornecida anterior: `imposition.py`, `print_window.py`.


### Winux 3.2.0

Arquivos próprios alterados em relação à versão fornecida anterior: `cups_backend.py`, `imposition.py`, `print_window.py`.


### Winux 3.3.0

Arquivos próprios alterados em relação à versão fornecida anterior: `cups_backend.py`, `imposition.py`, `main.py`, `pdf_panels.py`, `print_window.py`, `rendering.py`, `style.css`, `worker_cli.py`.


### Winux 3.3.1

Arquivos próprios alterados em relação à versão fornecida anterior: `print_window.py`.


### Winux 3.3.2

Arquivos próprios alterados em relação à versão fornecida anterior: `print_window.py`.


### Winux 3.3.3

Arquivos próprios alterados em relação à versão fornecida anterior: `cups_backend.py`, `imposition.py`, `main.py`, `print_window.py`.


### Winux 3.3.4

Arquivos próprios alterados em relação à versão fornecida anterior: `imposition.py`, `main.py`, `print_window.py`.


### Winux 3.3.5

Arquivos próprios alterados em relação à versão fornecida anterior: `imposition.py`, `presentation.py`, `print_window.py`.


### Winux 3.3.6

Arquivos próprios alterados em relação à versão fornecida anterior: `appearance.py`, `main.py`, `style-dark.css`.


### Winux 3.3.7

Arquivos próprios alterados em relação à versão fornecida anterior: `imposition.py`, `main.py`, `print_window.py`, `rendering.py`.


### Winux 3.3.8

Arquivos próprios alterados em relação à versão fornecida anterior: `presentation.py`.


### Winux 3.3.9

Arquivos próprios alterados em relação à versão fornecida anterior: `cups_backend.py`, `imposition.py`, `print_window.py`.


### Winux 3.3.10

Arquivos próprios alterados em relação à versão fornecida anterior: `async_core.py`, `main.py`, `presentation.py`, `rendering.py`.


### Winux 3.3.11

Arquivos próprios alterados em relação à versão fornecida anterior: `appearance.py`, `async_core.py`, `cancel_state.py`, `cups_backend.py`, `imposition.py`, `main.py`, `pdf_dependency.py`, `pdf_panels.py`, `rendering.py`, `worker_cli.py`.


## Anexo E Documentos narrativos completos do repositório

Os oito documentos seguintes estão transcritos integralmente, com níveis de títulos ajustados para caber no relatório e links de arquivos reposicionados. Seus limites, hipóteses e pendências pertencem às etapas indicadas em cada texto. O corpo do relatório explica quais foram superados pela 3.4.0.


### Documento README.md

#### Print&View PDF

Print&View PDF é a continuação do Winux PDF: um leitor com busca progressiva,
apresentação e preparação de impressão em livreto, pôster e várias páginas
por folha. A versão **3.4.0** consolida os recursos da Winux **3.3.11** com as
melhorias do Print&View, sem sufixo de teste.

##### Downloads

| Sistema | Pacote |
|---|---|
| Debian/Ubuntu | [print-view-pdf_3.4.0_all.deb](../packages/print-view-pdf_3.4.0_all.deb) |
| Linux com Flatpak, x86_64 | [PrintViewPDF-3.4.0-x86_64.flatpak](../packages/PrintViewPDF-3.4.0-x86_64.flatpak) |
| Windows 10/11, x64 | [PrintViewPDF-3.4.0-Setup-x64.exe](../packages/PrintViewPDF-3.4.0-Setup-x64.exe) |

Confira a integridade em [SHA256SUMS](../packages/SHA256SUMS). Os pacotes antigos
com `~test` permanecem como histórico; use os arquivos **3.4.0** acima.

##### Recursos

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

##### Instalar

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

##### Desenvolvimento

No Debian/Ubuntu, instale Python do sistema, GTK 3, GI/Cairo, Pillow,
cryptography, Poppler e CUPS client, então execute:

```bash
bash scripts/run.sh /caminho/documento.pdf
/usr/bin/python3 -m unittest discover -s tests -v
/usr/bin/python3 scripts/build_deb.py
```

Os testes gráficos exigem `DISPLAY`. O pypdf **6.20.1** está fixado em
`app/vendor` com sua licença preservada. Outros formatos são gerados por
[scripts/build_flatpak.py](../scripts/build_flatpak.py) e
[scripts/build_windows.py](../scripts/build_windows.py); consulte
[empacotamento e validação](../docs/ENTREGA-3.4.0.md).

As verificações automatizadas não substituem impressão física nem validação
com documentos grandes. O conteúdo do Flatpak foi exercitado fora do sandbox;
a instalação no sandbox requer validação na distribuição de destino. O
runtime Windows foi exercitado no Wine, sem certificar comportamento em todo
Windows/driver. Veja os resultados e limites em [ENTREGA-3.4.0](../docs/ENTREGA-3.4.0.md).

A referência é o desenvolvimento próprio do Winux. A
[análise estática do Foxit e UPDF](../docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md) é parcial;
não há alegação de equivalência completa nem código ou recursos desses leitores
incorporados à aplicação. A [revisão histórica](../docs/REVISAO-HISTORICO-WINUX.md)
registra a evolução dos 18 pacotes e a origem dos recursos.


### Documento docs/PROVENIENCIA.md

#### Origem e limites dos artefatos

Estado atual: **Print&View PDF 3.4.0**, com pypdf embutido **6.20.1**.
Os parágrafos abaixo registram também as etapas anteriores da recuperação.

O usuário declarou que o Winux foi desenvolvido por sua equipe e autorizou
sua continuidade com o nome Print&View PDF. O ponto de partida é o pacote
`winux-pdf_3.3.5_all.deb` fornecido nesta conversa, extraído com `dpkg-deb -x`,
sem executar os scripts de instalação do pacote.
SHA-256: `c4f816f508f0e46dde8ecfc37b8a18c6409223540451694fb3bc51bd3b5e86ca`.

O código em `app/` veio de `/usr/share/winux-pdf/`; os ícones em `assets/icons/`
vieram de `/usr/share/icons/hicolor/`. A cópia original extraída permanece
fora do checkout, em `/workspace/winux-reference`.
`winux-3.3.5-source-sha256.json` registra os hashes dos arquivos **antes**
das alterações. A licença MIT existente no repositório foi preservada;
os avisos e a licença BSD do pypdf também foram preservados.

O `.deb` antigo não incluía uma licença explícita da aplicação e seu documento
de copyright registrava essa ausência. Não se atribui licença MIT ao Foxit,
ao UPDF ou a seus componentes. Nenhum binário, imagem, ícone ou código desses
produtos foi incorporado à aplicação. As informações deles no repositório
são metadados/evidências da inspeção estática, incluindo os leitores completos
posteriormente obtidos pelo Google Drive, conforme o relatório de
[engenharia reversa](../docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md).

O arquivo de contexto é um relato histórico, não uma ordem de execução nem
evidência de que uma funcionalidade funciona. As primeiras correções e os
pacotes test1/test2 partiram da 3.3.5. Posteriormente foram fornecidos os três
PDFs históricos e os pacotes até **3.3.11**, totalizando 18 versões analisadas.
Os hashes estão em [historico-winux-manifest.json](../docs/historico-winux-manifest.json),
e a comparação em [REVISAO-HISTORICO-WINUX.md](../docs/REVISAO-HISTORICO-WINUX.md).
A entrega 3.4.0 consolidou os módulos e recursos dessa base, preservando
as melhorias próprias verificadas; detalhes em [ENTREGA-3.4.0](../docs/ENTREGA-3.4.0.md).
O vídeo citado não foi analisado e o link Claude retornou 403.

Inicialmente os ZIPs do Foxit e do UPDF e o arquivo `FoxitPDFReader.exe` não
foram transferidos: a ferramenta rejeitou arquivos maiores que 32 MiB. Os links
OneDrive fornecidos retornaram inicialmente bloqueio `403` do proxy de saída.
Após salvar domínios no rascunho, a API de compartilhamento retornou `401`
(`unauthenticated`), e os links com `download=1` retornaram `403`. Nenhum
arquivo foi obtido por essas rotas. Não se conclui que os links estejam inválidos.
O endereço do pacote UPDF completo em `download.updf.com` também foi bloqueado
pelo proxy. As regras salvas são um rascunho, não prova de aplicação em runtime.

`updf-9010200000-win-installer.exe` foi transferido (22.901.424 bytes).
Seu SHA-256, o inventário NSIS e os metadados do downloader estão nos arquivos
`updf-installer-summary.json`, `updf-installer-inventory.txt`,
`updf-downloader-pe.txt` e `updf-rea-artifact.json`. A extração com 7-Zip
produziu 83 arquivos. O REA 6.4.0 inspecionou o PE com `inspect-artifact`;
`objdump -p` e `strings` complementaram a inspeção do downloader interno.
Nenhum executável Windows foi executado, instalado ou modificado. A assinatura
Authenticode não foi validada; a presença de uma tabela de assinatura no PE
não é validação de assinatura ou autenticidade.

Ferramentas: Python/Cairo/GTK/Poppler do sistema; REA 6.4.0 oficial;
7-Zip 25.01 do Debian. O adaptador `python3-gi-cairo` e o 7-Zip foram baixados
com APT usando índices Debian com assinatura verificada, e extraídos em
`/workspace/.print-view-runtime`, sem alterar a instalação do sistema.


### Documento docs/ANALISE.md

#### Print&View PDF: análise da base e referências

**Entrega atual:** a 3.4.0 consolida Winux 3.3.11; consulte
[ENTREGA-3.4.0](../docs/ENTREGA-3.4.0.md). A análise da base 3.3.5 abaixo é histórica.

**Atualização:** os leitores completos agora estão acessíveis e foram analisados
estaticamente. Consulte [a análise atual de Foxit e UPDF](../docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md).
As limitações de acesso descritas abaixo registram a primeira etapa; não são
mais o estado atual dos ZIPs do Google Drive.

##### Resultado da primeira etapa

Foi recuperado o código real do Winux PDF **3.3.5** e criada sua continuação
Print&View PDF **3.3.6**. A engenharia reversa dos dois leitores Windows
**não está concluída**. Do UPDF foi possível examinar somente um instalador
online; o Foxit ainda não pôde ser transferido. Não se infere funcionamento
de um leitor a partir do funcionamento de seu instalador.

##### Arquitetura recuperada

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

##### Falhas reproduzidas e mudanças

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

##### UPDF: observações confirmadas

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

##### Comparação funcional pendente

| Fluxo desejado | Print&View atual | Foxit / UPDF |
|---|---|---|
| Leitura, zoom, rotação e ferramentas | Base recuperada e abertura/renderização exercitadas | Aplicativos completos ainda não disponíveis |
| Busca/seleção com realces precisos | Primeira correção validada com PDFs de teste | Comparação de interação/ordem de leitura pendente |
| Livreto frente/verso | Motor e seleção da prévia validados | Comportamento de passagem manual pendente |
| N-up e pôster | PDFs reais gerados e contagens verificadas | Regras/limites/margens de referência pendentes |
| Impressão física | Integração CUPS preservada; comando duplex testado por mock | Sem impressora nem sessão Windows |
| Camadas | Listadas, sem alterar visibilidade | Não comparado |
| Temas e múltiplos documentos | Não validados integralmente; uma única instância de documento no código | Não comparado |

##### Validação executada

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

##### Continuidade prioritária

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


### Documento docs/TESTAR-3.3.7.md

#### Print&View PDF 3.3.7~test1: versão de teste

Esta versão continua a base Winux 3.3.5 fornecida pelo autor. A 3.3.10 mencionada
no histórico não foi incorporada. Busca e impressão mantêm implementação própria
em Python/GTK/Poppler/pypdf/CUPS; não incluem o código dos leitores Windows.

##### Instalar

Baixe `packages/print-view-pdf_3.3.7~test1_all.deb` do repositório. No diretório
do download, execute:

```bash
sudo apt install './print-view-pdf_3.3.7~test1_all.deb'
print-view-pdf '/caminho/seu-documento.pdf'
```

O APT resolve as dependências declaradas. O pacote substitui `winux-pdf`;
não deve coexistir com ele. A associação padrão de PDF não é alterada
automaticamente. Para voltar, é necessário reinstalar seu pacote Winux original.

##### Busca: verificar com seus PDFs

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

##### Impressão

Teste primeiro **Salvar como PDF**, antes de usar papel:

- Livreto de 8 páginas, somente frente, somente verso e ambos os lados;
  confira que a prévia troca as páginas e que os PDFs preparados têm lados distintos.
- Encadernação esquerda/direita, N-up e pôster com sobreposição.
- Passagens manuais de frente/verso não devem usar duplex automático.

A prévia de livreto ainda exibe somente a primeira face selecionada. O motor
gera as faces restantes. A impressão física não foi validada neste ambiente.

##### Registrar um problema

Informe distribuição Linux, versão do pacote, termo pesquisado, opções
marcadas, página, zoom e rotação. Envie um PDF de exemplo que possa compartilhar
e uma captura do resultado esperado/obtido. O log fica em
`~/.cache/print-view-pdf/diagnostics.log`.


### Documento docs/TESTAR-TEST2.md

#### Print&View PDF 3.3.7~test2

Atualização da test1 para apresentação, temas e navegação. Mantém as melhorias
de busca e impressão; continua baseada no Winux 3.3.5 fornecido.

```bash
sudo apt install './print-view-pdf_3.3.7~test2_all.deb'
```

O pacote atualiza a test1 e substitui o antigo `winux-pdf` quando instalado.

##### O que mudou e como verificar

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


### Documento docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md

#### Engenharia reversa estática: Foxit e UPDF

##### Resultado e alcance

Agora foi possível acessar os **leitores completos** fornecidos na pasta do
Google Drive. Foram examinados os executáveis, imports/exports, recursos de
diálogos, strings com endereços e trechos de assembly relacionados a busca e
impressão. Esta análise supera a etapa anterior, limitada ao instalador UPDF.

É uma análise **parcial e estática**, não uma reconstrução integral dos produtos.
Nenhum programa Windows foi executado. Não foi recuperado código-fonte original,
e não foram medidos desempenho, latência, fidelidade visual ou impressão física.
O código da aplicação Print&View não foi alterado nesta rodada: foram adicionadas
evidências e uma ferramenta de análise reproduzível.

##### Artefatos observados

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

##### Foxit: impressão rastreada do controle ao código

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

###### Seletor de lados do livreto

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

##### UPDF: separação entre interface e biblioteca PDF

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

###### Rotinas de busca examinadas em assembly

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

###### Modelo de opções de impressão

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

##### Prioridades concretas para a continuação Linux

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

##### Evidências, reprodução e limitações

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


### Documento docs/REVISAO-HISTORICO-WINUX.md

#### Revisão do histórico Winux e da migração Print&View

**Nota posterior:** a consolidação e os pacotes 3.4.0 são descritos em
[ENTREGA-3.4.0](../docs/ENTREGA-3.4.0.md). Esta revisão registra o estado anterior.

##### Resultado e referência correta

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

##### Material e método

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
[manifest](../docs/historico-winux-manifest.json) registra as 18 versões, seus hashes e
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

##### Evolução reconstruída

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

##### Comparação para consolidação

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

###### Temas: recurso existente e defeito reproduzido

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

###### Busca, seleção e apresentação

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

###### Velocidade e tela preta

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

###### Impressão e pôster

Navegação por todas as faces e filtro de frente/verso já estão na 3.3.9.
Na 3.3.11, `booklet_print_pairs` serve à prévia e à geração. As verificações
conferiram faces e quantidade de páginas para ambos/frente/verso; não
substituem impressão física nem comparação geométrica completa.

Marcas correspondentes de encaixe aparecem na 3.3.7, condicionadas à
sobreposição e marcas habilitadas. Retirar a margem reservada na 3.2 foi uma
revisão deliberada; restaurar o desenho antigo altera a área útil. A montagem
física ainda precisa ser validada.

##### Segurança e empacotamento

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

##### Verificações desta revisão

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
[historico-winux-verificacao.json](../docs/historico-winux-verificacao.json).

Os 22 testes anteriores da test2 validam aquele pacote, não a migração integral
da 3.3.11. Não houve instalação pelo gerenciador de pacotes, impressão física
ou execução dos leitores no Windows nesta rodada.

##### Próxima versão

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


### Documento docs/ENTREGA-3.4.0.md

#### Print&View PDF 3.4.0: entrega e validação

A 3.4.0 consolida a base Winux 3.3.11 com a busca progressiva, geometria
CropBox/rotação e apresentação do Print&View. Os formatos são Debian `all`,
Flatpak `x86_64` e instalador Windows com runtime `x64`. Não há sufixo de teste.

##### Mudanças

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

##### Formatos e compilação

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

##### Verificações e limites

- **27 testes** no código final: passaram, sem ignorados, com GTK/Poppler reais.
- **27 testes no conteúdo extraído do `.deb`**: passaram, sem ignorados,
  usando `PRINT_VIEW_TEST_APP` apontando para a extração.
- **27 testes no runtime do Flatpak**: passaram, executados com seu Python/GTK incluído,
  fora do sandbox; não equivale a instalação e execução pelo `flatpak run`.
- Windows/Wine: abertura de PDF de quatro páginas, renderização, busca com
  quatro ocorrências e painel, geração de livreto; resultados em
  [windows-smoke-3.4.0.json](../docs/windows-smoke-3.4.0.json).
- Hooks/controle Debian, estrutura OSTree e inventário NSIS inspecionados.

A política de rede bloqueou o download do runtime Freedesktop do Flathub
neste ambiente. O bundle foi gerado, mas sua instalação/execução no sandbox
não foi validada. Impressão física, propriedades de todos os drivers, Windows
nativo e desempenho em PDFs pesados permanecem sem validação nesta entrega.

Os limites POSIX de CPU/memória usam `resource`/`prlimit` quando disponíveis
no Linux; o Windows usa timeout e cancelamento do processo Poppler, sem aplicar
esses mesmos limites POSIX. A impressão Windows rasteriza as páginas a 180 dpi
no diálogo nativo; não promete preservar vetores no spooler como a saída CUPS.

##### Origem e histórico

A revisão anterior descreve o estado **antes** da consolidação. Seus testes
sobre o Winux 3.3.11 original permanecem úteis: reproduzem o defeito original
do tema automático, enquanto a suíte atual verifica sua correção. Os pacotes
antigos `~test` são históricos. Consulte [PROVENIENCIA](../docs/PROVENIENCIA.md),
[REVISAO-HISTORICO-WINUX](../docs/REVISAO-HISTORICO-WINUX.md) e
[engenharia reversa](../docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md).


## Anexo F Registros estruturados completos

Estes registros são reproduções do checkout. Flags como native_windows_verified=false e sandbox_verified=false delimitam a validação, mesmo quando passed=true aparece em outro nível.


### Registro docs/validacao-3.4.0.json

````json
{
  "version": "3.4.0",
  "base_version": "Winux PDF 3.3.11",
  "validation": {
    "source_tests": {
      "run": 27,
      "passed": 27,
      "skipped": 0
    },
    "deb_extracted_tests": {
      "run": 27,
      "passed": 27,
      "skipped": 0
    },
    "windows_runtime_smoke": {
      "environment": "Wine 10.0 / Debian 13",
      "passed": true,
      "native_windows_verified": false,
      "physical_printing_verified": false
    },
    "flatpak_payload_tests": {
      "run": 27,
      "passed": 27,
      "skipped": 0,
      "sandbox_verified": false
    }
  },
  "source_module_sha256": {
    "appearance.py": "1f41078231d6a7ab85b817826978591724f1a0dcbe05556acfc23499d4f229ae",
    "async_core.py": "b38ee3f425c924bc9a681a46095f99d0903079caf7d5f125887c61060a990d0f",
    "cancel_state.py": "c56c1cca7cb33f8375bc716ab60751952067f9eb720f48bd3df4746f36d5c820",
    "cups_backend.py": "cf6732cb028c35c9fc09abd394ed20864d71420e741a6a016f860b8f9508f282",
    "imposition.py": "8a19f036dd11e5a6eef38d17f09777e61c9b6c4a3cd21c71b7da1b6b29a1ac37",
    "main.py": "5d49481f09f36a7e0b6c30d75a80a587822824135657c9bce57538118fefb949",
    "page_cache.py": "d339231d4d4dc06cc9c7c08190bdf72874294f7e0e2a609e1a772254c09ae856",
    "pdf_dependency.py": "b97a5431551b8a1fa5a3f49e27a7791e9753309975b9247baf8d70aac6cca8e5",
    "pdf_panels.py": "7390a26fc7015643450afbe562fbddf96a25a3d857a3faf7384ba4fd342878b2",
    "platform_runtime.py": "7c6d03d0f6032a4d0888be248e299ea43a009ae563ed89cd18fed85cdbbbfe74",
    "presentation.py": "9d0fec9c32ef15a43a56780c2332d6270e4c24527be57e8dd16b1e6d3ad525e5",
    "print_window.py": "99421e880dee024a58485a93a51f38332fb7f708a7e114d02deca9669bf83a6e",
    "rendering.py": "8d519f2129f2061b370b0b9d2eca6ee81f788b6a100c3e3f47c3552063cf08e4",
    "search_engine.py": "3a1d4912ffba06374066a17fafe8824fdd37466365586c76cf9e7fd43a459bb8",
    "themes.py": "c5263f1a61d5e72db45704a597f0214fb48c5e47d79b55492cc30575d2b7edc9",
    "version.py": "36f7896ab9f499430c7386716be5f1bbde6780af116c9a49497ec13c45026455",
    "windows_bootstrap.py": "537bf137e997dec1e61f19bb9adaa178ad1307118b793583b8c4cf3bc3e894f8",
    "windows_print.py": "3c2905d38de3ac9d601071ebd1650c39f264bc8ec50f85cc7e135cf483d26cd4",
    "worker_cli.py": "aa2f2fa1922e3b58c8131f1b852f246162a01990318053e8c5b03970f05e8fbb"
  },
  "artifacts": [
    {
      "file": "PrintViewPDF-3.4.0-Setup-x64.exe",
      "bytes": 67017156,
      "sha256": "2ee91c8828db0d246c5129bded8a47825fa681daf1b575f80bf4dd99989ab43e"
    },
    {
      "file": "PrintViewPDF-3.4.0-x86_64.flatpak",
      "bytes": 43197720,
      "sha256": "7f5926f32a5034677d6c26e947029e8359d511f29cdfbacc9afd27d1a38b7b08"
    },
    {
      "file": "print-view-pdf_3.4.0_all.deb",
      "bytes": 389952,
      "sha256": "229023b13486d51df93170a70623fedbb2dd2ff7fd188044e1bf7224c5c86273"
    },
    {
      "file": "print-view-pdf_3.4.0_source.tar.gz",
      "bytes": 684912,
      "sha256": "5d1858a527d741c303617e391c055d7d224011075cf358fb172c3a5932772fb2"
    }
  ]
}
````


### Registro docs/windows-smoke-3.4.0.json

````json
{
  "passed": true,
  "pages": 4,
  "hits": 4,
  "sidebar_rows": 4,
  "booklet_pages": 1,
  "pixbuf": [
    884,
    1253
  ],
  "python": "3.14.0 (tags/v3.14.0:ebf955d, Oct  7 2025, 10:15:03) [MSC v.1944 64 bit (AMD64)]",
  "platform": "win32",
  "environment": "Wine 10.0 on Debian 13, GTK native Win32 backend, synthetic PDF",
  "limitations": [
    "No native Windows machine tested",
    "No physical printing",
    "No installer execution under Wine32"
  ]
}
````


### Registro docs/historico-winux-verificacao.json

````json
{
  "target": "Winux PDF 3.3.11 original extracted source",
  "tests_run": 11,
  "passed": 10,
  "errors": 1,
  "failures": 0,
  "skipped": 0,
  "tests": [
    {
      "name": "test_booklet_output_all_sides",
      "status": "passed"
    },
    {
      "name": "test_booklet_preview_browses_all_faces",
      "status": "passed"
    },
    {
      "name": "test_cups_option_validation_without_printing",
      "status": "passed"
    },
    {
      "name": "test_jpeg_png_and_document_cache_identity",
      "status": "passed"
    },
    {
      "name": "test_presentation_initial_zoom_top_and_navigation",
      "status": "passed"
    },
    {
      "name": "test_reader_search_sidebar_and_navigation",
      "status": "passed"
    },
    {
      "name": "test_running_process_cancellation",
      "status": "passed"
    },
    {
      "name": "test_search_occurrences_case_and_whole_words",
      "status": "passed"
    },
    {
      "name": "test_search_query_bound",
      "status": "passed"
    },
    {
      "name": "test_system_theme_controller_initializes",
      "status": "error"
    },
    {
      "name": "test_theme_persistence_preserves_other_settings",
      "status": "passed"
    }
  ],
  "source_module_sha256": {
    "appearance.py": "0e5f54e5923b4395e1e6f59cda2336b92e5c8b573df34059c839cdb1d6c60d0a",
    "async_core.py": "d961b697db614b7ca3a3179c1de64e192c1f985fb8f09460e3bfadb060f2610f",
    "cancel_state.py": "c56c1cca7cb33f8375bc716ab60751952067f9eb720f48bd3df4746f36d5c820",
    "cups_backend.py": "f05bd23b7b9627fcd302c45128978ed7389c563d58ab594b118f7466f1af8fdd",
    "imposition.py": "eae81a2404496e79bfce41ad4638dea26c829e35b2d971a6fe049b3742c6dd73",
    "main.py": "4d3f1ad78bd3e987e6e5b15eef452a92b5981c9e72e3607121526cdd692aaf1c",
    "pdf_dependency.py": "e8879bfa0e2b4cf5722405d9608521151ba2063a09acf3400b421c019c58ee5d",
    "pdf_panels.py": "248548f3b2142ce416dcfcc340ae4e6ca52bd6d5a96c4d437cd6d5d6f3bbf20a",
    "presentation.py": "f20bbc25b06f37f86ba0ebbf73436d42115809d07cdd8b868249f26f28b27402",
    "print_window.py": "b468b9c7aa37a1ded99fe22815a8e4f0929c2ffcdac7632c860019a5158ad879",
    "rendering.py": "947f07265993eb5391390ccbe2e54581c4f89d26cd7dee96d2483d67225be257",
    "worker_cli.py": "2645f8743bd6306a8f3f2fe8b98eb7ab5f942e3c90c5ddef0793ca32b9a8bc42"
  },
  "conditions": [
    "GTK 3 and real Poppler",
    "Synthetic eight-page PDF",
    "Explicit light mode in reader tests; separate fresh system-mode subprocess",
    "Explicit presentation size for bare Xorg without a window manager",
    "CUPS command execution mocked; no printer jobs submitted"
  ],
  "limits": [
    "No physical printing",
    "No package manager installation",
    "No heavy-document benchmark",
    "No Windows readers executed"
  ]
}
````


### Registro docs/historico-winux-manifest.json

````json
[
  {
    "version": "2.3.0",
    "package_sha256": "1320acd4c8ec8fd44569353bdbd8b807e5e2223c03e06cb19eb541c643f064b2",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "c4af0118949183081b788624715e43c5727d6102c62218cb05a2ce9360404eea",
      "imposition.py": "9398feb257fea2c86cc381c7a6683bffb76a3ffbb171c75b7243237c46368aa0",
      "main.py": "6a0e2b0e475e3fd74f78e2c088db30a03c24baa8efd7e501ab8a375fb95a6163",
      "pdf_panels.py": "3ae1858441cabdf671a5211e33cce5d813b3a78e858853f976614b5873296c32",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "40b7971a214221546c4484a235dd6e2a545115666b8e24883a6f7e69a8add21d",
      "rendering.py": "6da1b10829afe1e10d78a32f9fac8ceccb4cc624c9f26229ef05ca8fae436dd7",
      "style.css": "05aef0a159ca23842d01716e1d58be7e02fac1e88f0ca2087b7844a762c58d01",
      "worker_cli.py": "e87ca415d61a088c024c4f97ec7b9ac6ad33b1c69c1b5d947b32cb34d05fcb5a"
    },
    "control_files_sha256": {
      "control": "689f736b273ffbc4dee201e65ee4979260c5e8264589e981ea7abce5dcd9f83b",
      "postinst": "91085881efd6d125bff968457e266f1f9521c073e15552ff696a867ab955276d",
      "postrm": "81b031962ef6e991af18da64af24756818b271395413d1950116c20aa8c20304"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "5.9.0",
    "changed_own_files_from_previous_supplied_version": [
      "async_core.py",
      "cups_backend.py",
      "imposition.py",
      "main.py",
      "pdf_panels.py",
      "presentation.py",
      "print_window.py",
      "rendering.py",
      "style.css",
      "worker_cli.py"
    ]
  },
  {
    "version": "3.0.0",
    "package_sha256": "fbdb4f0c2a3315180145160185dbc7fb33ca5b884d59902d568febe9836c836d",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "c4af0118949183081b788624715e43c5727d6102c62218cb05a2ce9360404eea",
      "imposition.py": "9398feb257fea2c86cc381c7a6683bffb76a3ffbb171c75b7243237c46368aa0",
      "main.py": "895f2588c6218c2771e2c494af8eb8e4bec185af3f5fe1538be7c683f63dad27",
      "pdf_panels.py": "3ae1858441cabdf671a5211e33cce5d813b3a78e858853f976614b5873296c32",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "40b7971a214221546c4484a235dd6e2a545115666b8e24883a6f7e69a8add21d",
      "rendering.py": "6da1b10829afe1e10d78a32f9fac8ceccb4cc624c9f26229ef05ca8fae436dd7",
      "style.css": "a2788afaa56ca549697033ba2e53d402be0f6b1f12d367af86c08b906b431d0e",
      "worker_cli.py": "e87ca415d61a088c024c4f97ec7b9ac6ad33b1c69c1b5d947b32cb34d05fcb5a"
    },
    "control_files_sha256": {
      "control": "19c91bcf88f0cae6b3a535e9ef29c0b1aa01e1891020b5f93ab5285795e3bcc5",
      "postinst": "91085881efd6d125bff968457e266f1f9521c073e15552ff696a867ab955276d",
      "postrm": "81b031962ef6e991af18da64af24756818b271395413d1950116c20aa8c20304"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "5.9.0",
    "changed_own_files_from_previous_supplied_version": [
      "main.py",
      "style.css"
    ]
  },
  {
    "version": "3.1.0",
    "package_sha256": "f46fd8dbbf0623dacdcec59fef8b4e4f65dfcba0dd622a7b978329bd388d359c",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "c4af0118949183081b788624715e43c5727d6102c62218cb05a2ce9360404eea",
      "imposition.py": "9398feb257fea2c86cc381c7a6683bffb76a3ffbb171c75b7243237c46368aa0",
      "main.py": "bad67b6dd2dfee4a19dcd1c7ae6427595cb697ae841c823040893b9193b9b4dd",
      "pdf_panels.py": "3ae1858441cabdf671a5211e33cce5d813b3a78e858853f976614b5873296c32",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "40b7971a214221546c4484a235dd6e2a545115666b8e24883a6f7e69a8add21d",
      "rendering.py": "6da1b10829afe1e10d78a32f9fac8ceccb4cc624c9f26229ef05ca8fae436dd7",
      "style.css": "23e3734f9bc45b10600d77df627fff45b997be1a6e7f80a2dfe7ef7262e3d4b4",
      "worker_cli.py": "e87ca415d61a088c024c4f97ec7b9ac6ad33b1c69c1b5d947b32cb34d05fcb5a"
    },
    "control_files_sha256": {
      "control": "ce63b083639ae7cb51b8a891c1eaaa3e26a6ae2cbe183a85b3ce5e125ae295c7",
      "postinst": "91085881efd6d125bff968457e266f1f9521c073e15552ff696a867ab955276d",
      "postrm": "81b031962ef6e991af18da64af24756818b271395413d1950116c20aa8c20304"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "5.9.0",
    "changed_own_files_from_previous_supplied_version": [
      "main.py",
      "style.css"
    ]
  },
  {
    "version": "3.1.1",
    "package_sha256": "1e0854a91c41611fca11b880f05e62e31011119d57cff95cc7b55f91c65fe59e",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "c4af0118949183081b788624715e43c5727d6102c62218cb05a2ce9360404eea",
      "imposition.py": "9398feb257fea2c86cc381c7a6683bffb76a3ffbb171c75b7243237c46368aa0",
      "main.py": "ddc2130da08070460130c6ccc2dac9c6892af400bdfb5d82cd12206780f6118e",
      "pdf_panels.py": "3ae1858441cabdf671a5211e33cce5d813b3a78e858853f976614b5873296c32",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "61f2d539b8b29c2b0d83b6633df7a959aff003ef7d0eb46b4f3e874cb59aa114",
      "rendering.py": "6da1b10829afe1e10d78a32f9fac8ceccb4cc624c9f26229ef05ca8fae436dd7",
      "style.css": "23e3734f9bc45b10600d77df627fff45b997be1a6e7f80a2dfe7ef7262e3d4b4",
      "worker_cli.py": "e87ca415d61a088c024c4f97ec7b9ac6ad33b1c69c1b5d947b32cb34d05fcb5a"
    },
    "control_files_sha256": {
      "control": "ad8f238e7f41294d6c96249c7529472a62d7fd09db387ee28c1d7cb94f483709",
      "postinst": "91085881efd6d125bff968457e266f1f9521c073e15552ff696a867ab955276d",
      "postrm": "81b031962ef6e991af18da64af24756818b271395413d1950116c20aa8c20304"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "5.9.0",
    "changed_own_files_from_previous_supplied_version": [
      "main.py",
      "print_window.py"
    ]
  },
  {
    "version": "3.1.3",
    "package_sha256": "ed20e15852a73c858a1b4be8a6458a6e68e6b58d41378579ba84bc726aec4eb9",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "c4af0118949183081b788624715e43c5727d6102c62218cb05a2ce9360404eea",
      "imposition.py": "58a4288f5ee132d0609b079af0f87a319674c3c4b8861084a04b299b74c92446",
      "main.py": "ddc2130da08070460130c6ccc2dac9c6892af400bdfb5d82cd12206780f6118e",
      "pdf_panels.py": "3ae1858441cabdf671a5211e33cce5d813b3a78e858853f976614b5873296c32",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "8565aa99a1105cbf0cdfb166b286a67e9a763a816a579a0c41d31f380b15b936",
      "rendering.py": "6da1b10829afe1e10d78a32f9fac8ceccb4cc624c9f26229ef05ca8fae436dd7",
      "style.css": "23e3734f9bc45b10600d77df627fff45b997be1a6e7f80a2dfe7ef7262e3d4b4",
      "worker_cli.py": "e87ca415d61a088c024c4f97ec7b9ac6ad33b1c69c1b5d947b32cb34d05fcb5a"
    },
    "control_files_sha256": {
      "control": "a7956fdeb22aecba37c631e4163ddb6f641013acd37163d377f5e96af2c81dc1",
      "postinst": "91085881efd6d125bff968457e266f1f9521c073e15552ff696a867ab955276d",
      "postrm": "81b031962ef6e991af18da64af24756818b271395413d1950116c20aa8c20304"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "5.9.0",
    "changed_own_files_from_previous_supplied_version": [
      "imposition.py",
      "print_window.py"
    ]
  },
  {
    "version": "3.2.0",
    "package_sha256": "0af5adf4b30aac1ef23360e02a59e1d8f24714c1afe12d4f069bc911561eb5d7",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "5f0abd4147a05bc7f52fc80a00e2fb0a4d8c10418f2dd4eb65dee4420d9a6bc8",
      "imposition.py": "3e6ce08069fde4d0eeb85903e0f367a6a67421e4971bac159e5a329db8ee6485",
      "main.py": "ddc2130da08070460130c6ccc2dac9c6892af400bdfb5d82cd12206780f6118e",
      "pdf_panels.py": "3ae1858441cabdf671a5211e33cce5d813b3a78e858853f976614b5873296c32",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "a87e4c8f7fb553f9e79469a9dbf9359df734ff017d37efb9b093ba6219ece1d4",
      "rendering.py": "6da1b10829afe1e10d78a32f9fac8ceccb4cc624c9f26229ef05ca8fae436dd7",
      "style.css": "23e3734f9bc45b10600d77df627fff45b997be1a6e7f80a2dfe7ef7262e3d4b4",
      "worker_cli.py": "e87ca415d61a088c024c4f97ec7b9ac6ad33b1c69c1b5d947b32cb34d05fcb5a"
    },
    "control_files_sha256": {
      "control": "847da8d69168d7593e937ed17bcc5495fd4a08e6d46e9760ced66b6bd80fe32b",
      "postinst": "91085881efd6d125bff968457e266f1f9521c073e15552ff696a867ab955276d",
      "postrm": "81b031962ef6e991af18da64af24756818b271395413d1950116c20aa8c20304"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "5.9.0",
    "changed_own_files_from_previous_supplied_version": [
      "cups_backend.py",
      "imposition.py",
      "print_window.py"
    ]
  },
  {
    "version": "3.3.0",
    "package_sha256": "1a5d72429cafdf4e836708fdf356f665e45bf16b2b9dd88394e9d4b4c9ea336e",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "f7be18ed77d0e87397a5868f8da9751aeb1db7646ea8b09772593b089010c8d4",
      "imposition.py": "d68ee863fcd339be734ec9e153078d29c9c6448b067687d12d6a67fa5bc0f28a",
      "main.py": "6631922eb7d9dac63c6afc8186bdfc2bf9fa3418fc6b302b19937839f33ab64b",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "5a36530a8e7952d2d52c1388f648f63e0af3b9dcc5ccc6246d245239e27689e7",
      "rendering.py": "9c95f070f2ca51662b03f4b90c0851608bb45493bc8cc2ff53f3db9b8bbd1de4",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "568ccb593604610553ae9e36d7a03a93adf7f4e5f1c4da054f607ba290522aa3",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "cups_backend.py",
      "imposition.py",
      "main.py",
      "pdf_panels.py",
      "print_window.py",
      "rendering.py",
      "style.css",
      "worker_cli.py"
    ]
  },
  {
    "version": "3.3.1",
    "package_sha256": "0f5f3882ec48669cf9227be138fe4d8f2da276b9a98e373da0bb1181a064f6c6",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "f7be18ed77d0e87397a5868f8da9751aeb1db7646ea8b09772593b089010c8d4",
      "imposition.py": "d68ee863fcd339be734ec9e153078d29c9c6448b067687d12d6a67fa5bc0f28a",
      "main.py": "6631922eb7d9dac63c6afc8186bdfc2bf9fa3418fc6b302b19937839f33ab64b",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "4a3cc3fde00dfd450b10915f5a4181345af40e652c0cef44946074c5c15a6233",
      "rendering.py": "9c95f070f2ca51662b03f4b90c0851608bb45493bc8cc2ff53f3db9b8bbd1de4",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "5c08771131f5949fdff2e365a1000c33cebece73a491c6203110305224c161f9",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "print_window.py"
    ]
  },
  {
    "version": "3.3.2",
    "package_sha256": "d7271c90412a64b36620b5718d31d61aa09baac8eee4b22c0714b1072a2a7654",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "f7be18ed77d0e87397a5868f8da9751aeb1db7646ea8b09772593b089010c8d4",
      "imposition.py": "d68ee863fcd339be734ec9e153078d29c9c6448b067687d12d6a67fa5bc0f28a",
      "main.py": "6631922eb7d9dac63c6afc8186bdfc2bf9fa3418fc6b302b19937839f33ab64b",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "c5f419a14e34e90e8f8d50b29ef379ecf3917f3700ef49ec7ddec51183dd897b",
      "rendering.py": "9c95f070f2ca51662b03f4b90c0851608bb45493bc8cc2ff53f3db9b8bbd1de4",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "16f51f5b67dbd34fbad6ec33d18486dadbb91addf40fbe606608369ec36d7767",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "print_window.py"
    ]
  },
  {
    "version": "3.3.3",
    "package_sha256": "b2cce021bc238fc12fcb51165a9635ad8723c9dbbdaad10b233386db3a586a77",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "d1aef9a0f3350d4c12baba55beef38a4e79cb66e197167bdc8b9dc5eb328ae5f",
      "imposition.py": "670a08bd479b2703ce972cad996d668058f56b5f68ce29e5780ab45466610f3b",
      "main.py": "74e7f177234aa66dc0e250e8108927d5b2facb230985b3a8d41b535fc3bcd6eb",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "3bc6d90726417395455ebfad7ee8f7708d32283669db337c1322087c8e5567bf",
      "rendering.py": "9c95f070f2ca51662b03f4b90c0851608bb45493bc8cc2ff53f3db9b8bbd1de4",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "2bcf698c9a4bf035b628f5f553568a4576cc557eef64919bd506945ff9437724",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "cups_backend.py",
      "imposition.py",
      "main.py",
      "print_window.py"
    ]
  },
  {
    "version": "3.3.4",
    "package_sha256": "8fafdb0b2a82bf6602c04cfd77c2d8a16ef6aed652f23ccf873290146a202107",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "d1aef9a0f3350d4c12baba55beef38a4e79cb66e197167bdc8b9dc5eb328ae5f",
      "imposition.py": "e556a3915827a068ddea7e6fc2059f6c04bf4eb5f8ee4e4cbdd27f0d6aeb4565",
      "main.py": "5e47d2953088ffc9888af4d5ebe48bf86c6273cf730b76f101ffd51ba135179a",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "4b20f895ad683af5ddba3d1b26dc5410a8d75bb7f1c6d59a32588f3689f48a87",
      "print_window.py": "aae60a5c51fe93cff5547c63761e045419e765930a1dc36f69be0902270994a3",
      "rendering.py": "9c95f070f2ca51662b03f4b90c0851608bb45493bc8cc2ff53f3db9b8bbd1de4",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "e4206b4775697a0960bb86e5b300821724fadf9ee10b5c1b410fdbcb620e1aa5",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "imposition.py",
      "main.py",
      "print_window.py"
    ]
  },
  {
    "version": "3.3.5",
    "package_sha256": "c4f816f508f0e46dde8ecfc37b8a18c6409223540451694fb3bc51bd3b5e86ca",
    "files_sha256": {
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "d1aef9a0f3350d4c12baba55beef38a4e79cb66e197167bdc8b9dc5eb328ae5f",
      "imposition.py": "dfb89b1f4a35908ec5b2c0756e42c457384595fb65e8cc988f15f7eefe5ef549",
      "main.py": "5e47d2953088ffc9888af4d5ebe48bf86c6273cf730b76f101ffd51ba135179a",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "ac11ea52fbd7364ad9f6ba0f5d490212174c7081b320460843d0abfda3743b6c",
      "print_window.py": "a9ed7cc7a705c743eab7f5613f84dfe2bd6b5f1f245262874d16a8c2b308fb72",
      "rendering.py": "9c95f070f2ca51662b03f4b90c0851608bb45493bc8cc2ff53f3db9b8bbd1de4",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "c04a478bc0c513a952401472275c75eed5b9b36510429f6413666553390f785b",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Keep Winux PDF readable and visually consistent even on dark Linux themes.\nexport GTK_THEME=\"${WINUX_PDF_GTK_THEME:-Adwaita:light}\"\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "imposition.py",
      "presentation.py",
      "print_window.py"
    ]
  },
  {
    "version": "3.3.6",
    "package_sha256": "ffce05b0c6dac2cddbcfc1c6a7bd7317d8fe48c7f8670022551eb68dccc92b58",
    "files_sha256": {
      "appearance.py": "483252847579c5fc0861433a956a9d9909cd69b2e309e3e1dfc115eed1e3f68f",
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "d1aef9a0f3350d4c12baba55beef38a4e79cb66e197167bdc8b9dc5eb328ae5f",
      "imposition.py": "dfb89b1f4a35908ec5b2c0756e42c457384595fb65e8cc988f15f7eefe5ef549",
      "main.py": "efcae10b58dff417461e0f6b8d5dd02497817c9a4770f9fbc05ac68741d8893c",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "ac11ea52fbd7364ad9f6ba0f5d490212174c7081b320460843d0abfda3743b6c",
      "print_window.py": "a9ed7cc7a705c743eab7f5613f84dfe2bd6b5f1f245262874d16a8c2b308fb72",
      "rendering.py": "9c95f070f2ca51662b03f4b90c0851608bb45493bc8cc2ff53f3db9b8bbd1de4",
      "style-dark.css": "953be596e18feb2adb245b981770489f3a08852285b93df59aeb686a461c50fe",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "6bb19748e603afa1d80d6e15c427c7505b79f987000e97c77e9adf092941512d",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Honor the desktop's GTK theme and the user's Winux PDF appearance setting.\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "appearance.py",
      "main.py",
      "style-dark.css"
    ]
  },
  {
    "version": "3.3.7",
    "package_sha256": "a0e3baab2bb106a67da39de2426b864eb2636c10e086c93391972f3eaf59e9b9",
    "files_sha256": {
      "appearance.py": "483252847579c5fc0861433a956a9d9909cd69b2e309e3e1dfc115eed1e3f68f",
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "d1aef9a0f3350d4c12baba55beef38a4e79cb66e197167bdc8b9dc5eb328ae5f",
      "imposition.py": "a580d12fc0af0fd35b7dc164238185cdd7c9d8c7d3b41f4c5561bf6378f05f8f",
      "main.py": "51f52c44c04bb443b9f9625b702c6e6dca02c39048019999c65b7153941bb9b3",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "ac11ea52fbd7364ad9f6ba0f5d490212174c7081b320460843d0abfda3743b6c",
      "print_window.py": "bfd090d876d543be28850905679d60e184487f04a4ee7db0e646b1bd5a89d199",
      "rendering.py": "2b9a5bdbb23905e751ea40f23d5b87367d8f080dda997a65009f9b841d607b70",
      "style-dark.css": "953be596e18feb2adb245b981770489f3a08852285b93df59aeb686a461c50fe",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "ad0c19d39aed764d556f6285dbf19bb53b2b7961b45058e3c8e0bcde4ec210ce",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Honor the desktop's GTK theme and the user's Winux PDF appearance setting.\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "imposition.py",
      "main.py",
      "print_window.py",
      "rendering.py"
    ]
  },
  {
    "version": "3.3.8",
    "package_sha256": "c495dd35d40fca60d409f3ea359bd1272f9b587c68d3362dd0a15f86433cb8df",
    "files_sha256": {
      "appearance.py": "483252847579c5fc0861433a956a9d9909cd69b2e309e3e1dfc115eed1e3f68f",
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "d1aef9a0f3350d4c12baba55beef38a4e79cb66e197167bdc8b9dc5eb328ae5f",
      "imposition.py": "a580d12fc0af0fd35b7dc164238185cdd7c9d8c7d3b41f4c5561bf6378f05f8f",
      "main.py": "51f52c44c04bb443b9f9625b702c6e6dca02c39048019999c65b7153941bb9b3",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "702d9c248a49170ffe66c42328173764c4e0d94dec63501250964a0d3f89e814",
      "print_window.py": "bfd090d876d543be28850905679d60e184487f04a4ee7db0e646b1bd5a89d199",
      "rendering.py": "2b9a5bdbb23905e751ea40f23d5b87367d8f080dda997a65009f9b841d607b70",
      "style-dark.css": "953be596e18feb2adb245b981770489f3a08852285b93df59aeb686a461c50fe",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "f6c9c395baea824f85dafb767b2a79dc7488184d6ae3b03633c71baa985faa3e",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Honor the desktop's GTK theme and the user's Winux PDF appearance setting.\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "presentation.py"
    ]
  },
  {
    "version": "3.3.9",
    "package_sha256": "ff19a3644a7a987db2371cc5b99de1c1e9b4b08ccb9e0a195ca67af791b6264f",
    "files_sha256": {
      "appearance.py": "483252847579c5fc0861433a956a9d9909cd69b2e309e3e1dfc115eed1e3f68f",
      "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
      "cups_backend.py": "41773e285e2cfe8e0659921efe2189bc0388de6df1605b38b17887db71427263",
      "imposition.py": "a11fc50c64fa3c616f6b317910ad9753e743cb10e1fd623e6154995a03a39bf5",
      "main.py": "51f52c44c04bb443b9f9625b702c6e6dca02c39048019999c65b7153941bb9b3",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "702d9c248a49170ffe66c42328173764c4e0d94dec63501250964a0d3f89e814",
      "print_window.py": "b468b9c7aa37a1ded99fe22815a8e4f0929c2ffcdac7632c860019a5158ad879",
      "rendering.py": "2b9a5bdbb23905e751ea40f23d5b87367d8f080dda997a65009f9b841d607b70",
      "style-dark.css": "953be596e18feb2adb245b981770489f3a08852285b93df59aeb686a461c50fe",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "26f48086571c51ec9662b91d40103a8a0da6af079865b8fd375db0aa05900e72",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Honor the desktop's GTK theme and the user's Winux PDF appearance setting.\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "cups_backend.py",
      "imposition.py",
      "print_window.py"
    ]
  },
  {
    "version": "3.3.10",
    "package_sha256": "9045e5d1788e8644be234745d79aa5514e776cf2c81224a7c96ae65df823f907",
    "files_sha256": {
      "appearance.py": "483252847579c5fc0861433a956a9d9909cd69b2e309e3e1dfc115eed1e3f68f",
      "async_core.py": "7c191882aeb6c403621ba0b559576e851b404b04e8da16d8e919f4bcbaf016e0",
      "cups_backend.py": "41773e285e2cfe8e0659921efe2189bc0388de6df1605b38b17887db71427263",
      "imposition.py": "a11fc50c64fa3c616f6b317910ad9753e743cb10e1fd623e6154995a03a39bf5",
      "main.py": "6ea4e370399bc18f878fc994ac0cba67c35f21748c032acaf5d8c46c0519db38",
      "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
      "presentation.py": "f20bbc25b06f37f86ba0ebbf73436d42115809d07cdd8b868249f26f28b27402",
      "print_window.py": "b468b9c7aa37a1ded99fe22815a8e4f0929c2ffcdac7632c860019a5158ad879",
      "rendering.py": "a3b900c468acb266991b8d1eafca6d5d327321ef06d4cf89e4c449e5f1a74e1c",
      "style-dark.css": "953be596e18feb2adb245b981770489f3a08852285b93df59aeb686a461c50fe",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
    },
    "control_files_sha256": {
      "control": "1102e4b610b7871cac90a7bd29a5db210fe14e84ea0bab91fba29f330a03c408",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Honor the desktop's GTK theme and the user's Winux PDF appearance setting.\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "async_core.py",
      "main.py",
      "presentation.py",
      "rendering.py"
    ]
  },
  {
    "version": "3.3.11",
    "package_sha256": "0f8b75a443ed7bb70a6dc88af69561b982025863c8e2d3669b0b617092772342",
    "files_sha256": {
      "appearance.py": "0e5f54e5923b4395e1e6f59cda2336b92e5c8b573df34059c839cdb1d6c60d0a",
      "async_core.py": "d961b697db614b7ca3a3179c1de64e192c1f985fb8f09460e3bfadb060f2610f",
      "cancel_state.py": "c56c1cca7cb33f8375bc716ab60751952067f9eb720f48bd3df4746f36d5c820",
      "cups_backend.py": "f05bd23b7b9627fcd302c45128978ed7389c563d58ab594b118f7466f1af8fdd",
      "imposition.py": "eae81a2404496e79bfce41ad4638dea26c829e35b2d971a6fe049b3742c6dd73",
      "main.py": "4d3f1ad78bd3e987e6e5b15eef452a92b5981c9e72e3607121526cdd692aaf1c",
      "pdf_dependency.py": "e8879bfa0e2b4cf5722405d9608521151ba2063a09acf3400b421c019c58ee5d",
      "pdf_panels.py": "248548f3b2142ce416dcfcc340ae4e6ca52bd6d5a96c4d437cd6d5d6f3bbf20a",
      "presentation.py": "f20bbc25b06f37f86ba0ebbf73436d42115809d07cdd8b868249f26f28b27402",
      "print_window.py": "b468b9c7aa37a1ded99fe22815a8e4f0929c2ffcdac7632c860019a5158ad879",
      "rendering.py": "947f07265993eb5391390ccbe2e54581c4f89d26cd7dee96d2483d67225be257",
      "style-dark.css": "953be596e18feb2adb245b981770489f3a08852285b93df59aeb686a461c50fe",
      "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
      "worker_cli.py": "2645f8743bd6306a8f3f2fe8b98eb7ab5f942e3c90c5ddef0793ca32b9a8bc42"
    },
    "control_files_sha256": {
      "control": "21a20456ed900f0ebdc02e75192d14f005a2f1e4d44239f3352313f67bd13fd3",
      "postinst": "ce894da2d4f05021456ec883824cce0cab9be54570c3d5d5b509b161400e772d",
      "postrm": "a4e351975f8b7b10ef507b6b5075970c676493b0680aa58631947956e047e346"
    },
    "launcher": "#!/bin/sh\n# Honor the desktop's GTK theme and the user's Winux PDF appearance setting.\nexport PYTHONUNBUFFERED=1\nexec python3 /usr/share/winux-pdf/main.py \"$@\"\n",
    "pypdf_version": "6.10.0",
    "changed_own_files_from_previous_supplied_version": [
      "appearance.py",
      "async_core.py",
      "cancel_state.py",
      "cups_backend.py",
      "imposition.py",
      "main.py",
      "pdf_dependency.py",
      "pdf_panels.py",
      "rendering.py",
      "worker_cli.py"
    ]
  }
]
````


### Registro docs/winux-3.3.5-source-sha256.json

````json
{
  "async_core.py": "a83f8178fdec88bbc26e637f8fc7948fb7e5ebbd4a0d0c818e2a2a90155d0997",
  "cups_backend.py": "d1aef9a0f3350d4c12baba55beef38a4e79cb66e197167bdc8b9dc5eb328ae5f",
  "imposition.py": "dfb89b1f4a35908ec5b2c0756e42c457384595fb65e8cc988f15f7eefe5ef549",
  "main.py": "5e47d2953088ffc9888af4d5ebe48bf86c6273cf730b76f101ffd51ba135179a",
  "pdf_panels.py": "36fc8eaf952df91c10487515732ab6018a4a7323b122a32405b15ca5a0ecb6a1",
  "presentation.py": "ac11ea52fbd7364ad9f6ba0f5d490212174c7081b320460843d0abfda3743b6c",
  "print_window.py": "a9ed7cc7a705c743eab7f5613f84dfe2bd6b5f1f245262874d16a8c2b308fb72",
  "rendering.py": "9c95f070f2ca51662b03f4b90c0851608bb45493bc8cc2ff53f3db9b8bbd1de4",
  "style.css": "6b8c2e35197b3228e6129352798a6933fbf07e4bb5ea527bcd929251c380829b",
  "vendor/pypdf/__init__.py": "612ff566b4378c13c7b1180cb2da89ac0b6cde5500a63fe530e30ae6a88b1b9c",
  "vendor/pypdf/_cmap.py": "0b8eea205808d522a7e4bad3e222b39c6964752b58a3a3b7259904292ee09241",
  "vendor/pypdf/_codecs/__init__.py": "035d44440b70b56ae91953b34d296b0b56b74fd1c29562c1591c067b7fcf7eed",
  "vendor/pypdf/_codecs/_codecs.py": "e3aa11649c92c06c42269d648c87abee3b3f4d84a38f81acda2d9471edeff9e1",
  "vendor/pypdf/_codecs/adobe_glyphs.py": "b7770314f0eac08cf5c3d07481d5738dd73c7842bd02e4639397fb95a130fdf6",
  "vendor/pypdf/_codecs/core_font_metrics.py": "14b3d66d3678871790597820d63a397b8a972821642846397bce54d9b2c533a9",
  "vendor/pypdf/_codecs/pdfdoc.py": "c5f4af30562cbf1b9a490d14bbdbd90ca681d16bbce61d6e0a20758bdac07145",
  "vendor/pypdf/_codecs/std.py": "0f240cb84a40184a52f6ecb58d67f87278fe92a4a13ce0228f9b08ed0d580fc1",
  "vendor/pypdf/_codecs/symbol.py": "9c86864089615822623cc1ebc149661871fefdf397c842af82e466b8a5dc1809",
  "vendor/pypdf/_codecs/zapfding.py": "3d0c63c510bad7a778d711777b15713f55bc9cce10ad97e33b7966b4bc6913fb",
  "vendor/pypdf/_crypt_providers/__init__.py": "2b767a02e5e15d579780b7adf93ba4ab682df47eba3a076ea6cbf1212d429a42",
  "vendor/pypdf/_crypt_providers/_base.py": "fdfe77323eaf8af84464c438bcdc4de46d083a0158fa7e7f95e91ed1cfea88d5",
  "vendor/pypdf/_crypt_providers/_cryptography.py": "f733a4933312b17e1a974454934a8cd1d29f7dc1e47b8c1f9845caf64c28450f",
  "vendor/pypdf/_crypt_providers/_fallback.py": "bec628a30475602015feaf87add21986451cac26fa1ef44134c626d3742d094f",
  "vendor/pypdf/_crypt_providers/_pycryptodome.py": "bb8bed2e8ecdbfa02a6513671f5a0d3425af4d86a8c1f4957febe5916def4fab",
  "vendor/pypdf/_doc_common.py": "54a5f4cd06ba5f658a9ed175b9c6224134b3dcf9f98ab11fc4da1f36e02a262e",
  "vendor/pypdf/_encryption.py": "319f3e012455b473ceb9c51df87f4a45f94eab902f88f14f8e5769901540a1ce",
  "vendor/pypdf/_font.py": "50ad53071d7979e53daa4661bf38a0e1823eb6365382007eca20b414b73767bb",
  "vendor/pypdf/_page.py": "f93c459a77c433dbd2541e94d1fdfa599e486ca5fe3e3efe9348eaf94552639c",
  "vendor/pypdf/_page_labels.py": "bfa0a9bba3495c2f5143f05e19d866d39695f19eb3c623d1367eaa129d41b951",
  "vendor/pypdf/_protocols.py": "eeacfdd8b55d3eb6244a97543e9029f54e065b98f13414df55ca545b052110ea",
  "vendor/pypdf/_reader.py": "9aaa6780e62c061509f0d3b658dbdac185404fecadac01f7f9d35ac009ce2024",
  "vendor/pypdf/_text_extraction/__init__.py": "6b7677deb4154e230a1adc2deff6df5e53e8b1b493f2bcc42e8367b74e77fd0c",
  "vendor/pypdf/_text_extraction/_layout_mode/__init__.py": "454408c22530ce778db5c9639d533a8e445a7a6ea980fee6383dbe3019ada6fc",
  "vendor/pypdf/_text_extraction/_layout_mode/_fixed_width_page.py": "789bde0dbc8ca281bdef4a893a13394706fd668cb2243ca7cd6a55f5aec84b6d",
  "vendor/pypdf/_text_extraction/_layout_mode/_text_state_manager.py": "5d5ac88de4dde6349d31ec41431b34b4be48e5150e8ad4663759842ce70a626e",
  "vendor/pypdf/_text_extraction/_layout_mode/_text_state_params.py": "872c3aa670bcba9064a055542772c7f21048207acdc22a9aa9c632cc8232afa6",
  "vendor/pypdf/_text_extraction/_text_extractor.py": "b54a9bbc2ebd305706406501b7f63caeab1535ffbcb0c171003c8a9da8b4a232",
  "vendor/pypdf/_utils.py": "2df8188c0ad153b97d19201bb681b3bbdbd507e7243e2d657b4eb543a7072656",
  "vendor/pypdf/_version.py": "2416f2ebd53fb332339ad719e9569c95eedc0157bb9e1573ee0205d0d07716aa",
  "vendor/pypdf/_writer.py": "1819e02d0b0bcd9c1fa483dc5c22e2a7849be22c93474c33c235dd6dd076a4e3",
  "vendor/pypdf/annotations/__init__.py": "7f693ffa3027dfd082076ecac50fdef771a29e7ce40076d49e749e1899758f21",
  "vendor/pypdf/annotations/_base.py": "79ea1cf6fdb0d798c05212978f8f25d5b07ae98801815fb6bf92085091febf0b",
  "vendor/pypdf/annotations/_markup_annotations.py": "b162a1181086ed7f688c0bc4691304a093fe7d8e8572b94574e9ad79f219066d",
  "vendor/pypdf/annotations/_non_markup_annotations.py": "676214bdc08e713729261497adec7ff6b8983360fae17c4543fbda735d013515",
  "vendor/pypdf/constants.py": "9f672ef873a6a16e7feb14165442a8e36ad2249d0ff7484bd6cf33fa9174a1cb",
  "vendor/pypdf/errors.py": "070d56f61c4eb03830ab053a628436974f89894c93aba979423542afe5b81850",
  "vendor/pypdf/filters.py": "237c2d528bdaeccdd68233730b2a74ac634854a9899a34bcebc8d8af5c0b347f",
  "vendor/pypdf/generic/__init__.py": "56ba9d61fb5010278f0d4dab5d532012a45a60547ccce57f7ef260a35f71feec",
  "vendor/pypdf/generic/_appearance_stream.py": "31c0cbd2070a34df4d5cd53a64fc60b7b398a25dbe168356615980c20030e0f3",
  "vendor/pypdf/generic/_base.py": "f488de45b70b1eb73f94b1947d564c8ee83ca3eb7af17ece35295f9c32a73e64",
  "vendor/pypdf/generic/_data_structures.py": "35f76eb49aa9f253fb1cd3e5eb9e3875b80f9bbc2616c755e376bde054e7b782",
  "vendor/pypdf/generic/_files.py": "36d4a4468e890608ac8b840ecab56778ef3dd5ba15b2e636e614708a3e97f510",
  "vendor/pypdf/generic/_fit.py": "5ff8800c98f5618e0f512b52eeb1560b6c51d8b5154af2ad500932d001402033",
  "vendor/pypdf/generic/_image_inline.py": "2a5000fd91a2446ce368f1b74af6eda8619e36a6d065517e515536302f2efd28",
  "vendor/pypdf/generic/_image_xobject.py": "7f560334bae2f927a5faaa72ca75c0ee7c7e662493a8061433ce9338414883af",
  "vendor/pypdf/generic/_link.py": "b4da99d86616c6a80566c948d032d97a85e59ed6b182c1c2f1791615f496c781",
  "vendor/pypdf/generic/_outline.py": "a8a6cc5f8d8e59faa7a2922213a054cba12f7532c67b766d8da89637ce49a5a6",
  "vendor/pypdf/generic/_rectangle.py": "94ea927c58af43180137d2d4f5aa87a313c7f1a08f4c350d81166c34451de9f7",
  "vendor/pypdf/generic/_utils.py": "bd30c07ac7c6f9c24d0ca8a5cff91b805a1d0084f37797a3a695871a3bc2a279",
  "vendor/pypdf/generic/_viewerpref.py": "b6a5445a6bddfc359316848ca51393b25d528a338d9ef71267e8d74e8fdc8cea",
  "vendor/pypdf/pagerange.py": "d9bb76d634199bef5aab66d57f74d7b87f3fc06571edbf53e94acc1570842614",
  "vendor/pypdf/papersizes.py": "e93cf9b1f34dff724e51aa58f3753e95a928867a57600d2148440d98e54b14bf",
  "vendor/pypdf/py.typed": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "vendor/pypdf/types.py": "b09ef01f393b111fc227b90ffacf2ef5ac459e40979c5a6bf27cdc8f50314dab",
  "vendor/pypdf/xmp.py": "00289e95b3fb680b03cb67e67b8a3d61de32ec7e0a7c46d4337494c4c97c8c8e",
  "worker_cli.py": "a06ecd6acb40673eacc5b7735e623eff511e954220b0532e645fabdaea5beb6f"
}
````


### Registro docs/pypdf-artifact.json

````json
{
  "version": "6.20.1",
  "filename": "pypdf-6.20.1-py3-none-any.whl",
  "sha256": "aa5a55ddcffdc5e5ab291d5decb23f6383f4e56f8e3263dc39af41fff03885ad",
  "url": "https://files.pythonhosted.org/packages/71/f8/4cbd09988b4b158260b7e0df38bf16f19e998bf0e257a18661a8da04280e/pypdf-6.20.1-py3-none-any.whl"
}
````


### Registro docs/updf-installer-summary.json

````json
{
  "installer_sha256": "b6286a07065b0a95c7f7f1543951b444f1d1256bb888af825b49351e75197a00",
  "installer_size": 22901424,
  "downloader_sha256": "dc274d1a2af72664f83642cbb831c61194f76136358d3d1ab035dc20a534b494",
  "downloader_size": 1258032,
  "extracted_file_count": 83,
  "full_package_url_strings": [
    "https://download.updf.cn/updf/basic/win/updf-8000000000-win-full.exe",
    "https://download.superace.com/updf/basic/win/updf-8000000000-win-full.exe",
    "https://download.updf.com/updf/basic/win/updf-9000000000-win-full.exe",
    "https://download.superace.com/updf/basic/win/updf-9000000000-win-full.exe"
  ],
  "static_only": true,
  "signature_verified": false,
  "reader_payload_present": false
}
````


### Registro packaging/windows-artifacts.json

````json
[
  {
    "file": "GTK3_Gvsbuild_2026.8.0_x64.zip",
    "url": "https://github.com/wingtk/gvsbuild/releases/download/2026.8.0/GTK3_Gvsbuild_2026.8.0_x64.zip",
    "sha256": "9be43d9029749062d2637070c856e73f8a1327a72259d08326b38155c139ecdc"
  },
  {
    "file": "Release-26.09.0-0.zip",
    "url": "https://github.com/oschwartz10612/poppler-windows/releases/download/v26.09.0-0/Release-26.09.0-0.zip",
    "sha256": "7a6f256a0ddf7536182246a5733331bf4677cbcc34f4663774947ad34556c8d0"
  },
  {
    "file": "python.3.14.0.nupkg",
    "url": "https://api.nuget.org/v3-flatcontainer/python/3.14.0/python.3.14.0.nupkg",
    "sha256": "620fb3527428fb354f093b0b8b634dfb8e3023115df68608fba7e91db69b4f4d"
  },
  {
    "file": "cffi-2.1.1-cp314-cp314-win_amd64.whl",
    "url": "https://files.pythonhosted.org/packages/a7/06/1c3e01e3ba14c39f6d10bfbac52753b7e22259e38088e5cfe1d704918690/cffi-2.1.1-cp314-cp314-win_amd64.whl",
    "sha256": "3222ba5d678f80a030e6afbcc33dc1ae5cb45facabb61cee2c7016b8432fde48"
  },
  {
    "file": "cryptography-50.0.2-cp311-abi3-win_amd64.whl",
    "url": "https://files.pythonhosted.org/packages/9a/4f/adfc442765721292fff86d314ce385d3249d22db42295c0dd057727b60f3/cryptography-50.0.2-cp311-abi3-win_amd64.whl",
    "sha256": "7afa5a6602a9f29af1f3a2965f831bae7c9d5d597b7cbb716d41ab3b7d89879c"
  },
  {
    "file": "pillow-12.3.0-cp314-cp314-win_amd64.whl",
    "url": "https://files.pythonhosted.org/packages/f1/e0/492879f69d94f91f60fc8cd05ba03650e9520afebb2fb7aa12777d7c7f38/pillow-12.3.0-cp314-cp314-win_amd64.whl",
    "sha256": "fdafc9cce40277e0f7a0feabce0ee50dd2fa1800f3b38015e51296b5e814048d"
  },
  {
    "file": "pycparser-3.11-py3-none-any.whl",
    "url": "https://files.pythonhosted.org/packages/90/11/0e6f11117525ff0eec40ebac3d313376f102df93ca44ad9e893ee85e4f89/pycparser-3.11-py3-none-any.whl",
    "sha256": "51d5a8ba2be0bbe440b99d2112604c95bbbc3c2748a64260186c541e1729cd80"
  }
]
````


## Anexo G Código completo dos testes existentes

Incluído para permitir verificar entradas, mocks, condições de skip, tempos e asserções, sem depender apenas da descrição do catálogo. Esta transcrição não é execução de teste.


### Fonte tests/test_consolidation.py

````python
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from test_regressions import APP
sys.path.insert(0, str(APP))
import rendering
from cancel_state import set_event


class ConsolidationTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get('DISPLAY'), 'Requires an X display')
    def test_fresh_system_theme_initializes_and_migrates_legacy(self):
        with tempfile.TemporaryDirectory() as temp:
            env = {**os.environ, 'XDG_CONFIG_HOME': temp}
            code = (f'import sys; sys.path.insert(0,{str(APP)!r}); '
                    'from appearance import AppearanceController; '
                    f'c=AppearanceController({str(APP)!r}); assert c.mode=="system"; c.close()')
            subprocess.run([sys.executable, '-c', code], env=env, check=True, timeout=5)
            legacy = Path(temp) / 'winux-pdf/settings.json'
            legacy.parent.mkdir(); legacy.write_text('{"appearance":"dark"}')
            code = (f'import sys; sys.path.insert(0,{str(APP)!r}); '
                    'from themes import read_theme; assert read_theme()=="dark"')
            subprocess.run([sys.executable, '-c', code], env=env, check=True, timeout=5)
            self.assertTrue((Path(temp) / 'print-view-pdf/preferences.json').is_file())

    def test_active_process_cancellation(self):
        event = threading.Event()
        trigger = threading.Timer(.2, event.set)
        set_event(event); trigger.start(); started = time.monotonic()
        try:
            with self.assertRaisesRegex(RuntimeError, 'cancelada'):
                rendering._run([sys.executable, '-c', 'import time; time.sleep(10)'], timeout=15)
            self.assertLess(time.monotonic() - started, 2)
        finally:
            set_event(None); trigger.join()
````


### Fonte tests/test_gui.py

````python
import os
from pathlib import Path
import sys
import time
import unittest
from unittest.mock import patch

import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
from test_regressions import APP, make_pdf
sys.path.insert(0, str(APP))
from main import PDFWindow, load_css
from print_window import PrintWindow


def wait_for(predicate, timeout=12):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        context = GLib.MainContext.default()
        while context.pending():
            context.iteration(False)
        if predicate():
            return
        time.sleep(.02)
    raise AssertionError('GTK readiness timeout')


@unittest.skipUnless(os.environ.get('DISPLAY'), 'Requires an X display')
class GUIRegressionTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'reader.pdf'
        make_pdf(self.pdf, ['ação ação'] + [f'PAGE{i}' for i in range(2, 9)])
        load_css()
        self.quit_patch = patch.object(Gtk, 'main_quit')
        self.quit_patch.start()
        self.errors = []
        self.window = PDFWindow()
        self.window._error = lambda msg: self.errors.append(msg)
        self.window.open_document(str(self.pdf))
        wait_for(lambda: self.window.page_count == 8 and self.window.current_pixbuf is not None)
        self.assertEqual(self.errors, [])

    def tearDown(self):
        self.window.destroy()
        self.quit_patch.stop()
        self.temp.cleanup()

    def test_search_navigation_selection_and_rotation(self):
        w = self.window
        w.find_entry.set_text('ação')
        wait_for(lambda: len(w.search_hits) == 2 and not w.search_running)
        self.assertEqual(w.find_status.get_text(), '1 de 2')
        w._find_next(); self.assertEqual(w.search_pos, 1)
        w._find_prev(); self.assertEqual(w.search_pos, 0)
        hit = w.search_hits[0]
        for rotation in (0, 90, 180, 270):
            w.rotation = rotation
            displayed = w._pdf_rect_to_display(hit['rects'][0], hit)
            restored = w._display_rect_to_pdf(displayed, hit)
            for a, b in zip(restored, hit['rects'][0]):
                self.assertAlmostEqual(a, b)
        w.rotation = 0
        rect = w._pdf_rect_to_display(hit['rects'][0], hit)
        w._finish_text_selection(rect)
        wait_for(lambda: bool(w.selected_words))
        self.assertEqual(w.selected_words[0]['text'], 'ação')
        w.find_entry.set_text('')
        self.assertEqual(w.search_hits, [])

    def test_search_sidebar_scroll_and_all_booklet_faces(self):
        w = self.window
        w.find_entry.set_text('PAGE')
        wait_for(lambda: not w.search_running and len(w.search_hits) == 7)
        self.assertEqual(len(w.find_results_list.get_children()), 7)
        w._select_search_hit(6)
        wait_for(lambda: w.displayed_page == 7 and not w._search_scroll_pending)
        p = PrintWindow(w, w.runner, str(self.pdf), 8, w.page_sizes, 0, w.cache_dir, lambda job: None)
        try:
            p.mode_stack.set_visible_child_name('booklet')
            for sides, count in [('both', 4), ('front', 2), ('back', 2)]:
                p.book_sides.set_active_id(sides)
                faces = p._booklet_faces()
                self.assertEqual(len(faces), count)
                p.booklet_preview_index = 0
                for index, face in enumerate(faces):
                    self.assertEqual(p._current_booklet_face(), face)
                    self.assertEqual(p.booklet_preview_index, index)
                    p._booklet_step(None, 1)
        finally:
            p.destroy()

    def test_booklet_preview_sides_binding_and_submit(self):
        w = self.window
        jobs = []
        p = PrintWindow(w, w.runner, str(self.pdf), 8, w.page_sizes, 0, w.cache_dir, jobs.append)
        try:
            p.mode_stack.set_visible_child_name('booklet')
            p.book_sides.set_active_id('front')
            self.assertEqual(p._mode_thumbnail_indices(), [7, 0])
            p.book_sides.set_active_id('back')
            self.assertEqual(p._mode_thumbnail_indices(), [1, 6])
            self.assertIn('verso', p.preview_info.get_text())
            self.assertFalse(p.auto_duplex.get_sensitive())
            p.binding.set_active_id('right')
            self.assertEqual(p._mode_thumbnail_indices(), [6, 1])
            p._controls_changed()
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 500, 500)
            self.assertFalse(p._draw_preview(p.preview, cairo.Context(surface)))
            p.dest_combo.append('cups:TestPrinter', 'TestPrinter')
            p.dest_combo.set_active_id('cups:TestPrinter')
            p._submit()
            self.assertEqual(jobs[0]['booklet_sides'], 'back')
            self.assertEqual(jobs[0]['booklet_binding'], 'right')
        finally:
            p.destroy()

    def test_search_results_arrive_before_end_and_options_cancel_old_query(self):
        import threading
        from search_engine import TextSearchIndex
        w = self.window
        index = TextSearchIndex(str(self.pdf), page_sizes=w.page_sizes)
        original = index.page
        release = threading.Event()
        def slow_page(page):
            if page == 1:
                release.wait(5)
            return original(page)
        index.page = slow_page
        w.search_index = index
        try:
            w.find_entry.set_text('ação')
            wait_for(lambda: len(w.search_hits) == 2 and w.search_running)
            self.assertIn('1/8 páginas', w.find_status.get_text())
            old_cancel = w.search_cancel
            w.find_options['match_case'].set_active(True)
            w.find_entry.set_text('AÇÃO')
            self.assertTrue(old_cancel.is_set())
            release.set()
            wait_for(lambda: not w.search_running and w.find_status.get_text() == 'Nenhuma ocorrência')
            self.assertEqual(w.search_hits, [])
            w.find_options['match_case'].set_active(False)
            w.find_options['ignore_accents'].set_active(True)
            w.find_entry.set_text('acao')
            wait_for(lambda: len(w.search_hits) == 2 and not w.search_running)
        finally:
            release.set()


if __name__ == '__main__':
    unittest.main()
````


### Fonte tests/test_regressions.py

````python
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import cairo

APP = Path(os.environ.get('PRINT_VIEW_TEST_APP', Path(__file__).resolve().parents[1] / 'app'))
sys.path.insert(0, str(APP))
import imposition
import rendering
import cups_backend
from pypdf import PdfReader


def make_pdf(path, pages, line_step=28):
    surface = cairo.PDFSurface(str(path), 420, 595)
    cr = cairo.Context(surface)
    cr.select_font_face('DejaVu Sans')
    cr.set_font_size(16)
    for text in pages:
        for row, line in enumerate(text.split('\n')):
            cr.move_to(40, 60 + row * line_step)
            cr.show_text(line)
        cr.show_page()
    surface.finish()


class CoreRegressionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'input.pdf'
        make_pdf(self.pdf, [f'PAGE{i}' for i in range(1, 9)])

    def tearDown(self):
        self.temp.cleanup()

    def test_cache_distinguishes_documents(self):
        other = self.root / 'other.pdf'
        make_pdf(other, ['DIFFERENT DOCUMENT'])
        a = rendering.render_page(str(self.pdf), 0, 420, self.root / 'cache')
        b = rendering.render_page(str(other), 0, 420, self.root / 'cache')
        self.assertNotEqual(__import__('hashlib').sha256(Path(a).read_bytes()).hexdigest(),
                            __import__('hashlib').sha256(Path(b).read_bytes()).hexdigest())

    def test_booklet_generated_sides_and_binding(self):
        for sides, expected in [('both', ['PAGE8', 'PAGE2', 'PAGE6', 'PAGE4']),
                                ('front', ['PAGE8', 'PAGE6']),
                                ('back', ['PAGE2', 'PAGE4'])]:
            out = self.root / f'{sides}.pdf'
            imposition.create_booklet(str(self.pdf), str(out), sides=sides)
            pages = PdfReader(out).pages
            self.assertEqual(len(pages), len(expected))
            for page, first in zip(pages, expected):
                self.assertTrue(page.extract_text().startswith(first))
        out = self.root / 'right.pdf'
        imposition.create_booklet(str(self.pdf), str(out), binding='right', sides='back')
        self.assertTrue(PdfReader(out).pages[0].extract_text().startswith('PAGE7'))

    def test_search_has_individual_occurrence_coordinates(self):
        make_pdf(self.pdf, ['ação ação\nSegundo texto', 'AÇÃO'])
        hits = rendering.search_text(str(self.pdf), 'ação')
        self.assertEqual([hit['page'] for hit in hits], [0, 0, 1])
        self.assertNotEqual(hits[0]['rects'], hits[1]['rects'])
        self.assertTrue(all(hit['width'] > 0 and hit['height'] > 0 for hit in hits))

    def test_manual_booklet_sides_are_not_duplex(self):
        job = {'print_mode': 'booklet', 'booklet_sides': 'back',
               'booklet_auto_duplex': True,
               'printer_options': {'sides': 'two-sided-long-edge'}}
        with patch.object(cups_backend.shutil, 'which', return_value='/usr/bin/lp'), \
             patch.object(cups_backend, '_run') as run:
            run.return_value = subprocess.CompletedProcess([], 0, 'queued', '')
            cups_backend.print_file('TestPrinter', str(self.pdf), job)
        cmd = run.call_args.args[0]
        self.assertIn('sides=one-sided', cmd)
        self.assertNotIn('sides=two-sided-short-edge', cmd)

    def test_worker_prepares_nup_and_poster(self):
        for mode, opts, count in [('multiple', {'pages_per_sheet': 4}, 2),
                                  ('poster', {'poster_scale': 200, 'poster_large_only': False,
                                              'poster_cut_marks': False, 'poster_labels': False}, 32)]:
            out = self.root / f'{mode}.pdf'
            job = {'print_mode': mode, 'paper_size': 'A4', **opts}
            subprocess.run([sys.executable, str(APP / 'worker_cli.py'), 'prepare', str(self.pdf), str(out)],
                           input=json.dumps(job), text=True, capture_output=True, check=True)
            self.assertEqual(len(PdfReader(out).pages), count)

    def test_intrinsic_rotation_and_cropbox_match_text_geometry(self):
        reader = PdfReader(self.pdf)
        page = reader.pages[0]
        page.cropbox.lower_left = (20, 30)
        page.cropbox.upper_right = (400, 570)
        page.rotate(90)
        writer = imposition.PdfWriter(); writer.add_page(page)
        writer.write(self.root / 'rotated.pdf')
        path = str(self.root / 'rotated.pdf')
        data = rendering.extract_page_words(path, 0)
        self.assertEqual((data['width'], data['height']), (540, 380))
        self.assertEqual(rendering.document_info(path)['sizes'], [(540, 380)])
        png = rendering.render_page(path, 0, 540, self.root / 'cache')
        from PIL import Image
        with Image.open(png) as image:
            self.assertEqual(image.size, (540, 380))
        self.assertTrue(all(0 <= w['x0'] < w['x1'] <= data['width'] for w in data['words']))

    def test_search_phrases_and_casefold_expansion(self):
        make_pdf(self.pdf, ['Straße Straße\nação\nseguinte'], line_step=18)
        self.assertEqual(len(rendering.search_text(str(self.pdf), 'STRASSE')), 2)
        hits = rendering.search_text(str(self.pdf), 'ação seguinte')
        self.assertEqual(len(hits), 1)
        self.assertEqual(len(hits[0]['rects']), 2)
        self.assertEqual(rendering.search_text(str(self.pdf), 'ausente'), [])
        self.assertEqual(rendering.search_text(str(self.pdf), ''), [])

    def test_nup_worker_rejects_fractional_count(self):
        with self.assertRaises(ValueError):
            imposition.prepare_output(str(self.pdf), str(self.root / 'bad.pdf'),
                                      {'print_mode': 'multiple', 'pages_per_sheet': 4.9})


if __name__ == '__main__':
    unittest.main()
````


### Fonte tests/test_search.py

````python
import sys
import threading
import unittest
from unittest.mock import patch
import test_regressions as fixtures
from test_regressions import make_pdf, APP
sys.path.insert(0, str(APP))
from search_engine import TextSearchIndex, page_hits


class SearchTests(unittest.TestCase):
    setUp = fixtures.CoreRegressionTests.setUp
    tearDown = fixtures.CoreRegressionTests.tearDown
    def test_options_and_real_pdf(self):
        make_pdf(self.pdf, ['ação AÇÃO acoes\nStraße STRASSE\nagir reagir'])
        index = TextSearchIndex(str(self.pdf))
        self.assertEqual(len(index.search('AÇÃO', match_case=True)), 1)
        self.assertEqual(len(index.search('ação')), 2)
        self.assertEqual(len(index.search('acao')), 0)
        self.assertEqual(len(index.search('acao', ignore_accents=True)), 2)
        self.assertEqual(len(index.search('agir')), 2)
        self.assertEqual(len(index.search('agir', whole_words=True)), 1)
        self.assertEqual(len(index.search('strasse', whole_words=True)), 2)

    def test_cache_reuse_and_cancellation_progress(self):
        index = TextSearchIndex(str(self.pdf))
        with patch('search_engine.extract_page_words', wraps=__import__('rendering').extract_page_words) as extract:
            self.assertEqual(len(index.search('PAGE1')), 1)
            self.assertEqual(len(index.search('PAGE2')), 1)
            self.assertEqual(extract.call_count, 8)
        cancel = threading.Event(); seen = []
        def progress(page, batch):
            seen.append(page)
            if page == 2: cancel.set()
        self.assertEqual(len(index.search('PAGE', cancel=cancel, on_page=progress)), 2)
        self.assertEqual(seen, [1, 2])
        self.assertEqual(index.search('PAGE', cancel=cancel), [])

    def test_hyphenation_does_not_join_columns(self):
        data = {'width': 420, 'height': 595, 'words': [
            {'text': 'impres-', 'block': 0, 'line': 0, 'x0': 10, 'y0': 10, 'x1': 60, 'y1': 25},
            {'text': 'são', 'block': 0, 'line': 1, 'x0': 10, 'y0': 26, 'x1': 40, 'y1': 41},
            {'text': 'outra', 'block': 1, 'line': 0, 'x0': 200, 'y0': 10, 'x1': 250, 'y1': 25}]}
        self.assertEqual(page_hits(data, 'impressão', 0), [])
        hits = page_hits(data, 'impressão', 0, join_hyphens=True)
        self.assertEqual(len(hits), 1); self.assertEqual(len(hits[0]['rects']), 2)
        self.assertEqual(page_hits(data, 'são outra', 0), [])

    def test_cache_eviction_and_changed_file(self):
        index = TextSearchIndex(str(self.pdf), max_cached_pages=2)
        index.search('PAGE')
        self.assertEqual(len(index.cache), 2)
        make_pdf(self.pdf, ['CHANGED'])
        with self.assertRaises(RuntimeError): index.search('CHANGED')
````


### Fonte tests/test_viewer.py

````python
import os
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import cairo
import test_regressions as fixtures
from test_gui import wait_for
from test_regressions import APP
sys.path.insert(0, str(APP))
from main import PDFWindow, Gtk, GdkPixbuf, GLib
from presentation import PresentationWindow
from async_core import BackgroundRunner
from themes import read_theme, load_theme


@unittest.skipUnless(os.environ.get('DISPLAY'), 'Requires an X display')
class ViewerTests(unittest.TestCase):
    setUp_fixture = fixtures.CoreRegressionTests.setUp
    tearDown_fixture = fixtures.CoreRegressionTests.tearDown

    def setUp(self):
        self.setUp_fixture()
        self.env = patch.dict(os.environ, {'XDG_CONFIG_HOME': str(self.root / 'config')}); self.env.start()
        self.quit = patch.object(Gtk, 'main_quit'); self.quit.start()
        self.w = PDFWindow(str(self.pdf))
        self.errors = []; self.w._error = self.errors.append
        wait_for(lambda: self.w.displayed_page == 0)

    def tearDown(self):
        self.w.destroy(); self.quit.stop(); self.env.stop(); self.tearDown_fixture()

    def test_theme_persistence_and_contrast(self):
        self.w.theme_combo.set_active_id('dark')
        self.assertEqual(read_theme(), 'dark')
        settings = Gtk.Settings.get_default()
        self.assertTrue(settings.get_property('gtk-application-prefer-dark-theme'))
        color = self.w.status_file.get_style_context().get_color(Gtk.StateFlags.NORMAL)
        self.assertGreater((color.red + color.green + color.blue) / 3, .65)
        self.w.theme_combo.set_active_id('light')
        self.assertFalse(settings.get_property('gtk-application-prefer-dark-theme'))
        color = self.w.status_file.get_style_context().get_color(Gtk.StateFlags.NORMAL)
        self.assertLess((color.red + color.green + color.blue) / 3, .5)
        self.assertEqual(read_theme(), 'light')

    def test_repeated_requests_do_not_cancel_same_running_render(self):
        from cancel_state import get_event
        started = threading.Event(); release = threading.Event(); events = []
        real_load = self.w._reader_pixbuf
        def slow(*args):
            events.append(get_event()); started.set(); release.wait(5)
            return real_load(*args)
        self.w.page_cache.clear()
        try:
            with patch.object(self.w, '_reader_pixbuf', side_effect=slow):
                self.w.goto_page(5)
                wait_for(started.is_set)
                for _ in range(20):
                    self.w.request_render()
                self.assertFalse(events[0].is_set())
                release.set()
                wait_for(lambda: self.w.displayed_page == 5)
        finally:
            release.set()

    def test_historical_reading_mode_keeps_top_at_250_percent(self):
        p = PresentationWindow(self.w, self.w.runner, str(self.pdf), self.w.page_sizes, 0, self.w.cache_dir)
        try:
            wait_for(lambda: p.pixbuf is not None and not p._loading)
            p.fit_combo.set_active_id('reading')
            wait_for(lambda: p.rendered_zoom == 250 and not p._loading)
            self.assertTrue(p._top_anchor)
            self.assertEqual(p.pan_y, p._pan_bounds()[3])
            p._goto(1)
            wait_for(lambda: p.page == 1 and not p._loading)
            self.assertEqual(p.zoom, 250)
            self.assertEqual(p.pan_y, p._pan_bounds()[3])
        finally:
            p.destroy()

    def test_prefetched_reader_page_is_immediate(self):
        wait_for(lambda: any(key[1] == 1 for key in self.w.page_cache.images))
        before = time.monotonic(); self.w.goto_page(1)
        self.assertEqual(self.w.displayed_page, 1)
        self.assertLess(time.monotonic() - before, .2)
        self.assertLessEqual(self.w.page_cache.bytes, self.w.page_cache.max_bytes)

    def test_presentation_fit_fill_center_and_error(self):
        p = PresentationWindow(self.w, self.w.runner, str(self.pdf), self.w.page_sizes, 0, self.w.cache_dir)
        try:
            wait_for(lambda: p.pixbuf is not None and not p._loading)
            W, H = p._canvas_size(); available = H - p._controls_height()
            self.assertLessEqual(p.pixbuf.get_width(), W)
            self.assertLessEqual(p.pixbuf.get_height(), available)
            self.assertGreater(p.pixbuf.get_height(), available * .88)
            self.assertEqual((p.pan_x, p.pan_y), (0, 0))
            p.fit_combo.set_active_id('fill')
            wait_for(lambda: not p._loading)
            self.assertGreaterEqual(p.pixbuf.get_width(), W - 30)
            old = p.pixbuf
            with patch.object(p, '_load_page_pixbuf', side_effect=RuntimeError('test render failure')):
                p._goto(5)
                wait_for(lambda: p._render_error is not None)
                self.assertIs(p.pixbuf, old)
                surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
                self.assertFalse(p._draw(p.canvas, cairo.Context(surface)))
                self.assertIn('test render failure', p._render_error)
            transparent = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 100, 100)
            transparent.fill(0); p.pixbuf = transparent
            p._loading = False; p._render_error = None
            p.pan_x = p.pan_y = 0
            surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
            p._draw(p.canvas, cairo.Context(surface)); surface.flush()
            y = int((H - p._controls_height()) / 2)
            offset = y * surface.get_stride() + (W // 2) * 4
            self.assertEqual(bytes(surface.get_data()[offset:offset + 3]), b'\xff\xff\xff')
        finally:
            p.destroy()

    def test_cached_presentation_page_invalidates_old_render(self):
        p = PresentationWindow(self.w, self.w.runner, str(self.pdf), self.w.page_sizes, 0, self.w.cache_dir)
        release = threading.Event()
        started = threading.Event()
        try:
            wait_for(lambda: p.pixbuf is not None and not p._loading)
            key = (0, p._target_width_for(0)); original = p.pixbuf
            p._cache_put(key, original)
            real_load = p._load_page_pixbuf
            def slow(page, target):
                if page == 5:
                    started.set(); release.wait(5)
                return real_load(page, target)
            with patch.object(p, '_load_page_pixbuf', side_effect=slow):
                p._goto(5); wait_for(started.is_set); p._goto(0)
                self.assertIs(p.pixbuf, original)
                release.set()
                deadline = time.monotonic() + .3
                while time.monotonic() < deadline:
                    while GLib.MainContext.default().pending(): GLib.MainContext.default().iteration(False)
                    time.sleep(.01)
                self.assertIs(p.pixbuf, original)
                self.assertEqual(p.page, 0)
        finally:
            release.set(); p.destroy()

    def test_render_is_not_blocked_by_auxiliary_workers(self):
        release = threading.Event(); started = [threading.Event() for _ in range(4)]
        def block(event):
            event.set(); release.wait(5)
        try:
            for i, event in enumerate(started):
                self.w.runner.submit(f'busy-{i}', lambda event=event: block(event))
            wait_for(lambda: all(event.is_set() for event in started))
            self.w.goto_page(5)
            wait_for(lambda: self.w.displayed_page == 5, timeout=3)
            self.assertFalse(release.is_set())
        finally:
            release.set()

    def test_latest_renderer_skips_obsolete_queue_entries(self):
        runner = BackgroundRunner(workers=1, latest_only=True)
        release = threading.Event(); started = threading.Event(); calls = []
        try:
            runner.submit('hold', lambda: (started.set(), release.wait(5)))
            wait_for(started.is_set)
            old = runner.submit('page', lambda: calls.append('old'))
            runner.submit('page', lambda: calls.append('new'))
            self.assertTrue(old.cancelled())
            release.set(); wait_for(lambda: calls == ['new'])
        finally:
            release.set(); runner.shutdown()

    def test_presentation_handles_portrait_and_landscape(self):
        from pypdf import PdfReader, PdfWriter
        from rendering import document_info
        reader = PdfReader(self.pdf); writer = PdfWriter()
        writer.add_page(reader.pages[0]); writer.add_page(reader.pages[1].rotate(90))
        path = self.root / 'mixed.pdf'; writer.write(path)
        p = PresentationWindow(self.w, self.w.runner, str(path), document_info(path)['sizes'], 0, self.w.cache_dir)
        try:
            wait_for(lambda: p.pixbuf is not None and not p._loading)
            p._goto(1); wait_for(lambda: not p._loading)
            W, H = p._canvas_size()
            self.assertGreater(p.pixbuf.get_width(), p.pixbuf.get_height())
            self.assertLessEqual(p.pixbuf.get_height(), H - p._controls_height())
            available = H - p._controls_height()
            self.assertTrue(abs(p.pixbuf.get_width() - (W - 24)) <= 3
                            or abs(p.pixbuf.get_height() - (available - 24)) <= 3)
            self.assertEqual((p.pan_x, p.pan_y), (0, 0))
        finally:
            p.destroy()
````


## Anexo H Procedimentos completos de construção e verificação

Os scripts são os existentes na versão 3.4.0. Os caminhos /workspace pertencem ao ambiente histórico. A leitura destes comandos não significa sua execução nesta consulta. Eles não devem ser executados em um sistema diferente sem conferir as dependências e caminhos explicados no roteiro.


### Procedimento scripts/run.sh

````text
#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec /usr/bin/python3 "$project_dir/app/main.py" "$@"
````


### Procedimento scripts/setup-cloud.sh

````text
#!/usr/bin/env bash
# Local runtime overlay for the Debian 13 cloud image; no system installation.
set -euo pipefail
runtime_dir=/workspace/.print-view-runtime
mkdir -p "$runtime_dir/apt/state/lists/partial" "$runtime_dir/apt/cache/archives/partial" "$runtime_dir/apt/log"
setup_dir="$(mktemp -d /tmp/print-view-apt-XXXXXX)"
trap 'rm -rf -- "$setup_dir"' EXIT
mkdir -p "$setup_dir/parts" "$setup_dir/sources"
cat > "$setup_dir/debian.sources" <<'EOF'
Types: deb
URIs: https://deb.debian.org/debian
Suites: trixie
Components: main
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg
EOF
cat > "$setup_dir/apt.conf" <<EOF
Dir::Etc::parts "$setup_dir/parts";
Dir::Etc::sourcelist "$setup_dir/debian.sources";
Dir::Etc::sourceparts "$setup_dir/sources";
Dir::State "$runtime_dir/apt/state";
Dir::Cache "$runtime_dir/apt/cache";
Dir::Log "$runtime_dir/apt/log";
APT::Sandbox::User "$(id -un)";
EOF
cd "$runtime_dir"
APT_CONFIG="$setup_dir/apt.conf" apt-get update
APT_CONFIG="$setup_dir/apt.conf" apt-get download python3-gi-cairo=3.50.0-4+b1 7zip=25.01+dfsg-1~deb13u2
dpkg-deb --extract python3-gi-cairo_3.50.0-4+b1_amd64.deb gi-cairo
dpkg-deb --extract 7zip_25.01+dfsg-1~deb13u2_amd64.deb 7zip
/usr/bin/python3 - <<'PY'
import gi
from pathlib import Path
overlay = Path('/workspace/.print-view-runtime/gi-cairo/usr/lib/python3/dist-packages/gi')
for source in Path(gi.__path__[0]).iterdir():
    target = overlay / source.name
    if not target.exists():
        target.symlink_to(source)
PY
PYTHONPATH="$runtime_dir/gi-cairo/usr/lib/python3/dist-packages" /usr/bin/python3 - <<'PY'
import gi
gi.require_foreign('cairo')
import cairo, PIL, cryptography
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
print('GTK/Cairo and Python PDF runtime available')
PY
"$runtime_dir/7zip/usr/lib/7zip/7z" i >/dev/null
````


### Procedimento scripts/build_deb.py

````python
#!/usr/bin/env python3
"""Build the renamed application without installing or touching the system."""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT / 'app'))
from version import VERSION


def build():
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='print-view-package-') as temp:
        stage = Path(temp)
        app = stage / 'usr/share/print-view-pdf'
        shutil.copytree(ROOT / 'app', app, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for p in app.rglob('*'):
            p.chmod(0o755 if p.is_dir() else 0o644)
        bin_dir = stage / 'usr/bin'; bin_dir.mkdir(parents=True)
        launcher = bin_dir / 'print-view-pdf'
        launcher.write_text('#!/bin/sh\nexec /usr/bin/python3 /usr/share/print-view-pdf/main.py "$@"\n')
        launcher.chmod(0o755)
        desktop_dir = stage / 'usr/share/applications'; desktop_dir.mkdir(parents=True)
        shutil.copy2(ROOT / 'assets/print-view-pdf.desktop', desktop_dir)
        shutil.copytree(ROOT / 'assets/icons', stage / 'usr/share/icons/hicolor')
        doc = stage / 'usr/share/doc/print-view-pdf'; doc.mkdir(parents=True)
        for src in (ROOT / 'LICENSE', ROOT / 'README.md', ROOT / 'docs/pypdf-LICENSE.txt',
                    ROOT / 'docs/ANALISE.md', ROOT / 'docs/PROVENIENCIA.md',
                    ROOT / 'docs/TESTAR-3.3.7.md', ROOT / 'docs/TESTAR-TEST2.md',
                    ROOT / 'docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md',
                    ROOT / 'docs/ENTREGA-3.4.0.md'):
            shutil.copy2(src, doc)
        control = stage / 'DEBIAN'; control.mkdir()
        (control / 'control').write_text(
            f'Package: print-view-pdf\nVersion: {VERSION}\nSection: graphics\nPriority: optional\n'
            'Architecture: all\nMaintainer: Print&View PDF contributors\n'
            'Depends: python3 (>= 3.9), python3-gi, python3-gi-cairo, gir1.2-gtk-3.0, '
            'python3-cairo, python3-cryptography, poppler-utils, cups-client, python3-pil\n'
            'Conflicts: winux-pdf\nReplaces: winux-pdf\n'
            f'Installed-Size: {sum(p.stat().st_size for p in stage.rglob("*") if p.is_file()) // 1024 + 1}\n'
            'Description: Print&View PDF reader and advanced printer for Linux\n'
            ' Continues Winux PDF 3.3.11 with progressive search, themes, presentation,\n'
            ' booklet, poster and N-up printing through CUPS.\n')
        (control / 'postinst').write_text('#!/bin/sh\nset -e\nif [ "$1" = configure ]; then\n  if command -v py3compile >/dev/null 2>&1; then py3compile /usr/share/print-view-pdf; fi\n  if command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database -q; fi\n  if command -v gtk-update-icon-cache >/dev/null 2>&1; then gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true; fi\nfi\n')
        (control / 'postrm').write_text('#!/bin/sh\nset -e\nif command -v py3clean >/dev/null 2>&1; then py3clean -p print-view-pdf; fi\nif command -v update-desktop-database >/dev/null 2>&1; then update-desktop-database -q; fi\nif command -v gtk-update-icon-cache >/dev/null 2>&1; then gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true; fi\n')
        (doc / 'copyright').write_text('Print&View PDF: MIT, see LICENSE.\nBundled pypdf 6.20.1: BSD-3-Clause, see pypdf-LICENSE.txt.\nOriginal Winux source continued with authorization from its authors.\n')
        for p in stage.rglob('*'):
            if p.is_dir(): p.chmod(0o755)
            elif p == launcher or p.name in ('postinst', 'postrm'): p.chmod(0o755)
            else: p.chmod(0o644)
        output = dist / f'print-view-pdf_{VERSION}_all.deb'
        subprocess.run(['dpkg-deb', '--root-owner-group', '--build', str(stage), str(output)], check=True)
    return output


if __name__ == '__main__':
    print(build())
````


### Procedimento scripts/build_flatpak.py

````python
#!/usr/bin/env python3
"""Bundle the Debian 13 Python/GTK runtime into a real Flatpak application."""
import argparse
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
from version import VERSION
APP_ID = 'io.github.airtonbp19edu.PrintViewPDF'


def build(flatpak, stage, repo, extra):
    if stage.exists():
        raise RuntimeError('Use an empty staging location; existing files are preserved.')
    files = stage / 'files'
    for name in ['bin', 'lib', 'libexec', 'share', 'etc']:
        (files / name).mkdir(parents=True, exist_ok=True)
    ignore = shutil.ignore_patterns('__pycache__', '*.pyc', 'test', 'tests', 'idlelib', 'tkinter')
    shutil.copytree(ROOT / 'app', files / 'share/print-view-pdf', ignore=ignore)
    shutil.copytree('/usr/lib/python3.13', files / 'python/lib/python3.13', ignore=ignore)
    site = files / 'python/lib/python3.13/site-packages'
    site.mkdir()
    for module in ['gi', 'cairo', 'PIL', 'cryptography', 'cffi', 'pycparser']:
        origin = Path('/usr/lib/python3/dist-packages') / module
        if origin.exists():
            shutil.copytree(origin, site / module, ignore=ignore)
    for origin in Path('/usr/lib/python3/dist-packages').glob('_cffi_backend*.so'):
        shutil.copy2(origin, site)
    adapter = extra / 'gi-cairo/usr/lib/python3/dist-packages/gi'
    for origin in adapter.glob('_gi_cairo*.so'):
        shutil.copy2(origin, site / 'gi')
    if not list((site / 'gi').glob('_gi_cairo*.so')):
        raise RuntimeError('python3-gi-cairo is required in the runtime overlay.')
    binaries = {'python3': Path('/usr/bin/python3.13')}
    for name in ('pdftocairo', 'pdftotext', 'pdfinfo', 'pdfunite', 'prlimit', 'lp', 'lpstat', 'lpoptions'):
        origin = str(Path('/usr/bin') / name) if (Path('/usr/bin') / name).exists() else str(extra / 'usr/bin' / name)
        if not Path(origin).exists():
            raise RuntimeError('Required executable missing: ' + name)
        with open(origin, 'rb') as source:
            if source.read(4) != b'\x7fELF':
                raise RuntimeError('An actual ELF executable is required: ' + origin)
        binaries[name] = Path(origin)
    for name, origin in binaries.items():
        shutil.copy2(origin, files / 'libexec' / name)
    shutil.copytree('/usr/lib/x86_64-linux-gnu/girepository-1.0', files / 'lib/girepository-1.0')
    pix = Path('/usr/lib/x86_64-linux-gnu/gdk-pixbuf-2.0/2.10.0')
    shutil.copytree(pix, files / 'lib/gdk-pixbuf-2.0/2.10.0')
    cache = files / 'lib/gdk-pixbuf-2.0/2.10.0/loaders.cache'
    cache.write_text(cache.read_text().replace('/usr/lib/x86_64-linux-gnu/', '/app/lib/'))
    shutil.copytree('/usr/share/glib-2.0/schemas', files / 'share/glib-2.0/schemas')
    shutil.copytree('/usr/share/fonts/truetype/dejavu', files / 'share/fonts/truetype/dejavu')
    shutil.copytree('/usr/share/icons/Adwaita', files / 'share/icons/Adwaita')
    shutil.copytree('/usr/share/mime', files / 'share/mime')
    shutil.copytree(ROOT / 'assets/icons', files / 'share/icons/hicolor', dirs_exist_ok=True)
    for icon in (files / 'share/icons/hicolor').rglob('print-view-pdf.png'):
        shutil.copy2(icon, icon.with_name(APP_ID + '.png'))
    (files / 'etc/fonts').mkdir()
    (files / 'etc/fonts/fonts.conf').write_text('''<?xml version="1.0"?>
<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">
<fontconfig><dir>/app/share/fonts</dir><dir>/usr/share/fonts</dir><dir>/run/host/fonts</dir>
<cachedir prefix="xdg">fontconfig</cachedir></fontconfig>
''')
    # All ELF dependencies, including libc, are paired with their own loader.
    # This avoids mixing a newer host-built extension with a different runtime libc.
    probes = list((files / 'libexec').iterdir()) + list(files.rglob('*.so'))
    dynamic_gui = [Path('/usr/lib/x86_64-linux-gnu') / name for name in
                   ('libgtk-3.so.0', 'libgdk-3.so.0', 'libatk-1.0.so.0',
                    'libpangocairo-1.0.so.0', 'libgdk_pixbuf-2.0.so.0')]
    probes.extend(dynamic_gui)
    libraries = set(dynamic_gui)
    for probe in probes:
        result = subprocess.run(['ldd', str(probe)], capture_output=True, text=True)
        for path in re.findall(r'(?:=>\s+)?(/[^\s()]+)', result.stdout):
            if Path(path).is_file():
                libraries.add(Path(path))
    for library in sorted(libraries):
        shutil.copy2(library, files / 'lib' / library.name)
    loader = Path('/lib64/ld-linux-x86-64.so.2').resolve()
    shutil.copy2(loader, files / 'lib/ld-linux-x86-64.so.2')
    for name in binaries:
        wrapper = files / 'bin' / name
        wrapper.write_text('''#!/bin/sh
base="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec "$base/lib/ld-linux-x86-64.so.2" --library-path "$base/lib" "$base/libexec/''' + name + '''" "$@"
''')
        wrapper.chmod(0o755)
    python = files / 'bin/print-view-python'
    python.write_text('''#!/bin/sh
base="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
export PYTHONHOME="$base/python"
export PYTHONPATH="$base/python/lib/python3.13/site-packages"
export LD_LIBRARY_PATH="$base/lib"
export GI_TYPELIB_PATH="$base/lib/girepository-1.0"
export GSETTINGS_SCHEMA_DIR="$base/share/glib-2.0/schemas"
cache_dir="${XDG_CACHE_HOME:-${TMPDIR:-/tmp}}/print-view-pdf"
mkdir -p "$cache_dir"
cache_id="$(printf '%s' "$base" | cksum | cut -d ' ' -f 1)"
module_cache="$cache_dir/loaders-$cache_id.cache"
if [ ! -f "$module_cache" ]; then
  temp_cache="$(mktemp "$cache_dir/.loaders-XXXXXX")"
  sed "s#/app/#$base/#g" "$base/lib/gdk-pixbuf-2.0/2.10.0/loaders.cache" > "$temp_cache"
  mv -f "$temp_cache" "$module_cache"
fi
export GDK_PIXBUF_MODULE_FILE="$module_cache"
export FONTCONFIG_FILE="$base/etc/fonts/fonts.conf"
export XDG_DATA_DIRS="$base/share:/usr/share"
export PRINT_VIEW_WORKER_PYTHON="$base/bin/print-view-python"
export PATH="$base/bin:$PATH"
exec "$base/bin/python3" "$@"
''')
    python.chmod(0o755)
    launcher = files / 'bin/print-view-pdf'
    launcher.write_text('''#!/bin/sh
base="$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
exec "$base/bin/print-view-python" "$base/share/print-view-pdf/main.py" "$@"
''')
    launcher.chmod(0o755)
    appdir = files / 'share/applications'
    appdir.mkdir()
    desktop = (ROOT / 'assets/print-view-pdf.desktop').read_text().replace('Icon=print-view-pdf', 'Icon=' + APP_ID)
    (appdir / (APP_ID + '.desktop')).write_text(desktop)
    metadata = files / 'share/metainfo'
    metadata.mkdir()
    shutil.copy2(ROOT / 'packaging' / (APP_ID + '.metainfo.xml'), metadata)
    docs = files / 'share/doc/print-view-pdf'
    shutil.copytree(ROOT / 'docs', docs)
    shutil.copy2(ROOT / 'LICENSE', docs)
    # Preserve installed Debian copyright notices for every bundled ELF package.
    notices = docs / 'runtime-copyright'
    notices.mkdir()
    packages = set()
    for path in libraries | set(binaries.values()):
        result = subprocess.run(['dpkg-query', '-S', str(path)], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            packages.add(line.split(': ')[0].split(':')[0])
    for package in packages:
        copyright = Path('/usr/share/doc') / package / 'copyright'
        if copyright.exists():
            shutil.copy2(copyright, notices / (package + '.txt'))
    shutil.copy2(ROOT / 'docs/cups-client-copyright.txt', notices / 'cups-client.txt')
    (stage / 'metadata').write_text(f'''[Application]
name={APP_ID}
runtime=org.freedesktop.Platform/x86_64/25.08
sdk=org.freedesktop.Sdk/x86_64/25.08
command=print-view-pdf

[Context]
shared=network;ipc;
sockets=wayland;fallback-x11;cups;
devices=dri;
filesystems=home;

[Session Bus Policy]
org.freedesktop.portal.*=talk
''')
    (stage / 'export').mkdir()
    export = stage / 'export/share'
    shutil.copytree(appdir, export / 'applications')
    shutil.copytree(metadata, export / 'metainfo')
    for icon in (files / 'share/icons/hicolor').rglob(APP_ID + '.png'):
        relative = icon.relative_to(files / 'share')
        target = export / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(icon, target)
    subprocess.run([flatpak, 'build-export', '--disable-sandbox', str(repo), str(stage), 'stable'], check=True)
    output = ROOT / 'dist' / f'PrintViewPDF-{VERSION}-x86_64.flatpak'
    subprocess.run([flatpak, 'build-bundle', '--runtime-repo=https://dl.flathub.org/repo/flathub.flatpakrepo',
                    str(repo), str(output), APP_ID, 'stable'], check=True)
    print(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--flatpak', default='flatpak')
    parser.add_argument('--stage', type=Path, default=ROOT / 'dist/flatpak-stage')
    parser.add_argument('--repo', type=Path, default=ROOT / 'dist/flatpak-repo')
    parser.add_argument('--extra-runtime', type=Path, required=True,
                        help='Runtime overlay with gi-cairo/ and optional usr/bin/lp*')
    args = parser.parse_args()
    build(args.flatpak, args.stage, args.repo, args.extra_runtime)
````


### Procedimento scripts/build_windows.py

````python
#!/usr/bin/env python3
"""Build an x64 Windows installer on Linux or Windows using pinned runtimes."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'app'))
from version import VERSION


def extract(z, name, destination):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(z.read(name))


def build(downloads, makensis, stage):
    downloads.mkdir(parents=True, exist_ok=True)
    items = json.loads((ROOT / 'packaging/windows-artifacts.json').read_text())
    for item in items:
        path = downloads / item['file']
        if not path.exists():
            with urllib.request.urlopen(item['url'], timeout=60) as response, path.open('wb') as out:
                shutil.copyfileobj(response, out)
        if hashlib.sha256(path.read_bytes()).hexdigest() != item['sha256']:
            raise RuntimeError('Dependency checksum mismatch: ' + item['file'])
    if stage.exists():
        raise RuntimeError('Use a new staging directory; existing files are preserved.')
    stage.mkdir(parents=True)
    with zipfile.ZipFile(downloads / 'python.3.14.0.nupkg') as z:
        for name in z.namelist():
            if name.startswith('tools/') and not name.endswith('/'):
                extract(z, name, stage / 'python' / name.removeprefix('tools/'))
    with zipfile.ZipFile(downloads / 'GTK3_Gvsbuild_2026.8.0_x64.zip') as z:
        for name in z.namelist():
            keep = ((name.startswith('bin/') and name.endswith('.dll')) or
                    name.startswith(('lib/girepository-1.0/', 'lib/gdk-pixbuf-2.0/',
                                     'share/glib-2.0/', 'share/icons/', 'share/doc/',
                                     'share/fontconfig/', 'etc/fonts/')))
            if keep and not name.endswith('/') and not name.endswith(('.pdb', '.lib', '.a')):
                extract(z, name, stage / 'gtk' / name)
        for name in z.namelist():
            if name.startswith('wheels/') and name.endswith('.whl'):
                wheel = downloads / Path(name).name
                extract(z, name, wheel)
    with zipfile.ZipFile(downloads / 'Release-26.09.0-0.zip') as z:
        prefix = 'poppler-26.09.0/Library/'
        for name in z.namelist():
            if name.startswith(prefix) and not name.endswith('/'):
                relative = name.removeprefix(prefix)
                if relative.startswith('bin/') and (relative.endswith('.dll') or Path(relative).name in
                        ('pdfinfo.exe', 'pdftocairo.exe', 'pdftotext.exe', 'pdfunite.exe')):
                    extract(z, name, stage / 'poppler' / relative)
                elif relative.startswith('share/'):
                    extract(z, name, stage / 'poppler' / relative)
            elif name.startswith('poppler-26.09.0/share/') and not name.endswith('/'):
                extract(z, name, stage / 'poppler' / name.removeprefix('poppler-26.09.0/'))
    for wheel in downloads.glob('*.whl'):
        # Only the locked Windows wheels and GTK's cp314 wheels, not the Linux build environment.
        if wheel.name not in {i['file'] for i in items} and not wheel.name.startswith(('pygobject-', 'pycairo-')):
            continue
        with zipfile.ZipFile(wheel) as z:
            for name in z.namelist():
                if not name.endswith('/'):
                    if '..' in Path(name).parts or Path(name).is_absolute():
                        raise RuntimeError('Invalid wheel path')
                    extract(z, name, stage / 'python/Lib/site-packages' / name)
    shutil.copytree(ROOT / 'app', stage / 'app', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copytree(ROOT / 'assets/icons', stage / 'share/icons/hicolor')
    shutil.copytree(ROOT / 'docs', stage / 'docs')
    shutil.copy2(ROOT / 'LICENSE', stage / 'LICENSE.txt')
    shutil.copy2(ROOT / 'README.md', stage / 'README.md')
    dist = ROOT / 'dist'
    dist.mkdir(exist_ok=True)
    subprocess.run([makensis, '-V2', f'-DAPP_VERSION={VERSION}', f'-DSTAGE={stage.resolve()}',
                    str(ROOT / 'packaging/windows-launcher.nsi')], check=True)
    output = dist / f'PrintViewPDF-{VERSION}-Setup-x64.exe'
    subprocess.run([makensis, '-V2', f'-DAPP_VERSION={VERSION}', f'-DSTAGE={stage.resolve()}',
                    f'-DOUTPUT={output.resolve()}', str(ROOT / 'packaging/windows-installer.nsi')], check=True)
    print(output)
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--downloads', type=Path, default=ROOT / 'dist/windows-downloads')
    parser.add_argument('--stage', type=Path, default=ROOT / 'dist/windows-stage')
    parser.add_argument('--makensis', default='makensis')
    args = parser.parse_args()
    build(args.downloads, args.makensis, args.stage)
````


### Procedimento scripts/smoke_windows.py

````python
#!/usr/bin/env python3
"""Exercise the Windows runtime with a generated PDF, without printing."""
import argparse
import json
from pathlib import Path
import sys
import tempfile
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--app', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
output = args.output.resolve()
sys.path.insert(0, str(args.app.resolve()))
from windows_bootstrap import configure
configure()
import cairo
from main import PDFWindow, load_css
from gi.repository import Gtk, GLib
from imposition import create_booklet
from pypdf import PdfReader

temp = tempfile.TemporaryDirectory(prefix='print-view-windows-smoke-', ignore_cleanup_errors=True)
pdf = Path(temp.name) / 'sample.pdf'
surface = cairo.PDFSurface(str(pdf), 420, 595)
cr = cairo.Context(surface)
cr.select_font_face('Arial')
cr.set_font_size(16)
for page in range(1, 5):
    cr.move_to(40, 60)
    cr.show_text('PAGE' + str(page))
    cr.show_page()
surface.finish()
load_css()
window = PDFWindow(str(pdf))
errors = []
window._error = errors.append
started = time.monotonic()
search_started = False
report = None


def poll():
    global search_started, report
    if errors or time.monotonic() - started > 30:
        report = {'passed': False, 'errors': errors, 'pages': window.page_count,
                  'image': window.current_pixbuf is not None, 'status': window.status_file.get_text()}
    elif window.page_count and window.current_pixbuf is not None:
        if not search_started:
            window.find_entry.set_text('PAGE')
            search_started = True
        elif not window.search_running and len(window.search_hits) == 4:
            booklet = Path(temp.name) / 'booklet.pdf'
            create_booklet(str(pdf), str(booklet), sides='back')
            report = {'passed': True, 'pages': window.page_count, 'hits': len(window.search_hits),
                      'sidebar_rows': len(window.find_results_list.get_children()),
                      'booklet_pages': len(PdfReader(booklet).pages),
                      'pixbuf': [window.current_pixbuf.get_width(), window.current_pixbuf.get_height()],
                      'python': sys.version, 'platform': sys.platform}
    if report is not None:
        output.write_text(json.dumps(report, indent=2) + '\n')
        window.destroy()
        return False
    return True


GLib.timeout_add(100, poll)
Gtk.main()
temp.cleanup()
raise SystemExit(0 if report and report['passed'] else 1)
````


### Procedimento scripts/verify_winux_history.py

````python
import atexit
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

# Audit checks for the original Winux 3.3.11 source, not the current app/.
# Isolate appearance settings from the user's desktop preferences.
_check_config = tempfile.TemporaryDirectory(prefix='winux-history-checks-')
atexit.register(_check_config.cleanup)
os.environ['XDG_CONFIG_HOME'] = str(Path(_check_config.name) / 'config')
if not os.environ.get('WINUX_HISTORY_APP'):
    raise SystemExit('Set WINUX_HISTORY_APP to an extracted Winux 3.3.11 source directory.')
if not os.environ.get('DISPLAY'):
    raise SystemExit('A usable DISPLAY is required; no GUI checks may be silently skipped.')
APP = Path(os.environ['WINUX_HISTORY_APP']).resolve()
if not (APP / 'cancel_state.py').is_file():
    raise SystemExit('Winux 3.3.11 modules were not found at WINUX_HISTORY_APP.')
sys.path.insert(0, str(APP))
import cairo
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GLib
import rendering
import imposition
import cups_backend
import cancel_state
import appearance
from main import PDFWindow, load_css
from presentation import PresentationWindow
from print_window import PrintWindow
from pypdf import PdfReader


def make_pdf(path, texts):
    surface = cairo.PDFSurface(str(path), 420, 595)
    cr = cairo.Context(surface)
    cr.select_font_face('DejaVu Sans')
    cr.set_font_size(16)
    for text in texts:
        for row, line in enumerate(text.split('\n')):
            cr.move_to(40, 60 + row * 28)
            cr.show_text(line)
        cr.show_page()
    surface.finish()


def wait_for(predicate, timeout=15):
    until = time.monotonic() + timeout
    while time.monotonic() < until:
        context = GLib.MainContext.default()
        for _ in range(100):
            if not context.pending():
                break
            context.iteration(False)
        if predicate():
            return
        time.sleep(.02)
    raise AssertionError('GTK readiness timeout')


class HistoryChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.pdf = self.root / 'sample.pdf'
        make_pdf(self.pdf, ['ação ação\nAÇÃO ações'] + [f'PAGE{i}' for i in range(2, 9)])
        self.windows = []
        self.quit_patch = patch.object(Gtk, 'main_quit')
        self.quit_patch.start()

    def tearDown(self):
        for window in reversed(self.windows):
            window.destroy()
        self.quit_patch.stop()
        self.temp.cleanup()

    def reader(self):
        # Explicit mode avoids the separate system-mode defect checked below.
        appearance.save_mode('light')
        load_css()
        window = PDFWindow()
        self.windows.append(window)
        errors = []
        window._error = errors.append
        window.open_document(str(self.pdf))
        wait_for(lambda: window.page_count == 8 and window.current_pixbuf is not None)
        self.assertEqual(errors, [])
        return window

    def test_search_occurrences_case_and_whole_words(self):
        hits = rendering.search_text(str(self.pdf), 'ação', whole_words=True)
        self.assertEqual(len(hits), 3)
        self.assertNotEqual(hits[0]['rects'], hits[1]['rects'])
        self.assertTrue(all(hit['snippet'] and hit['width'] and hit['height'] for hit in hits))
        self.assertEqual(len(rendering.search_text(str(self.pdf), 'ação', match_case=True, whole_words=True)), 2)

    def test_search_query_bound(self):
        with self.assertRaises(ValueError):
            rendering.search_text(str(self.pdf), 'x' * 257)

    def test_jpeg_png_and_document_cache_identity(self):
        jpeg = rendering.render_page(str(self.pdf), 0, 420, self.root / 'cache', image_format='jpeg')
        png = rendering.render_page(str(self.pdf), 0, 420, self.root / 'cache')
        self.assertTrue(rendering._valid_jpeg(jpeg))
        self.assertTrue(rendering._valid_png(png))
        make_pdf(self.pdf, ['MODIFIED DOCUMENT'])
        changed = rendering.render_page(str(self.pdf), 0, 420, self.root / 'cache', image_format='jpeg')
        self.assertNotEqual(jpeg, changed)

    def test_booklet_output_all_sides(self):
        for sides, expected in [('both', 4), ('front', 2), ('back', 2)]:
            out = self.root / f'{sides}.pdf'
            imposition.create_booklet(str(self.pdf), str(out), sides=sides)
            self.assertEqual(len(PdfReader(out).pages), expected)
            self.assertEqual(len(imposition.booklet_print_pairs(list(range(8)), sides)), expected)

    def test_running_process_cancellation(self):
        event = threading.Event()
        def trigger():
            time.sleep(.2)
            event.set()
        trigger_thread = threading.Thread(target=trigger)
        trigger_thread.start()
        cancel_state.set_event(event)
        start = time.monotonic()
        try:
            with self.assertRaisesRegex(RuntimeError, 'cancelada'):
                rendering._run([sys.executable, '-c', 'import time; time.sleep(10)'], timeout=15)
            self.assertLess(time.monotonic() - start, 2)
        finally:
            cancel_state.set_event(None)
            trigger_thread.join()

    def test_cups_option_validation_without_printing(self):
        with patch.object(cups_backend.shutil, 'which', return_value='/usr/bin/lp'), patch.object(cups_backend, '_run') as run:
            for key, value in [('media', 'A4\nBAD'), ('bad=key', 'A4'), ('media', 'x' * 161)]:
                with self.assertRaises(ValueError):
                    cups_backend.print_file('TestPrinter', str(self.pdf), {'printer_options': {key: value}})
            run.assert_not_called()

    def test_theme_persistence_preserves_other_settings(self):
        path = self.root / 'settings' / 'settings.json'
        path.parent.mkdir()
        path.write_text('{"other": 42}')
        for mode in ('dark', 'light', 'system'):
            appearance.save_mode(mode, path)
            self.assertEqual(appearance.read_mode(path), mode)
            self.assertEqual(json.loads(path.read_text())['other'], 42)
        self.assertEqual(path.parent.stat().st_mode & 0o777, 0o700)

    def test_system_theme_controller_initializes(self):
        env = os.environ.copy()
        env['XDG_CONFIG_HOME'] = str(self.root / 'fresh-system-config')
        code = (f'import sys; sys.path.insert(0, {str(APP)!r}); '
                'from appearance import AppearanceController; '
                f'AppearanceController({str(APP)!r}); print("initialized", flush=True)')
        result = subprocess.run([sys.executable, '-c', code], env=env,
                                capture_output=True, text=True, timeout=4)
        self.assertIn('initialized', result.stdout)

    def test_reader_search_sidebar_and_navigation(self):
        w = self.reader()
        w.find_entry.set_text('PAGE')
        wait_for(lambda: len(w.search_hits) == 7)
        self.assertEqual(len(w.find_results_list.get_children()), 7)
        w._select_search_hit(6)
        wait_for(lambda: w.page == 7 and not w._search_scroll_pending)
        self.assertEqual(w.find_status.get_text(), '7 de 7')

    def test_presentation_initial_zoom_top_and_navigation(self):
        w = self.reader()
        p = PresentationWindow(w, w.runner, str(self.pdf), w.page_sizes, 0, w.cache_dir)
        self.windows.append(p)
        # Bare Xorg has no window manager to honor fullscreen requests.
        p.set_default_size(1280, 900)
        p.resize(1280, 900)
        wait_for(lambda: p.pixbuf is not None)
        self.assertEqual(p.zoom, 250)
        self.assertTrue(p._top_anchor)
        p._goto(1)
        wait_for(lambda: p.page == 1 and p.rendered_zoom == 250 and p.pixbuf is not None)
        self.assertTrue(p._top_anchor)

    def test_booklet_preview_browses_all_faces(self):
        w = self.reader()
        p = PrintWindow(w, w.runner, str(self.pdf), 8, w.page_sizes, 0, w.cache_dir, lambda job: None)
        self.windows.append(p)
        p.mode_stack.set_visible_child_name('booklet')
        for sides in ('both', 'front', 'back'):
            p.book_sides.set_active_id(sides)
            faces = p._booklet_faces()
            p.booklet_preview_index = 0
            for index, face in enumerate(faces):
                self.assertEqual(p._current_booklet_face(), face)
                self.assertEqual(p.booklet_preview_index, index)
                p._booklet_step(None, 1)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HistoryChecks)
    names = [test.id().rsplit('.', 1)[-1] for test in suite]
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    errors = {test.id().rsplit('.', 1)[-1] for test, _ in result.errors}
    failures = {test.id().rsplit('.', 1)[-1] for test, _ in result.failures}
    report = {
        'target': 'Winux PDF 3.3.11 original extracted source',
        'tests_run': result.testsRun,
        'passed': result.testsRun - len(result.errors) - len(result.failures) - len(result.skipped),
        'errors': len(result.errors), 'failures': len(result.failures),
        'skipped': len(result.skipped),
        'tests': [{'name': n, 'status': 'error' if n in errors else 'failed' if n in failures else 'passed'} for n in names],
        'source_module_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(APP.glob('*.py'))},
        'conditions': ['GTK 3 and real Poppler', 'Synthetic eight-page PDF',
                       'Explicit light mode in reader tests; separate fresh system-mode subprocess',
                       'Explicit presentation size for bare Xorg without a window manager',
                       'CUPS command execution mocked; no printer jobs submitted'],
        'limits': ['No physical printing', 'No package manager installation',
                   'No heavy-document benchmark', 'No Windows readers executed'],
    }
    if os.environ.get('WINUX_HISTORY_RESULTS'):
        Path(os.environ['WINUX_HISTORY_RESULTS']).write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)
````


### Procedimento scripts/analyze_windows_readers.py

````python
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
````


### Procedimento scripts/headless-xorg.conf

````text
Section "Device"
 Identifier "Dummy"
 Driver "dummy"
 VideoRam 256000
EndSection
Section "Monitor"
 Identifier "Monitor"
 HorizSync 5.0-1000.0
 VertRefresh 5.0-200.0
 Modeline "1280x900" 108.00 1280 1328 1440 1688 900 903 909 934
EndSection
Section "Screen"
 Identifier "Screen"
 Device "Dummy"
 Monitor "Monitor"
 DefaultDepth 24
 SubSection "Display"
  Depth 24
  Modes "1280x900"
 EndSubSection
EndSection
````


### Procedimento packaging/windows-launcher.nsi

````text
Unicode true
!include "FileFunc.nsh"
Name "Print&View PDF"
OutFile "${STAGE}/PrintViewPDF.exe"
RequestExecutionLevel user
SilentInstall silent
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey /LANG=1033 "ProductName" "Print&View PDF"
VIAddVersionKey /LANG=1033 "FileDescription" "Print&View PDF launcher"
VIAddVersionKey /LANG=1033 "FileVersion" "${APP_VERSION}"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Print&View PDF contributors"
Function .onInit
  ${GetParameters} $0
  Exec '$\"$EXEDIR\python\pythonw.exe$\" $\"$EXEDIR\app\windows_bootstrap.py$\" $0'
  Quit
FunctionEnd
Section
SectionEnd
````


### Procedimento packaging/windows-installer.nsi

````text
Unicode true
!include "MUI2.nsh"
Name "Print&View PDF ${APP_VERSION}"
OutFile "${OUTPUT}"
InstallDir "$LOCALAPPDATA\Programs\PrintViewPDF"
RequestExecutionLevel user
SetCompressor /SOLID lzma
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey /LANG=1033 "ProductName" "Print&View PDF"
VIAddVersionKey /LANG=1033 "FileDescription" "Print&View PDF installer for Windows x64"
VIAddVersionKey /LANG=1033 "FileVersion" "${APP_VERSION}"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Print&View PDF contributors"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "PortugueseBR"
!insertmacro MUI_LANGUAGE "English"
Section "Print&View PDF"
  SetShellVarContext current
  SetOutPath "$INSTDIR"
  File /r "${STAGE}/*"
  CreateDirectory "$SMPROGRAMS\Print&View PDF"
  CreateShortCut "$SMPROGRAMS\Print&View PDF\Print&View PDF.lnk" "$INSTDIR\PrintViewPDF.exe"
  CreateShortCut "$DESKTOP\Print&View PDF.lnk" "$INSTDIR\PrintViewPDF.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintViewPDF" "DisplayName" "Print&View PDF ${APP_VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintViewPDF" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintViewPDF" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
  WriteRegStr HKCU "Software\Classes\Applications\PrintViewPDF.exe\shell\open\command" "" '$\"$INSTDIR\PrintViewPDF.exe$\" $\"%1$\"'
  WriteRegStr HKCU "Software\Classes\Applications\PrintViewPDF.exe\SupportedTypes" ".pdf" ""
SectionEnd
Section "Uninstall"
  SetShellVarContext current
  Delete "$DESKTOP\Print&View PDF.lnk"
  RMDir /r "$SMPROGRAMS\Print&View PDF"
  DeleteRegKey HKCU "Software\Classes\Applications\PrintViewPDF.exe"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintViewPDF"
  RMDir /r "$INSTDIR"
SectionEnd
````


### Procedimento packaging/io.github.airtonbp19edu.PrintViewPDF.metainfo.xml

````text
<?xml version="1.0" encoding="UTF-8"?>
<component type="desktop-application">
  <id>io.github.airtonbp19edu.PrintViewPDF</id>
  <name>Print&amp;View PDF</name>
  <summary>Read PDFs and prepare booklet, poster and multiple-page printing</summary>
  <summary xml:lang="pt_BR">Leia PDFs e prepare impressão em livreto, pôster e várias páginas por folha</summary>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>MIT</project_license>
  <developer id="io.github.airtonbp19edu"><name>Print&amp;View PDF contributors</name></developer>
  <description>
    <p>Print&amp;View PDF continues Winux PDF with progressive text search, light and dark themes, presentation, selection and advanced PDF print layouts.</p>
    <p xml:lang="pt_BR">Print&amp;View PDF continua o Winux PDF com busca progressiva, temas claro e escuro, apresentação, seleção e preparação avançada de impressão.</p>
  </description>
  <launchable type="desktop-id">io.github.airtonbp19edu.PrintViewPDF.desktop</launchable>
  <url type="homepage">https://github.com/airtonbp19edu/Print-and-View-PDF</url>
  <url type="bugtracker">https://github.com/airtonbp19edu/Print-and-View-PDF/issues</url>
  <provides><mediatype>application/pdf</mediatype></provides>
  <categories><category>Office</category><category>Viewer</category></categories>
  <content_rating type="oars-1.1"/>
  <releases><release version="3.4.0" date="2026-10-14"/></releases>
</component>
````


### Procedimento assets/print-view-pdf.desktop

````text
[Desktop Entry]
Type=Application
Name=Print&View PDF
GenericName=Leitor e Impressor de PDF
Comment=Leitura de PDF com impressão avançada, livreto, pôster e apresentação
Exec=print-view-pdf %f
TryExec=print-view-pdf
Icon=print-view-pdf
Terminal=false
Categories=Office;Viewer;
MimeType=application/pdf;
StartupWMClass=print-view-pdf
StartupNotify=true
````


### Procedimento packages/SHA256SUMS

````text
2ee91c8828db0d246c5129bded8a47825fa681daf1b575f80bf4dd99989ab43e  PrintViewPDF-3.4.0-Setup-x64.exe
7f5926f32a5034677d6c26e947029e8359d511f29cdfbacc9afd27d1a38b7b08  PrintViewPDF-3.4.0-x86_64.flatpak
f12e476cf114eff9588dad3cfb5427376a0a5d06eddc57555472b6cd428c1bab  print-view-pdf_3.3.7~test1_all.deb
534d7ccf6168c4529cbb4dcead7b4b08aee58a188cca1093e4be0f9eb204abb0  print-view-pdf_3.3.7~test2_all.deb
229023b13486d51df93170a70623fedbb2dd2ff7fd188044e1bf7224c5c86273  print-view-pdf_3.4.0_all.deb
5d1858a527d741c303617e391c055d7d224011075cf358fb172c3a5932772fb2  print-view-pdf_3.4.0_source.tar.gz
````


## Anexo I Inventário integral dos 156 arquivos rastreados

Os tamanhos e hashes abaixo foram calculados dos arquivos locais em 19/10/2026. Arquivos de texto podem ter CRLF nesta cópia; por isso seus hashes locais podem diferir dos blobs LF no Git sem haver modificação lógica. Os relatórios recém-criados não pertencem a esse inventário inicial. Os metadados PE e assemblies da análise de referência estão listados individualmente com seus hashes; seus milhares de linhas não são confundidos com código próprio de produto.


### Grupo raiz

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| .gitignore | 45 | 35f74a78f1e02d8efdf457fb6a76e40f7d0e29f7fb88132252be80628bba7160 |
| LICENSE | 1091 | 2ba9d9d0de261bd2b36d06a5e475acebc46ceac06135c4c70be407b95939428d |
| README.md | 4563 | bb01752cf4638e223400e5dccdd78045eabf1a084dc854eee841f76370e0ce3f |


### Grupo app próprio

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| app/appearance.py | 6728 | 2121ba8a118cdd5dc4fc2a921743bc65db3592aa86f9068d1d632358e339c68a |
| app/async_core.py | 3935 | 898fc96e24760a8e9fab23834bd4416e4e3e5dcd36cff71642a37f18d68ffefe |
| app/cancel_state.py | 247 | f18724cee137035853f9c8367a0ed1bde2f72fc3b99ca671514eab2de982bb30 |
| app/cups_backend.py | 18078 | 051cd76a1c6c990f5036fc699639c0afb87ecfcfd94129986fff57c932fcd7ae |
| app/imposition.py | 26289 | f92951cd6822e9df2beec9db63988d10422ac8c38cbdd081cd21be5ae128913d |
| app/main.py | 90738 | 860a5dc96672502fa0d8832d0a146ed6b06cbfb9389fea2e61362711b0681207 |
| app/page_cache.py | 1112 | 2a64157ff63dda54132d0bbdfd13d0743baeeeee345134a5103e4131022808ab |
| app/pdf_dependency.py | 297 | dfa4ddc57d1dc286cdb61568128a84ae8ee22847a4efefd3744ba57952aef8f5 |
| app/pdf_panels.py | 3448 | f1071ebaeb9667da120becd11f3b2e7d4b1fbf04b8333756b177ff1e3e797114 |
| app/platform_runtime.py | 549 | 3b8b7d52cddbd6948ab0f49887b9fb5d490c1313c982ad6af22ecaa63399090c |
| app/presentation.py | 24225 | 223444cd91cca30e0711c62a834033925c4c5eba51e7a0d75f6e0592aab82966 |
| app/print_window.py | 75274 | 0aaa68041bc0ed02e9b847ad579ed16c8dafdde0e845be7fcb769a4f4c36e06a |
| app/rendering.py | 16350 | 8c1cb2d03c99d9ac894cb40fe3653053ac25f59d7f837e313f2d7b647b769215 |
| app/search_engine.py | 5017 | 62a812f5a8f199059d995beabc458aefbf045095431ecec9e6702c6761908b2e |
| app/style-dark.css | 3490 | 5d1acdf7c0a0ee1242c643d1abfe350777e3bc511b291902e90cf6cfca1d5c5f |
| app/style.css | 5651 | bc95dbf9da029803d6aff93008c81aae58712edf2bbfb9a52b82a640331f4bf5 |
| app/themes.py | 1661 | b7ad3f6607d65fb1f5248e832fa61b80c342be1788e54bc8407f325a148eee20 |
| app/version.py | 19 | 3b210eb5fcfda5fad14fab4619407bbaef43c5f2cb43f8981ecc9d6378b0e83e |
| app/windows_bootstrap.py | 1994 | 397d3124d4d6262833c201b83f62603dce854091119145050790a986fbe4e50f |
| app/windows_print.py | 4666 | 38f84d3c968fdf2193d0dc720391680552e868a040652ecbb598d56aac6232bd |
| app/worker_cli.py | 4476 | 25ba4c2c45c6f6514701db2ee35e5c789928ac8519cc0149b6a14292116fdac6 |


### Grupo biblioteca pypdf

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| app/vendor/pypdf/__init__.py | 1547 | 6c76122a654796c9dab1544ba56f15b7f752c21fec10197a10008d8250dabcf7 |
| app/vendor/pypdf/_cmap.py | 21559 | 10c18abb3d7b59feb940d8826a416f8baa49139ff390fd9ef88a825c89a8ee13 |
| app/vendor/pypdf/_codecs/__init__.py | 1569 | 9eb365f81a39b31289d0ecb755b524f122bbb9dcbde17323e791a2f37cebc754 |
| app/vendor/pypdf/_codecs/_codecs.py | 11001 | 64a97aa5b8dd1122e4546816492b40021a10b0bcb68752f992a441e9196dfec7 |
| app/vendor/pypdf/_codecs/adobe_glyphs.py | 594972 | 706cc2d4829b648feb50114d1d164734d19114ba9b2e980d78cca1c5fda62fe6 |
| app/vendor/pypdf/_codecs/core_font_metrics.py | 119459 | bf2e30a126daabddeb657be04ee020f5e479bee7d7d1c4ce8ec386dbdb52fc21 |
| app/vendor/pypdf/_codecs/pdfdoc.py | 4533 | b6fd76d7c43405e6a9de8d170d6d817e7728e71aea063f957b4f2d60d9fe5518 |
| app/vendor/pypdf/_codecs/std.py | 2888 | c5b6f97af74e23c32422fb49e1eb0719547d56930101eb5a6c9f13ae9e7be1f9 |
| app/vendor/pypdf/_codecs/symbol.py | 4923 | f9f29915e8d2be65b2e18f022b4b7d2be08442d59b634035dbb197a90f71fab8 |
| app/vendor/pypdf/_codecs/zapfding.py | 4936 | 2f7ac4c0b640046f365cf86f5dfeb49b4d7bdcde2a4a5512963f703ff33ecb9b |
| app/vendor/pypdf/_configuration.py | 11586 | 18ede031a2b52daf316cae71d04254599549941de1d92dbdf85f336476e09b3f |
| app/vendor/pypdf/_crypt_providers/__init__.py | 2850 | e66abfa3294bc2eefe825e729ddc30c96a6bf7d92114375f01baf8a723019233 |
| app/vendor/pypdf/_crypt_providers/_base.py | 1773 | 035134b8ceeb28eda0a6869b7c28102ea5afa7f8bfaace14e3a1d1d164b0b6d2 |
| app/vendor/pypdf/_crypt_providers/_cryptography.py | 7497 | 9906c2eb8f5f53e59cd0dcf10c1d013c2eaee18d2a8e90e9ff0c955a568101b0 |
| app/vendor/pypdf/_crypt_providers/_fallback.py | 3475 | 4565be0c1aaed8b320a881ac158aff809803e707186326db511b9ea7e6f1998f |
| app/vendor/pypdf/_crypt_providers/_pycryptodome.py | 4160 | 202a97d6b43a3f8dfd3a7f9202519f56fb291de97c1a2218cfba38bb56f5a5bc |
| app/vendor/pypdf/_doc_common.py | 65015 | 55d4fcf35d9706a1266037cae7e62c288a60c8de566bf5bb025c9b8c89fbafc1 |
| app/vendor/pypdf/_encryption.py | 54986 | e8f13f5a9011cb9995ea1106b8dcbf9442e8712154493da2ca8ba56d6bb4ea33 |
| app/vendor/pypdf/_page.py | 106614 | ada370d1fbb8aee74ed99af5e00d43e515003205636d019b448be84b182dfff9 |
| app/vendor/pypdf/_page_labels.py | 11737 | d78680c9085afe860a66dcae47281bd17912bd386e613b5e3fd8b08dd47155ca |
| app/vendor/pypdf/_protocols.py | 2487 | ada7e3dd2edf564eef67c6a3064317e715f41e336d324b71da6c3b23d77c6e4f |
| app/vendor/pypdf/_reader.py | 74193 | d6b89e14f51f1b4de0ce0b3f7156e091c551e3496f4fd960aa58eed41421546a |
| app/vendor/pypdf/_text_extraction/__init__.py | 11389 | cdc06c948455242349b6e9b552e4879bbb04ced705af9df55266bc238829ff4f |
| app/vendor/pypdf/_text_extraction/_layout_mode/__init__.py | 364 | af17011b14bbe33b80eae3326c354576c34df99286115f68e7be13464cbcb80e |
| app/vendor/pypdf/_text_extraction/_layout_mode/_fixed_width_page.py | 18740 | 84c6d5c90a2e6aeb174ca4d660fafc9010b5e44af38894edb1e055361ce78a42 |
| app/vendor/pypdf/_text_extraction/_layout_mode/_text_state_manager.py | 7773 | 314fb228078f9636085fe480af964e50c1ac8be3cf7a336dfd3b09932c012ce4 |
| app/vendor/pypdf/_text_extraction/_layout_mode/_text_state_params.py | 6784 | 9280407b13c80276615e8dfa8da570d157a82cd3c1d85df5927dd3cacdc7f3c3 |
| app/vendor/pypdf/_text_extraction/_text_extractor.py | 15659 | 403e3e69f3f36763295583ae4ad0015e54e8e071689025ca82a2909a3f6c59b4 |
| app/vendor/pypdf/_utils.py | 24353 | cff98445afa787c5e5f0f45988f2518c9674382c5f1a00dda380530384eeaeea |
| app/vendor/pypdf/_version.py | 24 | d4bfaa3a6977f97e181c7fdc9a471f49a7743edd2c567b33a115b6d31f232727 |
| app/vendor/pypdf/_writer.py | 144477 | 42ea7cb86c15cc52ce4fa1aa69e873c8f79813136b66944d213fe3d0def09e3c |
| app/vendor/pypdf/actions/__init__.py | 408 | b276bcbee52bdbd645a676edf3b127a07fdf1022288619769b6de6c4abde92a7 |
| app/vendor/pypdf/actions/_actions.py | 7865 | 9d3c64a9a6f7bc38947ad2632c73306d62ba8aaf3b0e95cc00f4649372f5bda5 |
| app/vendor/pypdf/annotations/__init__.py | 1032 | 50b233490fb74b08f564a346970b782194305d4777752625a4bcca4a9379467c |
| app/vendor/pypdf/annotations/_base.py | 990 | 444161daadfdb287afd8572ee1b97c3fcaa2ba9e27bf455ff7e60c6452bc0f73 |
| app/vendor/pypdf/annotations/_markup_annotations.py | 12209 | 10c39f6cf11c58ee7ce009873534108439e95e39f48a5f9c44530af23e5b1faf |
| app/vendor/pypdf/annotations/_non_markup_annotations.py | 3802 | ecce1881d7a52c8d479ea742ba53a3686fc62630e946feaea5cc1ac9f26d9629 |
| app/vendor/pypdf/constants.py | 25062 | 793a5fa1c82c9f7640bacd14e5314a92400b7ba5b54ed0f8eeaf36c18101c193 |
| app/vendor/pypdf/errors.py | 2021 | 175ba31f0a8848b64619f32a1c5c64aeeee6885e9f9e104bfc57712a45f77491 |
| app/vendor/pypdf/filters.py | 39462 | bde70425f2ca78d7e03a293bd5a165143e615de8356ac1090bd4612ed4396954 |
| app/vendor/pypdf/generic/__init__.py | 3583 | fac04b30e1f5958b87843eb9371861fd9419adbd1ca542c5debed459e7af86fc |
| app/vendor/pypdf/generic/_appearance_stream.py | 44742 | 8353c3845e81fcfb1f0b4a4b52e414e02a0415310a7264fbf4578d35ebb58cd5 |
| app/vendor/pypdf/generic/_base.py | 35287 | d590006bfbb3b911138dbb4479cc4f41b0ada5944abb80cb4ee146fa3d7ead9d |
| app/vendor/pypdf/generic/_color.py | 3277 | 5e1d5ac74b262f053b7074847a765b004c312c73a17fb607358235a9f690a2af |
| app/vendor/pypdf/generic/_data_structures.py | 74959 | bbf1fac615e3f7442a5c7f197fbaaf3869f50d788d2a734ec5e411721e8372f2 |
| app/vendor/pypdf/generic/_files.py | 19526 | 673084dea5a3ce84e059334995cd98737bcc842b45beab50d78dd9c9cf73f271 |
| app/vendor/pypdf/generic/_fit.py | 5725 | 552cfbf974b6c0107b25e1f9f2923e809452ce01aebab603c44dfc9d28819a49 |
| app/vendor/pypdf/generic/_font.py | 44593 | 9ea48bdc1f130c78335f339ddda8b696d34fc0bba6487f27a74b3e54f2fbf4c0 |
| app/vendor/pypdf/generic/_image_inline.py | 15523 | 4279d75bb16c0c07f1f3693e99f6306418cfb6fb3d1bbe8fed874d7b1dd4182a |
| app/vendor/pypdf/generic/_image_xobject.py | 28866 | d39b69503967b9ecfb8887a5a28e4f367c389583609490caeba1d660e19447e9 |
| app/vendor/pypdf/generic/_link.py | 6357 | 6528b1bc8524dc1ada0e21a7560c69933cdefeb8490b97857ee4ec5daf3f7fb5 |
| app/vendor/pypdf/generic/_outline.py | 1127 | 49e60093687082d53239e080ba91c711072467357a622d2f057ddb3bc802205d |
| app/vendor/pypdf/generic/_rectangle.py | 4104 | 83f95dadc428619a2c67301e01aac81046f6bb8ab34a74b4a34db8576054985b |
| app/vendor/pypdf/generic/_utils.py | 8100 | ca4dfff0f44bd06c45bda01190f5735de64f2ea4edf72f5e212c85a76ff52146 |
| app/vendor/pypdf/generic/_viewerpref.py | 7762 | e7cd14732e793be8f6989b7ad7448694a6895040cdf06d08473065ffb0c4c05d |
| app/vendor/pypdf/pagerange.py | 8127 | 8f1bd34643de3bcbc128050e08d7cf9cd327f63fb6b86ccac23d3cb7e3d1e12f |
| app/vendor/pypdf/papersizes.py | 1465 | 3022b9bec27680614f8bb4f5a3af7dbd544eb098e3fe7b7cb23671cac6627ef2 |
| app/vendor/pypdf/py.typed | 0 | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| app/vendor/pypdf/types.py | 1995 | 7a96fce15379a259c52a2cd95f348659ac0926bd1c1466c0269e516951c08015 |
| app/vendor/pypdf/xmp.py | 32957 | 430ec0b4e9cc180271b618e2950395a616da2315180ea1990e2aae24f35b8a2a |


### Grupo assets

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| assets/icons/128x128/apps/print-view-pdf.png | 6128 | a43e3dd528ea5d40d77af627d4f00a930d0160caf335814b32452c6d56757e88 |
| assets/icons/16x16/apps/print-view-pdf.png | 1331 | cb33a5bc3b6b193bf7e3a8ab4e9d744c0c2e7368d9bad4d7adff08ea70a6b497 |
| assets/icons/24x24/apps/print-view-pdf.png | 1531 | 6799fefc42e27a2410654d54d50393489fd7daa35093cd1f1bebcddc22ff8a21 |
| assets/icons/256x256/apps/print-view-pdf.png | 24389 | 8fd3a92efe48f42be2775898efe9d5ecff309e9680a9fc419f6abf27330267af |
| assets/icons/32x32/apps/print-view-pdf.png | 2066 | cfcdec58c6b329d8eda16a3b8b39d6354d880881136c2c5e9422fcc3cef1f046 |
| assets/icons/48x48/apps/print-view-pdf.png | 3241 | 7623a667b31271d674dacc1deeee99ac5853e32ec93a0a1251accd6b235bfaf9 |
| assets/icons/64x64/apps/print-view-pdf.png | 4596 | ea3da2277ef74dae6970568e8303288345b77900027c3781300d569efa4e0531 |
| assets/icons/scalable/apps/print-view-pdf.svg | 1996 | 5080d25a7476b648acde7328bbcb306fe7020f888ebc2442cfa968c10789988d |
| assets/print-view-pdf.desktop | 369 | 33d8ee1f4c86ab7febbf3a3a49f8bff65846ea7c2e7239db6a9078fb7f029bea |


### Grupo docs

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| docs/ANALISE.md | 8525 | 79091b465fa2087aea25ea7077ab172b53e9828e045a79ad771b7787cbb76b13 |
| docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md | 12779 | d392d7a733bb038a7893dc4eed4bd322313dfde12287441bb44104828ff266e8 |
| docs/ENTREGA-3.4.0.md | 5253 | 66ee0d14edb9a91fb6b9913b6bd4ab8ef3b3408469e07f7a069232924cfe1d48 |
| docs/PROVENIENCIA.md | 3857 | 72e661347e2243989c85655695b418b87dce481096d56158f01262e4d9090d5c |
| docs/REVISAO-HISTORICO-WINUX.md | 14907 | d7832d511b478adb5df5147c7f3ea67f63d26f8891bcf988e0dccbf3b1cd7f25 |
| docs/TESTAR-3.3.7.md | 3460 | 2cfc4edc6c1bde66e04fcfd992fd5197a8e1c59ff651c38c6885b482286cee61 |
| docs/TESTAR-TEST2.md | 2518 | a9f1af9bd77a92c0483e687edee272090a3989b0532381b80c29436c67b2fd1d |
| docs/cups-client-copyright.txt | 6918 | 1f086a33c33c9da37675cb72265f0bce6c1b678980bb6724ee21cf3d6e409779 |
| docs/historico-winux-manifest.json | 33305 | 45bcaac377413d2057a409bac1810e9ff1d3046084743acf899dbd8630d9e194 |
| docs/historico-winux-verificacao.json | 2849 | 2e093263a02f4c0a502cc303e30c076ec121b08f3427ff3660ed559655893906 |
| docs/pypdf-LICENSE.txt | 1634 | 9975270e8a2102d9ac408a96b35067e901de1f904256e2c2c9846697b317908e |
| docs/pypdf-artifact.json | 308 | 9abf9401f1fd2b091f6607dfb35f47f99b49b7dea130486ce850167812c7f8ed |
| docs/updf-downloader-pe.txt | 160243 | 64a50b517015aac3adaf01c2ceb2ba058705ae55655faba14fe725c08dff98db |
| docs/updf-installer-inventory.txt | 17664 | eac0fa0901e4647ec2abaad27b5c84a814a2debdfb6aeb4339f45d6a16314787 |
| docs/updf-installer-summary.json | 730 | cb6a04276e30f61bee590778d7f1b56596bf41d55df5104cd045747e8b7d0dbf |
| docs/updf-rea-artifact.json | 9178 | 01f53c20f9008c5e4e6ebaf3ee3323d1066e0f1b14456c488b3e9fba1ca4969d |
| docs/validacao-3.4.0.json | 3088 | 64c85f8e7b1264b72b9fbd16f5ef511c3bb37427f1d7e0387828b81c554e26c3 |
| docs/windows-smoke-3.4.0.json | 484 | d6e5ffd7ec3af609cfd8f4b98da062c266db2289e014d8b90c4d0c0695072465 |
| docs/winux-3.3.5-source-sha256.json | 6959 | 537030eef1c941aaf4c24f2fa663f0779a6cc2632c8a08281df12661cf69317c |


### Grupo evidências Windows

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| docs/windows-evidence/FoxitPDFReader-pe.json | 166759 | 00d5f3a687179e24e911b8ee6c1f5e31c0b3b02d18025a1b792b1ec9de608ef8 |
| docs/windows-evidence/PDFTextSearcher_FindNext.asm.txt | 2689 | caa9b20e163b7aeaef6a227ad36f2f3e684d66e3ac0f0e3d73d2c5893743a0f8 |
| docs/windows-evidence/PDFTextSearcher_FindPrev.asm.txt | 2689 | 4aff2322ff31ac67ad216d023a04d9b9e06c8a1c09516e9f9ece284342aa3b29 |
| docs/windows-evidence/PDFTextSearcher_GetBounds.asm.txt | 11037 | 4df6b90f94bf8a1f603b7fc35259ac9a6a1846c4e717bfa32c5ea205aae1bc4d |
| docs/windows-evidence/PDFTextSearcher_GetCurrentTextPageRotationAndBoundingBox.asm.txt | 3198 | cc283f4276055d22dcca083b7d77211442667217894be5d40c979b8b4e0bdce8 |
| docs/windows-evidence/PDFText_SelectAllQuads.asm.txt | 5288 | 0f6cded6c760df2657d34aa03d4d0793f55c69dcc2bdccf4aff9c0d003711b8a |
| docs/windows-evidence/UPDF-pe.json | 247194 | 89ad4c44a73efcbd4505ddf2c9f86018425630a46c20deef1bb1aeced8a1ef13 |
| docs/windows-evidence/UPDFKit-pe.json | 202941 | 9fd100247712c3cf0f12a43310323ae5fbc0dd2cba5e77275554ba17edfeb5ad |
| docs/windows-evidence/foxit-control-10388-0x0.asm.txt | 4685 | a58245a810e76402332964f9d8f44e90348c96cd5ea6edd6e8d03f8d5bced3e2 |
| docs/windows-evidence/foxit-control-10389-0x0.asm.txt | 4203 | be9885be31c5184229ddb89673372c17e6d2826f05ed2e4893ba9b376ffc875e |
| docs/windows-evidence/foxit-control-10394-0x0.asm.txt | 4478 | 2cddd90af02fe981ca5c98a4d59120403d985cace5bbf143c3c86e9e51726e57 |
| docs/windows-evidence/foxit-control-10399-0x1.asm.txt | 3897 | abd19301a37b15e902164d708433138987585f500930c07232a05b25101f72ae |
| docs/windows-evidence/foxit-control-10400-0x1.asm.txt | 4090 | 5eb0f7ba735a0f4ffa7b7d6897f2f2856f492ea3fbe6fb2baaad9079077dbeb8 |
| docs/windows-evidence/foxit-control-10424-0x0.asm.txt | 3987 | d8fa99b9953a73f59dfddf08fb3345aacc91800e9804fb3a05679392832711e7 |
| docs/windows-evidence/foxit-control-10427-0x0.asm.txt | 4344 | 38905e029046f6ca5089c80377780b4fe8250c119825ed220d9da028f3e818f1 |
| docs/windows-evidence/foxit-print-message-map.json | 1434 | 562d44321340befafc3f5b158a5bad56712c27af38bd4b81c953f1d69631f0b5 |
| docs/windows-evidence/foxit-rea-artifact.json | 6709 | b0be643b5cc6cd9f2955d6aa67164e8fbf58d8c9c72729854efa4501f8b8b01f |
| docs/windows-evidence/updf-rea-artifact.json | 6641 | bfc2efadfe7e1ffb0fa27e0cc6a33b15b30ea522af5f5a9c664e3a0117aea6ff |
| docs/windows-evidence/updf-selected-function-ranges.json | 1061 | aed8728b9270570e7ef180f43cea1d15c1d09b4fb08174b2af52fcaaa615fe50 |


### Grupo packages

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| packages/PrintViewPDF-3.4.0-Setup-x64.exe | 67017156 | 2ee91c8828db0d246c5129bded8a47825fa681daf1b575f80bf4dd99989ab43e |
| packages/PrintViewPDF-3.4.0-x86_64.flatpak | 43197720 | 7f5926f32a5034677d6c26e947029e8359d511f29cdfbacc9afd27d1a38b7b08 |
| packages/SHA256SUMS | 603 | 522266ad8287f47913d69a4e6e0a608fc58073ed59b0f442e1ce8d417b7c9c97 |
| packages/print-view-pdf_3.3.7~test1_all.deb | 330748 | f12e476cf114eff9588dad3cfb5427376a0a5d06eddc57555472b6cd428c1bab |
| packages/print-view-pdf_3.3.7~test2_all.deb | 333884 | 534d7ccf6168c4529cbb4dcead7b4b08aee58a188cca1093e4be0f9eb204abb0 |
| packages/print-view-pdf_3.4.0_all.deb | 389952 | 229023b13486d51df93170a70623fedbb2dd2ff7fd188044e1bf7224c5c86273 |
| packages/print-view-pdf_3.4.0_source.tar.gz | 684912 | 5d1858a527d741c303617e391c055d7d224011075cf358fb172c3a5932772fb2 |


### Grupo packaging

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| packaging/io.github.airtonbp19edu.PrintViewPDF.metainfo.xml | 1465 | 4714915a5eb8ff5c188ced122a22a4ed7ee47bd6654eb6fcc8097a609e0fa3af |
| packaging/windows-artifacts.json | 1949 | 6597023355e655de16d993a8c772b2f67eb6db6b3cac984ccdca5fd31aac39c8 |
| packaging/windows-installer.nsi | 2115 | 8b6ac9250e45fdf5e3f16514cbcffd90120cd9f41299b82bd00c8ea2732462bb |
| packaging/windows-launcher.nsi | 619 | 1b3b02d2d9e794661452f72c4fc905f2411e9d88fce7b9a1e0b21b93a6b6496e |


### Grupo scripts

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| scripts/analyze_windows_readers.py | 9274 | c29ed42556854242d72ccbb183197c719907203462536e94ad8e4da08ba97b89 |
| scripts/build_deb.py | 4000 | 01419a7939f10bb6b10d248ee9ece1dda05941e52bd1bcd1ccaffb23f832251f |
| scripts/build_flatpak.py | 9320 | 7d20a89f7c43c0d9fca5bac212c344d19064717e24e3f15d29d3056e7123007c |
| scripts/build_windows.py | 5098 | a907ee5a6a5e7a687988d73e858077b1fae0def8552839e4afc5ae218da3824d |
| scripts/headless-xorg.conf | 430 | 78a38c757428862df1bb50f3e2674082f50b5bae3052ab2bd0c24f1c35757f1a |
| scripts/run.sh | 165 | 0cfb2cdbff7d408786731dbedea249da57f4b01a6ded5cfa4b89cceb4b01df39 |
| scripts/setup-cloud.sh | 1870 | 5459521030987cb9c2af5747f28c762f982317609fd8a9b3592dae3d3431611b |
| scripts/smoke_windows.py | 2611 | 75c3b323f24230934dca627b4ba8011923a2f0c9bdc1dbe3a86ee8d6e2ed022e |
| scripts/verify_winux_history.py | 10502 | 3d415210eacab9257f065fe0e4c60b84c40c555c406e50433c4272ce58566002 |


### Grupo tests

| Arquivo | Bytes | SHA-256 local |
| --- | --- | --- |
| tests/test_consolidation.py | 1874 | 07b2ef891c65c1252edddd2d0c0efbdadb2a376e417d2ec42ca51d8e87c8eec6 |
| tests/test_gui.py | 6548 | 22d7b311ce206ce811a573869ae9e58c259d1863757c8cc3ff9f4f2f41527000 |
| tests/test_regressions.py | 6031 | 9e3e301d2259606ba12a67cd390305a9d6eb5c01690d259314e3e0b056ec4736 |
| tests/test_search.py | 2787 | 2559d07fcff0f21905b860346227459415db3c44e7f8f483b2de66a13d8dd51b |
| tests/test_viewer.py | 9532 | 486ff402f385e37168e3f4323de8432a602f31249975af0d4fc8dcd3c2c29dfe |


## Anexo J Histórico de arquivos por commit

Este registro identifica em qual commit cada caminho foi acrescentado ou modificado. Não corresponde a apontamento de horas e inclui alterações de biblioteca de terceiros.


````text
COMMIT f7653415988dd681371edd5e73e900eaf0d06b1c
DATA 2026-10-13T19:44:46-03:00
ASSUNTO Initial commit

A	LICENSE
A	README.md
COMMIT 15260c29b87b390d5f1e35d6a8c7b55b616fd6de
DATA 2026-10-14T00:37:46Z
ASSUNTO feat: restore Winux base and improve PDF word search

A	.gitignore
M	README.md
A	app/async_core.py
A	app/cups_backend.py
A	app/imposition.py
A	app/main.py
A	app/pdf_panels.py
A	app/presentation.py
A	app/print_window.py
A	app/rendering.py
A	app/search_engine.py
A	app/style.css
A	app/vendor/pypdf/__init__.py
A	app/vendor/pypdf/_cmap.py
A	app/vendor/pypdf/_codecs/__init__.py
A	app/vendor/pypdf/_codecs/_codecs.py
A	app/vendor/pypdf/_codecs/adobe_glyphs.py
A	app/vendor/pypdf/_codecs/core_font_metrics.py
A	app/vendor/pypdf/_codecs/pdfdoc.py
A	app/vendor/pypdf/_codecs/std.py
A	app/vendor/pypdf/_codecs/symbol.py
A	app/vendor/pypdf/_codecs/zapfding.py
A	app/vendor/pypdf/_crypt_providers/__init__.py
A	app/vendor/pypdf/_crypt_providers/_base.py
A	app/vendor/pypdf/_crypt_providers/_cryptography.py
A	app/vendor/pypdf/_crypt_providers/_fallback.py
A	app/vendor/pypdf/_crypt_providers/_pycryptodome.py
A	app/vendor/pypdf/_doc_common.py
A	app/vendor/pypdf/_encryption.py
A	app/vendor/pypdf/_font.py
A	app/vendor/pypdf/_page.py
A	app/vendor/pypdf/_page_labels.py
A	app/vendor/pypdf/_protocols.py
A	app/vendor/pypdf/_reader.py
A	app/vendor/pypdf/_text_extraction/__init__.py
A	app/vendor/pypdf/_text_extraction/_layout_mode/__init__.py
A	app/vendor/pypdf/_text_extraction/_layout_mode/_fixed_width_page.py
A	app/vendor/pypdf/_text_extraction/_layout_mode/_text_state_manager.py
A	app/vendor/pypdf/_text_extraction/_layout_mode/_text_state_params.py
A	app/vendor/pypdf/_text_extraction/_text_extractor.py
A	app/vendor/pypdf/_utils.py
A	app/vendor/pypdf/_version.py
A	app/vendor/pypdf/_writer.py
A	app/vendor/pypdf/annotations/__init__.py
A	app/vendor/pypdf/annotations/_base.py
A	app/vendor/pypdf/annotations/_markup_annotations.py
A	app/vendor/pypdf/annotations/_non_markup_annotations.py
A	app/vendor/pypdf/constants.py
A	app/vendor/pypdf/errors.py
A	app/vendor/pypdf/filters.py
A	app/vendor/pypdf/generic/__init__.py
A	app/vendor/pypdf/generic/_appearance_stream.py
A	app/vendor/pypdf/generic/_base.py
A	app/vendor/pypdf/generic/_data_structures.py
A	app/vendor/pypdf/generic/_files.py
A	app/vendor/pypdf/generic/_fit.py
A	app/vendor/pypdf/generic/_image_inline.py
A	app/vendor/pypdf/generic/_image_xobject.py
A	app/vendor/pypdf/generic/_link.py
A	app/vendor/pypdf/generic/_outline.py
A	app/vendor/pypdf/generic/_rectangle.py
A	app/vendor/pypdf/generic/_utils.py
A	app/vendor/pypdf/generic/_viewerpref.py
A	app/vendor/pypdf/pagerange.py
A	app/vendor/pypdf/papersizes.py
A	app/vendor/pypdf/py.typed
A	app/vendor/pypdf/types.py
A	app/vendor/pypdf/xmp.py
A	app/worker_cli.py
A	assets/icons/128x128/apps/print-view-pdf.png
A	assets/icons/16x16/apps/print-view-pdf.png
A	assets/icons/24x24/apps/print-view-pdf.png
A	assets/icons/256x256/apps/print-view-pdf.png
A	assets/icons/32x32/apps/print-view-pdf.png
A	assets/icons/48x48/apps/print-view-pdf.png
A	assets/icons/64x64/apps/print-view-pdf.png
A	assets/icons/scalable/apps/print-view-pdf.svg
A	assets/print-view-pdf.desktop
A	docs/ANALISE.md
A	docs/ENGENHARIA-REVERSA-FOXIT-UPDF.md
A	docs/PROVENIENCIA.md
A	docs/TESTAR-3.3.7.md
A	docs/pypdf-LICENSE.txt
A	docs/updf-downloader-pe.txt
A	docs/updf-installer-inventory.txt
A	docs/updf-installer-summary.json
A	docs/updf-rea-artifact.json
A	docs/windows-evidence/FoxitPDFReader-pe.json
A	docs/windows-evidence/PDFTextSearcher_FindNext.asm.txt
A	docs/windows-evidence/PDFTextSearcher_FindPrev.asm.txt
A	docs/windows-evidence/PDFTextSearcher_GetBounds.asm.txt
A	docs/windows-evidence/PDFTextSearcher_GetCurrentTextPageRotationAndBoundingBox.asm.txt
A	docs/windows-evidence/PDFText_SelectAllQuads.asm.txt
A	docs/windows-evidence/UPDF-pe.json
A	docs/windows-evidence/UPDFKit-pe.json
A	docs/windows-evidence/foxit-control-10388-0x0.asm.txt
A	docs/windows-evidence/foxit-control-10389-0x0.asm.txt
A	docs/windows-evidence/foxit-control-10394-0x0.asm.txt
A	docs/windows-evidence/foxit-control-10399-0x1.asm.txt
A	docs/windows-evidence/foxit-control-10400-0x1.asm.txt
A	docs/windows-evidence/foxit-control-10424-0x0.asm.txt
A	docs/windows-evidence/foxit-control-10427-0x0.asm.txt
A	docs/windows-evidence/foxit-print-message-map.json
A	docs/windows-evidence/foxit-rea-artifact.json
A	docs/windows-evidence/updf-rea-artifact.json
A	docs/windows-evidence/updf-selected-function-ranges.json
A	docs/winux-3.3.5-source-sha256.json
A	packages/SHA256SUMS
A	packages/print-view-pdf_3.3.7~test1_all.deb
A	scripts/analyze_windows_readers.py
A	scripts/build_deb.py
A	scripts/headless-xorg.conf
A	scripts/run.sh
A	scripts/setup-cloud.sh
A	tests/test_gui.py
A	tests/test_regressions.py
A	tests/test_search.py
COMMIT e4fbdad068bdf7dd57c22ca11f3fae54d81220ba
DATA 2026-10-14T01:06:53Z
ASSUNTO fix: improve presentation framing themes and page navigation

M	README.md
M	app/async_core.py
M	app/main.py
A	app/page_cache.py
M	app/presentation.py
A	app/themes.py
A	docs/TESTAR-TEST2.md
M	packages/SHA256SUMS
A	packages/print-view-pdf_3.3.7~test2_all.deb
M	scripts/build_deb.py
A	tests/test_viewer.py
COMMIT 597df84df5ed41b4103d8c01ec09dfbec7c60aa9
DATA 2026-10-14T02:33:32Z
ASSUNTO Audit Winux history through 3.3.11 and document migration gaps

M	README.md
M	docs/PROVENIENCIA.md
A	docs/REVISAO-HISTORICO-WINUX.md
A	docs/historico-winux-manifest.json
A	docs/historico-winux-verificacao.json
A	scripts/verify_winux_history.py
COMMIT e01c947e63a34887094a1ef7a3f877309a580bdb
DATA 2026-10-14T03:22:20Z
ASSUNTO Release Print&View PDF 3.4.0 for Debian, Flatpak and Windows

M	README.md
A	app/appearance.py
M	app/async_core.py
A	app/cancel_state.py
M	app/cups_backend.py
M	app/imposition.py
M	app/main.py
A	app/pdf_dependency.py
A	app/platform_runtime.py
M	app/presentation.py
M	app/print_window.py
M	app/rendering.py
M	app/search_engine.py
A	app/style-dark.css
M	app/themes.py
M	app/vendor/pypdf/__init__.py
M	app/vendor/pypdf/_cmap.py
M	app/vendor/pypdf/_codecs/__init__.py
M	app/vendor/pypdf/_codecs/_codecs.py
M	app/vendor/pypdf/_codecs/adobe_glyphs.py
M	app/vendor/pypdf/_codecs/core_font_metrics.py
M	app/vendor/pypdf/_codecs/symbol.py
M	app/vendor/pypdf/_codecs/zapfding.py
A	app/vendor/pypdf/_configuration.py
M	app/vendor/pypdf/_crypt_providers/__init__.py
M	app/vendor/pypdf/_crypt_providers/_base.py
M	app/vendor/pypdf/_crypt_providers/_cryptography.py
M	app/vendor/pypdf/_crypt_providers/_fallback.py
M	app/vendor/pypdf/_crypt_providers/_pycryptodome.py
M	app/vendor/pypdf/_doc_common.py
M	app/vendor/pypdf/_encryption.py
D	app/vendor/pypdf/_font.py
M	app/vendor/pypdf/_page.py
M	app/vendor/pypdf/_page_labels.py
M	app/vendor/pypdf/_protocols.py
M	app/vendor/pypdf/_reader.py
M	app/vendor/pypdf/_text_extraction/__init__.py
M	app/vendor/pypdf/_text_extraction/_layout_mode/__init__.py
M	app/vendor/pypdf/_text_extraction/_layout_mode/_fixed_width_page.py
M	app/vendor/pypdf/_text_extraction/_layout_mode/_text_state_manager.py
M	app/vendor/pypdf/_text_extraction/_layout_mode/_text_state_params.py
M	app/vendor/pypdf/_text_extraction/_text_extractor.py
M	app/vendor/pypdf/_utils.py
M	app/vendor/pypdf/_version.py
M	app/vendor/pypdf/_writer.py
A	app/vendor/pypdf/actions/__init__.py
A	app/vendor/pypdf/actions/_actions.py
M	app/vendor/pypdf/annotations/_base.py
M	app/vendor/pypdf/annotations/_markup_annotations.py
M	app/vendor/pypdf/annotations/_non_markup_annotations.py
M	app/vendor/pypdf/constants.py
M	app/vendor/pypdf/filters.py
M	app/vendor/pypdf/generic/_appearance_stream.py
M	app/vendor/pypdf/generic/_base.py
A	app/vendor/pypdf/generic/_color.py
M	app/vendor/pypdf/generic/_data_structures.py
M	app/vendor/pypdf/generic/_files.py
M	app/vendor/pypdf/generic/_fit.py
A	app/vendor/pypdf/generic/_font.py
M	app/vendor/pypdf/generic/_image_inline.py
M	app/vendor/pypdf/generic/_image_xobject.py
M	app/vendor/pypdf/generic/_link.py
M	app/vendor/pypdf/generic/_outline.py
M	app/vendor/pypdf/generic/_rectangle.py
M	app/vendor/pypdf/generic/_utils.py
M	app/vendor/pypdf/generic/_viewerpref.py
M	app/vendor/pypdf/pagerange.py
M	app/vendor/pypdf/xmp.py
A	app/version.py
A	app/windows_bootstrap.py
A	app/windows_print.py
M	app/worker_cli.py
M	docs/ANALISE.md
A	docs/ENTREGA-3.4.0.md
M	docs/PROVENIENCIA.md
M	docs/REVISAO-HISTORICO-WINUX.md
A	docs/cups-client-copyright.txt
A	docs/pypdf-artifact.json
A	docs/validacao-3.4.0.json
A	docs/windows-smoke-3.4.0.json
A	packages/PrintViewPDF-3.4.0-Setup-x64.exe
A	packages/PrintViewPDF-3.4.0-x86_64.flatpak
M	packages/SHA256SUMS
A	packages/print-view-pdf_3.4.0_all.deb
A	packages/print-view-pdf_3.4.0_source.tar.gz
A	packaging/io.github.airtonbp19edu.PrintViewPDF.metainfo.xml
A	packaging/windows-artifacts.json
A	packaging/windows-installer.nsi
A	packaging/windows-launcher.nsi
M	scripts/build_deb.py
A	scripts/build_flatpak.py
A	scripts/build_windows.py
A	scripts/smoke_windows.py
A	tests/test_consolidation.py
M	tests/test_gui.py
M	tests/test_viewer.py
````


## Anexo K Ferramentas encontradas no PATH da sessão atual

Consulta somente de localização. Não foi testada a execução destas ferramentas, uma distribuição WSL nem instalações em outros diretórios. Ausência no PATH não significa ausência em toda a máquina.


| Ferramenta | Localização encontrada |
| --- | --- |
| dpkg-deb | Não encontrada no PATH desta sessão |
| flatpak | Não encontrada no PATH desta sessão |
| makensis | Não encontrada no PATH desta sessão |
| pdftocairo | Não encontrada no PATH desta sessão |
| pdftotext | Não encontrada no PATH desta sessão |
| pdfinfo | C:\Users\Airtonbp19\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdfinfo.EXE |
| pdfunite | Não encontrada no PATH desta sessão |
| wsl | C:\WINDOWS\system32\wsl.EXE |
| bash | Não encontrada no PATH desta sessão |
| 7z | Não encontrada no PATH desta sessão |


## Anexo L Registro das conferências realizadas nesta elaboração

- Leitura do estado Git e dos cinco commits locais.
- Inventário dos 156 arquivos rastreados, tamanhos e hashes.
- Leitura dos oito documentos narrativos e dos registros de validação e proveniência.
- Inventário sintático dos módulos e dos 27 métodos de teste, sem importar ou executar a aplicação.
- Recálculo SHA-256 dos seis artefatos com seis correspondências.
- Comparação normalizada dos 19 módulos próprios com o registro da entrega, com 19 correspondências.
- Comparação normalizada de 81 arquivos de app no Debian e 81 no tarball de fontes, sem diferenças de conteúdo.
- Consulta de localização de ferramentas no PATH.
- Elaboração do roteiro, dos 57 itens de continuidade e dos critérios de encerramento.

Não houve build, instalação, impressão, teste funcional novo ou mudança em código de aplicação nesta solicitação. Os únicos arquivos de entrega adicionados a este checkout são este relatório em HTML e sua versão Markdown.

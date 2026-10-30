# Print&View PDF 3.4.1 para Linux

## Resultado da entrega em 30/10/2026

Foram gerados os pacotes Linux com a central de preferências e validados em Debian 13.7 x86_64. O Debian foi instalado com apt; o Flatpak foi instalado com o runtime org.freedesktop.Platform/x86_64/25.08 e testado dentro do sandbox real. A distribuição atual está na [release v3.4.1](https://github.com/airtonbp19edu/Print-and-View-PDF/releases/tag/v3.4.1).

| Artefato em packages/ | Tamanho | SHA-256 |
|---|---:|---|
| print-view-pdf_3.4.1_all.deb | 399,144 bytes | `314ff46abc57bd960f5641b648e1ccdd1ddb33f208fa15cf16514196cbec0bc8` |
| PrintViewPDF-3.4.1-x86_64.flatpak | 35,282,912 bytes | `7da8257e04643028d49aabea4fc4a17feec4d786984b5fff51b4e4b8e3833a96` |

Os seis artefatos anteriores foram preservados e seus hashes foram recalculados com sucesso. SHA256SUMS contém os seis anteriores e estes dois novos arquivos. O instalador Windows disponível continua na versão 3.4.0.

## Código e funcionalidades incluídos

A versão inclui a primeira central funcional de Aparência, Interface, Leitura e Busca, acessível pela engrenagem, Arquivo → Preferências ou Ctrl+,. Ela permite prévia de tema, Aplicar, Cancelar, Salvar e fechar e restauração dos padrões por seção. Cancelar restaura o último estado aplicado; uma falha ao gravar conserva o diálogo aberto.

Os padrões de interface incluem painéis e tamanho de janela. Os padrões de leitura incluem ajuste de página/largura, zoom de 25% a 400% e memória opcional de página, zoom e rotação por documento. Essa memória é limitada a 50 arquivos, não altera o PDF e invalida entradas quando tamanho ou data de modificação mudam. A posição de rolagem dentro da página ainda não é lembrada.

As opções da busca também são persistidas quando alteradas pela barra. O JSON preserva chaves desconhecidas, migra o tema antigo e usa substituição atômica. A sincronização dos botões laterais bloqueia callbacks recursivos. O lote corresponde a PV-CFG-01 a PV-CFG-04; o escopo completo está em [PREFERENCIAS-PRIMEIRA-IMPLEMENTACAO](PREFERENCIAS-PRIMEIRA-IMPLEMENTACAO.md).

## Testes realmente executados nesta entrega

| Contexto | Executados | Aprovados | Falhas/erros | Ignorados | Tempo medido |
|---|---:|---:|---:|---:|---:|
| Fonte Linux | 41 | 40 | 0 | 1 | 33.325 s |
| .deb realmente instalado | 41 | 40 | 0 | 1 | 52.126 s |
| Flatpak dentro do sandbox real | 41 | 40 | 0 | 1 | 66.364 s |

O caso ignorado verifica um detalhe de propriedade de caches específico do Windows. Os outros 40 incluem os 13 testes de preferências aplicáveis ao Linux e os 27 testes anteriores. Estes são os mesmos casos executados em três contextos; não são 120 casos distintos. Os limites de espera e os testes de desempenho da suíte anterior foram mantidos.

A validação inclui persistência, migração, JSON inválido, gravação atômica, falha de disco simulada, prévia/Cancelamento do tema, Aplicar seguido de Cancelar, memória e isolamento entre PDFs, busca progressiva, seleção, rotação, cache, apresentação e geração de layouts de impressão. Os testes de impressão usam documentos e preparação reais, além de mocks onde indicado no próprio teste; não enviaram folhas a uma impressora física.

Foram comparados por SHA-256 os 83 arquivos da aplicação na fonte local, na cópia Linux, no Debian instalado e no Flatpak instalado: todos correspondem. Também foram comparados os 2973 arquivos do payload Flatpak com os arquivos implantados: nenhuma diferença. O contexto do sandbox foi registrado a partir de /.flatpak-info, com o aplicativo 3.4.1, o runtime e o interpretador /app/bin/print-view-python.

As quatro telas foram renderizadas a partir dos widgets GTK reais e inspecionadas visualmente. Não são mockups. A sessão usa X11 virtual por Xvfb, sem certificar um desktop físico ou Wayland.

Os lançadores padrão `/usr/bin/print-view-pdf` e `flatpak run --user io.github.airtonbp19edu.PrintViewPDF` também passaram por um smoke de inicialização: permaneceram ativos por cinco segundos, sem erros de inicialização, e foram encerrados pelo teste. [Resultado](validation/3.4.1/linux-launcher-smoke-3.4.1.json).

## Falhas encontradas e corrigidas no Flatpak

O primeiro candidato gerava erro `/bin/sh: undefined symbol: rl_full_quoting_desired`. As bibliotecas Debian estavam na busca global de /app/lib e interferiam no shell do Freedesktop. O empacotador passou a colocá-las em /app/lib/print-view-runtime e a usar o carregador ELF correspondente, sem exportar LD_LIBRARY_PATH globalmente. O parâmetro --argv0 mantém o wrapper como sys.executable para que os subprocessos usem o mesmo carregador.

Com isso, o sandbox passou a abrir Python/GTK, mas revelou a falta do provedor legacy do OpenSSL. O segundo candidato teve 40 itens, 14 falhas, 2 erros e 1 ignorado; um módulo de testes não chegou a ser importado. A falha de cryptography/pypdf impedia os processos auxiliares de abrir PDFs, e vários testes gráficos acabavam em timeout.

Foi incluído o provedor correspondente à libcrypto empacotada e definido OPENSSL_MODULES. Não foi usado CRYPTOGRAPHY_OPENSSL_NO_LEGACY. A importação em subprocessos e uma operação de cifra legada foram exercitadas com sucesso. A execução final dos 41 casos ficou sem falhas ou erros. Os logs e o JSON das tentativas anteriores foram mantidos com nomes distintos; somente o candidato final aprovado permanece em packages/.

## Por que houve demora

O computador não tinha WSL instalado na verificação inicial. Foi necessário preparar um ambiente Linux próprio: baixar a imagem oficial Debian, conferir seu SHA-512, extrair o disco, criar uma VM de 2 CPUs/3 GiB e instalar as dependências de GTK, Poppler, CUPS, Xvfb e Flatpak. A instalação inicial envolveu 178 novos pacotes, seguida de quatro componentes para carregamento de imagens SVG. Os registros de apt documentam início e fim das instalações.

O VirtualBox registrou o backend NEM e “Snail execution mode is active”, em vez do acesso direto a VT-x. A configuração inicial também gerou caches e uma nova imagem de inicialização Linux. Duas consultas SSH excederam o orçamento inicial enquanto compactação e download do runtime estavam ativos; a consulta foi repetida com um orçamento maior.

Depois da preparação vieram duas correções reais do empacotamento Flatpak e novas construções. Validar somente a fonte ou executar o payload fora do sandbox não teria detectado essas incompatibilidades. Os tempos medidos das suítes estão na tabela; o intervalo de parede entre mensagens e retomadas não deve ser confundido com tempo de compilação.

## Arquivos de evidência

- [Resumo estruturado da entrega](validation/3.4.1/LINUX-3.4.1-ENTREGA-2026-10-30.json).
- [Testes da fonte](validation/3.4.1/linux-source-3.4.1.json) e [log completo](validation/3.4.1/linux-source-3.4.1.log).
- [Testes do Debian instalado](validation/3.4.1/linux-deb-tests-3.4.1.json) e [log completo](validation/3.4.1/linux-deb-tests-3.4.1.log).
- [Testes finais do sandbox](validation/3.4.1/linux-flatpak-sandbox-tests-3.4.1.json) e [log completo](validation/3.4.1/linux-flatpak-sandbox-tests-3.4.1.log).
- [Identidade dos arquivos instalados](validation/3.4.1/linux-payload-verification-3.4.1.json) e [contexto do sandbox](validation/3.4.1/linux-flatpak-sandbox-context-3.4.1.json).
- [Histórico da instalação de dependências](validation/3.4.1/debian-build-apt-history-3.4.1.txt) e [versões instaladas](validation/3.4.1/debian-build-packages-3.4.1.txt).
- [Primeira falha do sandbox](validation/3.4.1/linux-flatpak-sandbox-initial-failure-3.4.1.log) e [falhas antes da inclusão do provedor OpenSSL](validation/3.4.1/linux-flatpak-sandbox-before-crypto-fix-3.4.1.json).
- [Aparência](screenshots/linux-preferences-appearance-3.4.1.png), [Interface](screenshots/linux-preferences-interface-3.4.1.png), [Leitura](screenshots/linux-preferences-reading-3.4.1.png) e [Busca](screenshots/linux-preferences-search-3.4.1.png).

Os arquivos incluídos nos pacotes preservam o registro da fonte antes da validação pós-instalação. Este relatório externo consolida os resultados finais dos instaladores.

## Instalação

```bash
sudo apt install ./print-view-pdf_3.4.1_all.deb
```

```bash
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user flathub org.freedesktop.Platform//25.08
flatpak install --user ./PrintViewPDF-3.4.1-x86_64.flatpak
flatpak run io.github.airtonbp19edu.PrintViewPDF
```

## Limites e pendências que esta entrega não fecha

Continuam sem validação nesta entrega: impressão física, integração com desktop/Wayland, outras distribuições, documentos grandes de uso real, novo instalador Windows e desempenho da regressão completa no Windows. A tentativa Windows anterior permanece registrada separadamente; a aprovação Linux não a substitui.

Os outros lotes do guia Linuxit, presets de impressão, preferências adicionais de apresentação/exportação, OCR, edição e seleção precisa por caracteres não foram implementados por este build. Não há alegação de equivalência integral com Foxit. Os pacotes são distribuídos pela [release GitHub v3.4.1](https://github.com/airtonbp19edu/Print-and-View-PDF/releases/tag/v3.4.1). Não há publicação no Flathub.

O ambiente dedicado de build foi desligado após a validação. Configurações e discos locais não fazem parte da publicação.

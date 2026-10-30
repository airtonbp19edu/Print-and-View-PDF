# Primeira implementação da central de preferências

> Registro da primeira rodada de implementação e da prévia Windows. A entrega Linux posterior, com .deb e Flatpak 3.4.1 e os testes do sandbox, está em [ENTREGA-3.4.1-LINUX](ENTREGA-3.4.1-LINUX.md). As menções abaixo a Linux pendente descrevem a rodada Windows anterior.

Implementação de desenvolvimento em 30/10/2026, correspondente ao primeiro lote PV-CFG-01 a PV-CFG-04 do guia do Linuxit. O código da aplicação fica no Print&View; a fonte Linuxit não foi alterada.

## Como ver a interface

No Windows com o PrintViewPDF instalado nesta máquina, execute `scripts/preview-preferences.cmd`. O lançador abre a fonte em desenvolvimento com o runtime instalado, usando um perfil separado em `.runtime/preferences-preview`. A instalação normal e suas preferências não são substituídas. Se necessário, defina PRINT_VIEW_RUNTIME com a pasta que contém python/, gtk/ e poppler/.

Para executar com Python/GTK já preparados no Linux, use:

```bash
python3 scripts/preview_preferences.py
```

Na aplicação executada a partir da fonte, abra **Arquivo → Preferências**, use o botão de engrenagem ou **Ctrl+,**. O botão também funciona sem um PDF aberto.

## O que está ligado ao aplicativo

- Aparência: tema do sistema, claro e escuro, com prévia imediata. Cancelar restaura o último tema aplicado, sem salvar a prévia.
- Interface: painel lateral, faixa de comandos e opção de lembrar seu estado e o tamanho da janela no fechamento.
- Leitura: ajustar página, ajustar largura ou zoom de 25% a 400%. O padrão vale para a próxima abertura de PDF.
- Memória por documento, opcional e desligada por padrão: página, zoom e rotação de até 50 arquivos. O estado é invalidado se tamanho ou data de modificação mudar; o arquivo PDF não é editado. A posição de rolagem dentro da página ainda não é lembrada.
- Busca: caixa, palavra inteira, acentos, hifenização e abertura do painel de resultados. As opções da barra também são persistidas. Aplicar novos padrões reinicia uma consulta ativa e invalida resultados antigos.
- Restaurar padrões por seção modifica o rascunho. Aplicar salva e mantém a janela aberta. Salvar e fechar salva e fecha. Cancelar descarta somente mudanças posteriores ao último Aplicar.
- A gravação central preserva chaves desconhecidas e registros de documentos e usa arquivo temporário seguido de substituição atômica. Valores inválidos usam padrões; falha de gravação mantém a janela e o rascunho disponíveis.
- Compatibilidade com o JSON de tema anterior e migração da preferência Winux foram preservadas.

## Validação

O resultado final desta rodada está em `validation/3.4.1/preferencias-validacao-2026-10-30.json`. As imagens em docs/screenshots/ são renderizações dos widgets GTK reais; não são um desenho conceitual em HTML.

Uma falha anterior da limpeza de caches usava os.getuid no Windows e foi encontrada ao abrir janelas nos testes. Agora a limpeza de diretórios antigos é ignorada quando não há identidade POSIX para conferir o proprietário; o cache da própria sessão continua sendo removido no fechamento.

## Limites desta entrega

Este é o primeiro lote funcional para avaliação. Presets de impressão, preferências de apresentação, exportação, OCR, edição de PDF e os demais lotes do guia continuam fora desta implementação. Os instaladores antigos em packages/ não contêm estas alterações. Nenhuma release ou atualização da instalação normal foi produzida.

As preferências pertencem ao perfil do aplicativo, não ao PDF. A aprovação dos testes próprios não estabelece equivalência integral com Foxit nem substitui validação Linux/Flatpak ou impressão física.

## Resultado final da rodada em Windows

- **14/14 testes novos aprovados**, zero falhas, erros ou pulos, na fonte final. Incluem 8 testes de persistência e 6 de integração GTK/Windows. O teste de retorno aos documentos usa PDFs reais e Poppler. O conjunto final também captura exceções de callbacks GTK, para não aceitar um erro somente impresso no console como sucesso.
- Foram conferidos prévia/Cancelamento do tema, Aplicar seguido de Cancelar, valores inválidos, falha de gravação, migração, chaves de versões futuras, limites de histórico e isolamento de arquivos.
- A seleção programática dos botões laterais agora bloqueia os callbacks durante a sincronização: isso evita recursão ao ocultar o painel pelas preferências.
- Sintaxe dos arquivos Python alterados conferida; `git diff --check` sem erros.
- A suíte completa foi tentada na iteração anterior à última correção dos callbacks: **41 casos, 27 aprovados, 13 falhas e 1 erro**. Os treze casos gráficos pararam em `GTK readiness timeout` no setUp (orçamento de 12 segundos); o caso de tema novo em subprocesso excedeu cinco segundos. Seus cenários posteriores não foram validados por essa execução. O arquivo `preferencias-regressao-windows-2026-10-30.json` preserva esses resultados e a identidade daquela fonte.
- A validação final focada usou até 60 segundos para aguardar operações de abertura/renderização, sem declarar uma meta de desempenho. As métricas de velocidade dos testes antigos não foram relaxadas nem declaradas aprovadas.
- Linux e Flatpak não foram executados nesta rodada. A suíte de regressão integral e o desempenho de inicialização continuam pendentes de investigação antes de uma release.

Os hashes dos módulos Python da fonte final foram conferidos contra o relatório dos 14 testes, após a execução. Esta rodada entrega uma prévia de desenvolvimento, não uma atualização dos instaladores 3.4.0.

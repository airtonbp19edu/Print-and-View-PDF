# Evidências da versão 3.4.1

## Resultado Linux

| Contexto | Casos | Aprovados | Falhas/erros | Ignorados | Tempo |
|---|---:|---:|---:|---:|---:|
| Fonte no Debian 13.7 | 41 | 40 | 0 | 1 | 33,325 s |
| Debian instalado | 41 | 40 | 0 | 1 | 52,126 s |
| Flatpak no sandbox real | 41 | 40 | 0 | 1 | 66,364 s |

O caso ignorado é específico do Windows. São os mesmos casos em três ambientes,
não 120 testes distintos. A suíte da fonte no GitHub Actions é uma execução
adicional; não substitui a instalação e a validação dos pacotes.

## Arquivos completos

- [Resumo da entrega](LINUX-3.4.1-ENTREGA-2026-10-30.json).
- [Fonte — JSON](linux-source-3.4.1.json) e [log](linux-source-3.4.1.log).
- [Debian instalado — JSON](linux-deb-tests-3.4.1.json) e [log](linux-deb-tests-3.4.1.log).
- [Sandbox Flatpak — JSON](linux-flatpak-sandbox-tests-3.4.1.json) e [log](linux-flatpak-sandbox-tests-3.4.1.log).
- [Conferência dos 83 arquivos da aplicação e dos 2.973 arquivos do payload](linux-payload-verification-3.4.1.json).
- [Contexto coletado dentro do sandbox](linux-flatpak-sandbox-context-3.4.1.json).
- [Inicialização pelos lançadores padrão](linux-launcher-smoke-3.4.1.json).
- [Versões do ambiente](debian-build-packages-3.4.1.txt) e [histórico apt](debian-build-apt-history-3.4.1.txt).

## Tentativas anteriores e correções

O primeiro bundle falhou por misturar bibliotecas do aplicativo com o shell do
Freedesktop. A tentativa seguinte abriu GTK, mas a falta do provedor OpenSSL
impediu os processos PDF de iniciar. Os arquivos finais corrigem os dois problemas.

- [Primeira falha do sandbox](linux-flatpak-sandbox-initial-failure-3.4.1.log).
- [Antes da correção OpenSSL — JSON](linux-flatpak-sandbox-before-crypto-fix-3.4.1.json) e [log](linux-flatpak-sandbox-before-crypto-fix-3.4.1.log).

## Prévia Windows anterior ao empacotamento Linux

- [14 testes da prévia aprovados](preferencias-validacao-2026-10-30.json).
- [Tentativa anterior da suíte completa Windows](preferencias-regressao-windows-2026-10-30.json): timeouts e limites preservados, sem aprovação integral Windows.

Esses registros descrevem etapas e identidades de fonte diferentes. Não
constituem um instalador Windows 3.4.1 nem validam toda a regressão Windows.

## Tratamento dos registros e limites

Os testes, contagens, rastros de falha e hashes foram preservados. Caminhos da
máquina de build e do usuário foram normalizados para variáveis, e identificadores
locais de VM foram removidos do resumo público. Os hashes dos arquivos originais
estão em [original-report-sha256.json](original-report-sha256.json).

Os assets da release são os mesmos bytes dos pacotes aprovados; a organização
posterior de README/documentação não recompilou esses artefatos. O campo de
publicação do resumo registra a fase de validação, anterior à publicação.

Impressão física, desktop/Wayland, outras distribuições, PDFs grandes e
regressão integral Windows continuam fora da validação declarada. Consulte a
[entrega](../../ENTREGA-3.4.1-LINUX.md) para o escopo completo.

Os hashes da aplicação correspondem aos arquivos usados no build. Checkouts Git podem normalizar terminações de linha CRLF/LF; essa normalização altera o hash dos arquivos sem alterar seu código. A formatação de saída das ferramentas foi preservada nos logs.

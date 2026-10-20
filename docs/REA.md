# REA no Print&View PDF

O [REA — Reverse Engineer Anything](https://github.com/morluto/rea) está instalado
neste projeto, no escopo do repositório, para apoiar os estudos de engenharia
reversa (Foxit, UPDF e outros leitores) que alimentam os recursos do app.

## O que foi instalado

| Arquivo | Função |
| --- | --- |
| `.codex/config.toml` | Registra o servidor MCP `rea` (pacote npm `rea-agents@6.7.0`) só para este projeto. |
| `.agents/skills/reverse-engineer-anything/` | Skill oficial do REA 6.7.0 (fluxos de análise e referências), lida pelo Codex a partir do repositório. |

Nada foi alterado na configuração pessoal do Codex (`~/.codex`), então o REA
aparece apenas quando o Codex abre esta pasta.

## Requisitos

- Node.js e npm no `PATH` (o servidor é iniciado com `npx`, que baixa o pacote na primeira execução).
- O Codex precisa tratar a pasta como projeto confiável para carregar `.codex/config.toml`.
- Reinicie o Codex depois de sincronizar para que ele leia o servidor e a skill.
- Análise nativa (DLL/EXE) usa um motor já instalado: Ghidra, Hopper ou IDA. Análise de
  JavaScript/Electron e de sites não precisa de motor nativo.
- No Linux, Ghidra, JADX e a análise de JavaScript/Electron exigem um `ps` compatível com procps.

## Windows x Linux

O arquivo vem configurado para Windows (`cmd.exe /d /c npx ...`), que é a máquina
principal de desenvolvimento. Para usar no Linux, troque `command`/`args` pelas
linhas comentadas no próprio arquivo:

```toml
command = "npx"
args = ["-y", "rea-agents@6.7.0", "mcp"]
```

## Verificar

```bash
npx -y rea-agents@6.7.0 --help
```

No Codex, o comando `/mcp` deve listar o servidor `rea` (207 ferramentas na 6.7.0).

## Atualizar

1. Troque `rea-agents@6.7.0` pela nova versão em `.codex/config.toml`.
2. Substitua `.agents/skills/reverse-engineer-anything/` pela pasta `skills/reverse-engineer-anything`
   do pacote da mesma versão (`npm pack rea-agents@<versão>`), para que skill e servidor continuem combinando.
3. Reinicie o Codex.

## Timeouts

`startup_timeout_sec = 30` e `tool_timeout_sec = 450` são os valores que o próprio
`rea setup` grava para o Codex (450 s cobre a inicialização padrão do Ghidra mais
120 s de folga). Aumente `tool_timeout_sec` se uma análise longa estourar o prazo.

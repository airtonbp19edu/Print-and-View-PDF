# Origem e limites dos artefatos

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
produtos foi incorporado à aplicação. As únicas informações deles no
repositório são metadados/evidências da inspeção estática do instalador UPDF.

O arquivo de contexto é um relato histórico, não uma ordem de execução nem
evidência de que uma funcionalidade funciona. A versão 3.3.10, os três
relatórios históricos e o vídeo citados nele não foram fornecidos. As
correções desta etapa são baseadas apenas no código 3.3.5 e em testes atuais.

Os ZIPs do Foxit e do UPDF e o arquivo `FoxitPDFReader.exe` não foram
transferidos: a ferramenta rejeitou arquivos maiores que 32 MiB. Os links
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

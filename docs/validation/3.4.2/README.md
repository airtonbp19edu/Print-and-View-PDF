# Evidências da versão 3.4.2 (Linux)

Estado: **pacote Debian construído e exercitado; Flatpak ainda não gerado.** O Flatpak
3.4.2 precisa ser construído e validado na VM de build do projeto, porque depende do
runtime da Flathub e do Debian 13 usado como origem das bibliotecas. Enquanto isso não
acontecer, a correção das fontes do Flatpak só está comprovada pelo teste da configuração
gerada e por simulação, não pelo Flatpak real.

## O que mudou em relação à 3.4.1

Três correções visuais, descritas no [histórico](../../../CHANGELOG.md): fontes do Flatpak,
largura mínima do painel lateral e dois ícones que o Adwaita não tem. Nenhum recurso novo.

## Pacote Debian

| Item | Resultado |
|---|---|
| Arquivo | `print-view-pdf_3.4.2_all.deb`, 420.404 bytes |
| SHA-256 | `02e6722081c29fc1d6386e51b483b2eb89858ea7120a2f89ec741c7c1ccca8bd` ([arquivo](linux-deb-3.4.2.sha256)) |
| Instalação | `dpkg -i`, versão 3.4.2 instalada |
| Arquivos da aplicação | 85 na fonte e 85 no pacote instalado; SHA-256 de todos iguais |
| Suíte completa contra o app instalado | 47 casos, 46 aprovados, 0 falhas/erros, 1 ignorado (específico do Windows), ~20 s ([log](linux-deb-tests-3.4.2.log)) |
| Inicialização | `main.py` instalado permaneceu ativo por 6 s com um PDF |

Os 47 casos são os 41 da 3.4.1 mais 6 novos: 3 de fontes, 1 de painel lateral e 2 de ícones.
Os testes de painel e de ícones falham sem as correções e passam com elas.

## Ambiente e limites desta validação

- Ubuntu 24.04 com Python 3.12 e X11 virtual (Xvfb). **Não** é o Debian 13.7 usado na 3.4.1.
- O lançador padrão `/usr/bin/print-view-pdf` não pôde ser exercitado: neste ambiente `python3`
  aponta para o 3.13 e os módulos GTK instalados são do 3.12. É uma peculiaridade do ambiente,
  não do pacote; o mesmo `main.py` instalado foi iniciado com o Python 3.12.
- Não há validação em Wayland, desktop físico, impressora, outras distribuições nem Flatpak.
- Capturas de tela do app com as correções foram inspecionadas durante o desenvolvimento
  (fonte sem serifa, coluna lateral inteira, ícone "Largura" e ícone da aba); não foram
  arquivadas como evidência.

## Pendente para fechar a 3.4.2

1. Gerar o Flatpak 3.4.2 na VM de build, instalar e rodar os 47 casos dentro do sandbox.
2. Dentro do sandbox, com fontes do sistema presentes, capturar a janela com um PDF aberto e
   conferir interface sem serifa, os quatro ícones laterais inteiros e o botão "Largura".
3. Acrescentar o Flatpak e sua linha SHA-256 à release e só então publicá-la.

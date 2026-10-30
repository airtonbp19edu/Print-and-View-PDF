# Histórico de versões

## 3.4.2 — Linux — 30/10/2026 (em preparação; ainda não publicada)

Correções visuais do Linux, principalmente do Flatpak. Os recursos da 3.4.1 não mudaram.

- Flatpak: a configuração de fontes passou a incluir a do runtime. Antes, em desktops com muitas fontes, "Sans" caía numa fonte qualquer (por exemplo serifada) e toda a interface mudava de aparência; agora há também DejaVu como reserva.
- Painel lateral: a largura deixou de ficar fixa em 158 px. Ela nunca é menor que o conteúdo, então a coluna de ícones e o título "Páginas" não saem cortados com fontes mais largas.
- Ícones: o botão "Largura" e o ícone da aba do documento pediam ícones que o tema Adwaita não tem e apareciam como imagem quebrada. Os dois agora vêm no próprio app (`app/icons`), valendo para Flatpak, Debian e Windows.
- Testes novos para as três correções (fontes do Flatpak, layout do painel lateral e disponibilidade dos ícones): 47 casos, 1 ignorado.
- O pacote Debian 3.4.2 foi construído e exercitado instalado; o Flatpak 3.4.2 ainda precisa ser gerado e validado na VM de build. O instalador Windows continua em 3.4.0.

[Evidências da 3.4.2](docs/validation/3.4.2/README.md)

## 3.4.1 — Linux — 30/10/2026

- Central de preferências de Aparência, Interface, Leitura e Busca.
- Rascunho, prévia de tema, Aplicar, Cancelar e restauração por seção.
- Persistência atômica, migração do tema e preservação de chaves desconhecidas.
- Memória opcional de página, zoom e rotação para até 50 documentos.
- Correção de callbacks recursivos nos botões laterais e guarda de propriedade de cache no Windows.
- Flatpak: bibliotecas ELF privadas, wrapper Python preservado em subprocessos e provedor OpenSSL correspondente.
- Pacotes Debian e Flatpak instalados e exercitados; 40 casos aprovados em cada um, com um caso específico do Windows ignorado.

O instalador Windows disponível permanece em 3.4.0. A prévia Windows da fonte
possui validação própria e não equivale a um instalador Windows 3.4.1.

[Entrega e limites](docs/ENTREGA-3.4.1-LINUX.md) · [Evidências](docs/validation/3.4.1/README.md)

## 3.4.0 — marco anterior

Consolida os recursos da Winux 3.3.11 com busca progressiva, temas, apresentação,
seleção, impressão avançada e empacotamento Debian, Flatpak e Windows.

[Registro histórico da entrega](docs/ENTREGA-3.4.0.md)

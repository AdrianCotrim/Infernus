# CLAUDE.md

Contexto do projeto Infernus para o Claude (e para qualquer pessoa nova no
repositório). Leia isto antes de mexer no código. O design completo, com as
imagens de referência, está em [docs/GDD.md](docs/GDD.md).

## O jogo

**Infernus** é um Metroidvania 2D em pixel art, feito em Python com Pygame.
Uma garota anja acorda sem suas memórias numa terra pútrida e deserta, tendo
como única defesa um escudo.

**Sinopse:** a anja (ou humana) acorda sem memórias, mas vozes clamam por ajuda
numa terra pútrida e deserta. Quem te trouxe aqui? Quem precisa de você?
Encontre as respostas.

**Inspirações:** Hollow Knight (exploração, mapa interligado, atmosfera
melancólica) e The Binding of Isaac (temática orgânica e grotesca).

### Escopo do projeto

É um Metroidvania, mas o escopo é propositalmente pequeno: **uma única área**,
com poucas salas.

- 3 inimigos
- 1 chefe
- 2 ou 3 armas (escudos)
- no mínimo 1 habilidade

Não proponha conteúdo fora desse escopo sem que peçam.

### Direção de arte

- Pixel art.
- **Regra principal:** a protagonista é clara e quente e funciona como uma
  fonte de luz. O cenário é escuro e frio. Todo elemento novo deve respeitar
  esse contraste.
- O mundo é **um corpo por dentro**: carne, veias, olhos, órgãos, em roxos e
  vinhos apodrecidos.
- **Protagonista:** cabelo ruivo e volumoso, cachecol vermelho com listras
  amarelas cobrindo a boca, casaco amarelo-alaranjado, saia vermelha, meias e
  botas marrons e um escudo redondo de madeira com centro de metal. A sprite
  sheet de caminhada (direita, esquerda, de costas e de frente) está em
  `docs/referencias/personagem-caminhada.png`.
- Paleta aproximada da protagonista: cabelo `#B4582C`/`#7E3519`, pele
  `#F4CDA5`, cachecol `#C0392B` com listra `#F5B841`, casaco
  `#F4A73A`/`#D47A1F`, saia `#A3271F`, escudo `#8B5A2B`/`#4E2E17`, metal
  `#B9BEC6`.
- Paleta do cenário (a mesma da tela de título): fundo `#14060E`, carne
  `#1E0914`/`#280C1A`/`#3A1024`, veias `#3A1030` → `#6E1B2E` → `#A3232F` →
  `#E0303E` → `#FF8A6A`, texto creme `#FCE3B0`.
- **Técnica de pixel art:** desenhe a cena numa superfície de 320×180 e amplie
  4× (vizinho mais próximo) para 1280×720, para todos os pixels terem o mesmo
  tamanho. A tela de título já faz isso. Texto da interface pode ser desenhado
  direto em 1280×720.

### Gameplay definida no GDD

- **Moveset:** andar para a esquerda e a direita, pular, investida com escudo
  para a esquerda e a direita (dano e knockback no impacto) e parry que
  paralisa o inimigo por alguns segundos. O escudo é arma e defesa.
- **Combate:** o jogador leva dano ao encostar no inimigo. Cada investida
  bem-sucedida causa 1 ponto de dano.
- **Inimigo 1:** anda devagar até o jogador, tem 3 de vida e de tempos em
  tempos ataca com um leve dash. É o `Inimigo` em `infernus/entidades/inimigo.py`.
- **Inimigos 2 e 3:** a definir. Existe o conceito de um **inimigo olho**
  (globo ocular com veias vermelhas e um nervo pendurado), em
  `docs/referencias/inimigo-olho.png`.
- **Chefe:** um cérebro com um olho no centro e uma figura presa a ele por
  veias (`docs/referencias/chefe-cerebro.png`). A luta é na sala do cérebro.

### Mapa

A área é um corpo, e as salas são órgãos. O coração é o centro que liga tudo.

- Início → Cidade inicial (com Loja) → Boca → **Coração** (hub)
- Coração → Pulmão 1 → Escudo 2 e Escudo 3
- Coração → Pulmão 2 → Câmara de level up e Escudo 3
- Coração → Mapa
- Coração → Caminho até o chefe → Parkour → **Cérebro** (luta contra o chefe)

Rascunho em `docs/referencias/mapa-rascunho.png`.

### Roadmap do GDD e situação atual

| #  | Etapa                               | Situação |
| -- | ----------------------------------- | -------- |
| 1  | Definir resolução                   | Feito (1280×720) |
| 2  | Movimentação básica                 | Feito, com coyote time e jump buffer |
| 3  | Colisão básica com objetos          | Feito (plataformas de teste) |
| 4  | Ataques e parry                     | Feito (dash com hitbox e parry) |
| 5  | Desenhar inimigo                    | Placeholder (retângulo) |
| 6  | Movimentação do inimigo             | Feito |
| 7  | Colisão de ataque com inimigo       | Feito |
| 8  | Sistema de vida                     | Feito |
| 9  | Colisão de dano com inimigo         | Feito |
| 10 | Estado de falha                     | A fazer |
| 11 | Montar os 3 inimigos                | 1 de 3 |
| 12 | Level design                        | A fazer |
| —  | Tela de título                      | Feito |

### Decisões em aberto

- Como são os inimigos 2 e 3 (o olho é só um conceito).
- O rascunho do mapa tem um "Escudo 3" no Pulmão 1 e outro no Pulmão 2. Falta
  saber se é o mesmo item.
- Quais são as 2 ou 3 armas (escudos) e qual é a habilidade.
- A arte final ainda não existe no jogo: jogador, inimigo e plataformas são
  retângulos coloridos.

Quando uma tarefa depender de uma dessas decisões, pergunte em vez de inventar.

## Código

### Estrutura

```
main.py                  atalho: python main.py
infernus/
  __main__.py            python -m infernus
  jogo.py                abre a janela e encadeia tela de título → fase
  config.py              resolução, FPS, título da janela, caminhos de assets
  entidades/
    jogador.py           Jogador: movimento, pulo, dash, parry, vida, knockback
    inimigo.py           Inimigo 1: perseguição, preparação, ataque, stun, morte
    alvo_teste.py        alvo para validar a hitbox do dash
  combate/
    ataque_dash.py       dano e knockback da investida nos alvos
    hitbox.py            hitbox do dash à frente do jogador
    parry.py             resolve ataques do inimigo contra o parry
  telas/
    titulo.py            tela de título (coração pulsante)
  fases/
    fase_teste.py        fase de testes do combate (loop e desenho)
assets/fonts/            Jersey 25 e Silkscreen (licença SIL OFL)
docs/GDD.md              Game Design Document
docs/referencias/        imagens de referência do GDD
tests/                   testes com pytest
```

Lugar de cada coisa nova:

- Personagem ou objeto com estado próprio vai em `entidades/`.
- Regra de combate entre entidades vai em `combate/`.
- Cada sala ou órgão do mapa vira um módulo em `fases/`.
- Menus e telas fora da gameplay vão em `telas/`.
- Imagens, sons e fontes vão em `assets/`, sempre lidos pelos caminhos de
  `config.py`.

### Rodar e testar

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt pytest
python main.py                   # ou python -m infernus
python -m infernus.telas.titulo  # só a tela de título
python -m pytest
```

Para testar sem abrir janela (CI ou terminal), use `SDL_VIDEODRIVER=dummy`.

### Convenções

- **Idioma:** classes, métodos, variáveis e comentários em português
  (`Jogador`, `atualizar`, `iniciar_dash`). Alguns métodos antigos estão em
  inglês (`take_damage`, `apply_knockback`) e as constantes de tuning também
  (`PLAYER_SPEED`, `ENEMY_ATTACK_WINDUP`). Mantenha o nome que já existe ao
  mexer nesses pontos. Não renomeie em massa sem pedirem.
- **Tuning:** valores de jogo são constantes em MAIÚSCULAS no topo do módulo
  da entidade ou tela. Não espalhe números mágicos.
- **Estados:** entidades usam `Enum` (`EstadoJogador`, `EstadoInimigo`) e um
  `tempo_estado` decrescente.
- **Tempo:** `atualizar(..., dt)` recebe `dt` em segundos. **Atenção às
  unidades misturadas:** o jogador anda e cai em pixels por quadro
  (`PLAYER_SPEED`, `GRAVITY`, `JUMP_FORCE`, `KNOCKBACK_SPEED`), mas o dash, o
  inimigo e o alvo usam pixels por segundo multiplicados por `dt`. Ao criar
  algo novo, prefira pixels por segundo × `dt`.
- **Interfaces:** contratos entre módulos usam `typing.Protocol`
  (`AlvoAtacavel`, `InimigoAtordoavel`).
- **Cores de depuração na fase de teste:**
  - jogador: amarelo; dash: ciano; dash em cooldown: laranja; parry: magenta;
    pisca em branco quando está invulnerável;
  - inimigo: vermelho; pisca em branco na preparação do ataque; amarelo quando
    atordoado.
- **Testes:** pytest, um arquivo por área em `tests/`, nomes de teste em
  inglês, como os que já existem. Lógica nova vem com teste. Para o que
  desenha, ao menos um teste de que desenha sem erro.
- **Desempenho:** o jogo roda a 60 FPS, então cada quadro tem 16,6 ms. Evite
  laços por pixel a cada quadro. Pré-renderize em superfícies e use cache,
  como a tela de título faz.

### Combate atual (resumo do comportamento)

- **Dano no jogador** (`Jogador.take_damage`): tira vida, aplica knockback
  com impulso para cima por `KNOCKBACK_DURATION` (sem controle horizontal) e
  deixa invulnerável por `INVULNERABILITY_DURATION`. Dano durante a
  invulnerabilidade é ignorado.
- **Dash:** dura `DASH_DURATION`, tem cooldown `DASH_COOLDOWN`. A hitbox à
  frente acerta cada alvo uma vez por dash, causando `DASH_DAMAGE` e
  `DASH_KNOCKBACK`. Ao acertar, o dash para antes do alvo.
- **Parry:** janela de `PARRY_DURATION`. Um ataque que acerta durante o parry
  não causa dano e atordoa o inimigo por `STUN_DURATION`.
- **Inimigo:** persegue, prepara o ataque piscando cada vez mais rápido,
  avança com o ataque e se recupera. Não age enquanto está atordoado ou sendo
  empurrado pelo knockback, e morre (estado `DEAD`) com vida 0.

### Tela de título

Em `infernus/telas/titulo.py`. A tela é a câmara do coração: um coração em
pixel art bate em ritmo dobrado ("tum-tum", cerca de 70 bpm), cada batida
manda um pulso pelas veias e desenha um pico no eletrocardiograma, e o título
pulsa no ritmo. Ela surge do preto em `DURACAO_ENTRADA` segundos, já com o
título e o "APERTE QUALQUER BOTÃO". Qualquer tecla, clique ou botão de
controle faz o fade de saída e começa o jogo.

## Git

- Commits no padrão Conventional Commits, **em português**: `feat:`, `fix:`,
  `refactor:`, `docs:`, `test:`, `chore:`.
- Uma branch por mudança (`feat/...`, `fix/...`, `refactor/...`,
  `docs/...`), com Pull Request para a `main`.
- Rode `python -m pytest` antes de abrir o PR.
- Nunca commite marcadores de conflito (`<<<<<<<`, `=======`, `>>>>>>>`). Um
  merge com conflito já quebrou a `main` uma vez. Depois de resolver um merge,
  rode `grep -rn '^<<<<<<<' --include=*.py .` e os testes.

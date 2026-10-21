# Infernus

Metroidvania 2D em pixel art feito com Python e Pygame. Uma garota anja acorda
sem memórias numa terra pútrida e deserta, tendo um escudo como única defesa. A
aventura se passa dentro de um corpo, onde cada sala é um órgão, até o chefe no
cérebro.

O design completo (escopo, arte, história, inimigos, mapa e roadmap) está em
[docs/GDD.md](docs/GDD.md).

## Executar

No terminal, dentro da pasta do projeto.

Windows (PowerShell):

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Linux e macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

O jogo abre na tela de título. Para ver só a tela de título, rode
`python tela_titulo.py`. Para fechar, feche a janela do jogo.

## Testes

```bash
python -m pip install pytest
python -m pytest
```

## Estrutura

| Arquivo            | Responsabilidade |
| ------------------ | ---------------- |
| `main.py`          | Janela, loop principal e desenho da fase de teste. |
| `tela_titulo.py`   | Tela de título animada (coração pulsante). |
| `jogador.py`       | Movimento, pulo, dash, parry, vida e knockback do jogador. |
| `inimigo.py`       | Inimigo 1: perseguição, preparação, ataque e atordoamento. |
| `combate.py`       | Dano e knockback da investida (dash) nos inimigos. |
| `sistema_parry.py` | Resolução dos ataques inimigos contra o parry. |
| `hitbox.py`        | Hitbox do dash à frente do jogador. |
| `alvo_teste.py`    | Alvo usado para validar a hitbox do dash. |
| `assets/fonts/`    | Fontes da interface (licença SIL OFL). |
| `docs/GDD.md`      | Game Design Document. |
| `tests/`           | Testes automatizados (pytest). |

## Tela de título

A tela de título é a câmara do coração, a sala central do mapa. Depois de um
momento de silêncio, o coração começa a bater em ritmo dobrado ("tum-tum"). Cada
batida manda um pulso de luz pelas veias da câmara e desenha um pico no
eletrocardiograma embaixo da tela. O título aparece na terceira batida e passa a
pulsar no ritmo. Logo depois surge o "APERTE QUALQUER BOTÃO".

- Qualquer tecla, clique do mouse ou botão de controle avança.
- Durante a introdução, o primeiro aperto pula direto para o título.
- Com o aviso na tela, apertar escurece a tela e inicia o jogo.

A cena é desenhada em 320×180 e ampliada 4× para 1280×720, para manter os pixels
do mesmo tamanho. Os tempos, as cores e as posições são constantes no topo de
`tela_titulo.py`.

## Controles

- Avançar na tela de título: qualquer botão.
- Movimento: A/D ou setas esquerda/direita.
- Pulo: Espaço.
- Dash: E.
- Parry: W ou seta para cima.

O dash tem duração de `DASH_DURATION` e cooldown de `DASH_COOLDOWN`, ambos
configurados em `jogador.py`. Durante o cooldown, o personagem aparece em laranja
e o dash não pode ser iniciado.

Dash e parry têm estados próprios. O parry abre uma janela de `PARRY_DURATION`
configurável e muda temporariamente a cor do personagem. O inimigo de demonstração
se aproxima e tenta atacar quando está ao alcance. Aparar no momento do acerto
impede dano ao jogador e atordoa o inimigo por `STUN_DURATION`; fora da janela,
o jogador recebe dano. Inimigos atordoados não se movem nem atacam. Durante o
dash, uma hitbox translúcida à frente do personagem pode atingir o alvo de teste,
uma vez por dash, aplicando dano e knockback horizontal baseado em velocidade do
próprio alvo. O alvo de teste existe para validar essa integração.

Ao receber dano do inimigo, o jogador entra temporariamente em knockback:
`KNOCKBACK_SPEED`, `KNOCKBACK_VERTICAL_FORCE` e `KNOCKBACK_DURATION`, em
`jogador.py`, controlam a intensidade e a duração da reação. Durante esse estado,
o impulso continua respeitando a gravidade e as colisões, mas o controle
horizontal fica bloqueado até a recuperação automática.

Durante o dash, acertar o inimigo interrompe imediatamente a investida e posiciona
o jogador antes do inimigo, evitando atravessá-lo. O inimigo recebe `DASH_DAMAGE`
e o knockback configurado por `DASH_KNOCKBACK` em `combate.py`; o cooldown do dash
é preservado e o mesmo inimigo não pode ser atingido novamente pela mesma
investida.

## Créditos

- Fonte [Jersey 25](https://fonts.google.com/specimen/Jersey+25), da Soft Type
  Project, sob a SIL Open Font License 1.1 (`assets/fonts/OFL-Jersey25.txt`).
- Fonte [Silkscreen](https://fonts.google.com/specimen/Silkscreen), da
  Silkscreen Project, sob a SIL Open Font License 1.1
  (`assets/fonts/OFL-Silkscreen.txt`).

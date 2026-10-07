# Infernus

Projeto inicial feito com Pygame.

## Executar

No terminal, dentro da pasta do projeto:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

Para fechar, feche a janela do jogo.

## Controles

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
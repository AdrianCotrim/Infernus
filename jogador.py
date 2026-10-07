from enum import Enum, auto

import pygame


PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 6
PLAYER_DASH_SPEED = 1080
DASH_DURATION = 0.15
DASH_COOLDOWN = 0.5
PARRY_DURATION = 0.15
GRAVITY = 0.7
JUMP_FORCE = 15
COYOTE_TIME = 0.10
JUMP_BUFFER_TIME = 0.12
JUMP_HOLD_TIME = 0.15
JUMP_CUT_MULTIPLIER = 0.5


class EstadoJogador(Enum):
    NORMAL = auto()
    DASHING = auto()
    PARRYING = auto()


class Jogador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.vida = 5
        self.estado = EstadoJogador.NORMAL
        self.tempo_estado = 0.0
        self.direcao = 1
        self.direcao_dash = 1
        self.tempo_dash_decorrido = 0.0
        self.distancia_dash_aplicada = 0
        self.dash_cooldown_timer = 0.0
        self.velocidade_y = 0
        self.no_chao = True
        self.coyote_timer = 0.0
        self.jump_buffer_started_at = None
        self.jump_held = False
        self.jump_started_at = None

    def take_damage(self, amount):
        self.vida = max(0, self.vida - amount)

    @property
    def dash_disponivel(self):
        return self.dash_cooldown_timer == 0.0

    def iniciar_dash(self):
        if self.estado is not EstadoJogador.NORMAL or not self.dash_disponivel:
            return

        self.estado = EstadoJogador.DASHING
        self.tempo_estado = DASH_DURATION
        self.dash_cooldown_timer = DASH_COOLDOWN
        self.direcao_dash = self.direcao
        self.tempo_dash_decorrido = 0.0
        self.distancia_dash_aplicada = 0

    def iniciar_parry(self):
        if self.estado is not EstadoJogador.NORMAL:
            return

        self.estado = EstadoJogador.PARRYING
        self.tempo_estado = PARRY_DURATION

    def registrar_pulo(self):
        self.jump_held = True
        self.jump_buffer_started_at = pygame.time.get_ticks()

    def soltar_pulo(self):
        self.jump_held = False
        if self.jump_started_at is None or self.velocidade_y >= 0:
            return

        elapsed = pygame.time.get_ticks() - self.jump_started_at
        if elapsed < JUMP_HOLD_TIME * 1000:
            self.velocidade_y *= JUMP_CUT_MULTIPLIER

    def _iniciar_pulo(self):
        self.velocidade_y = -JUMP_FORCE
        self.no_chao = False
        self.coyote_timer = 0.0
        self.jump_started_at = pygame.time.get_ticks()
        if not self.jump_held:
            self.velocidade_y *= JUMP_CUT_MULTIPLIER

    def _pode_pular(self):
        return self.no_chao or self.coyote_timer > 0

    def _consumir_buffer_se_puder_pular(self):
        if self.jump_buffer_started_at is None:
            return

        elapsed = pygame.time.get_ticks() - self.jump_buffer_started_at
        if elapsed >= JUMP_BUFFER_TIME * 1000:
            self.jump_buffer_started_at = None
            return

        if self._pode_pular():
            self._iniciar_pulo()
            self.jump_buffer_started_at = None

    def _atualizar_movimento_horizontal(self, tecla_pressionada, largura_tela):
        if tecla_pressionada(pygame.K_a) or tecla_pressionada(pygame.K_LEFT):
            velocidade_x = -PLAYER_SPEED
        elif tecla_pressionada(pygame.K_d) or tecla_pressionada(pygame.K_RIGHT):
            velocidade_x = PLAYER_SPEED
        else:
            velocidade_x = 0

        if velocidade_x:
            self.direcao = 1 if velocidade_x > 0 else -1

        self.rect.x += velocidade_x
        self.rect.x = max(0, min(largura_tela - self.rect.width, self.rect.x))

    def _atualizar_normal(self, tecla_pressionada, largura_tela):
        self._atualizar_movimento_horizontal(tecla_pressionada, largura_tela)

    def _mover_durante_dash(self, largura_tela, duracao):
        self.tempo_dash_decorrido += duracao
        distancia_total = round(PLAYER_DASH_SPEED * self.tempo_dash_decorrido)
        distancia_incremental = distancia_total - self.distancia_dash_aplicada
        self.rect.x += self.direcao_dash * distancia_incremental
        self.distancia_dash_aplicada = distancia_total
        self.rect.x = max(0, min(largura_tela - self.rect.width, self.rect.x))

    def _atualizar_dashing(self, largura_tela, dt):
        duracao_movimento = min(dt, self.tempo_estado)
        self._mover_durante_dash(largura_tela, duracao_movimento)
        self.tempo_estado = max(0.0, self.tempo_estado - dt)
        if self.tempo_estado == 0:
            self.estado = EstadoJogador.NORMAL

    def _atualizar_parrying(self, tecla_pressionada, largura_tela, dt):
        self._atualizar_movimento_horizontal(tecla_pressionada, largura_tela)
        self.tempo_estado = max(0.0, self.tempo_estado - dt)
        if self.tempo_estado == 0:
            self.estado = EstadoJogador.NORMAL

    def _atualizar_dash_cooldown(self, dt):
        if self.dash_cooldown_timer > 0:
            self.dash_cooldown_timer = max(0.0, self.dash_cooldown_timer - dt)

    def atualizar(self, teclas, plataformas, largura_tela, dt=1 / 60):
        def tecla_pressionada(chave):
            if isinstance(teclas, dict):
                return teclas.get(chave, False)
            return bool(teclas[chave])

        self._atualizar_dash_cooldown(dt)

        if self.estado is EstadoJogador.NORMAL:
            self._atualizar_normal(tecla_pressionada, largura_tela)
        elif self.estado is EstadoJogador.DASHING:
            self._atualizar_dashing(largura_tela, dt)
        elif self.estado is EstadoJogador.PARRYING:
            self._atualizar_parrying(tecla_pressionada, largura_tela, dt)

        if self.no_chao:
            self.coyote_timer = COYOTE_TIME
        elif self.coyote_timer > 0:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)
        else:
            self.coyote_timer = 0.0

        self._consumir_buffer_se_puder_pular()

        self.velocidade_y += GRAVITY
        self.rect.y += self.velocidade_y

        self.no_chao = False
        for plataforma in plataformas:
            if (
                self.rect.colliderect(plataforma)
                and self.velocidade_y >= 0
                and self.rect.bottom >= plataforma.top
                and self.rect.bottom <= plataforma.top + 30
            ):
                self.rect.bottom = plataforma.top
                self.velocidade_y = 0
                self.no_chao = True
                break

        if self.no_chao:
            self.coyote_timer = COYOTE_TIME

        self._consumir_buffer_se_puder_pular()

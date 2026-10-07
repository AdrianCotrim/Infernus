from enum import Enum, auto

import pygame


ENEMY_WIDTH = 40
ENEMY_HEIGHT = 50
ENEMY_SPEED = 90
ENEMY_ATTACK_RANGE = 38
ENEMY_ATTACK_WIDTH = 34
ENEMY_ATTACK_COOLDOWN = 0.8
ENEMY_ATTACK_DAMAGE = 1
STUN_DURATION = 2.0


class EstadoInimigo(Enum):
    NORMAL = auto()
    STUNNED = auto()


class Inimigo:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.estado = EstadoInimigo.NORMAL
        self.tempo_atordoado = 0.0
        self.tempo_ataque = 0.0
        self.direcao = -1

    def aplicar_stun(self, duracao=STUN_DURATION):
        self.estado = EstadoInimigo.STUNNED
        self.tempo_atordoado = duracao

    def _atualizar_stun(self, dt):
        self.tempo_atordoado = max(0.0, self.tempo_atordoado - dt)
        if self.tempo_atordoado == 0:
            self.estado = EstadoInimigo.NORMAL

    def _hitbox_ataque(self):
        hitbox = pygame.Rect(
            0,
            self.rect.centery - self.rect.height // 4,
            ENEMY_ATTACK_WIDTH,
            self.rect.height // 2,
        )
        if self.direcao > 0:
            hitbox.left = self.rect.right
        else:
            hitbox.right = self.rect.left
        return hitbox

    def atualizar(self, dt, jogador_rect):
        if self.estado is EstadoInimigo.STUNNED:
            self._atualizar_stun(dt)
            return None

        distancia = jogador_rect.centerx - self.rect.centerx
        self.direcao = 1 if distancia >= 0 else -1

        if abs(distancia) > ENEMY_ATTACK_RANGE:
            movimento = min(
                abs(distancia) - ENEMY_ATTACK_RANGE,
                ENEMY_SPEED * dt,
            )
            self.rect.x += round(self.direcao * movimento)

        self.tempo_ataque = max(0.0, self.tempo_ataque - dt)
        if self.tempo_ataque > 0:
            return None

        hitbox_ataque = self._hitbox_ataque()
        if not hitbox_ataque.colliderect(jogador_rect):
            return None

        self.tempo_ataque = ENEMY_ATTACK_COOLDOWN
        return hitbox_ataque

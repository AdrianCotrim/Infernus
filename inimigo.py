from enum import Enum, auto

import pygame


ENEMY_WIDTH = 40
ENEMY_HEIGHT = 50
ENEMY_SPEED = 90
ENEMY_ATTACK_RANGE = 38
ENEMY_ATTACK_WIDTH = 34
ENEMY_ATTACK_COOLDOWN = 0.8
ENEMY_ATTACK_DAMAGE = 1
ENEMY_ATTACK_KNOCKBACK = 260
ENEMY_ATTACK_WINDUP = 0.55
ENEMY_WINDUP_FLASH_START_INTERVAL = 0.22
ENEMY_WINDUP_FLASH_END_INTERVAL = 0.07
ENEMY_ATTACK_DURATION = 0.22
ENEMY_ATTACK_RECOVERY = 0.25
ENEMY_ATTACK_SPEED = 240
ENEMY_CONTACT_DAMAGE = 1
ENEMY_CONTACT_KNOCKBACK = 200
MAX_ENEMY_HEALTH = 3
STUN_DURATION = 2.0


class EstadoInimigo(Enum):
    NORMAL = auto()
    CHASE = auto()
    ATTACK_WINDUP = auto()
    ATTACK = auto()
    ATTACK_RECOVERY = auto()
    STUNNED = auto()
    DEAD = auto()


class Inimigo:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, ENEMY_WIDTH, ENEMY_HEIGHT)
        self.max_health = MAX_ENEMY_HEALTH
        self.health = MAX_ENEMY_HEALTH
        self.estado = EstadoInimigo.NORMAL
        self.tempo_atordoado = 0.0
        self.tempo_ataque = 0.0
        self.tempo_estado = 0.0
        self.tempo_preparacao = 0.0
        self.tempo_flash_preparacao = 0.0
        self.flash_preparacao = False
        self.direcao = -1
        self.ataque_direcao = 1
        self.ataque_hitbox = None
        self.ataque_atingiu_jogador = False
        self.velocidade_knockback_x = 0.0
        self.contato_cooldown = 0.0
        self.ataque_damage = ENEMY_ATTACK_DAMAGE
        self.ataque_knockback = ENEMY_ATTACK_KNOCKBACK

    @property
    def vivo(self):
        return self.estado is not EstadoInimigo.DEAD

    @property
    def piscando_preparacao(self):
        return (
            self.vivo
            and self.estado is EstadoInimigo.ATTACK_WINDUP
            and self.flash_preparacao
        )

    def take_damage(self, amount, direction=0, knockback=0.0):
        if not self.vivo or amount <= 0:
            return False

        self.health = max(0, self.health - amount)
        if direction or knockback:
            self.apply_knockback(direction, knockback)

        if self.health <= 0:
            self.estado = EstadoInimigo.DEAD
            self.tempo_atordoado = 0.0
            self.tempo_ataque = 0.0
            self.tempo_estado = 0.0
            self.ataque_hitbox = None
            self._encerrar_preparacao()
            return True

        return True

    def apply_knockback(self, direction, force):
        self.velocidade_knockback_x = direction * force

    def _atualizar_knockback(self, dt):
        if self.velocidade_knockback_x > 0:
            self.velocidade_knockback_x = max(
                0.0,
                self.velocidade_knockback_x - 1200 * dt,
            )
        elif self.velocidade_knockback_x < 0:
            self.velocidade_knockback_x = min(
                0.0,
                self.velocidade_knockback_x + 1200 * dt,
            )

    def _hitbox_ataque(self):
        hitbox = pygame.Rect(
            0,
            self.rect.centery - self.rect.height // 4,
            ENEMY_ATTACK_WIDTH,
            self.rect.height // 2,
        )
        if self.ataque_direcao > 0:
            hitbox.left = self.rect.right
        else:
            hitbox.right = self.rect.left
        return hitbox

    def _iniciar_preparacao(self):
        self.tempo_preparacao = 0.0
        self.tempo_flash_preparacao = 0.0
        self.flash_preparacao = False

    def _encerrar_preparacao(self):
        self.tempo_preparacao = 0.0
        self.tempo_flash_preparacao = 0.0
        self.flash_preparacao = False

    def _atualizar_flash_preparacao(self, dt):
        self.tempo_preparacao = min(
            ENEMY_ATTACK_WINDUP,
            self.tempo_preparacao + dt,
        )
        progresso = self.tempo_preparacao / ENEMY_ATTACK_WINDUP
        intervalo = ENEMY_WINDUP_FLASH_START_INTERVAL + (
            ENEMY_WINDUP_FLASH_END_INTERVAL - ENEMY_WINDUP_FLASH_START_INTERVAL
        ) * progresso
        self.tempo_flash_preparacao += dt
        while self.tempo_flash_preparacao >= intervalo:
            self.tempo_flash_preparacao -= intervalo
            self.flash_preparacao = not self.flash_preparacao

    def aplicar_stun(self, duracao=STUN_DURATION):
        self.estado = EstadoInimigo.STUNNED
        self.tempo_atordoado = duracao
        self.tempo_ataque = 0.0
        self.tempo_estado = 0.0
        self.ataque_hitbox = None
        self._encerrar_preparacao()

    def cancelar_ataque(self):
        self.ataque_hitbox = None
        self.ataque_atingiu_jogador = True
        self.aplicar_stun(STUN_DURATION)

    def _atualizar_stun(self, dt):
        self.tempo_atordoado = max(0.0, self.tempo_atordoado - dt)
        if self.tempo_atordoado == 0:
            self.estado = EstadoInimigo.NORMAL

    def _atualizar_estado_ataque(self, dt, jogador_rect):
        if self.estado is EstadoInimigo.ATTACK_WINDUP:
            self._atualizar_flash_preparacao(dt)
            self.tempo_estado = max(0.0, self.tempo_estado - dt)
            if self.tempo_estado <= 0:
                self.estado = EstadoInimigo.ATTACK
                self.tempo_estado = ENEMY_ATTACK_DURATION
                self.ataque_atingiu_jogador = False
                self.ataque_hitbox = self._hitbox_ataque()
                self._encerrar_preparacao()
            return self.ataque_hitbox

        if self.estado is EstadoInimigo.ATTACK:
            self.rect.x += round(self.ataque_direcao * ENEMY_ATTACK_SPEED * dt)
            self.ataque_hitbox = self._hitbox_ataque()
            self.tempo_estado = max(0.0, self.tempo_estado - dt)
            if self.tempo_estado <= 0:
                self.estado = EstadoInimigo.ATTACK_RECOVERY
                self.tempo_estado = ENEMY_ATTACK_RECOVERY
                self.tempo_ataque = ENEMY_ATTACK_COOLDOWN
                self.ataque_hitbox = None
            return self.ataque_hitbox

        if self.estado is EstadoInimigo.ATTACK_RECOVERY:
            self.tempo_estado = max(0.0, self.tempo_estado - dt)
            if self.tempo_estado <= 0:
                self.estado = EstadoInimigo.NORMAL
            return None

        return None

    def atualizar(self, dt, jogador_rect):
        if self.estado is EstadoInimigo.DEAD:
            return None

        self._atualizar_knockback(dt)
        self.contato_cooldown = max(0.0, self.contato_cooldown - dt)

        if self.estado is EstadoInimigo.STUNNED:
            self._atualizar_stun(dt)
            return None

        distancia = jogador_rect.centerx - self.rect.centerx
        self.direcao = 1 if distancia >= 0 else -1

        if self.estado in (EstadoInimigo.NORMAL, EstadoInimigo.CHASE):
            self.estado = EstadoInimigo.CHASE
            if abs(distancia) > ENEMY_ATTACK_RANGE:
                movimento = min(
                    abs(distancia) - ENEMY_ATTACK_RANGE,
                    ENEMY_SPEED * dt,
                )
                self.rect.x += round(self.direcao * movimento)
                distancia = jogador_rect.centerx - self.rect.centerx

            self.ataque_direcao = self.direcao
            ataque_hitbox = self._hitbox_ataque()
            if (
                self.tempo_ataque <= 0
                and (
                    abs(distancia) <= ENEMY_ATTACK_RANGE
                    or ataque_hitbox.colliderect(jogador_rect)
                )
            ):
                self.estado = EstadoInimigo.ATTACK_WINDUP
                self.tempo_estado = ENEMY_ATTACK_WINDUP
                self.ataque_hitbox = ataque_hitbox
                self.ataque_atingiu_jogador = False
                self._iniciar_preparacao()
                return self.ataque_hitbox

        if self.estado in (
            EstadoInimigo.ATTACK_WINDUP,
            EstadoInimigo.ATTACK,
            EstadoInimigo.ATTACK_RECOVERY,
        ):
            return self._atualizar_estado_ataque(dt, jogador_rect)

        self.tempo_ataque = max(0.0, self.tempo_ataque - dt)
        return None

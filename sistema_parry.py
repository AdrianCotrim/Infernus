from enum import Enum, auto
from typing import Protocol

import pygame

from inimigo import ENEMY_ATTACK_DAMAGE, STUN_DURATION
from jogador import EstadoJogador, Jogador


class InimigoAtordoavel(Protocol):
    def aplicar_stun(self, duracao: float) -> None:
        ...


class ResultadoAtaque(Enum):
    SEM_ACERTO = auto()
    DANO = auto()
    APARADO = auto()


class SistemaParry:
    @staticmethod
    def _direcao_knockback(ataque_rect, jogador, inimigo):
        if inimigo.rect.centerx < jogador.rect.centerx:
            return 1
        if inimigo.rect.centerx > jogador.rect.centerx:
            return -1

        direcao_inimigo = getattr(inimigo, "direcao", 1)
        return 1 if direcao_inimigo >= 0 else -1

    def resolver(
        self,
        ataque_rect: pygame.Rect | None,
        jogador: Jogador,
        inimigo: InimigoAtordoavel,
    ) -> ResultadoAtaque:
        if ataque_rect is None or not ataque_rect.colliderect(jogador.rect):
            return ResultadoAtaque.SEM_ACERTO

        if jogador.estado is EstadoJogador.PARRYING:
            inimigo.aplicar_stun(STUN_DURATION)
            return ResultadoAtaque.APARADO

        direcao_knockback = self._direcao_knockback(ataque_rect, jogador, inimigo)
        jogador.take_damage(ENEMY_ATTACK_DAMAGE, direcao_knockback)
        return ResultadoAtaque.DANO

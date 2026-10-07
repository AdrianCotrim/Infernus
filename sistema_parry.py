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

        jogador.take_damage(ENEMY_ATTACK_DAMAGE)
        return ResultadoAtaque.DANO

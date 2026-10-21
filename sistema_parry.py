from enum import Enum, auto
from typing import Protocol

import pygame

from inimigo import ENEMY_ATTACK_DAMAGE, ENEMY_ATTACK_KNOCKBACK, STUN_DURATION
from jogador import EstadoJogador, Jogador


class InimigoAtordoavel(Protocol):
    rect: pygame.Rect
    ataque_atingiu_jogador: bool
    ataque_direcao: int
    ataque_damage: int
    ataque_knockback: float

    def aplicar_stun(self, duracao: float) -> None:
        ...

    def cancelar_ataque(self) -> None:
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

        if getattr(inimigo, "ataque_atingiu_jogador", False):
            return ResultadoAtaque.SEM_ACERTO

        if jogador.estado is EstadoJogador.PARRYING:
            inimigo.cancelar_ataque()
            return ResultadoAtaque.APARADO

        dano = getattr(inimigo, "ataque_damage", ENEMY_ATTACK_DAMAGE)
        direcao = -getattr(
            inimigo,
            "ataque_direcao",
            1 if inimigo.rect.centerx < jogador.rect.centerx else -1,
        )
        knockback = getattr(inimigo, "ataque_knockback", ENEMY_ATTACK_KNOCKBACK)
        jogador.take_damage(dano, direcao, knockback)
        inimigo.ataque_atingiu_jogador = True
        return ResultadoAtaque.DANO

from typing import Iterable, Protocol

import pygame


DASH_DAMAGE = 1
DASH_KNOCKBACK = 360


class AlvoAtacavel(Protocol):
    rect: pygame.Rect

    def take_damage(self, amount: int) -> None:
        ...

    def apply_knockback(self, direction: int, force: float) -> None:
        ...


class SistemaAtaqueDash:
    def __init__(self):
        self._alvos_atingidos: set[int] = set()

    def atualizar(
        self,
        hitbox: pygame.Rect | None,
        direcao: int,
        alvos: Iterable[AlvoAtacavel],
    ) -> None:
        if hitbox is None:
            self._alvos_atingidos.clear()
            return

        for alvo in alvos:
            alvo_id = id(alvo)
            if alvo_id in self._alvos_atingidos:
                continue
            if not hitbox.colliderect(alvo.rect):
                continue

            alvo.take_damage(DASH_DAMAGE)
            alvo.apply_knockback(direcao, DASH_KNOCKBACK)
            self._alvos_atingidos.add(alvo_id)

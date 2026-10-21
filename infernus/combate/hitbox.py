import pygame


DASH_HITBOX_WIDTH = 48
DASH_HITBOX_HEIGHT = 48
DASH_HITBOX_GAP = 4


class HitboxDash:
    def __init__(self):
        self.rect = None

    def atualizar(self, jogador_rect, direcao, ativa):
        if not ativa:
            self.rect = None
            return

        self.rect = pygame.Rect(
            0,
            0,
            DASH_HITBOX_WIDTH,
            DASH_HITBOX_HEIGHT,
        )
        self.rect.centery = jogador_rect.centery
        if direcao > 0:
            self.rect.left = jogador_rect.right + DASH_HITBOX_GAP
        else:
            self.rect.right = jogador_rect.left - DASH_HITBOX_GAP

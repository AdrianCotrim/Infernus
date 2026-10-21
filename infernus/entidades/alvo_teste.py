import pygame


KNOCKBACK_DECELERATION = 1200


class AlvoTeste:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 40, 50)
        self.vida = 3
        self.velocidade_knockback_x = 0.0

    def take_damage(self, amount):
        self.vida = max(0, self.vida - amount)

    def apply_knockback(self, direction, force):
        self.velocidade_knockback_x = direction * force

    def atualizar(self, dt):
        self.rect.x += round(self.velocidade_knockback_x * dt)
        if self.velocidade_knockback_x > 0:
            self.velocidade_knockback_x = max(
                0.0,
                self.velocidade_knockback_x - KNOCKBACK_DECELERATION * dt,
            )
        elif self.velocidade_knockback_x < 0:
            self.velocidade_knockback_x = min(
                0.0,
                self.velocidade_knockback_x + KNOCKBACK_DECELERATION * dt,
            )

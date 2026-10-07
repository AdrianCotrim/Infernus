import pygame

from combate import DASH_DAMAGE, DASH_KNOCKBACK, SistemaAtaqueDash
from hitbox import HitboxDash
from jogador import DASH_DURATION, EstadoJogador, Jogador
from alvo_teste import AlvoTeste


class DummyTarget:
    def __init__(self, rect):
        self.rect = rect
        self.damage_taken = []
        self.knockbacks = []

    def take_damage(self, amount):
        self.damage_taken.append(amount)

    def apply_knockback(self, direction, force):
        self.knockbacks.append((direction, force))


def test_hitbox_exists_only_while_active_and_faces_forward():
    hitbox = HitboxDash()
    player_rect = pygame.Rect(100, 100, 40, 60)

    hitbox.atualizar(player_rect, 1, ativa=False)
    assert hitbox.rect is None

    hitbox.atualizar(player_rect, 1, ativa=True)
    assert hitbox.rect is not player_rect
    assert hitbox.rect.left >= player_rect.right
    assert hitbox.rect.centery == player_rect.centery

    hitbox.atualizar(player_rect, -1, ativa=True)
    assert hitbox.rect.right <= player_rect.left
    assert hitbox.rect.centery == player_rect.centery

    hitbox.atualizar(player_rect, -1, ativa=False)
    assert hitbox.rect is None


def test_hitbox_can_hit_target_without_physical_player_collision():
    player_rect = pygame.Rect(100, 100, 40, 60)
    hitbox = HitboxDash()
    hitbox.atualizar(player_rect, 1, ativa=True)
    target = DummyTarget(pygame.Rect(hitbox.rect.x, hitbox.rect.y, 20, 20))
    system = SistemaAtaqueDash()

    assert not player_rect.colliderect(target.rect)
    assert hitbox.rect.colliderect(target.rect)

    system.atualizar(hitbox.rect, 1, [target])

    assert target.damage_taken == [DASH_DAMAGE]
    assert target.knockbacks == [(1, DASH_KNOCKBACK)]


def test_target_is_hit_only_once_per_dash_and_can_be_hit_again_afterward():
    hitbox = HitboxDash()
    player_rect = pygame.Rect(100, 100, 40, 60)
    hitbox.atualizar(player_rect, -1, ativa=True)
    target = DummyTarget(pygame.Rect(hitbox.rect.x, hitbox.rect.y, 20, 20))
    system = SistemaAtaqueDash()

    system.atualizar(hitbox.rect, -1, [target])
    system.atualizar(hitbox.rect, -1, [target])
    assert target.damage_taken == [DASH_DAMAGE]
    assert target.knockbacks == [(-1, DASH_KNOCKBACK)]

    system.atualizar(None, -1, [target])
    system.atualizar(hitbox.rect, -1, [target])

    assert target.damage_taken == [DASH_DAMAGE, DASH_DAMAGE]
    assert target.knockbacks == [(-1, DASH_KNOCKBACK), (-1, DASH_KNOCKBACK)]


def test_dash_hits_a_target_during_gameplay_updates():
    player = Jogador(100, 100)
    player.iniciar_dash()
    target = DummyTarget(pygame.Rect(310, 110, 40, 50))
    hitbox = HitboxDash()
    attack_system = SistemaAtaqueDash()

    for _ in range(8):
        player.atualizar({}, [], 800, dt=DASH_DURATION / 9)
        hitbox.atualizar(
            player.rect,
            player.direcao_dash,
            player.estado is EstadoJogador.DASHING,
        )
        attack_system.atualizar(hitbox.rect, player.direcao_dash, [target])

    assert target.damage_taken == [DASH_DAMAGE]
    assert target.knockbacks == [(1, DASH_KNOCKBACK)]


def test_dash_knockback_is_target_velocity_and_moves_target_over_time():
    player_rect = pygame.Rect(100, 100, 40, 60)
    hitbox = HitboxDash()
    hitbox.atualizar(player_rect, 1, ativa=True)
    target = AlvoTeste(hitbox.rect.x, hitbox.rect.y)
    initial_x = target.rect.x
    attack_system = SistemaAtaqueDash()

    attack_system.atualizar(hitbox.rect, 1, [target])

    assert target.vida == 3 - DASH_DAMAGE
    assert target.velocidade_knockback_x == DASH_KNOCKBACK

    target.atualizar(0.05)

    assert target.rect.x > initial_x
    assert 0 < target.velocidade_knockback_x < DASH_KNOCKBACK


def test_dash_knockback_velocity_follows_leftward_dash():
    target = AlvoTeste(100, 100)

    target.apply_knockback(-1, DASH_KNOCKBACK)

    assert target.velocidade_knockback_x == -DASH_KNOCKBACK

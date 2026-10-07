import pygame

from inimigo import (
    ENEMY_ATTACK_COOLDOWN,
    ENEMY_SPEED,
    STUN_DURATION,
    EstadoInimigo,
    Inimigo,
)
from jogador import Jogador, PARRY_DURATION
from sistema_parry import ResultadoAtaque, SistemaParry


def test_attack_during_parry_does_not_damage_player_and_stuns_enemy():
    player = Jogador(100, 100)
    enemy = Inimigo(140, 105)
    system = SistemaParry()
    player.iniciar_parry()
    attack_rect = enemy.atualizar(0.05, player.rect)

    result = system.resolver(attack_rect, player, enemy)

    assert attack_rect is not None
    assert result is ResultadoAtaque.APARADO
    assert player.vida == 5
    assert enemy.estado is EstadoInimigo.STUNNED
    assert enemy.tempo_atordoado == STUN_DURATION


def test_attack_outside_parry_window_damages_player_without_stunning_enemy():
    player = Jogador(100, 100)
    enemy = Inimigo(140, 105)
    attack_rect = pygame.Rect(player.rect.x, player.rect.y, 20, 20)
    system = SistemaParry()
    player.iniciar_parry()
    player.atualizar(
        {},
        [],
        800,
        dt=PARRY_DURATION,
    )

    result = system.resolver(attack_rect, player, enemy)

    assert result is ResultadoAtaque.DANO
    assert player.vida == 4
    assert enemy.estado is EstadoInimigo.NORMAL


def test_non_colliding_enemy_attack_has_no_effect():
    player = Jogador(100, 100)
    enemy = Inimigo(140, 105)
    system = SistemaParry()

    result = system.resolver(pygame.Rect(500, 500, 20, 20), player, enemy)

    assert result is ResultadoAtaque.SEM_ACERTO
    assert player.vida == 5
    assert enemy.estado is EstadoInimigo.NORMAL


def test_stunned_enemy_neither_moves_nor_attacks_until_stun_expires():
    player = pygame.Rect(200, 100, 40, 60)
    enemy = Inimigo(150, 105)
    enemy.aplicar_stun(STUN_DURATION)
    initial_rect = enemy.rect.copy()
    enemy.tempo_ataque = 0

    attack = enemy.atualizar(STUN_DURATION / 2, player)

    assert enemy.estado is EstadoInimigo.STUNNED
    assert enemy.rect == initial_rect
    assert attack is None

    attack = enemy.atualizar(STUN_DURATION / 2, player)

    assert enemy.estado is EstadoInimigo.NORMAL
    assert enemy.rect == initial_rect
    assert attack is None


def test_enemy_moves_toward_player_and_attacks_when_in_range():
    player = pygame.Rect(200, 100, 40, 60)
    enemy = Inimigo(100, 105)
    enemy.tempo_ataque = ENEMY_ATTACK_COOLDOWN
    enemy.atualizar(0.5, player)

    assert enemy.rect.x == 100 + round(ENEMY_SPEED * 0.5)

    enemy.rect.x = player.left - enemy.rect.width - 2
    enemy.tempo_ataque = 0
    attack = enemy.atualizar(0, player)

    assert attack is not None
    assert attack.colliderect(player)

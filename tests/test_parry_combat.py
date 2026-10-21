import pygame

from infernus.entidades.inimigo import (
    ENEMY_ATTACK_COOLDOWN,
    ENEMY_ATTACK_DURATION,
    ENEMY_ATTACK_RECOVERY,
    ENEMY_ATTACK_WINDUP,
    ENEMY_SPEED,
    MAX_ENEMY_HEALTH,
    STUN_DURATION,
    EstadoInimigo,
    Inimigo,
)
from infernus.entidades.jogador import EstadoJogador, Jogador, PARRY_DURATION
from infernus.combate.parry import ResultadoAtaque, SistemaParry


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
    assert not enemy.piscando_preparacao


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
    assert player.estado is EstadoJogador.KNOCKBACK
    assert player.velocidade_knockback_x < 0
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


def test_enemy_damage_and_knockback_stop_its_ai_until_impulse_ends():
    player = pygame.Rect(200, 100, 40, 60)
    enemy = Inimigo(150, 105)
    enemy.take_damage(1)
    enemy.apply_knockback(-1, 360)
    initial_x = enemy.rect.x

    attack = enemy.atualizar(0.05, player)

    assert enemy.vida == 2
    assert enemy.rect.x < initial_x
    assert attack is None


def test_windup_flashes_faster_then_resets_when_attack_starts():
    player = pygame.Rect(200, 100, 40, 60)
    enemy = Inimigo(180, 105)
    initial_rect = enemy.rect.copy()

    enemy.atualizar(0, player)
    assert enemy.estado is EstadoInimigo.ATTACK_WINDUP
    assert not enemy.piscando_preparacao

    enemy.atualizar(0.2, player)
    assert enemy.piscando_preparacao
    enemy.atualizar(0.15, player)
    assert not enemy.piscando_preparacao
    enemy.atualizar(0.1, player)
    assert enemy.piscando_preparacao
    assert enemy.rect == initial_rect

    enemy.atualizar(ENEMY_ATTACK_WINDUP - 0.45, player)
    assert enemy.estado is EstadoInimigo.ATTACK
    assert not enemy.piscando_preparacao

    enemy.atualizar(ENEMY_ATTACK_DURATION, player)
    assert enemy.estado is EstadoInimigo.ATTACK_RECOVERY
    assert not enemy.piscando_preparacao
    enemy.atualizar(ENEMY_ATTACK_RECOVERY, player)
    assert enemy.estado is EstadoInimigo.NORMAL
    assert not enemy.piscando_preparacao


def test_windup_flash_stops_on_stun_and_restarts_for_a_new_windup():
    player = pygame.Rect(200, 100, 40, 60)
    enemy = Inimigo(180, 105)

    enemy.atualizar(0, player)
    enemy.atualizar(0.2, player)
    assert enemy.piscando_preparacao

    enemy.aplicar_stun()
    assert not enemy.piscando_preparacao
    enemy.atualizar(STUN_DURATION, player)
    enemy.atualizar(0, player)
    assert enemy.estado is EstadoInimigo.ATTACK_WINDUP
    assert enemy.tempo_preparacao == 0
    assert enemy.tempo_flash_preparacao == 0
    assert not enemy.piscando_preparacao


def test_windup_flash_stops_when_enemy_dies():
    player = pygame.Rect(200, 100, 40, 60)
    enemy = Inimigo(180, 105)

    enemy.atualizar(0, player)
    enemy.atualizar(0.2, player)
    assert enemy.piscando_preparacao

    enemy.take_damage(MAX_ENEMY_HEALTH)

    assert enemy.estado is EstadoInimigo.DEAD
    assert not enemy.piscando_preparacao
    assert enemy.atualizar(0.2, player) is None

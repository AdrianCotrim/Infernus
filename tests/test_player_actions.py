import pygame
import pytest

from jogador import (
    DASH_COOLDOWN,
    DASH_DURATION,
    PLAYER_DASH_SPEED,
    PLAYER_SPEED,
    PARRY_DURATION,
    EstadoJogador,
    Jogador,
)


def test_player_starts_in_normal_state():
    player = Jogador(100, 100)

    assert player.estado is EstadoJogador.NORMAL


def test_normal_movement_and_jump_remain_available():
    player = Jogador(100, 100)
    player.atualizar({pygame.K_d: True}, [], 800)

    assert player.rect.x == 100 + PLAYER_SPEED

    player.registrar_pulo()
    player.atualizar({}, [], 800)

    assert player.velocidade_y < 0
    assert player.estado is EstadoJogador.NORMAL


def test_dash_moves_in_the_facing_direction_and_expires():
    player = Jogador(300, 100)
    player.atualizar({pygame.K_a: True}, [], 800)
    start_x = player.rect.x

    player.iniciar_dash()
    player.atualizar({pygame.K_d: True}, [], 800, dt=DASH_DURATION / 2)

    assert player.rect.x == start_x - round(PLAYER_DASH_SPEED * DASH_DURATION / 2)
    assert player.estado is EstadoJogador.DASHING

    player.atualizar({}, [], 800, dt=DASH_DURATION / 2)

    assert player.rect.x == start_x - round(PLAYER_DASH_SPEED * DASH_DURATION)
    assert player.estado is EstadoJogador.NORMAL


def test_dash_moves_right_by_default():
    player = Jogador(100, 100)

    player.iniciar_dash()
    player.atualizar({}, [], 800, dt=DASH_DURATION / 2)

    assert player.rect.x == 100 + round(PLAYER_DASH_SPEED * DASH_DURATION / 2)
    assert player.estado is EstadoJogador.DASHING


def test_dash_does_not_restart_while_active():
    player = Jogador(100, 100)
    player.iniciar_dash()
    player.atualizar({}, [], 800, dt=DASH_DURATION / 2)

    remaining_time = player.tempo_estado
    player.iniciar_dash()

    assert player.estado is EstadoJogador.DASHING
    assert player.tempo_estado == pytest.approx(remaining_time)


def test_dash_does_not_move_beyond_its_remaining_duration():
    player = Jogador(100, 100)
    player.iniciar_dash()
    player.atualizar({}, [], 800, dt=DASH_DURATION * 2)

    assert player.rect.x == 100 + round(PLAYER_DASH_SPEED * DASH_DURATION)
    assert player.estado is EstadoJogador.NORMAL


def test_dash_distance_is_consistent_across_update_rates():
    single_update = Jogador(300, 100)
    single_update.iniciar_dash()
    single_update.atualizar({}, [], 800, dt=DASH_DURATION)

    multiple_updates = Jogador(300, 100)
    multiple_updates.iniciar_dash()
    for _ in range(10):
        multiple_updates.atualizar({}, [], 800, dt=DASH_DURATION / 10)

    assert multiple_updates.rect.x == single_update.rect.x


def test_dash_movement_does_not_change_when_hitbox_is_not_used():
    player_with_hitbox = Jogador(300, 100)
    player_without_hitbox = Jogador(300, 100)
    player_with_hitbox.iniciar_dash()
    player_without_hitbox.iniciar_dash()

    for _ in range(4):
        player_with_hitbox.atualizar({}, [], 800, dt=DASH_DURATION / 4)
        player_without_hitbox.atualizar({}, [], 800, dt=DASH_DURATION / 4)

    assert player_with_hitbox.rect == player_without_hitbox.rect


def test_parry_expires_after_its_activation_window_and_keeps_movement():
    player = Jogador(100, 100)

    player.iniciar_parry()
    player.atualizar({pygame.K_d: True}, [], 800, dt=PARRY_DURATION / 2)

    assert player.estado is EstadoJogador.PARRYING
    assert player.rect.x == 100 + PLAYER_SPEED

    player.atualizar({}, [], 800, dt=PARRY_DURATION / 2)

    assert player.estado is EstadoJogador.NORMAL


def test_parry_cannot_be_restarted_while_active():
    player = Jogador(100, 100)
    player.iniciar_parry()
    player.atualizar({}, [], 800, dt=PARRY_DURATION / 2)

    remaining_time = player.tempo_estado
    player.iniciar_parry()

    assert player.estado is EstadoJogador.PARRYING
    assert player.tempo_estado == pytest.approx(remaining_time)

    player.atualizar({}, [], 800, dt=PARRY_DURATION / 2)

    assert player.estado is EstadoJogador.NORMAL


def test_parry_does_not_interrupt_an_active_dash():
    player = Jogador(100, 100)
    player.iniciar_dash()

    player.iniciar_parry()

    assert player.estado is EstadoJogador.DASHING


def test_actions_cannot_replace_an_active_action():
    player = Jogador(100, 100)

    player.iniciar_dash()
    player.iniciar_parry()

    assert player.estado is EstadoJogador.DASHING
    assert player.tempo_estado == pytest.approx(DASH_DURATION)


def test_dash_cannot_restart_immediately_after_dash_ends():
    player = Jogador(100, 100)
    player.iniciar_dash()
    assert player.dash_cooldown_timer == DASH_COOLDOWN

    player.atualizar({}, [], 800, dt=DASH_DURATION)

    assert player.estado is EstadoJogador.NORMAL
    assert not player.dash_disponivel

    player.iniciar_dash()

    assert player.estado is EstadoJogador.NORMAL


def test_dash_becomes_available_when_cooldown_expires():
    player = Jogador(100, 100)
    player.iniciar_dash()
    player.atualizar({}, [], 800, dt=DASH_COOLDOWN)

    assert player.dash_disponivel

    player.iniciar_dash()

    assert player.estado is EstadoJogador.DASHING


def test_repeated_dash_requests_during_cooldown_are_not_queued():
    player = Jogador(100, 100)
    player.iniciar_dash()
    player.atualizar({}, [], 800, dt=DASH_DURATION)

    for _ in range(5):
        player.iniciar_dash()
        player.atualizar({}, [], 800, dt=(DASH_COOLDOWN - DASH_DURATION) / 5)

    assert player.dash_disponivel
    assert player.estado is EstadoJogador.NORMAL

    player.atualizar({}, [], 800, dt=0)
    assert player.estado is EstadoJogador.NORMAL

    player.iniciar_dash()
    assert player.estado is EstadoJogador.DASHING


def test_cooldown_does_not_block_movement_jump_or_parry():
    player = Jogador(100, 100)
    player.iniciar_dash()
    player.atualizar({}, [], 800, dt=DASH_DURATION)
    start_x = player.rect.x

    player.atualizar({pygame.K_d: True}, [], 800, dt=0)
    assert player.rect.x == start_x + PLAYER_SPEED

    player.registrar_pulo()
    player.atualizar({}, [], 800, dt=0)
    assert player.velocidade_y < 0

    player.iniciar_parry()
    assert player.estado is EstadoJogador.PARRYING
    assert not player.dash_disponivel

import pytest

from jogador import COYOTE_TIME, Jogador


def test_coyote_timer_starts_when_grounded():
    player = Jogador(0, 100)
    player.no_chao = True

    player.atualizar({}, [], 800, 0.016)

    assert player.coyote_timer == pytest.approx(COYOTE_TIME)


def test_coyote_timer_is_consumed_by_jump():
    player = Jogador(0, 100)
    player.no_chao = False
    player.coyote_timer = 0.08
    player.registrar_pulo()

    player.atualizar({}, [], 800, 0.016)

    assert player.velocidade_y < 0
    assert player.coyote_timer == 0.0

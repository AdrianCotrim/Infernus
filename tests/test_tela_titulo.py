import pygame
import pytest

from tela_titulo import (
    DURACAO_ENTRADA,
    DURACAO_SAIDA,
    FORCA_SEGUNDA_BATIDA,
    PRIMEIRA_BATIDA,
    TelaTitulo,
    altura_ecg,
    batidas,
    intensidade_batida,
)


def test_silence_before_first_heartbeat():
    assert batidas(PRIMEIRA_BATIDA - 0.01, 2.0) == []
    assert intensidade_batida(PRIMEIRA_BATIDA - 0.01) == 0
    assert altura_ecg(PRIMEIRA_BATIDA - 0.01) == 0


def test_each_heartbeat_has_a_weaker_second_beat():
    recentes = batidas(PRIMEIRA_BATIDA + 0.3, 1.0)

    assert [forca for _, forca in recentes] == [1.0, FORCA_SEGUNDA_BATIDA]


def test_heartbeat_window_only_returns_recent_beats():
    tempo = 600.0
    recentes = batidas(tempo, 1.0)

    assert recentes
    assert all(tempo - 1.0 <= instante <= tempo for instante, _ in recentes)


def test_screen_fades_in_from_black():
    tela = TelaTitulo()

    assert tela.opacidade_preto == 1

    tela.atualizar(DURACAO_ENTRADA / 2)

    assert 0 < tela.opacidade_preto < 1

    tela.atualizar(DURACAO_ENTRADA / 2)

    assert tela.opacidade_preto == 0


def test_button_fades_out_and_finishes():
    tela = TelaTitulo()
    tela.atualizar(DURACAO_ENTRADA)
    tela.processar_botao()
    tela.atualizar(DURACAO_SAIDA / 2)

    assert tela.saindo
    assert not tela.concluida
    assert 0 < tela.opacidade_preto < 1

    tela.atualizar(DURACAO_SAIDA / 2)

    assert tela.concluida
    assert tela.opacidade_preto == 1


def test_button_during_fade_in_never_brightens_screen():
    tela = TelaTitulo()
    tela.atualizar(DURACAO_ENTRADA / 4)
    antes = tela.opacidade_preto
    tela.processar_botao()
    tela.atualizar(0.01)

    assert tela.opacidade_preto >= antes - 0.05


@pytest.mark.parametrize("tempo", [0.0, 0.6, DURACAO_ENTRADA, 5.0, 30.0])
def test_title_screen_renders_at_every_stage(tempo):
    pygame.font.init()
    tela = pygame.Surface((1280, 720))
    tela_titulo = TelaTitulo()
    tela_titulo.atualizar(tempo)

    tela_titulo.desenhar(tela)

    if tempo >= DURACAO_ENTRADA:
        assert tela.get_at((0, 0))[:3] != (0, 0, 0)

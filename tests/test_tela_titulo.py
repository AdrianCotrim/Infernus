import pygame
import pytest

from tela_titulo import (
    DURACAO_SAIDA,
    FORCA_SEGUNDA_BATIDA,
    INSTANTE_AVISO,
    INSTANTE_TITULO,
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


def test_title_appears_on_third_heartbeat():
    tela = TelaTitulo()
    tela.atualizar(INSTANTE_TITULO - 0.01)

    assert not tela.titulo_visivel

    tela.atualizar(0.02)

    assert tela.titulo_visivel
    assert not tela.aviso_visivel


def test_button_during_intro_skips_to_full_title():
    tela = TelaTitulo()
    tela.atualizar(0.5)
    tela.processar_botao()

    assert tela.titulo_visivel
    assert tela.aviso_visivel
    assert not tela.saindo


def test_button_with_prompt_visible_fades_out_and_finishes():
    tela = TelaTitulo()
    tela.atualizar(INSTANTE_AVISO)
    tela.processar_botao()
    tela.atualizar(DURACAO_SAIDA / 2)

    assert tela.saindo
    assert not tela.concluida

    tela.atualizar(DURACAO_SAIDA / 2)

    assert tela.concluida


@pytest.mark.parametrize("tempo", [0.0, 0.6, INSTANTE_TITULO, INSTANTE_AVISO, 30.0])
def test_title_screen_renders_at_every_stage(tempo):
    pygame.font.init()
    tela = pygame.Surface((1280, 720))
    tela_titulo = TelaTitulo()
    tela_titulo.atualizar(tempo)

    tela_titulo.desenhar(tela)

    assert tela.get_at((0, 0))[:3] != (0, 0, 0)

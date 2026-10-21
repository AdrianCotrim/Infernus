import pygame

from infernus.config import ALTURA_TELA, LARGURA_TELA, TITULO_JANELA
from infernus.fases.fase_teste import executar_fase_teste
from infernus.telas.titulo import executar_tela_titulo


def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption(TITULO_JANELA)
    relogio = pygame.time.Clock()

    if executar_tela_titulo(tela, relogio):
        executar_fase_teste(tela, relogio)

    pygame.quit()

import pygame

from jogador import PLAYER_HEIGHT, PLAYER_WIDTH, Jogador

WIDTH = 1280
HEIGHT = 720

PLATFORM_WIDTH = WIDTH
PLATFORM_HEIGHT = 32
PLATFORM_Y = HEIGHT - 100


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Infernus Prototype")
    clock = pygame.time.Clock()
    running = True

    player = Jogador(
        WIDTH // 2 - PLAYER_WIDTH // 2,
        PLATFORM_Y - PLAYER_HEIGHT,
    )
    platform = pygame.Rect(0, PLATFORM_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.registrar_pulo()

        keys = pygame.key.get_pressed()
        player.atualizar(keys, platform, WIDTH)

        screen.fill((20, 20, 30))
        pygame.draw.rect(screen, (220, 220, 220), platform)
        pygame.draw.rect(screen, (255, 220, 60), player.rect)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
import pygame


def main():
    pygame.init()
    screen = pygame.display.set_mode((960, 540))
    pygame.display.set_caption("Infernus")
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((24, 27, 32))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
import pygame


def main():
    pygame.init()

    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
    pygame.display.set_caption("Infernus")
    clock = pygame.time.Clock()
    running = True
    fullscreen = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    fullscreen = not fullscreen
                    if fullscreen:
                        screen = pygame.display.set_mode(
                            (info.current_w, info.current_h), pygame.FULLSCREEN
                        )
                    else:
                        screen = pygame.display.set_mode((1280, 720))

        screen.fill((24, 27, 32))
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
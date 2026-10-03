import pygame

WIDTH = 1280
HEIGHT = 720
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 6
GRAVITY = 0.7
JUMP_FORCE = 15

PLATFORM_WIDTH = WIDTH
PLATFORM_HEIGHT = 32
PLATFORM_Y = HEIGHT - 100


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Infernus Prototype")
    clock = pygame.time.Clock()
    running = True

    player = pygame.Rect(
        WIDTH // 2 - PLAYER_WIDTH // 2,
        PLATFORM_Y - PLAYER_HEIGHT - 50,
        PLAYER_WIDTH,
        PLAYER_HEIGHT,
    )
    platform = pygame.Rect(0, PLATFORM_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT)

    player_vx = 0
    player_vy = 0
    on_ground = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and on_ground:
                    player_vy = -JUMP_FORCE
                    on_ground = False

        keys = pygame.key.get_pressed()

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            player_vx = -PLAYER_SPEED
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            player_vx = PLAYER_SPEED
        else:
            player_vx = 0

        player.x += player_vx
        player.x = max(0, min(WIDTH - player.width, player.x))

        player_vy += GRAVITY
        player.y += player_vy

        on_ground = False
        if player.colliderect(platform):
            if player_vy >= 0 and player.bottom >= platform.top and player.bottom <= platform.top + 30:
                player.bottom = platform.top
                player_vy = 0
                on_ground = True

        screen.fill((20, 20, 30))
        pygame.draw.rect(screen, (220, 220, 220), platform)
        pygame.draw.rect(screen, (255, 220, 60), player)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
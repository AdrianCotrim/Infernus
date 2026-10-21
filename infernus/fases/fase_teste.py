import pygame

from infernus.combate.ataque_dash import SistemaAtaqueDash
from infernus.combate.hitbox import HitboxDash
from infernus.combate.parry import ResultadoAtaque, SistemaParry
from infernus.config import ALTURA_TELA, FPS, LARGURA_TELA
from infernus.entidades.alvo_teste import AlvoTeste
from infernus.entidades.inimigo import ENEMY_CONTACT_DAMAGE, EstadoInimigo, Inimigo
from infernus.entidades.jogador import EstadoJogador, PLAYER_HEIGHT, PLAYER_WIDTH, Jogador

WIDTH = LARGURA_TELA
HEIGHT = ALTURA_TELA
PLAYER_COLOR = (255, 220, 60)
DASH_COLOR = (60, 220, 255)
DASH_COOLDOWN_COLOR = (255, 150, 70)
PARRY_COLOR = (255, 80, 220)
DASH_HITBOX_COLOR = (255, 60, 80, 110)
TEST_TARGET_COLOR = (180, 80, 220)
ENEMY_COLOR = (210, 75, 85)
STUNNED_ENEMY_COLOR = (255, 235, 80)
ENEMY_WINDUP_FLASH_COLOR = (255, 255, 255)
ENEMY_ATTACK_COLOR = (255, 120, 60, 120)

PLATFORM_WIDTH = WIDTH
PLATFORM_HEIGHT = 32
PLATFORM_Y = HEIGHT - 100


def executar_fase_teste(screen, clock):
    """Fase de testes do combate. Roda até a janela ser fechada."""
    running = True

    player = Jogador(
        WIDTH // 2 - PLAYER_WIDTH // 2,
        PLATFORM_Y - PLAYER_HEIGHT,
    )
    dash_hitbox = HitboxDash()
    dash_attack = SistemaAtaqueDash()
    test_target = AlvoTeste(WIDTH // 2 + 190, PLATFORM_Y - 50)
    enemy = Inimigo(WIDTH // 2 - 220, PLATFORM_Y - 50)
    parry_system = SistemaParry()
    target_font = pygame.font.Font(None, 24)
    platforms = [
        pygame.Rect(0, PLATFORM_Y, PLATFORM_WIDTH, PLATFORM_HEIGHT),
        pygame.Rect(500, 510, 220, PLATFORM_HEIGHT),
        pygame.Rect(700, 405, 220, PLATFORM_HEIGHT),
        pygame.Rect(500, 300, 220, PLATFORM_HEIGHT),
        pygame.Rect(700, 195, 220, PLATFORM_HEIGHT),
    ]

    while running:
        dt = clock.tick(FPS) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.registrar_pulo()
                elif event.key == pygame.K_e:
                    player.iniciar_dash()
                elif event.key in (pygame.K_UP, pygame.K_w):
                    player.iniciar_parry()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    player.soltar_pulo()

        keys = pygame.key.get_pressed()
        player.atualizar(keys, platforms, WIDTH, dt)
        dash_hitbox.atualizar(
            player.rect,
            player.direcao_dash,
            player.estado is EstadoJogador.DASHING,
        )
        dash_acertou = dash_attack.atualizar(
            dash_hitbox.rect,
            player.direcao_dash,
            [enemy],
            player.rect,
        )
        if dash_acertou:
            player.interromper_dash()
        test_target.atualizar(dt)
        enemy_attack = enemy.atualizar(dt, player.rect)
        if enemy.rect.colliderect(player.rect) and enemy.vivo and enemy.contato_cooldown == 0:
            player.take_damage(
                ENEMY_CONTACT_DAMAGE,
                1 if enemy.rect.centerx < player.rect.centerx else -1,
            )
            enemy.contato_cooldown = 0.5
        attack_result = parry_system.resolver(enemy_attack, player, enemy)

        screen.fill((20, 20, 30))
        for platform in platforms:
            pygame.draw.rect(screen, (220, 220, 220), platform)
        pygame.draw.rect(screen, TEST_TARGET_COLOR, test_target.rect)
        enemy_color = (
            STUNNED_ENEMY_COLOR
            if enemy.estado is EstadoInimigo.STUNNED
            else ENEMY_WINDUP_FLASH_COLOR
            if enemy.piscando_preparacao
            else ENEMY_COLOR
        )
        pygame.draw.rect(screen, enemy_color, enemy.rect)
        if enemy_attack is not None:
            attack_surface = pygame.Surface(enemy_attack.size, pygame.SRCALPHA)
            attack_surface.fill(ENEMY_ATTACK_COLOR)
            screen.blit(attack_surface, enemy_attack)
        player_color = PLAYER_COLOR
        if player.estado is EstadoJogador.DASHING:
            player_color = DASH_COLOR
        elif player.estado is EstadoJogador.PARRYING:
            player_color = PARRY_COLOR
        elif player.estado is EstadoJogador.KNOCKBACK:
            player_color = ENEMY_ATTACK_COLOR[:3]
        elif not player.dash_disponivel:
            player_color = DASH_COOLDOWN_COLOR
        if player.invulneravel and player.piscando:
            player_color = (255, 255, 255)
        pygame.draw.rect(screen, player_color, player.rect)
        if dash_hitbox.rect is not None:
            hitbox_surface = pygame.Surface(
                dash_hitbox.rect.size,
                pygame.SRCALPHA,
            )
            hitbox_surface.fill(DASH_HITBOX_COLOR)
            screen.blit(hitbox_surface, dash_hitbox.rect)
        target_text = target_font.render(
            f"Alvo de teste: {test_target.vida} HP",
            True,
            (255, 255, 255),
        )
        screen.blit(target_text, (test_target.rect.x - 24, test_target.rect.y - 24))
        player_text = target_font.render(
            f"Jogador: {player.vida} HP",
            True,
            (255, 255, 255),
        )
        screen.blit(player_text, (20, 20))
        if attack_result is ResultadoAtaque.APARADO:
            parry_text = target_font.render("PARRY!", True, PARRY_COLOR)
            screen.blit(parry_text, (player.rect.x, player.rect.y - 24))
        pygame.display.flip()

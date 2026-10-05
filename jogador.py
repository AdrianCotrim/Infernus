import pygame


PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 6
GRAVITY = 0.7
JUMP_FORCE = 15
JUMP_BUFFER_TIME = 0.12


class Jogador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocidade_y = 0
        self.no_chao = True
        self.jump_buffer_started_at = None

    def registrar_pulo(self):
        self.jump_buffer_started_at = pygame.time.get_ticks()

    def _consumir_buffer_se_puder_pular(self):
        if self.jump_buffer_started_at is None:
            return

        elapsed = pygame.time.get_ticks() - self.jump_buffer_started_at
        if elapsed >= JUMP_BUFFER_TIME * 1000:
            self.jump_buffer_started_at = None
            return

        if self.no_chao:
            self.velocidade_y = -JUMP_FORCE
            self.no_chao = False
            self.jump_buffer_started_at = None

    def atualizar(self, teclas, plataforma, largura_tela):
        if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
            velocidade_x = -PLAYER_SPEED
        elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
            velocidade_x = PLAYER_SPEED
        else:
            velocidade_x = 0

        self.rect.x += velocidade_x
        self.rect.x = max(0, min(largura_tela - self.rect.width, self.rect.x))

        self._consumir_buffer_se_puder_pular()

        self.velocidade_y += GRAVITY
        self.rect.y += self.velocidade_y

        self.no_chao = False
        if self.rect.colliderect(plataforma):
            if (
                self.velocidade_y >= 0
                and self.rect.bottom >= plataforma.top
                and self.rect.bottom <= plataforma.top + 30
            ):
                self.rect.bottom = plataforma.top
                self.velocidade_y = 0
                self.no_chao = True

        self._consumir_buffer_se_puder_pular()

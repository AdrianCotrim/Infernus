import pygame


PLAYER_WIDTH = 40
PLAYER_HEIGHT = 60
PLAYER_SPEED = 6
GRAVITY = 0.7
JUMP_FORCE = 15
COYOTE_TIME = 0.10
JUMP_BUFFER_TIME = 0.12
JUMP_HOLD_TIME = 0.15
JUMP_CUT_MULTIPLIER = 0.5


class Jogador:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.velocidade_y = 0
        self.no_chao = True
        self.coyote_timer = 0.0
        self.jump_buffer_started_at = None
        self.jump_held = False
        self.jump_started_at = None

    def registrar_pulo(self):
        self.jump_held = True
        self.jump_buffer_started_at = pygame.time.get_ticks()

    def soltar_pulo(self):
        self.jump_held = False
        if self.jump_started_at is None or self.velocidade_y >= 0:
            return

        elapsed = pygame.time.get_ticks() - self.jump_started_at
        if elapsed < JUMP_HOLD_TIME * 1000:
            self.velocidade_y *= JUMP_CUT_MULTIPLIER

    def _iniciar_pulo(self):
        self.velocidade_y = -JUMP_FORCE
        self.no_chao = False
        self.coyote_timer = 0.0
        self.jump_started_at = pygame.time.get_ticks()
        if not self.jump_held:
            self.velocidade_y *= JUMP_CUT_MULTIPLIER

    def _pode_pular(self):
        return self.no_chao or self.coyote_timer > 0

    def _consumir_buffer_se_puder_pular(self):
        if self.jump_buffer_started_at is None:
            return

        elapsed = pygame.time.get_ticks() - self.jump_buffer_started_at
        if elapsed >= JUMP_BUFFER_TIME * 1000:
            self.jump_buffer_started_at = None
            return

        if self._pode_pular():
            self._iniciar_pulo()
            self.jump_buffer_started_at = None

    def atualizar(self, teclas, plataformas, largura_tela, dt=1 / 60):
        def tecla_pressionada(chave):
            if isinstance(teclas, dict):
                return teclas.get(chave, False)
            return bool(teclas[chave])

        if tecla_pressionada(pygame.K_a) or tecla_pressionada(pygame.K_LEFT):
            velocidade_x = -PLAYER_SPEED
        elif tecla_pressionada(pygame.K_d) or tecla_pressionada(pygame.K_RIGHT):
            velocidade_x = PLAYER_SPEED
        else:
            velocidade_x = 0

        self.rect.x += velocidade_x
        self.rect.x = max(0, min(largura_tela - self.rect.width, self.rect.x))

        if self.no_chao:
            self.coyote_timer = COYOTE_TIME
        elif self.coyote_timer > 0:
            self.coyote_timer = max(0.0, self.coyote_timer - dt)
        else:
            self.coyote_timer = 0.0

        self._consumir_buffer_se_puder_pular()

        self.velocidade_y += GRAVITY
        self.rect.y += self.velocidade_y

        self.no_chao = False
        for plataforma in plataformas:
            if (
                self.rect.colliderect(plataforma)
                and self.velocidade_y >= 0
                and self.rect.bottom >= plataforma.top
                and self.rect.bottom <= plataforma.top + 30
            ):
                self.rect.bottom = plataforma.top
                self.velocidade_y = 0
                self.no_chao = True
                break

        if self.no_chao:
            self.coyote_timer = COYOTE_TIME

        self._consumir_buffer_se_puder_pular()

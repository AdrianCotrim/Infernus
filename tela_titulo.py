import bisect
import math
import random
from pathlib import Path

import pygame


LARGURA_BASE = 320
ALTURA_BASE = 180
LARGURA_REFERENCIA = 1280

PRIMEIRA_BATIDA = 1.2
INTERVALO_BATIDA = 0.86
ATRASO_SEGUNDA_BATIDA = 0.22
FORCA_SEGUNDA_BATIDA = 0.55
DURACAO_ENTRADA = 1.5
DURACAO_SAIDA = 0.5
VELOCIDADE_PULSO = 130
VELOCIDADE_ECG = 110
ALTURA_LINHA_ECG = 172
ALCANCE_PULSO = 21

CENTRO_CORACAO = (160, 116)
TAMANHO_CORACAO = 13

PASTA_FONTES = Path(__file__).parent / "assets" / "fonts"
FONTE_TITULO = PASTA_FONTES / "Jersey25-Regular.ttf"
FONTE_AVISO = PASTA_FONTES / "Silkscreen-Regular.ttf"
TEXTO_TITULO = "INFERNUS"
TEXTO_AVISO = "APERTE QUALQUER BOTÃO"

COR_FUNDO = (20, 6, 14)
COR_CAMARA_EXTERNA = (30, 9, 20)
COR_CAMARA = (40, 12, 26)
COR_BORDA_CAMARA = (58, 16, 36)
CORES_TEXTURA = ((26, 7, 15), (14, 4, 9))
CORES_PULSO = (
    (58, 16, 48),
    (110, 27, 46),
    (163, 35, 47),
    (224, 48, 62),
    (255, 138, 106),
)
COR_CONTORNO_CORACAO = (42, 12, 24)
CORES_CORACAO = ((255, 154, 138), (224, 80, 90), (184, 48, 60), (122, 28, 42))
COR_VEIA_CORACAO = (90, 30, 58)
COR_BRILHO = (255, 70, 60)
COR_ECG = (224, 48, 62)
COR_PONTA_ECG = (255, 138, 106)
COR_TITULO = (252, 227, 176)
SOMBRAS_TITULO = ((8, (194, 40, 58)), (16, (74, 12, 24)))
COR_MARCADOR_AVISO = (224, 48, 62)


def arredondar(valor):
    return math.floor(valor + 0.5)


def suavizar(progresso):
    progresso = min(1.0, max(0.0, progresso))
    return progresso * progresso * (3 - 2 * progresso)


def batidas(tempo, janela):
    """Batidas (instante, força) que aconteceram em [tempo - janela, tempo]."""
    if tempo < PRIMEIRA_BATIDA:
        return []

    inicio = tempo - janela
    primeira = max(
        0,
        math.floor(
            (inicio - ATRASO_SEGUNDA_BATIDA - PRIMEIRA_BATIDA) / INTERVALO_BATIDA
        ),
    )
    ultima = math.floor((tempo - PRIMEIRA_BATIDA) / INTERVALO_BATIDA)
    resultado = []
    for indice in range(primeira, ultima + 1):
        base = PRIMEIRA_BATIDA + indice * INTERVALO_BATIDA
        for instante, forca in (
            (base, 1.0),
            (base + ATRASO_SEGUNDA_BATIDA, FORCA_SEGUNDA_BATIDA),
        ):
            if inicio <= instante <= tempo:
                resultado.append((instante, forca))
    return resultado


def intensidade_batida(tempo):
    total = sum(
        forca * math.exp(-(tempo - instante) * 7)
        for instante, forca in batidas(tempo, 1.0)
    )
    return min(1.0, total)


def altura_ecg(tempo):
    altura = 0.0
    for instante, forca in batidas(tempo, 0.12):
        decorrido = tempo - instante
        if decorrido < 0.04:
            altura += forca * 9 * decorrido / 0.04
        elif decorrido < 0.08:
            altura += forca * (9 - 13 * (decorrido - 0.04) / 0.04)
        elif decorrido < 0.12:
            altura += forca * (-4 + 4 * (decorrido - 0.08) / 0.04)
    return altura


def _dentro_coracao(x, y):
    a = x * x + y * y - 1
    return a * a * a - x * x * y * y * y <= 0


def desenhar_coracao(tamanho):
    raio = math.ceil(tamanho * 1.4)
    superficie = pygame.Surface((raio * 2 + 1, raio * 2 + 1))
    superficie.fill((0, 0, 0))
    superficie.set_colorkey((0, 0, 0))

    def normalizado(px, py):
        return px / tamanho, -(py - tamanho * 0.15) / tamanho

    for py in range(-raio, raio + 1):
        for px in range(-raio, raio + 1):
            x, y = normalizado(px, py)
            if not _dentro_coracao(x, y):
                continue
            borda = not all(
                _dentro_coracao(*normalizado(px + dx, py + dy))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))
            )
            luz = -x * 0.6 + y * 0.8
            if borda:
                cor = COR_CONTORNO_CORACAO
            elif luz > 0.95:
                cor = CORES_CORACAO[0]
            elif luz > 0.45:
                cor = CORES_CORACAO[1]
            elif luz > -0.35:
                cor = CORES_CORACAO[2]
            else:
                cor = CORES_CORACAO[3]
            superficie.set_at((px + raio, py + raio), cor)

    for passo in range(arredondar(tamanho * 1.6)):
        x = arredondar(-2 + math.sin(passo * 0.5) * 2 - passo * 0.25)
        y = arredondar(-tamanho * 0.7 + passo)
        superficie.set_at((x + raio, y + raio), COR_VEIA_CORACAO)
    for passo in range(arredondar(tamanho * 1.1)):
        x = arredondar(4 + passo * 0.35 + math.sin(passo * 0.6))
        y = arredondar(-tamanho * 0.4 + passo)
        superficie.set_at((x + raio, y + raio), COR_VEIA_CORACAO)

    return superficie, raio


def desenhar_fundo(rng):
    fundo = pygame.Surface((LARGURA_BASE, ALTURA_BASE))
    fundo.fill(COR_FUNDO)
    for y in range(ALTURA_BASE):
        meia = arredondar(
            150 * math.sqrt(max(0, 1 - ((y - 95) / 100) ** 2)) + 4 * math.sin(y * 0.2)
        )
        if meia > 0:
            fundo.fill(COR_CAMARA_EXTERNA, (160 - meia, y, meia * 2, 1))
    for y in range(ALTURA_BASE):
        meia = arredondar(
            118 * math.sqrt(max(0, 1 - ((y - 95) / 82) ** 2))
            + 3 * math.sin(y * 0.3 + 1)
        )
        if meia > 0:
            fundo.fill(COR_CAMARA, (160 - meia, y, meia * 2, 1))
            fundo.set_at((160 - meia, y), COR_BORDA_CAMARA)
            fundo.set_at((160 + meia - 1, y), COR_BORDA_CAMARA)
    for _ in range(700):
        cor = CORES_TEXTURA[0] if rng.random() < 0.5 else CORES_TEXTURA[1]
        fundo.set_at(
            (int(rng.random() * LARGURA_BASE), int(rng.random() * ALTURA_BASE)), cor
        )
    return fundo


def gerar_veias(rng):
    """Pixels das veias como (x, y, distância até o coração, profundidade)."""
    veias = []
    centro_x, centro_y = CENTRO_CORACAO

    def crescer(x, y, angulo, comprimento, distancia, profundidade):
        passo = 0
        while passo < comprimento:
            angulo += (rng.random() - 0.5) * 0.35
            x += math.cos(angulo)
            y += math.sin(angulo)
            px, py = arredondar(x), arredondar(y)
            if not (0 <= px < LARGURA_BASE and 0 <= py < ALTURA_BASE):
                return
            veias.append((px, py, distancia + passo, profundidade))
            if profundidade < 2 and passo > 10 and rng.random() < 0.04:
                desvio = 0.7 if rng.random() < 0.5 else -0.7
                crescer(
                    x,
                    y,
                    angulo + desvio,
                    comprimento * 0.5,
                    distancia + passo,
                    profundidade + 1,
                )
            passo += 1

    for indice in range(13):
        angulo = indice / 13 * math.tau + rng.random() * 0.3
        crescer(
            centro_x + math.cos(angulo) * 16,
            centro_y + math.sin(angulo) * 14,
            angulo,
            110 + rng.random() * 90,
            0,
            0,
        )
    return veias


def _carregar_fonte(caminho, tamanho):
    if caminho.exists():
        return pygame.font.Font(caminho, tamanho)
    return pygame.font.Font(None, tamanho)


def _texto_com_sombras(fonte, texto, cor):
    principal = fonte.render(texto, False, cor)
    deslocamento_maximo = SOMBRAS_TITULO[-1][0]
    superficie = pygame.Surface(
        (principal.get_width(), principal.get_height() + deslocamento_maximo),
        pygame.SRCALPHA,
    )
    for deslocamento, cor_sombra in reversed(SOMBRAS_TITULO):
        superficie.blit(fonte.render(texto, False, cor_sombra), (0, deslocamento))
    superficie.blit(principal, (0, 0))
    return superficie


def _texto_espacado(fonte, texto, cor, espacamento):
    letras = [fonte.render(letra, False, cor) for letra in texto]
    largura = sum(letra.get_width() for letra in letras) + espacamento * (
        len(letras) - 1
    )
    altura = max(letra.get_height() for letra in letras)
    superficie = pygame.Surface((largura, altura), pygame.SRCALPHA)
    x = 0
    for letra in letras:
        superficie.blit(letra, (x, 0))
        x += letra.get_width() + espacamento
    return superficie


class TelaTitulo:
    def __init__(self):
        self.tempo = 0.0
        self.tempo_saida = None
        self._recursos = None
        self._tamanho_recursos = None
        self._coracoes = {}
        self._titulos_escalados = {}

    @property
    def opacidade_preto(self):
        """Quanto de preto cobre a tela: 1 no início e na saída, 0 no meio."""
        entrada = 1 - suavizar(self.tempo / DURACAO_ENTRADA)
        saida = suavizar(self.tempo_saida / DURACAO_SAIDA) if self.saindo else 0.0
        return max(entrada, saida)

    @property
    def saindo(self):
        return self.tempo_saida is not None

    @property
    def concluida(self):
        return self.saindo and self.tempo_saida >= DURACAO_SAIDA

    def processar_botao(self):
        if not self.saindo:
            self.tempo_saida = 0.0

    def atualizar(self, dt):
        self.tempo += dt
        if self.saindo:
            self.tempo_saida += dt

    def _preparar_recursos(self, tamanho_tela):
        if self._tamanho_recursos == tamanho_tela:
            return

        rng = random.Random(17)
        fator = tamanho_tela[0] / LARGURA_REFERENCIA
        fonte_titulo = _carregar_fonte(FONTE_TITULO, round(220 * fator))
        fonte_aviso = _carregar_fonte(FONTE_AVISO, round(24 * fator))

        texto_aviso = _texto_espacado(
            fonte_aviso, TEXTO_AVISO, COR_TITULO, round(4 * fator)
        )
        lado_marcador = max(1, round(8 * fator))
        vao = round(18 * fator)
        aviso = pygame.Surface(
            (
                texto_aviso.get_width() + 2 * (lado_marcador + vao),
                texto_aviso.get_height(),
            ),
            pygame.SRCALPHA,
        )
        y_marcador = (aviso.get_height() - lado_marcador) // 2
        aviso.fill(COR_MARCADOR_AVISO, (0, y_marcador, lado_marcador, lado_marcador))
        aviso.fill(
            COR_MARCADOR_AVISO,
            (aviso.get_width() - lado_marcador, y_marcador, lado_marcador, lado_marcador),
        )
        aviso.blit(texto_aviso, (lado_marcador + vao, 0))

        fundo = desenhar_fundo(rng)
        veias = gerar_veias(rng)
        for x, y, _, profundidade in veias:
            lado = 1 if profundidade else 2
            fundo.fill(CORES_PULSO[0], (x, y, lado, lado))
        veias.sort(key=lambda veia: veia[2])

        self._recursos = {
            "fator": fator,
            "fundo": fundo,
            "veias": veias,
            "distancias_veias": [veia[2] for veia in veias],
            "base": pygame.Surface((LARGURA_BASE, ALTURA_BASE)),
            "brilho": pygame.Surface((LARGURA_BASE, ALTURA_BASE)),
            "titulo": _texto_com_sombras(fonte_titulo, TEXTO_TITULO, COR_TITULO),
            "aviso": aviso,
            "escurecer": pygame.Surface(tamanho_tela),
        }
        self._recursos["escurecer"].fill((0, 0, 0))
        self._titulos_escalados = {}
        self._tamanho_recursos = tamanho_tela

    def _coracao(self, tamanho):
        chave = arredondar(tamanho * 10)
        if chave not in self._coracoes:
            self._coracoes[chave] = desenhar_coracao(chave / 10)
        return self._coracoes[chave]

    def _titulo(self, escala):
        chave = arredondar(escala * 200)
        if chave not in self._titulos_escalados:
            original = self._recursos["titulo"]
            fator = chave / 200
            tamanho = (
                round(original.get_width() * fator),
                round(original.get_height() * fator),
            )
            self._titulos_escalados[chave] = pygame.transform.scale(original, tamanho)
        return self._titulos_escalados[chave]

    def _desenhar_veias(self, base, tempo):
        veias = self._recursos["veias"]
        distancias = self._recursos["distancias_veias"]
        intensidades = {}
        for instante, forca in batidas(tempo, 1.6):
            frente = (tempo - instante) * VELOCIDADE_PULSO
            inicio = bisect.bisect_left(distancias, frente - ALCANCE_PULSO)
            fim = bisect.bisect_right(distancias, frente + ALCANCE_PULSO)
            for indice in range(inicio, fim):
                distancia = distancias[indice]
                diferenca = (distancia - frente) / 7
                intensidades[indice] = intensidades.get(indice, 0.0) + (
                    forca
                    * math.exp(-diferenca * diferenca)
                    * max(0.25, 1 - distancia / 240)
                )

        for indice, intensidade in intensidades.items():
            cor = min(4, math.floor(min(1.0, intensidade) * 4.99))
            if cor == 0:
                continue
            x, y, _, profundidade = veias[indice]
            lado = 1 if profundidade else 2
            base.fill(CORES_PULSO[cor], (x, y, lado, lado))

    def _desenhar_brilho(self, base, intensidade):
        centro = (CENTRO_CORACAO[0], CENTRO_CORACAO[1] - 2)
        raio = 30 + intensidade * 9
        brilho = self._recursos["brilho"]
        for proporcao, alfa in ((1, 0.04), (0.72, 0.06), (0.46, 0.09), (0.26, 0.12)):
            cor = tuple(round(canal * alfa) for canal in COR_BRILHO)
            raio_anel = arredondar(raio * proporcao)
            if raio_anel <= 0:
                continue
            brilho.fill((0, 0, 0))
            pygame.draw.circle(brilho, cor, centro, raio_anel)
            base.blit(brilho, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    def _desenhar_ecg(self, base, tempo):
        for x in range(LARGURA_BASE):
            atraso = (LARGURA_BASE - 1 - x) / VELOCIDADE_ECG
            y = arredondar(ALTURA_LINHA_ECG - altura_ecg(tempo - atraso))
            cor = COR_PONTA_ECG if x > LARGURA_BASE - 8 else COR_ECG
            base.set_at((x, y), cor)

    def desenhar(self, tela):
        self._preparar_recursos(tela.get_size())
        recursos = self._recursos
        tempo = self.tempo
        intensidade = intensidade_batida(tempo)
        base = recursos["base"]

        base.blit(recursos["fundo"], (0, 0))
        self._desenhar_veias(base, tempo)
        self._desenhar_brilho(base, intensidade)

        coracao, raio = self._coracao(TAMANHO_CORACAO * (1 + intensidade * 0.1))
        base.blit(coracao, (CENTRO_CORACAO[0] - raio, CENTRO_CORACAO[1] - raio))

        self._desenhar_ecg(base, tempo)
        tela.blit(pygame.transform.scale(base, tela.get_size()), (0, 0))

        fator = recursos["fator"]
        largura_tela = tela.get_width()
        original = recursos["titulo"]
        titulo = self._titulo(1 + intensidade * 0.05)
        origem_y = 44 * fator + original.get_height() * 0.6
        y = origem_y - titulo.get_height() * 0.6
        tela.blit(titulo, ((largura_tela - titulo.get_width()) / 2, y))

        aviso = recursos["aviso"]
        aceso = tempo < PRIMEIRA_BATIDA or intensidade > 0.25
        aviso.set_alpha(255 if aceso else 64)
        tela.blit(aviso, ((largura_tela - aviso.get_width()) / 2, 612 * fator))

        preto = self.opacidade_preto
        if preto > 0:
            escurecer = recursos["escurecer"]
            escurecer.set_alpha(round(255 * preto))
            tela.blit(escurecer, (0, 0))


def executar_tela_titulo(tela, relogio):
    """Mostra a tela de título. Retorna False se a janela for fechada."""
    controles = [
        pygame.joystick.Joystick(indice)
        for indice in range(pygame.joystick.get_count())
    ]
    tela_titulo = TelaTitulo()

    while not tela_titulo.concluida:
        dt = relogio.tick(60) / 1000

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                return False
            if evento.type == pygame.JOYDEVICEADDED:
                controles.append(pygame.joystick.Joystick(evento.device_index))
            elif evento.type in (
                pygame.KEYDOWN,
                pygame.MOUSEBUTTONDOWN,
                pygame.JOYBUTTONDOWN,
            ):
                tela_titulo.processar_botao()

        tela_titulo.atualizar(dt)
        tela_titulo.desenhar(tela)
        pygame.display.flip()

    return True


if __name__ == "__main__":
    pygame.init()
    janela = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Infernus")
    executar_tela_titulo(janela, pygame.time.Clock())
    pygame.quit()

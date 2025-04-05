from machine import Pin, SoftI2C, ADC
import neopixel
import utime
import random
from ssd1306 import SSD1306_I2C
import math

# --- Configuração dos pinos ---
LED_PIN = 7        # GPIO7 para a matriz NeoPixel (5x5)
JOYSTICK_X = 27    # GPIO27 (VRx do joystick)
JOYSTICK_Y = 26    # GPIO26 (VRy do joystick)
BUTTON_B = 6       # GPIO6 para o botão B (tiro)
OLED_SDA = 14      # GPIO14 (SDA do OLED)
OLED_SCL = 15      # GPIO15 (SCL do OLED)

# --- Inicialização ---
np = neopixel.NeoPixel(Pin(LED_PIN), 25)
joy_x = ADC(Pin(JOYSTICK_X))
joy_y = ADC(Pin(JOYSTICK_Y))
button_b = Pin(BUTTON_B, Pin.IN, Pin.PULL_UP)
i2c = SoftI2C(scl=Pin(OLED_SCL), sda=Pin(OLED_SDA))
oled = SSD1306_I2C(128, 64, i2c)
joy_button = Pin(22, Pin.IN, Pin.PULL_UP)
brightness = 0.1
match = 1


# --- Variáveis do Jogo ---
MATRIX_MAP = [  
    [24, 23, 22, 21, 20],  # Linha 0 (topo)
    [15, 16, 17, 18, 19],  # Linha 1
    [14, 13, 12, 11, 10],  # Linha 2
    [5, 6, 7, 8, 9],       # Linha 3
    [4, 3, 2, 1, 0]        # Linha 4 (base)
]

nave_pos = [2, 4]  # [x, y] - Linha inferior (4)
tiros = []         # Lista de tiros ativos

inimigos_1 = [[i, 0] for i in range(5)]  # Inimigos na linha superior
inimigos_2 = []
inimigos_3 = []

direcao_inimigos = 1  # 1 = direita, -1 = esquerda
game_speed = 0.95
score = 0
vidas = 3
game_state = "RUNNING"

# --- Funções do Jogo ---

def apply_brightness(color, brightness):
    """Ajusta o brilho de uma cor RGB (0-255)"""
    r, g, b = color
    return (
        int(r * brightness),
        int(g * brightness),
        int(b * brightness)
    )

def set_pixel(x, y, color):
    """Acende o LED na posição (x,y)"""
    if 0 <= x < 5 and 0 <= y < 5:
        np[MATRIX_MAP[y][x]] = color

def clear_matrix():
    """Apaga todos os LEDs"""
    for i in range(25):
        np[i] = (0, 0, 0)

def draw_game():
    global brightness, inimigos_1, inimigos_2, inimigos_3
    """Desenha todos os elementos na matriz"""
    clear_matrix()
    
    # Desenha nave (roxo)
    set_pixel(nave_pos[0], nave_pos[1], apply_brightness((50, 200, 133),brightness))
    
    # Desenha tiros (azul)
    for tiro in tiros:
        set_pixel(tiro[0], tiro[1], apply_brightness((255, 255, 0),brightness))
    
    # Desenha inimigos (vermelho)
    for inimigo in inimigos_1:
        set_pixel(inimigo[0], inimigo[1], apply_brightness((255, 0, 0),brightness))
    
    for inimigo in inimigos_2:
        set_pixel(inimigo[0], inimigo[1], apply_brightness((0, 255, 0),brightness))
    
    for inimigo in inimigos_3:
        set_pixel(inimigo[0], inimigo[1], apply_brightness((0, 0, 255),brightness))
    
    np.write()

def update_display():
    """Atualiza o display OLED"""
    oled.fill(0)
    oled.text(f"Score: {score}", 0, 0)
    oled.text(f"Vidas: {vidas}", 0, 20)
    oled.show()


def atirar():
    """Dispara um novo tiro"""
    if len(tiros) < 3:  # Limite de 2 tiros simultâneos
        tiros.append([nave_pos[0], nave_pos[1] - 1])

def mover_tiros():
    """Atualiza posição dos tiros"""
    for tiro in tiros[:]:
        tiro[1] -= 1  # Move para cima
        if tiro[1] < 0:
            tiros.remove(tiro)

def mover_nave():
    """Controla movimento da nave com joystick"""
    x = joy_x.read_u16()
    if x < 15000 and nave_pos[0] > 0:  # Esquerda
        nave_pos[0] -= 1
    elif x > 50000 and nave_pos[0] < 4:  # Direita
        nave_pos[0] += 1

def mover_inimigos():
    """Movimenta os inimigos corretamente e verifica fim de jogo"""
    global direcao_inimigos, game_state, vidas, inimigos_1, inimigos_2, inimigos_3

    # Verifica se algum inimigo atingiu a borda
    mudar_direcao = False

    if direcao_inimigos == 1:
        if any(inimigo[0] >= 4 for inimigo in inimigos_1):
            mudar_direcao = True
        if any(inimigo[0] >= 4 for inimigo in inimigos_2):
            mudar_direcao = True
        if any(inimigo[0] >= 4 for inimigo in inimigos_3):
            mudar_direcao = True

    elif direcao_inimigos == -1:
        if any(inimigo[0] <= 0 for inimigo in inimigos_1):
            mudar_direcao = True
        if any(inimigo[0] <= 0 for inimigo in inimigos_2):
            mudar_direcao = True
        if any(inimigo[0] <= 0 for inimigo in inimigos_3):
            mudar_direcao = True
        
    if mudar_direcao:
        direcao_inimigos *= -1
        for inimigo in inimigos_1:
            inimigo[1] += 1  # Desce uma linha
        for inimigo in inimigos_2:
            inimigo[1] += 1  # Desce uma linha
        for inimigo in inimigos_3:
            inimigo[1] += 1  # Desce uma linha
    else:
        for inimigo in inimigos_1:
            inimigo[0] += direcao_inimigos  # Move lateralmente
        for inimigo in inimigos_2:
            inimigo[0] += direcao_inimigos  # Move lateralmente
        for inimigo in inimigos_3:
            inimigo[0] += direcao_inimigos  # Move lateralmente

    # Verifica se algum inimigo chegou ao fundo
    # Versão corrigida:
    if any(inimigo[1] >= 4 for grupo in [inimigos_1, inimigos_2, inimigos_3] for inimigo in grupo):
            vidas -= 1
            if vidas <= 0:
                game_state = "GAME_OVER"
            reset_positions()


def verificar_colisoes():
    """Verifica colisões entre tiros e inimigos"""
    global score, inimigos_1, inimigos_2, inimigos_3
    
    for tiro in tiros[:]:
        for inimigo in inimigos_1[:]:
            if tiro[0] == inimigo[0] and tiro[1] == inimigo[1]:
                if tiro in tiros:  # Verifica se ainda está na lista
                    tiros.remove(tiro)
                if inimigo in inimigos_1:
                    inimigos_1.remove(inimigo)
                    score += 10
                break  # Sai do laço interno para evitar erro

    for tiro in tiros[:]:
        for inimigo in inimigos_2[:]:
            if tiro[0] == inimigo[0] and tiro[1] == inimigo[1]:
                if tiro in tiros:  # Verifica se ainda está na lista
                    tiros.remove(tiro)
                if inimigo in inimigos_2:
                    inimigos_2.remove(inimigo)
                    score += 10
                break  # Sai do laço interno para evitar erro
    
    for tiro in tiros[:]:
        for inimigo in inimigos_3[:]:
            if tiro[0] == inimigo[0] and tiro[1] == inimigo[1]:
                if tiro in tiros:  # Verifica se ainda está na lista
                    tiros.remove(tiro)
                if inimigo in inimigos_3:
                    inimigos_3.remove(inimigo)
                    score += 10
                break  # Sai do laço interno para evitar erro


def reset_positions():
    global nave_pos, tiros, inimigos_1, inimigos_2,inimigos_3, match
    nave_pos = [2, 4]
    tiros = []
    inimigos_1 = [[i, 0] for i in range(5)]
    if match == 2:
        inimigos_1 = [[i, 0] for i in range(5)]
        inimigos_2 = [[i, 1] for i in range(5)]
    if match >= 3:
        inimigos_1 = [[i, 0] for i in range(5)]
        inimigos_2 = [[i, 1] for i in range(5)]
        inimigos_3 = [[i, 2] for i in range(5)]


def reset_game():
    global nave_pos, tiros, inimigos, score, vidas, game_state, game_speed, match
    nave_pos = [2, 4]
    tiros = []
    score = 0
    vidas = 3
    match = 1
    game_speed = 0.95
    game_state = "RUNNING"


# --- Loop Principal ---
last_update = utime.ticks_ms()
button_b.irq(trigger=Pin.IRQ_FALLING, handler=lambda p: atirar())

# --- Temporizadores separados ---

last_tiro_update = utime.ticks_ms()
tiro_update_interval = 200  # Tiros movem a cada 200ms

last_game_update = utime.ticks_ms()
game_speed = 100  # Atualizações gerais, como nave (a cada 100ms)

last_enemy_move = utime.ticks_ms()
enemy_move_interval = 2000  # ms (1 segundo para descer)

last_tiro_move = utime.ticks_ms()
tiro_move_interval = 200  # ms (mais rápido que o padrão atual)

last_nave_move = utime.ticks_ms()
nave_move_interval = 200  # A nave só pode se mover a cada 200 ms

while True:
    now = utime.ticks_ms()

    if game_state == "RUNNING":

        if utime.ticks_diff(now, last_nave_move) >= nave_move_interval:
            last_nave_move = now
            mover_nave()


        # Mover inimigos
        if utime.ticks_diff(now, last_enemy_move) >= enemy_move_interval:
            last_enemy_move = now
            mover_inimigos()

        # Mover tiros
        if utime.ticks_diff(now, last_tiro_move) >= tiro_move_interval:
            last_tiro_move = now
            verificar_colisoes()  # Verifica antes do movimento
            mover_tiros()
            verificar_colisoes()  # Verifica após o movimento

        draw_game()
        update_display()

        if (len(inimigos_1) == 0 and len(inimigos_2) == 0 and len(inimigos_2) == 0): # Poucos inimigos restantes
            match +=1
            reset_positions()
            # Aumenta dificuldade
            enemy_move_interval = max(300, int(enemy_move_interval * 0.9))
    
    elif game_state == "GAME_OVER":
        oled.fill(0)
        oled.text("GAME OVER", 30, 20)
        oled.text(f"Score: {score}", 30, 40)
        oled.show()
        utime.sleep(3)
        reset_game()

    utime.sleep_ms(10)
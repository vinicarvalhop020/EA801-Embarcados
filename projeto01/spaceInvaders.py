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
inimigos = [[i, 0] for i in range(5)]  # Inimigos na linha superior
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
    global brightness
    """Desenha todos os elementos na matriz"""
    clear_matrix()
    
    # Desenha nave (verde)
    set_pixel(nave_pos[0], nave_pos[1], apply_brightness((0, 255, 0),brightness))
    
    # Desenha tiros (azul)
    for tiro in tiros:
        set_pixel(tiro[0], tiro[1], apply_brightness((0, 0, 255),brightness))
    
    # Desenha inimigos (vermelho)
    for inimigo in inimigos:
        set_pixel(inimigo[0], inimigo[1], apply_brightness((255, 0, 0),brightness))
    
    np.write()

def update_display():
    """Atualiza o display OLED"""
    oled.fill(0)
    oled.text(f"Score: {score}", 0, 0)
    oled.text(f"Vidas: {vidas}", 0, 20)
    oled.show()

def mover_nave():
    """Controla movimento da nave com joystick"""
    x = joy_x.read_u16()
    if x < 15000 and nave_pos[0] > 0:  # Esquerda
        nave_pos[0] -= 1
    elif x > 50000 and nave_pos[0] < 4:  # Direita
        nave_pos[0] += 1

def atirar():
    """Dispara um novo tiro"""
    if len(tiros) < 2:  # Limite de 2 tiros simultâneos
        tiros.append([nave_pos[0], nave_pos[1] - 1])

def mover_tiros():
    """Atualiza posição dos tiros"""
    for tiro in tiros[:]:
        tiro[1] -= 1  # Move para cima
        if tiro[1] < 0:
            tiros.remove(tiro)

def mover_inimigos():
    """Movimenta os inimigos e verifica colisões"""
    global direcao_inimigos, game_state, vidas
    
    # Movimento lateral
    for inimigo in inimigos:
        inimigo[0] += direcao_inimigos
    
    # Verifica bordas
    if any(inimigo[0] >= 4 for inimigo in inimigos) and direcao_inimigos == 1:
        direcao_inimigos = -1
        for inimigo in inimigos:
            inimigo[1] += 1  # Desce uma linha
    elif any(inimigo[0] <= 0 for inimigo in inimigos) and direcao_inimigos == -1:
        direcao_inimigos = 1
        for inimigo in inimigos:
            inimigo[1] += 1
    
    # Verifica se inimigos chegaram no fundo
    if any(inimigo[1] >= 4 for inimigo in inimigos):
        vidas -= 1
        if vidas <= 0:
            game_state = "GAME_OVER"
        reset_positions()

def verificar_colisoes():
    """Verifica colisões entre tiros e inimigos"""
    global score, inimigos
    
    for tiro in tiros[:]:
        for inimigo in inimigos[:]:
            if tiro[0] == inimigo[0] and tiro[1] == inimigo[1]:
                tiros.remove(tiro)
                inimigos.remove(inimigo)
                score += 10
                break

def reset_positions():
    """Reinicia posições após perder vida"""
    global nave_pos, tiros, inimigos
    nave_pos = [2, 4]
    tiros = []
    inimigos = [[i, 0] for i in range(5)]


def reset_game():
    """Reinicia o jogo completamente"""
    global nave_pos, tiros, inimigos, score, vidas, game_state, game_speed
    nave_pos = [2, 4]
    tiros = []
    inimigos = [[i, 0] for i in range(5)]
    score = 0
    vidas = 3
    game_speed = 0.5
    game_state = "RUNNING"



# --- Loop Principal ---
last_update = utime.ticks_ms()
button_b.irq(trigger=Pin.IRQ_FALLING, handler=lambda p: atirar())

# --- Temporizadores separados ---
last_enemy_update = utime.ticks_ms()
enemy_update_interval = 3000  # Inimigos movem a cada 3 segundo

last_tiro_update = utime.ticks_ms()
tiro_update_interval = 200  # Tiros movem a cada 200ms

last_game_update = utime.ticks_ms()
game_speed = 100  # Atualizações gerais, como nave (a cada 100ms)

while True:
    now = utime.ticks_ms()

    if game_state == "RUNNING":
        # --- Atualiza movimentação dos tiros ---
        if utime.ticks_diff(now, last_tiro_update) > tiro_update_interval:
            last_tiro_update = now
            mover_tiros()
            verificar_colisoes()  # Verifica colisões logo após mover os tiros

        # --- Atualiza movimentação dos inimigos ---
        if utime.ticks_diff(now, last_enemy_update) > enemy_update_interval:
            last_enemy_update = now
            mover_inimigos()

        # --- Atualiza nave e desenha o jogo ---
        if utime.ticks_diff(now, last_game_update) > game_speed:
            last_game_update = now
            mover_nave()
            draw_game()
            update_display()

            if len(inimigos) < 2:
                reset_positions()
                enemy_update_interval = max(300, int(enemy_update_interval * 0.9))  # Mais rápido
                tiro_update_interval = max(100, int(tiro_update_interval * 0.9))

    elif game_state == "GAME_OVER":
        oled.fill(0)
        oled.text("GAME OVER", 30, 20)
        oled.text(f"Score: {score}", 30, 40)
        oled.show()
        utime.sleep(3)
        reset_game()

    utime.sleep_ms(10)
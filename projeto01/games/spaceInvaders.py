from machine import Pin, SoftI2C, ADC,PWM
import neopixel
import utime
import random
from ssd1306 import SSD1306_I2C
import math
import time
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
buzzer = PWM(Pin(21))
dificuldade = 0
last_score = -1
start_defeat = False




# --- Variáveis do Jogo ---
MATRIX_MAP = [  
    [24, 23, 22, 21, 20],  # Linha 0 (topo)
    [15, 16, 17, 18, 19],  # Linha 1
    [14, 13, 12, 11, 10],  # Linha 2
    [5, 6, 7, 8, 9],       # Linha 3
    [4, 3, 2, 1, 0]        # Linha 4 (base)
]

nave_pos = [2, 4]
tiros = []
inimigos_1 = [[i, 0] for i in range(5)]  # Inimigos vermelhos (linha 0)
inimigos_2 = []  # Inimigos verdes (aparecem depois)
inimigos_3 = []  # Inimigos azuis (aparecem depois)
match = 1
game_state = "RUNNING"  # Começa no estado START
brightness = 0.1
match = 1
direcao_inimigos = 1  # 1 = direita, -1 = esquerda
score = 0
first_move = True  
lose_state = False
reset = False


# Modifique estas variáveis globais
sound_queue = []
current_sound = None
sound_start_time = 0
MAX_SOUND_QUEUE = 3  # Limite máximo de sons na fila

def play_tone_non_blocking(frequency, duration):
    """Adiciona um som à fila de reprodução com limite de tamanho"""
    if len(sound_queue) < MAX_SOUND_QUEUE:
        sound_queue.append((frequency, duration))

def process_sounds():
    """Gerencia a reprodução dos sons na fila de forma mais eficiente"""
    global current_sound, sound_start_time, start_defeat
    
    now = utime.ticks_ms()

    if start_defeat: #prioridade se é start ou defeat
        current_sound = sound_queue.pop(-1)
        buzzer.freq(current_sound[0])  # current_sound[0] é a frequency
        buzzer.duty_u16(2000)

    # Se está tocando um som, verifica se já terminou
    if current_sound is not None:
        elapsed = utime.ticks_diff(now, sound_start_time)
        if elapsed >= current_sound[1]:  # current_sound[1] é a duration
            buzzer.duty_u16(0)  # Desliga o buzzer
            current_sound = None
    
    # Se não está tocando nada e há sons na fila
    if current_sound is None and sound_queue:
        # Pega o som mais recente (em vez do mais antigo)
        current_sound = sound_queue.pop(-1)
        buzzer.freq(current_sound[0])  # current_sound[0] é a frequency
        buzzer.duty_u16(2000)
        sound_start_time = now
        # Limpa a fila para evitar acúmulo
        sound_queue.clear()


def ship_sounds(action):
    """Efeitos sonoros melhorados"""
    if action == "tiro":
        # Laser espacial descendente (mais realista)
        play_tone_non_blocking(1200, 30)  # Frequência alta inicial
        play_tone_non_blocking(900, 30)   # Queda rápida
        play_tone_non_blocking(600, 40)   # Finalização
    
    elif action == "explosao":
        # Explosão com ruído "granulado"
        play_tone_non_blocking(300, 80)
        play_tone_non_blocking(200, 80)
        play_tone_non_blocking(150, 100)
    
    elif action == "movimento":
        # Feedback sutil ao mover nave
        play_tone_non_blocking(500, 15)
    

def game_sounds(action):
    global start_defeat
    """Sons de jogo melhorados"""
    if action == "game_start":
        # Fanfarra de início (3 notas ascendentes)
        start_defeat = True
        play_tone_non_blocking(523, 150)  # Dó
        play_tone_non_blocking(659, 150)  # Mi
        play_tone_non_blocking(784, 200)  # Sol
        start_defeat = False
    
    elif action == "game_over":
        if lose_state:  
            # Som descendente (triste)
            start_defeat = True
            play_tone_non_blocking(392, 300)  # Sol
            play_tone_non_blocking(349, 300)  # Fá
            play_tone_non_blocking(330, 300)  # Mi
            play_tone_non_blocking(294, 500)  # Ré (mais longo)
            start_defeat = False

    elif action == "hit":
        play_tone_non_blocking(130, 300)  # Dó grave

def start_game():
    global game_state, effect_start_time, effect_step
    game_state = "START"
    effect_start_time = utime.ticks_ms()
    effect_step = 0
    game_sounds("game_start")  # Adicione um som específico para início

def lose_game():
    global game_state, effect_start_time, effect_step, lose_state
    lose_state = True
    game_state = "LOSE"
    effect_start_time = utime.ticks_ms()
    effect_step = 0
    game_sounds("game_over")
    show_loose_screen()

COUNTDOWN_PATTERNS = {
    3: [
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1]
    ],
    2: [
        [1, 1, 1, 1, 1],
        [0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1]
    ],
    1: [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0]
    ]
}

LOSE_PATTERNS = {
    'L': [
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1]
    ],
    'O': [
        [0, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 0, 0, 1],
        [0, 1, 1, 1, 0]
    ],
    'S': [
        [0, 1, 1, 1, 1],
        [1, 0, 0, 0, 0],
        [0, 1, 1, 1, 0],
        [0, 0, 0, 0, 1],
        [1, 1, 1, 1, 0]
    ],
    'E': [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 0],
        [1, 1, 1, 1, 1]
    ],
    'R': [
        [1, 1, 1, 1, 0],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 0],
        [1, 0, 0, 1, 0],
        [1, 0, 0, 0, 1]
    ]
}

def show_pattern(pattern, number, color):
    """Desenha um número na matriz LED"""
    if pattern == "start":
        pattern = COUNTDOWN_PATTERNS.get(number)
        if not pattern:
            return
        
        for y in range(5):
            for x in range(5):
                if pattern[y][x]:
                    set_pixel(x, y, color)
                else:
                    set_pixel(x, y, (0, 0, 0))
        np.write()
    
    if pattern == "lose":
        pattern = LOSE_PATTERNS.get(number)
        if not pattern:
            return
        
        for y in range(5):
            for x in range(5):
                if pattern[y][x]:
                    set_pixel(x, y, color)
                else:
                    set_pixel(x, y, (0, 0, 0))
        np.write()


def process_game_effects():
    global game_state, effect_start_time, effect_step, first_move
    
    now = utime.ticks_ms()
    
    if game_state == "START":
        if effect_step == 0:  # Início da contagem
            show_pattern("start",3, apply_brightness((0, 0, 255), brightness))
            play_tone_non_blocking(784, 150)  # Sol
            effect_step = 1
            effect_start_time = now
            
        elif effect_step == 1 and utime.ticks_diff(now, effect_start_time) >= 1000:
            show_pattern("start",2, apply_brightness((0, 0, 255), brightness))
            play_tone_non_blocking(659, 150)  # Mi
            effect_step = 2
            effect_start_time = now
            
        elif effect_step == 2 and utime.ticks_diff(now, effect_start_time) >= 1000:
            show_pattern("start",1, apply_brightness((0, 0, 255), brightness))
            play_tone_non_blocking(523, 150)  # Dó
            effect_step = 3
            effect_start_time = now
            
        elif effect_step == 3 and utime.ticks_diff(now, effect_start_time) >= 1000:
            clear_matrix()
            play_tone_non_blocking(1046, 200)  # Dó agudo (início)
            reset_game()
            game_state = "RUNNING"
    
    elif game_state == "LOSE":
        if effect_step == 0:
            show_pattern("lose","L", apply_brightness((255, 0, 0), brightness))
            effect_step = 1
            effect_start_time = now
        elif effect_step == 1 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern("lose","O", apply_brightness((255, 0, 0), brightness))
            effect_step = 2
            effect_start_time = now
        elif effect_step == 2 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern("lose","S", apply_brightness((255, 0, 0), brightness))
            effect_step = 3
            effect_start_time = now
        elif effect_step == 3 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern("lose","E", apply_brightness((255, 0, 0), brightness))
            effect_step = 4
            effect_start_time = now
        elif effect_step == 4 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern("lose","R", apply_brightness((255, 0, 0), brightness))
            effect_step = 5
            effect_start_time = now
        elif effect_step == 5 and utime.ticks_diff(now, effect_start_time) >= 2000:
            clear_matrix()
            reset_game()
            game_state = "RUNNING"
            first_move = -1

def show_start_screen():
    """Tela inicial no OLED"""
    oled.fill(0)
    oled.text("SPACE INAVADERS", 5, 20)
    oled.text("Pressione B", 25, 40)
    oled.show()

def show_loose_screen():
        oled.fill(0)
        oled.text(f"QUE PENA", 0, 0)
        oled.text(f"VOCE PERDEU!", 0, 20)
        oled.show()

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
    global last_score, reset
    if (score != last_score or reset):
        oled.fill(0)
        oled.text(f"Pontos: {score}", 0, 0)
        oled.text(f"Vidas: {vidas}", 0, 20)
        oled.text(f"Fase {match}", 0, 30)
        oled.show()
        last_score = score
        reset = False

def atirar():
    """Dispara um novo tiro"""
    if len(tiros) < 3:  # Limite de 2 tiros simultâneos
        tiros.append([nave_pos[0], nave_pos[1] - 1])
        ship_sounds("tiro")

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
    global direcao_inimigos, game_state, vidas, inimigos_1, inimigos_2, inimigos_3, first_move

    if first_move:
        first_move = False
        return
    
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
            game_sounds("hit")
            if vidas <= 0:
                lose_game()
            else:
                reset_positions()


def verificar_colisoes():
    """Verifica colisões entre tiros e inimigos"""
    global score, inimigos_1, inimigos_2, inimigos_3
    
    for tiro in tiros[:]:
        for inimigo in inimigos_1[:]:
            if tiro[0] == inimigo[0] and tiro[1] == inimigo[1]:
                ship_sounds("explosao")
                if tiro in tiros:  # Verifica se ainda está na lista
                    tiros.remove(tiro)
                if inimigo in inimigos_1:
                    inimigos_1.remove(inimigo)
                    score += 10
                break  # Sai do laço interno para evitar erro

    for tiro in tiros[:]:
        for inimigo in inimigos_2[:]:
            if tiro[0] == inimigo[0] and tiro[1] == inimigo[1]:
                ship_sounds("explosao")
                if tiro in tiros:  # Verifica se ainda está na lista
                    tiros.remove(tiro)
                if inimigo in inimigos_2:
                    inimigos_2.remove(inimigo)
                    score += 10
                break  # Sai do laço interno para evitar erro
    
    for tiro in tiros[:]:
        for inimigo in inimigos_3[:]:
            if tiro[0] == inimigo[0] and tiro[1] == inimigo[1]:
                ship_sounds("explosao")
                if tiro in tiros:  # Verifica se ainda está na lista
                    tiros.remove(tiro)
                if inimigo in inimigos_3:
                    inimigos_3.remove(inimigo)
                    score += 10
                break  # Sai do laço interno para evitar erro


def reset_positions():
    global nave_pos, tiros, inimigos_1, inimigos_2, inimigos_3, match
    nave_pos = [2, 4]
    tiros = []
    
    # Recria os inimigos baseado na fase atual
    inimigos_1 = [[i, 0] for i in range(5)]
    
    if match >= 2:
        inimigos_2 = [[i, -1] for i in range(5)]  # Começa "escondido"
    
    if match >= 3:
        inimigos_3 = [[i, -2] for i in range(5)]  # Começa "escondido


def reset_game():
    global nave_pos, tiros, inimigos_1, inimigos_2, inimigos_3, score, vidas, game_state, match, enemy_move_interval, dificuldade,lose_state, reset, start_defeat
    nave_pos = [2, 4]
    tiros = []
    inimigos_1 = [[i, 0] for i in range(5)]
    inimigos_2 = []
    inimigos_3 = []
    enemy_move_interval = 2000
    score = 0
    vidas = 3
    match = 1
    game_state = "START"  # Volta para o estado inicial
    lose_state = False  # Adicione esta linha
    dificuldade = 0
    reset = True
    start_defeat = False
    show_start_screen()


# --- Loop Principal ---
last_update = utime.ticks_ms()
button_b.irq(trigger=Pin.IRQ_FALLING, handler=lambda p: atirar())

# --- Temporizadores separados ---

#last_tiro_update = utime.ticks_ms()
#tiro_update_interval = 200  # Tiros movem a cada 200ms

last_enemy_move = utime.ticks_ms()
enemy_move_interval = 2000  # ms (1 segundo para descer)

last_tiro_move = utime.ticks_ms()
tiro_move_interval = 200  # ms (mais rápido que o padrão atual)

last_nave_move = utime.ticks_ms()
nave_move_interval = 200  # A nave só pode se mover a cada 200 ms


# --- Inicialização ---

show_start_screen()
while button_b.value() == 1:  # Espera pressionar o botão B
    time.sleep(0.1)
start_game()

while True:
    print(game_state)
    now = utime.ticks_ms()
    process_game_effects()
    process_sounds()  # Gerencia a reprodução dos sons
     
    if game_state == "RUNNING":
        # Movimento da nave
        if utime.ticks_diff(now, last_nave_move) >= nave_move_interval:
            last_nave_move = now
            if joy_x.read_u16() < 15000 or joy_x.read_u16() > 50000:
                ship_sounds("movimento")
            mover_nave()

        # Movimento dos inimigos
        if utime.ticks_diff(now, last_enemy_move) >= enemy_move_interval:
            last_enemy_move = now
            mover_inimigos()

        # Movimento dos tiros
        if utime.ticks_diff(now, last_tiro_move) >= tiro_move_interval:
            last_tiro_move = now
            verificar_colisoes()
            mover_tiros()
            verificar_colisoes()

        draw_game()
        update_display()
        utime.sleep_ms(10)

        # Verifica se todos inimigos foram destruídos
        if len(inimigos_1) == 0 and len(inimigos_2) == 0 and len(inimigos_3) == 0:
            match += 1
            reset_positions()
            enemy_move_interval = max(300, int(enemy_move_interval * 0.9))
            dificuldade += 1 

  

       
    
    

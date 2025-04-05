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
BUTTON_B = 6       # GPIO6 para o botão B (reset)
OLED_SDA = 14      # GPIO14 (SDA do OLED)
OLED_SCL = 15      # GPIO15 (SCL do OLED)

# --- Inicialização dos componentes ---
np = neopixel.NeoPixel(Pin(LED_PIN), 25)  # Matriz 5x5
joy_x = ADC(Pin(JOYSTICK_X))
joy_y = ADC(Pin(JOYSTICK_Y))
button_b = Pin(BUTTON_B, Pin.IN, Pin.PULL_UP)
i2c = SoftI2C(scl=Pin(OLED_SCL), sda=Pin(OLED_SDA))
oled = SSD1306_I2C(128, 64, i2c)
joy_button = Pin(22, Pin.IN, Pin.PULL_UP) 

# Variáveis globais para armazenar o último estado do joystick
last_joystick_check = 0
joystick_interval = 50  # ms (mesmo intervalo do timer anterior)
last_x = 32768
last_y = 32768
threshold = 10000
game_state = "RUNNING"  # Pode ser: "RUNNING", "LOSE", "START"
effect_start_time = 0
effect_step = 0
dificuldade = 1


def check_joystick_movement():
    global direction, last_x, last_y, last_joystick_check
    
    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_joystick_check) >= joystick_interval:
        last_joystick_check = now
        
        x = joy_x.read_u16()
        y = joy_y.read_u16()
        
        if abs(x - last_x) > threshold or abs(y - last_y) > threshold:
            new_dir = read_joystick()
            current_dir = direction
            
            if new_dir and new_dir != oposite(current_dir):
                direction = new_dir
                print(f"Movimento detectado! Direção: {direction}")
        
        last_x, last_y = x, y

# --- Mapeamento FÍSICO da matriz (conforme manual) ---
MATRIX_MAP = [  
    [24, 23, 22, 21, 20],  # Linha 0 (topo)
    [15, 16, 17, 18, 19],  # Linha 1
    [14, 13, 12, 11, 10],  # Linha 2
    [5, 6, 7, 8, 9],       # Linha 3
    [4, 3, 2, 1, 0]        # Linha 4 (base)
]

# --- Variáveis do jogo ---
snake = [(2, 2)]    # Cobra inicia no centro
direction = "RIGHT"  # Direção inicial
food = (0, 0)       # Posição da comida
score = 0           # Pontuação
game_speed = 0.9    # Velocidade 
brightness = 0.1
cor_fruta_atual = [255,0,0]
sound_queue = []
sound_start_time = 0
current_sound = None

from machine import Pin, PWM
import time

# Configura o buzzer (GPIO21 conforme manual da BitDoglab)
buzzer = PWM(Pin(21))

def play_tone_non_blocking(frequency, duration):
    """Adiciona um som à fila de reprodução"""
    sound_queue.append((frequency, duration))

def process_sounds():
    """Gerencia a reprodução dos sons na fila (deve ser chamado no loop principal)"""
    global current_sound, sound_start_time
    
    now = utime.ticks_ms()
    
    # Se está tocando um som, verifica se já terminou
    if current_sound is not None:
        # duration é armazenado junto com frequency na fila como uma tupla
        if utime.ticks_diff(now, sound_start_time) >= current_sound[1]:  # current_sound[1] é a duration
            buzzer.duty_u16(0)  # Desliga o buzzer
            current_sound = None
    
    # Se não está tocando nada e há sons na fila
    if current_sound is None and sound_queue:
        current_sound = sound_queue.pop(0)  # Armazena (frequency, duration)
        buzzer.freq(current_sound[0])  # current_sound[0] é a frequency
        buzzer.duty_u16(32768)
        sound_start_time = now

def snake_sounds(action):
    """Adiciona sons à fila conforme a ação"""
    if action == "eat":
        play_tone_non_blocking(523, 100)  # Dó (100ms)
        play_tone_non_blocking(659, 100)  # Mi (100ms)

    elif action == "move":
        play_tone_non_blocking(100, 20)  # Som curto de movimento (20ms)

def game_sounds(action):
    if action == "game_start":
        for freq in [392, 349, 330]:
            play_tone_non_blocking(freq, 1000)  # 150ms por nota

    elif action == "game_over":
        for freq in [330, 349, 400]:
            play_tone_non_blocking(freq, 1000)  # 150ms por nota

def oposite(direction):
    if direction == 'LEFT':
        return 'RIGHT'
    if direction == 'RIGHT':
        return 'LEFT'
    if direction == 'UP':
        return 'DOWN'
    if direction == 'DOWN':
        return 'UP'

def apply_brightness(color, brightness):
    """Ajusta o brilho de uma cor RGB (0-255)"""
    r, g, b = color
    return (
        int(r * brightness),
        int(g * brightness),
        int(b * brightness)
    )

def start_game():
    global game_state, effect_start_time, effect_step
    game_state = "START"
    effect_start_time = utime.ticks_ms()
    effect_step = 0
    game_sounds("game_start")  # Adicione um som específico para início

def lose_game():
    global game_state, effect_start_time, effect_step
    game_state = "LOSE"
    effect_start_time = utime.ticks_ms()
    effect_step = 0
    game_sounds("game_over")

# Adicione no início do código (com as outras variáveis globais)
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

def show_number(number, color):
    """Desenha um número na matriz LED"""
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

def process_game_effects():
    global game_state, effect_start_time, effect_step
    
    now = utime.ticks_ms()
    
    if game_state == "START":
        if effect_step == 0:  # Mostra "3" (azul)
            show_number(3, apply_brightness((0, 0, 255), brightness))
     # Som para contagem
            effect_step = 1
            effect_start_time = now
            
        elif effect_step == 1:  # Espera 1 segundo
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                show_number(2, apply_brightness((0, 0, 255), brightness))
                effect_step = 2
                effect_start_time = now
                
        elif effect_step == 2:  # Espera 1 segundo
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                show_number(1, apply_brightness((0, 0, 255), brightness))
                effect_step = 3
                effect_start_time = now
                
        elif effect_step == 3:  # Espera 1 segundo e inicia
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                clear_matrix()
                reset_game()
                game_state = "RUNNING"

    elif game_state == "LOSE":
        if effect_step == 0:  # Mostra "3" (azul)
            show_number(3, apply_brightness((255, 0, 0), brightness))
     # Som para contagem
            effect_step = 1
            effect_start_time = now
            
        elif effect_step == 1:  # Espera 1 segundo
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                show_number(2, apply_brightness((255, 0, 0), brightness))
                effect_step = 2
                effect_start_time = now
                
        elif effect_step == 2:  # Espera 1 segundo
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                show_number(1, apply_brightness((255, 0, 0), brightness))
                effect_step = 3
                effect_start_time = now
                
        elif effect_step == 3:  # Espera 1 segundo e inicia
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                clear_matrix()
                reset_game()
                game_state = "RUNNING"
        

# --- Funções principais ---
def set_pixel(x, y, color):
    """Acende o LED na posição (x,y) com RGB"""
    if 0 <= x < 5 and 0 <= y < 5:
        np[MATRIX_MAP[y][x]] = color

def clear_matrix():
    """Apaga todos os LEDs"""
    for i in range(25):
        np[i] = (0, 0, 0)
    np.write()

def show_start_screen():
    """Tela inicial no OLED"""
    oled.fill(0)
    oled.text("SNAKE GAME", 30, 20)
    oled.text("Pressione B", 25, 40)
    oled.show()


last_score = -1

def update_display():
    global last_score
    if score != last_score:
        oled.fill(0)
        oled.text(f"Pontos: {score}", 0, 0)
        oled.text(f"Dificulade: {dificuldade}", 0, 20)
        oled.show()
        last_score = score

def read_joystick():
    """Lê o joystick e retorna a direção"""
    x = joy_x.read_u16()
    y = joy_y.read_u16()
    if x < 15000: return "LEFT"
    elif x > 50000: return "RIGHT"
    elif y < 15000: return "UP"
    elif y > 50000: return "DOWN"
    return None

def place_food():
    """Gera comida em posição aleatória"""
    global food
    while True:
        food = (random.randint(0, 4), random.randint(0, 4))
        if food not in snake:
            break

def reset_game():
    """Reinicia o jogo"""
    global snake, direction, score, game_speed, dificuldade
    snake = [(2, 2)]
    direction = "RIGHT"
    score = 0
    game_speed = 0.9
    dificuldade = 0
    place_food()
    update_display()

def update_snake():
    global snake, direction, score, game_speed, dificuldade
    
    head_x, head_y = snake[0]
    
    # Calcula nova posição (CORRIGIDO)
    if direction == "UP":
        head_y = (head_y + 1) % 5
    elif direction == "DOWN":
        head_y = (head_y - 1) % 5
    elif direction == "LEFT":
        head_x = (head_x - 1) % 5
    elif direction == "RIGHT":
        head_x = (head_x + 1) % 5
    
    # Debug (opcional)
    print(f"Movendo: {direction} ({head_x}, {head_y}) | Snake: {snake}")
    snake_sounds("move")

    # Verifica colisão
    if (head_x, head_y) in snake:
        lose_game()
        return
    
    # Insere nova cabeça
    snake.insert(0, (head_x, head_y))
    
    # Verifica se comeu
    if (head_x, head_y) == food:
        snake_sounds("eat")
        score += 1
        place_food()
        # Aumenta dificuldade
        game_speed = max(0.1, game_speed * 0.95)
        dificuldade +=1
    else:
        snake.pop()  # Remove cauda se não comeu

def draw():
    """Desenha a cobra e comida na matriz"""
    clear_matrix()
    draw_snake_color()
    set_pixel(food[0], food[1], apply_brightness((255,255,255), brightness))  # Comida vermelha
    np.write()

def draw_snake_color():
    """Desenha a cobra com cores variadas baseadas no HSL"""
    for i, pixel in enumerate(snake):
        # Converte o índice do segmento para uma cor
        color = set_hue(i)
        set_pixel(pixel[0], pixel[1], apply_brightness(color, brightness))

def set_hue(indice):
    """recebe um indice na conbra, faz o hue variar em 360/25 = 15 graus"""
    
    #Começa a partir do vermelho (255,0,0) -> hue = 0 graus
    if indice == 0:
        R = 255
        G = 0
        B = 0
        return (R,G,B)
    
    hue = indice * 15
    # Converte para RGB (0-255)
    r, g, b = hue_to_rgb(hue)
    return (int(r * 255), int(g * 255), int(b * 255))

def hue_to_rgb(h, S=1.0, V=1.0):
    """
    Converte um valor de hue (matiz) para RGB.
    
    Parâmetros:
    - h: ângulo de hue (0-360)
    - S: saturação (0-1), padrão 1.0
    - V: valor/brightness (0-1), padrão 1.0
    
    Retorna:
    - Tupla (R, G, B) com valores entre 0 e 1
    """
    # Normaliza h para o intervalo [0, 360)
    h = h % 360
    
    # Calcula f
    H = h / 60.0
    f = H - math.floor(H)
    
    # Calcula os valores intermediários
    p = V * (1 - S)
    q = V * (1 - S * f)
    t = V * (1 - S * (1 - f))
    
    # Determina R, G, B baseado no intervalo de h
    if 0 <= h < 60 or 300 <= h < 360:
        R = V
    elif 60 <= h < 120:
        R = q
    elif 120 <= h < 240:
        R = p
    else:  # 240 <= h < 300
        R = t
    
    if 0 <= h < 60:
        G = t
    elif 60 <= h < 180:
        G = V
    elif 180 <= h < 240:
        G = q
    else:  # 240 <= h < 360
        G = p
    
    if 0 <= h < 120:
        B = p
    elif 120 <= h < 180:
        B = t
    elif 180 <= h < 300:
        B = V
    else:  # 300 <= h < 360
        B = q
    
    return (R, G, B)


# --- Inicialização ---
show_start_screen()
while button_b.value() == 1:  # Espera pressionar o botão B
    time.sleep(0.1)
start_game()

# --- Loop principal ---
last_update = utime.ticks_ms()

while True:

    now = utime.ticks_ms()
    process_game_effects()
    process_sounds()  # Gerencia a reprodução dos sons
    check_joystick_movement()  # Chama a verificação do joystick

    if game_state == "RUNNING":
        if utime.ticks_diff(now, last_update) >= int(game_speed * 1000):
            last_update = now
            update_snake()
            draw()
            update_display()
            utime.sleep_ms(10)
            
        
    
    
    
        

from machine import Pin, SoftI2C, ADC
import neopixel
import time
import random
from machine import Timer
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
last_x = 32768  # Valor central do ADC (0-65535)
last_y = 32768
threshold = 10000  # Sensibilidade do movimento

def check_joystick_movement(timer):
    global direction, last_x, last_y
    
    x = joy_x.read_u16()
    y = joy_y.read_u16()
    
    # Detecta mudanças significativas nos eixos
    if abs(x - last_x) > threshold or abs(y - last_y) > threshold:
        new_dir = read_joystick()
        current_dir = direction  # Armazena a direção atual
        
        # Só muda se não for oposta à direção atual
        if new_dir and new_dir != oposite(current_dir):
            direction = new_dir
            print(f"Movimento detectado! Direção: {direction}")
    
    last_x, last_y = x, y

# Configura o timer para verificar a cada 50ms interrupção por timer 
timer = Timer()
timer.init(period=50, mode=Timer.PERIODIC, callback=check_joystick_movement)

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

from machine import Pin, PWM
import time

# Configura o buzzer (GPIO21 conforme manual da BitDoglab)
buzzer = PWM(Pin(21))

def play_tone(frequency, duration=0.1):
    """Toca um tom na frequência especificada"""
    buzzer.freq(frequency)
    buzzer.duty_u16(32768)  # 50% duty cycle
    time.sleep(duration)
    buzzer.duty_u16(0)  # Desliga

def snake_sounds(action):
    if action == "eat":
        # Som quando come a fruta
        play_tone(523, 0.1)  # Dó
        play_tone(659, 0.1)  # Mi
    elif action == "game_over":
        # Som de game over
        for freq in [392, 349, 330, 311]:
            play_tone(freq, 0.15)
    elif action == "move":
        # Som de movimento opcional
        play_tone(100, 0.02)

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

def lose_game():
    """Efeito de game over com piscadas em vermelho"""
    for _ in range(3):  # Repete o efeito 3 vezes
        # Pisca toda a matriz em vermelho
        for x in range(5):
            for y in range(5):
                set_pixel(x, y, apply_brightness((255, 0, 0), brightness))  # Vermelho
        np.write()
        time.sleep(0.2)  # Tempo ligado
        
        # Apaga tudo
        clear_matrix()
        snake_sounds("game_over")
        time.sleep(0.2)  # Tempo desligado
    
    reset_game()  # Reinicia o jogo após o efeito


def start_game():
    """Efeito de game over com piscadas em azul"""
    for _ in range(3):  # Repete o efeito 3 vezes
        # Pisca toda a matriz em vermelho
        for x in range(5):
            for y in range(5):
                set_pixel(x, y, apply_brightness((0, 0, 255), brightness))  # Vermelho
        np.write()
        time.sleep(0.2)  # Tempo ligado
        
        # Apaga tudo
        clear_matrix()
        time.sleep(0.5)  # Tempo desligado
    
    reset_game()  # Reinicia o jogo após o efeito


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

def update_display():
    """Atualiza o OLED com a pontuação"""
    oled.fill(0)
    oled.text(f"Score: {score}", 0, 0)
    oled.text(f"Speed: {game_speed}s", 0, 20)
    oled.show()

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
    global snake, direction, score
    snake = [(2, 2)]
    direction = "RIGHT"
    score = 0
    place_food()
    update_display()

def update_snake():
    """Atualiza a posição da cobra"""
    global snake, direction, score
    
    head_x, head_y = snake[0]

    if direction == "UP":
        head_y = (head_y + 1) % 5
    elif direction == "DOWN":
        head_y = (head_y - 1) % 5
    elif direction == "LEFT":
        head_x = (head_x - 1) % 5
    elif direction == "RIGHT":
        head_x = (head_x + 1) % 5

    if(head_x, head_y) in snake:
        lose_game()
        return
    
    snake.insert(0, (head_x, head_y))

    if (head_x, head_y) == food:
        snake_sounds("eat")
        score += 1
        place_food()
        #game_speed = max(0.1, game_speed * 0.9)  # Reduz 10% do tempo, mínimo 0.1s
    else:
        snake.pop()
        snake_sounds("move")

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
reset_game()

# --- Loop principal ---
while True:
    if button_b.value() == 0:
        start_game()
    
    # Verificação extra de segurança
    head_x, head_y = snake[0]
    next_x, next_y = head_x, head_y
    
    if direction == "UP":
        next_y = (head_y - 1) % 5
    elif direction == "DOWN":
        next_y = (head_y + 1) % 5
    elif direction == "LEFT":
        next_x = (head_x - 1) % 5
    elif direction == "RIGHT":
        next_x = (head_x + 1) % 5
    
    # Se a próxima posição for o corpo (exceto a cauda), não atualiza
    if (next_x, next_y) in snake[:-1]:
        continue
        
    update_snake()
    snake_sounds("move")
    update_display()
    draw()
    time.sleep(game_speed)
from machine import Pin, ADC, SoftI2C, Timer
import neopixel
import time
import random
import utime
from ssd1306 import SSD1306_I2C

# --- Configuração de Hardware ---
# Matriz de LEDs
np = neopixel.NeoPixel(Pin(7), 25)  # GPIO7 para matriz 5x5 NeoPixel
LED_MATRIX = [
    [24, 23, 22, 21, 20],  # Linha 0 (topo)
    [15, 16, 17, 18, 19],  # Linha 1
    [14, 13, 12, 11, 10],  # Linha 2
    [5, 6, 7, 8, 9],       # Linha 3
    [4, 3, 2, 1, 0]        # Linha 4 (base - jogador)
]

# Display OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))  # GPIO15 (SCL), GPIO14 (SDA)
oled = SSD1306_I2C(128, 64, i2c)

# Joystick
vrx = ADC(Pin(27))  # GPIO27 (VRx)
vry = ADC(Pin(26))  # GPIO26 (VRy)
JOYSTICK_THRESHOLD_LOW = 12000  # Limite para esquerda
JOYSTICK_THRESHOLD_HIGH = 52000  # Limite para direita

# Botões
botao_b = Pin(6, Pin.IN, Pin.PULL_UP)  # GPIO6 (Botão B)

# --- Variáveis do Jogo ---
player_pos = 2        # Posição inicial do jogador (centro)
score = 0             # Pontuação
game_active = False   # Estado do jogo
cars = []             # Lista de carros obstáculos
last_car_move = 0     # Último tempo de movimento
car_speed = 500       # Velocidade inicial dos carros (ms)
last_car_spawn = 0    # Último tempo de geração de carros
spawn_interval = 2000 # Intervalo entre geração de carros (ms)

# --- Funções Auxiliares ---
def clear_matrix():
    """Apaga todos os LEDs da matriz"""
    for i in range(25):
        np[i] = (0, 0, 0)
    np.write()

def set_pixel(x, y, color):
    """Acende um LED específico na matriz"""
    if 0 <= x < 5 and 0 <= y < 5:
        np[LED_MATRIX[y][x]] = color

def show_start_screen():
    """Exibe a tela inicial no OLED"""
    oled.fill(0)
    oled.text("CARRINHO GAME", 15, 20)
    oled.text("Pressione B", 25, 40)
    oled.show()

def show_game_over():
    """Exibe tela de game over"""
    oled.fill(0)
    oled.text("GAME OVER", 30, 20)
    oled.text(f"Score: {score}", 30, 40)
    oled.show()

def update_display():
    """Atualiza o display com a pontuação"""
    oled.fill(0)
    oled.text(f"Score: {score}", 0, 0)
    oled.text(f"Speed: {car_speed}ms", 0, 20)
    oled.show()

# --- Funções do Jogo ---
def generate_cars():
    """Gera novos carros obstáculos"""
    global last_car_spawn
    
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_car_spawn) >= spawn_interval:
        # Gera 1-2 carros em posições aleatórias
        for _ in range(random.randint(1, 2)):
            col = random.randint(0, 4)
            cars.append([0, col])  # Adiciona na linha 0 (topo)
        last_car_spawn = current_time

def draw_cars():
    """Desenha todos os carros na matriz"""
    for car in cars:
        set_pixel(car[1], car[0], (64, 0, 0))  # Vermelho para carros

def draw_game_state():
    """Desenha o estado atual do jogo"""
    clear_matrix()
    draw_cars()
    set_pixel(player_pos, 4, (0, 0, 64))  # Azul para jogador
    np.write()

def move_cars():
    """Movimenta os carros e verifica colisões"""
    global cars, game_active, score, car_speed, last_car_move
    
    current_time = utime.ticks_ms()
    if utime.ticks_diff(current_time, last_car_move) < car_speed:
        return
    
    last_car_move = current_time
    
    # Verifica colisões
    for car in cars:
        if car[0] == 4 and car[1] == player_pos:
            game_active = False
            show_game_over()
            return
    
    # Movimenta carros
    for car in cars:
        car[0] += 1  # Move para baixo
    
    # Remove carros que saíram da tela
    cars = [car for car in cars if car[0] < 5]
    
    # Pontuação: conta carros que chegaram ao final
    score += len([car for car in cars if car[0] == 4])
    
    # Aumenta dificuldade
    if score > 0 and score % 5 == 0:
        car_speed = max(200, car_speed - 50)  # Aumenta velocidade
    
    update_display()

# --- Interrupções ---
def joystick_handler(timer):
    """Controla o movimento do jogador"""
    global player_pos
    if game_active:
        x_value = vrx.read_u16()
        
        if x_value < JOYSTICK_THRESHOLD_LOW:
            player_pos = max(0, player_pos - 1)  # Esquerda
        elif x_value > JOYSTICK_THRESHOLD_HIGH:
            player_pos = min(4, player_pos + 1)  # Direita
        
        draw_game_state()

def button_handler(pin):
    """Controla início/reinício do jogo"""
    global game_active, score, player_pos, cars, car_speed
    
    if not game_active:
        # Inicia novo jogo
        game_active = True
        score = 0
        player_pos = 2
        cars = []
        car_speed = 500
        clear_matrix()
        oled.fill(0)
        oled.show()
    else:
        # Reinicia o jogo
        game_active = False
        clear_matrix()
        show_game_over()

# Configura interrupções
joystick_timer = Timer()
joystick_timer.init(period=100, mode=Timer.PERIODIC, callback=joystick_handler)
botao_b.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

# --- Inicialização ---
show_start_screen()
while botao_b.value() == 1:  # Espera pressionar o botão B
    time.sleep(0.1)

# --- Loop Principal ---
while True:
    current_time = utime.ticks_ms()
    
    if game_active:
        generate_cars()
        move_cars()
        draw_game_state()
    
    time.sleep(0.02)  # Pequeno delay para reduzir uso da CPU
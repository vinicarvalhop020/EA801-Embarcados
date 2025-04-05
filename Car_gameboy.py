from machine import Pin, ADC, SoftI2C, PWM
from ssd1306 import SSD1306_I2C
import neopixel
import time
import random
import machine

# Configurações iniciais
np = neopixel.NeoPixel(Pin(7), 25)
NUM_LEDS = 25

LED_MATRIX = [
    [24, 23, 22, 21, 20],
    [15, 16, 17, 18, 19],
    [14, 13, 12, 11, 10],
    [5, 6, 7, 8, 9],
    [4, 3, 2, 1, 0]
]

# Display OLED
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)

# Joystick
vrx = ADC(Pin(27))  # Horizontal
vry = ADC(Pin(26))  # Vertical
JOYSTICK_THRESHOLD_LOW = 12000
JOYSTICK_THRESHOLD_HIGH = 52000

# Botões
botao_b = Pin(6, Pin.IN, Pin.PULL_UP)

# Variáveis do jogo
player_x = 2
player_y = 4
score = 100
game_active = False
cars = []
last_car_move = 0
last_car_generation = 0
should_generate_cars = True
initial_cars_generated = False  # Nova flag para controle

# Variáveis de debounce
DEBOUNCE_TIME = 300  # 300ms
last_button_time = 0

# Função otimizada para desenhar o estado do jogo
def draw_game_state():
    np.fill((0, 0, 0))  # Limpa tudo
    
    # Desenha carros
    for car in cars:
        if 0 <= car[0] < 5:
            np[LED_MATRIX[car[0]][car[1]]] = (64, 0, 0)  # Vermelho
    
    # Desenha jogador
    np[LED_MATRIX[player_y][player_x]] = (0, 0, 64)  # Azul
    np.write()

# Função de debounce
def debounce():
    global last_button_time
    current_time = time.ticks_ms()
    if current_time - last_button_time < DEBOUNCE_TIME:
        return False
    last_button_time = current_time
    return True

# Função de interrupção do botão B
def button_handler(pin):
    global game_active, score, player_x, player_y, cars, should_generate_cars, initial_cars_generated
    
    if not debounce():
        return
    
    if not game_active:
        # Inicia novo jogo
        game_active = True
        score = 100
        player_x = 2
        player_y = 4
        cars = []
        should_generate_cars = True
        initial_cars_generated = False  # Reseta a flag
        generate_initial_cars()  # Gera apenas a primeira fileira
        oled.fill(0)
        oled.text("Pontos: 100", 0, 0)
        oled.show()
        draw_game_state()
    else:
        # Reinicia o jogo
        game_active = False
        show_game_over()

# Configura interrupção do botão
botao_b.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

# Geração da PRIMEIRA fileira de carros
def generate_initial_cars():
    global cars, initial_cars_generated
    positions = [0, 1, 2, 3, 4]
    random.shuffle(positions)
    
    num_cars = random.randint(1, 3)
    for i in range(num_cars):
        if i >= len(positions):
            break
        cars.append([0, positions[i]])
    
    initial_cars_generated = True

# Geração das fileiras SUBSEQUENTES
def generate_subsequent_cars():
    global cars
    positions = [0, 1, 2, 3, 4]
    random.shuffle(positions)
    
    num_cars = random.randint(1, 3)
    for i in range(num_cars):
        if i >= len(positions):
            break
        # Verifica se já não existe carro na posição
        if not any(car[1] == positions[i] for car in cars if car[0] == 0):
            cars.append([0, positions[i]])

def move_cars():
    global cars, game_active, score, last_car_move, should_generate_cars, last_car_generation
    
    current_time = time.ticks_ms()
    
    # Movimentação dos carros (a cada 500ms)
    if current_time - last_car_move >= 500:
        last_car_move = current_time
        
        # Verifica colisão
        for car in cars:
            if car[0] == player_y and car[1] == player_x:
                game_active = False
                show_game_over()
                return
        
        # Movimenta carros
        cars_passed = 0
        new_cars = []
        for car in cars:
            car[0] += 1
            if car[0] < 5:
                new_cars.append(car)
            else:
                cars_passed += 1
        
        cars = new_cars
        score = max(0, score - cars_passed)
        
        if score <= 0:
            game_active = False
            show_win_message()
            return
    
    # Geração de novos carros (a cada 1s após a primeira fileira)
    if initial_cars_generated and current_time - last_car_generation >= 500:
        if should_generate_cars:
            generate_subsequent_cars()
        should_generate_cars = not should_generate_cars
        last_car_generation = current_time
    
    update_display()
    draw_game_state()

# ... (o restante das funções permanece igual)

def game_loop():
    while True:
        if game_active:
            move_cars()
        time.sleep(0.05)

# Inicia o jogo
game_loop()
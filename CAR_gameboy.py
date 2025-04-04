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

# Joystick com sensibilidade alta
vrx = ADC(Pin(27))  # Horizontal
vry = ADC(Pin(26))  # Vertical
JOYSTICK_THRESHOLD_LOW = 12000  # esquerda/baixo
JOYSTICK_THRESHOLD_HIGH = 52000  # direita/cima

# Botões com interrupção
botao_b = Pin(6, Pin.IN, Pin.PULL_UP)

# Variáveis do jogo
player_x = 2
player_y = 4  # Começa na última linha (linha 4)
score = 100  # Começa em 100 agora
game_active = False
cars = []
last_car_move = 0
last_car_generation = 0
should_generate_cars = True  # Controla a geração alternada de carros

# Função de interrupção do joystick (agora com movimento vertical)
def joystick_handler(pin):
    global player_x, player_y
    x_value = vrx.read_u16()
    y_value = vry.read_u16()
    
    # Movimento horizontal
    if x_value < JOYSTICK_THRESHOLD_LOW:
        player_x = max(0, player_x - 1)  # Move para esquerda
    elif x_value > JOYSTICK_THRESHOLD_HIGH:
        player_x = min(4, player_x + 1)  # Move para direita
    
    # Movimento vertical
    if y_value < JOYSTICK_THRESHOLD_LOW:
        player_y = min(4, player_y + 1)  # Move para baixo
    elif y_value > JOYSTICK_THRESHOLD_HIGH:
        player_y = max(0, player_y - 1)  # Move para cima
    
    if game_active:
        draw_game_state()

# Configura interrupção do joystick
joystick_timer = machine.Timer()
joystick_timer.init(period=100, mode=machine.Timer.PERIODIC, callback=lambda t: joystick_handler(None))

# Função de interrupção do botão B
def button_handler(pin):
    global game_active, score, player_x, player_y, cars, last_car_move, should_generate_cars
    
    if not game_active:
        # Inicia novo jogo
        game_active = True
        score = 100  # Começa em 100
        player_x = 2
        player_y = 4
        cars = []
        should_generate_cars = True
        generate_cars()
        clear_matrix()
        oled.fill(0)
        oled.text("Pontos: 100", 0, 0)
        oled.show()
    else:
        # Reinicia o jogo
        game_active = False
        clear_matrix()
        show_game_over()

botao_b.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

# Funções do jogo
def draw_game_state():
    clear_matrix()
    draw_cars()
    np[LED_MATRIX[player_y][player_x]] = (0, 0, 64)  # Desenha jogador (azul)
    np.write()

def move_cars():
    global cars, game_active, score, last_car_move, should_generate_cars
    
    if time.ticks_ms() - last_car_move < 500:  # Delay de 0.5s
        return
    
    last_car_move = time.ticks_ms()
    
    # Verifica colisão
    for car in cars:
        if car[0] == player_y and car[1] == player_x:
            game_active = False
            show_game_over()
            return
    
    # Movimenta carros
    for car in cars:
        car[0] += 1  # Move os carros para baixo
    
    # Remove carros que saíram da tela e atualiza pontuação
    cars_before = len(cars)
    cars = [car for car in cars if car[0] < 5]
    cars_passed = cars_before - len(cars)
    score = max(0, score - cars_passed)  # Reduz a pontuação
    
    # Verifica se o jogador ganhou
    if score <= 0:
        game_active = False
        show_win_message()
        return
    
    # Gera novos carros alternadamente
    if time.ticks_ms() - last_car_generation > 1000:  # Gera carros a cada 1s
        if should_generate_cars:
            generate_cars()
        should_generate_cars = not should_generate_cars  # Alterna a geração
        last_car_generation = time.ticks_ms()
    
    update_display()

def generate_cars():
    global cars
    # Gera carros apenas na primeira linha (linha 0)
    positions = random.sample([0, 1, 2, 3, 4], random.randint(1, 3))  # 1-3 carros por linha
    for pos in positions:
        cars.append([0, pos])  # [linha, coluna]

def draw_cars():
    for car in cars:
        if 0 <= car[0] < 5:  # Verifica se o carro está dentro da matriz
            np[LED_MATRIX[car[0]][car[1]]] = (64, 0, 0)  # Desenha carros (vermelhos)

def clear_matrix():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()

def update_display():
    oled.fill(0)
    oled.text(f"Pontos: {score}", 0, 0)
    oled.show()

def show_game_over():
    clear_matrix()
    oled.fill(0)
    oled.text("Game Over!", 20, 20)
    oled.show()

def show_win_message():
    # Pisca a matriz toda em azul
    for _ in range(5):
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 64)
        np.write()
        oled.fill(0)
        oled.text("Voce ganhou!", 20, 20)
        oled.show()
        time.sleep(0.5)
        
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 0)
        np.write()
        time.sleep(0.5)

# Loop principal
def game_loop():
    while True:
        if game_active:
            move_cars()
        time.sleep(0.05)

# Inicia o jogo
game_loop()

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

# Função otimizada para desenhar o estado do jogo sem piscar
def draw_game_state():
    # Primeiro desenha todos os elementos em um buffer
    buffer = [(0, 0, 0) for _ in range(NUM_LEDS)]
    
    # Desenha carros inimigos
    for car in cars:
        if 0 <= car[0] < 5:
            led_index = LED_MATRIX[car[0]][car[1]]
            buffer[led_index] = (64, 0, 0)  # Vermelho
    
    # Desenha jogador
    led_index = LED_MATRIX[player_y][player_x]
    buffer[led_index] = (0, 0, 64)  # Azul
    
    # Aplica tudo de uma vez
    for i in range(NUM_LEDS):
        np[i] = buffer[i]
    np.write()

# Função de interrupção do joystick
def joystick_handler(pin):
    global player_x, player_y
    x_value = vrx.read_u16()
    y_value = vry.read_u16()
    
    if x_value < JOYSTICK_THRESHOLD_LOW:
        player_x = max(0, player_x - 1)
    elif x_value > JOYSTICK_THRESHOLD_HIGH:
        player_x = min(4, player_x + 1)
    
    if y_value < JOYSTICK_THRESHOLD_LOW:
        player_y = min(4, player_y + 1)
    elif y_value > JOYSTICK_THRESHOLD_HIGH:
        player_y = max(0, player_y - 1)
    
    if game_active:
        draw_game_state()

# Configura interrupção do joystick
joystick_timer = machine.Timer()
joystick_timer.init(period=100, mode=machine.Timer.PERIODIC, callback=lambda t: joystick_handler(None))

# Função de interrupção do botão B
def button_handler(pin):
    global game_active, score, player_x, player_y, cars, should_generate_cars
    
    if not game_active:
        # Inicia novo jogo
        game_active = True
        score = 100
        player_x = 2
        player_y = 4
        cars = []
        should_generate_cars = True
        generate_cars()
        oled.fill(0)
        oled.text("Pontos: 100", 0, 0)
        oled.show()
        draw_game_state()  # Desenha estado inicial
    else:
        # Reinicia o jogo
        game_active = False
        show_game_over()

botao_b.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

def move_cars():
    global cars, game_active, score, last_car_move, should_generate_cars
    
    if time.ticks_ms() - last_car_move < 500:
        return
    
    last_car_move = time.ticks_ms()
    
    # Verifica colisão
    for car in cars:
        if car[0] == player_y and car[1] == player_x:
            game_active = False
            show_game_over()
            return
    
    # Movimenta carros e conta os que saíram
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
    
    # Gera novos carros alternadamente
    if time.ticks_ms() - last_car_generation > 1000:
        if should_generate_cars:
            generate_cars()
        should_generate_cars = not should_generate_cars
        last_car_generation = time.ticks_ms()
    
    update_display()
    draw_game_state()  # Desenha o novo estado

def generate_cars():
    global cars
    positions = [0, 1, 2, 3, 4]
    
    # Embaralha simplesmente selecionando posições aleatórias
    num_cars = random.randint(1, 3)
    for _ in range(num_cars):
        if not positions:
            break
        pos = random.choice(positions)
        positions.remove(pos)
        cars.append([0, pos])

def update_display():
    oled.fill(0)
    oled.text(f"Pontos: {score}", 0, 0)
    oled.show()

def show_game_over():
    for i in range(NUM_LEDS):
        np[i] = (0, 0, 0)
    np.write()
    oled.fill(0)
    oled.text("Game Over!", 20, 20)
    oled.show()

def show_win_message():
    for _ in range(5):
        # Pisca azul
        for i in range(NUM_LEDS):
            np[i] = (0, 0, 64)
        np.write()
        oled.fill(0)
        oled.text("Voce ganhou!", 20, 20)
        oled.show()
        time.sleep(0.5)
        
        # Apaga
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
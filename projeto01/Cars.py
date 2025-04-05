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

# Variáveis de debounce
DEBOUNCE_TIME = 300
last_button_time = 0

# Função para embaralhar manualmente (substitui o random.shuffle)
def manual_shuffle(arr):
    for i in range(len(arr)-1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def set_pixel(x, y, color):
    """Acende o LED na posição (x,y) com RGB"""
    if 0 <= x < 5 and 0 <= y < 5:
        np[LED_MATRIX[y][x]] = color

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

def draw_game_state():
    np.fill((0, 0, 0))
    for car in cars:
        if 0 <= car[0] < 5:
            np[LED_MATRIX[car[0]][car[1]]] = (64, 0, 0)
    np[LED_MATRIX[player_y][player_x]] = (0, 0, 64)
    np.write()

def debounce():
    global last_button_time
    current_time = time.ticks_ms()
    if current_time - last_button_time < DEBOUNCE_TIME:
        return False
    last_button_time = current_time
    return True

def apply_brightness(color, brightness):
    """Ajusta o brilho de uma cor RGB (0-255)"""
    r, g, b = color
    return (
        int(r * brightness),
        int(g * brightness),
        int(b * brightness)
    )

def button_handler(pin):
    global game_active, score, player_x, player_y, cars, should_generate_cars
    
    if not debounce():
        return
    
    if not game_active:
        show_number(3, apply_brightness((0, 0, 255), 0.1))
        time.sleep_ms(500)
        show_number(2, apply_brightness((0, 0, 255), 0.1))
        time.sleep_ms(500)
        show_number(1, apply_brightness((0, 0, 255), 0.1))
        time.sleep_ms(500)
        game_active = True
        score = 100
        player_x = 2
        player_y = 4
        cars = []
        should_generate_cars = True
        generate_subsequent_cars()
        oled.fill(0)
        oled.text("Pontos: 100", 0, 0)
        oled.show()
        draw_game_state()
    else:
        game_active = False
        show_game_over()

botao_b.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

def generate_subsequent_cars():
    global cars
    positions = manual_shuffle([0, 1, 2, 3, 4])
    num_cars = random.randint(1, 3)
    
    new_cars = []
    for pos in positions[:num_cars]:
        if not any(car[1] == pos and car[0] == 0 for car in cars):
            new_cars.append([0, pos])
    
    cars.extend(new_cars)

def move_cars():
    global cars, game_active, score, last_car_move, should_generate_cars, last_car_generation
    
    current_time = time.ticks_ms()
    
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
    
    # Geração de novos carros
    if current_time - last_car_generation >= 500:
        if should_generate_cars:
            generate_subsequent_cars()
        should_generate_cars = not should_generate_cars
        last_car_generation = current_time
    
    update_display()
    draw_game_state()

def update_display():
    oled.fill(0)
    oled.text(f"Pontos: {score}", 0, 0)
    oled.show()

def show_game_over():
    np.fill((0, 0, 0))
    np.write()
    oled.fill(0)
    oled.text("Game Over!", 20, 20)
    oled.show()

def show_win_message():
    for _ in range(5):
        np.fill((0, 0, 64))
        np.write()
        oled.fill(0)
        oled.text("Voce ganhou!", 20, 20)
        oled.show()
        time.sleep(0.5)
        np.fill((0, 0, 0))
        np.write()
        time.sleep(0.5)

def game_loop():
    while True:
        if game_active:
            move_cars()
        time.sleep(0.05)

# Configura interrupção do joystick
joystick_timer = machine.Timer()
joystick_timer.init(period=100, mode=machine.Timer.PERIODIC, callback=lambda t: joystick_handler(None))

# Função de interrupção do joystick
def joystick_handler(pin):
    global player_x, player_y
    if not game_active:
        return
    
    x_value = vrx.read_u16()
    y_value = vry.read_u16()
    
    new_x = player_x
    new_y = player_y
    
    if x_value < JOYSTICK_THRESHOLD_LOW:
        new_x = max(0, player_x - 1)
    elif x_value > JOYSTICK_THRESHOLD_HIGH:
        new_x = min(4, player_x + 1)
    
    if y_value < JOYSTICK_THRESHOLD_LOW:
        new_y = min(4, player_y + 1)
    elif y_value > JOYSTICK_THRESHOLD_HIGH:
        new_y = max(0, player_y - 1)
    
    if new_x != player_x or new_y != player_y:
        player_x, player_y = new_x, new_y
        draw_game_state()

# Inicia o jogo
game_loop()
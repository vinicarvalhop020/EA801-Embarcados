from machine import Pin, ADC, SoftI2C, PWM
from ssd1306 import SSD1306_I2C
import neopixel
import utime  # Alterado de time para utime
import random
import machine
import math

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

VICTORY_SOUND = [
    (392, 200),  # Sol
    (523, 200),  # Dó agudo
    (659, 300),  # Mi
    (784, 400)   # Sol agudo
]

GAMEOVER_SOUND = [
    (165, 400),  # Mi
    (131, 600),  # Dó
    (110, 800)   # Lá mais grave
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
game_over = False
BUZZER_PIN = 21  # GPIO21 para Buzzer A (conforme seu hardware)
buzzer = PWM(Pin(BUZZER_PIN))
engine_sound_enabled = True
last_sound_update = 0
current_frequency = 200
target_frequency = 0
engine_rpm = 0 

# Variáveis de debounce
DEBOUNCE_TIME = 500
last_button_time = 0

# Função para embaralhar manualmente (substitui o random.shuffle)
def manual_shuffle(arr):
    for i in range(len(arr)-1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def update_engine_sound():
    global last_sound_update, current_frequency, target_frequency, engine_rpm
    
    if not engine_sound_enabled or not game_active:
        buzzer.duty_u16(0)
        return
    
    current_time = utime.ticks_ms()
    
    # Atualiza a cada 50ms para manter um som mais constante
    if current_time - last_sound_update > 50:
        last_sound_update = current_time
        
        
        base_freq = 200  # Frequência mínima (mais grave)
        
        # Calcula variação baseada na posição e movimento
        position_factor = abs(player_x - 2) * 30  # 0 a 60
        movement_factor = 0
        
        # Adiciona variação quando o jogador se move
        if player_x != 2 or player_y != 4:
            movement_factor = 50 + random.randint(0, 30)
        
        target_frequency = base_freq + position_factor + movement_factor
        
        # Suaviza a transição
        if current_frequency < target_frequency:
            current_frequency = min(current_frequency + 5, target_frequency)
        elif current_frequency > target_frequency:
            current_frequency = max(current_frequency - 5, target_frequency)
        
        # Aplica a frequência com volume moderado
        buzzer.freq(int(current_frequency))
        
        # Efeito de ronco - variação no volume
        volume = 2000 + int(math.sin(utime.ticks_ms() / 200) * 10000)
        buzzer.duty_u16(volume)

        # Efeito aleatório de "arrancada"
        if random.random() < 0.1:  # 10% de chance
            buzzer.freq(int(current_frequency * 1.2))
            buzzer.duty_u16(30000)
            utime.sleep_ms(30)
            buzzer.freq(int(current_frequency))

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
    current_time = utime.ticks_ms()  # Alterado de time para utime
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
    global game_active, score, player_x, player_y, cars, should_generate_cars, game_over, engine_sound_enabled
    
    if not debounce():
        return
    
    if not game_active:
        game_active = True
        game_over = False
        engine_sound_enabled = True
        
        # Música da contagem regressiva (notas em Hz, duração em ms)
        COUNTDOWN_SOUND = [
            (523, 200),  # Dó
            (392, 200),  # Sol
            (523, 200), # Dó
            (659, 400)   # Mi
        ]
        
        # Toca a primeira parte da música junto com o número 3
        show_number(3, apply_brightness((0, 0, 255), 0.1))
        for note, duration in COUNTDOWN_SOUND[:2]:
            buzzer.freq(note)
            buzzer.duty_u16(32768)  # 50% volume
            utime.sleep_ms(duration)
            buzzer.duty_u16(0)
            utime.sleep_ms(50)
        
        # Número 2 com continuação da música
        show_number(2, apply_brightness((0, 0, 255), 0.1))
        for note, duration in COUNTDOWN_SOUND[2:]:
            buzzer.freq(note)
            buzzer.duty_u16(32768)
            utime.sleep_ms(duration)
            buzzer.duty_u16(0)
            utime.sleep_ms(50)
        
        # Número 1 com nota final
        show_number(1, apply_brightness((0, 0, 255), 0.1))
        buzzer.freq(784)  # Sol agudo
        buzzer.duty_u16(32768)
        utime.sleep_ms(400)
        buzzer.duty_u16(0)
        
        # Inicia o jogo
        score = 100
        player_x = 2
        player_y = 4
        cars = []
        should_generate_cars = False
        generate_subsequent_cars()
        oled.fill(0)
        oled.text("Pontos: 100", 0, 0)
        oled.show()
        draw_game_state()
    else:
        if game_over == True:
            game_active = False
            engine_sound_enabled = False
            show_game_over()

botao_b.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

def generate_subsequent_cars():
    global cars
    positions = manual_shuffle([0, 1, 2, 3, 4])
    num_cars = random.randint(1, 4)
    
    new_cars = []
    for pos in positions[:num_cars]:
        if not any(car[1] == pos and car[0] == 0 for car in cars):
            new_cars.append([0, pos])
    
    cars.extend(new_cars)

def move_cars():
    global cars, game_active, score, last_car_move, should_generate_cars, last_car_generation, game_over
    
    current_time = utime.ticks_ms()  # Alterado de time para utime
    
    if current_time - last_car_move >= 500:
        last_car_move = current_time
        
        # Verifica colisão
        for car in cars:
            if car[0] == player_y and car[1] == player_x:
                game_active = False
                game_over = True
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
    
    update_engine_sound()
    update_display()
    draw_game_state()

def update_display():
    oled.fill(0)
    oled.text(f"Pontos: {score}", 0, 0)
    oled.show()

def show_game_over():
    global engine_sound_enabled
    engine_sound_enabled = False
    buzzer.duty_u16(0)  # Desliga o som do motor
    
    # Efeito visual
    np.fill((64, 0, 0))  # Vermelho
    np.write()
    oled.fill(0)
    oled.text("Game Over!", 20, 20)
    oled.text("Pressione B", 20, 40)
    oled.show()
    
    # Toca o som de Game Over
    for note, duration in GAMEOVER_SOUND:
        buzzer.freq(note)
        buzzer.duty_u16(49152)  # 75% volume para mais impacto
        utime.sleep_ms(duration)
        buzzer.duty_u16(0)  # Pausa curta entre notas
        utime.sleep_ms(50)
    
    # Pisca os LEDs vermelhos
    for _ in range(3):
        np.fill((64, 0, 0))
        np.write()
        utime.sleep_ms(200)
        np.fill((0, 0, 0))
        np.write()
        utime.sleep_ms(200)
    
    buzzer.duty_u16(0)  # Garante que o buzzer seja desligado

def show_win_message():
    global engine_sound_enabled
    engine_sound_enabled = False
    buzzer.duty_u16(0)  # Desliga o som do motor
    
    for i in range(5):
        # Toca a melodia de vitória
        for note, duration in VICTORY_SOUND:
            buzzer.freq(note)
            buzzer.duty_u16(32768)  # 50% volume
            utime.sleep_ms(duration)
            buzzer.duty_u16(0)  # Pausa entre notas
            utime.sleep_ms(50)
        
        # Efeito visual
        np.fill((0, 0, 64))  # Azul
        np.write()
        oled.fill(0)
        oled.text("Voce ganhou!", 20, 20)
        oled.show()
        utime.sleep_ms(300)
        
        np.fill((0, 0, 0))  # Apaga
        np.write()
        utime.sleep_ms(300)

    buzzer.duty_u16(0)  # Garante que o buzzer seja desligado

def show_start_screen():
    """Tela inicial no OLED"""
    oled.fill(0)
    oled.text("RACING CARS", 5, 20)
    oled.text("Pressione B", 25, 40)
    oled.show()

def game_loop():
    while True:
        if game_active:
            move_cars()
        utime.sleep(0.05)  # Alterado de time para utime

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
show_start_screen()
game_loop()
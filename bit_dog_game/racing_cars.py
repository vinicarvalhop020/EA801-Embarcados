def game_vars_cars():
    global i2c, oled, joy_x, joy_y, JOYSTICK_THRESHOLD_LOW, JOYSTICK_THRESHOLD_HIGH, machine
    global botao_b_dog, player_x, player_y, score, game_active, cars, last_car_move, button_a
    global last_car_generation, should_generate_cars, game_over, BUZZER_PIN, buzzer
    global engine_sound_enabled, last_sound_update, current_frequency, target_frequency
    global engine_rpm, DEBOUNCE_TIME, last_button_time, np, joystick_timer, last_button_time
    global direction, last_x, last_y, last_joystick_check, joystick_interval, threshold, last_joystick_time
    global button_b, brightness, utime, random, math, MATRIX_MAP_RACING, ast_joystick_time
    global COUNTDOWN_PATTERNS_RACING, VICTORY_SOUND, GAMEOVER_SOUND

    from machine import Pin, ADC, SoftI2C, PWM, Timer
    from ssd1306 import SSD1306_I2C
    import neopixel
    import utime
    import random
    import math

    # Display OLED
    i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
    oled = SSD1306_I2C(128, 64, i2c)

    # Joystick
    joy_x = ADC(Pin(27))  # Horizontal
    joy_y = ADC(Pin(26))  # Vertical
    JOYSTICK_THRESHOLD_LOW = 12000
    JOYSTICK_THRESHOLD_HIGH = 52000
    BUZZER_PIN = 21  # GPIO21 para Buzzer

    # Botões
    button_b = Pin(6, Pin.IN, Pin.PULL_UP)
    button_a = Pin(5, Pin.IN, Pin.PULL_UP)
    np = neopixel.NeoPixel(Pin(7), 25)  # Matriz 5x5

    # Variáveis do jogo
    joystick_interval = 50  # ms (mesmo intervalo do timer anterior)
    player_x = 2
    player_y = 4
    score = 100
    game_active = False
    cars = []
    last_car_move = 0
    last_car_generation = 0
    should_generate_cars = True
    game_over = False
    buzzer = PWM(Pin(BUZZER_PIN))
    engine_sound_enabled = True
    last_sound_update = 0
    current_frequency = 200
    target_frequency = 0
    last_joystick_time = 0
    engine_rpm = 0 
    threshold = 10000
    last_joystick_check = 0
    brightness = 0.1

    # Variáveis de debounce
    DEBOUNCE_TIME = 500
    last_button_time = 0
    ast_joystick_time = 0

    # --- Variáveis globais ---
    MATRIX_MAP_RACING = [
        [24, 23, 22, 21, 20],
        [15, 16, 17, 18, 19],
        [14, 13, 12, 11, 10],
        [5, 6, 7, 8, 9],
        [4, 3, 2, 1, 0]
    ]

    COUNTDOWN_PATTERNS_RACING = {
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


def manual_shuffle(arr):
    """Implementa um metodo de embaralhar uma lista"""
    for i in range(len(arr)-1, 0, -1):
        j = random.randint(0, i)
        arr[i], arr[j] = arr[j], arr[i]
    return arr

def update_engine_sound():
    """Controla os sons do carro, motor e arranque"""
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

def set_pixel_cars(x, y, color):
    """Acende o LED na posição (x,y) com RGB"""
    if 0 <= x < 5 and 0 <= y < 5:
        np[MATRIX_MAP_RACING[y][x]] = color

def show_number(number, color):
    """Desenha um número na matriz LED"""
    pattern = COUNTDOWN_PATTERNS_RACING.get(number)
    if not pattern:
        return
    
    for y in range(5):
        for x in range(5):
            if pattern[y][x]:
                set_pixel_cars(x, y, color)
            else:
                set_pixel_cars(x, y, (0, 0, 0))
    np.write()

def draw_game_state():
    """Desenha o estado do jogo"""
    np.fill((0, 0, 0))
    for car in cars:
        if 0 <= car[0] < 5:
            np[MATRIX_MAP_RACING[car[0]][car[1]]] = (64, 0, 0)
    np[MATRIX_MAP_RACING[player_y][player_x]] = (0, 0, 64)
    np.write()

def debounce():
    """Controla o debounce dos botões"""
    global last_button_time
    current_time = utime.ticks_ms()  # Alterado de time para utime
    if current_time - last_button_time < DEBOUNCE_TIME:
        return False
    last_button_time = current_time
    return True

def apply_brightness_cars(color, brightness):
    """Ajusta o brilho de uma cor RGB (0-255)"""
    r, g, b = color
    return (
        int(r * brightness),
        int(g * brightness),
        int(b * brightness)
    )

def button_handler():
    """Controla o botão de reset ao apertar B"""
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
        show_number(3, apply_brightness_cars((0, 0, 255), 0.1))
        for note, duration in COUNTDOWN_SOUND[:2]:
            buzzer.freq(note)
            buzzer.duty_u16(32768)  # 50% volume
            utime.sleep_ms(duration)
            buzzer.duty_u16(0)
            utime.sleep_ms(50)
        
        # Número 2 com continuação da música
        show_number(2, apply_brightness_cars((0, 0, 255), 0.1))
        for note, duration in COUNTDOWN_SOUND[2:]:
            buzzer.freq(note)
            buzzer.duty_u16(32768)
            utime.sleep_ms(duration)
            buzzer.duty_u16(0)
            utime.sleep_ms(50)
        
        # Número 1 com nota final
        show_number(1, apply_brightness_cars((0, 0, 255), 0.1))
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
            show_game_over_cars()

def generate_subsequent_cars():
    """gera uma sequencia de inimigos"""
    global cars
    positions = manual_shuffle([0, 1, 2, 3, 4])
    num_cars = random.randint(1, 4)
    
    new_cars = []
    for pos in positions[:num_cars]:
        if not any(car[1] == pos and car[0] == 0 for car in cars):
            new_cars.append([0, pos])
    
    cars.extend(new_cars)

def move_cars():
    """move a posição dos carros inimigos"""
    global cars, game_active, score, last_car_move, should_generate_cars, last_car_generation, game_over
    
    current_time = utime.ticks_ms()  # Alterado de time para utime
    
    if current_time - last_car_move >= 500:
        last_car_move = current_time
        
        # Verifica colisão
        for car in cars:
            if car[0] == player_y and car[1] == player_x:
                game_active = False
                game_over = True
                show_game_over_cars()
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
            show_win_message_cars()
            return
    
    # Geração de novos carros
    if current_time - last_car_generation >= 500:
        if should_generate_cars:
            generate_subsequent_cars()
        should_generate_cars = not should_generate_cars
        last_car_generation = current_time
    
    update_engine_sound()
    update_display_cars()
    draw_game_state()

def update_display_cars():
    """Mostra no OLED a posição atual do jogador na corrida"""
    oled.fill(0)
    oled.text(f"Posicao: {score}", 0, 0)
    oled.text(f"Voltar menu (A)",0, 10)
    oled.show()

def show_game_over_cars():
    """Mostra no OLED game over"""
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

def show_win_message_cars():
    """Mostra no OLED Vitoria"""
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

def show_start_screen_cars():
    """Tela inicial no OLED"""
    oled.fill(0)
    oled.text("RACING CARS", 5, 20)
    oled.text("Pressione B", 25, 40)
    oled.show()

def clear_matrix_cars():
    """Apaga todos os LEDs"""
    for i in range(25):
        np[i] = (0, 0, 0)

def joystick_moves():
    """Contra a posição do jogador com base na leitura do joystick"""
    global player_x, player_y, last_joystick_check
    
    if not game_active:
        return
    
    now = utime.ticks_ms()

    if utime.ticks_diff(now, last_joystick_check) >= joystick_interval:
        last_joystick_check = now
    
        x_value = joy_x.read_u16()
        y_value = joy_y.read_u16()
    
        new_x = player_x
        new_y = player_y
    
        # Movimento horizontal
        if x_value < JOYSTICK_THRESHOLD_LOW:
            new_x = max(0, player_x - 1)
        elif x_value > JOYSTICK_THRESHOLD_HIGH:
            new_x = min(4, player_x + 1)
    
        # Movimento vertical
        if y_value < JOYSTICK_THRESHOLD_LOW:
            new_y = min(4, player_y + 1)
        elif y_value > JOYSTICK_THRESHOLD_HIGH:
            new_y = max(0, player_y - 1)
        
        # Atualiza apenas se houve mudança
        if new_x != player_x or new_y != player_y:
            player_x, player_y = new_x, new_y
            draw_game_state()
            update_engine_sound()  # Atualiza o som do motor quando o jogador se move


def run():
    """função principal do jogo"""
    game_vars_cars()
    show_start_screen_cars()
    while True:
        if game_active:
            joystick_moves()
            move_cars()
        utime.sleep(0.05)  # Alterado de time para utime

        if button_a.value() == 0:
            break

        if button_b.value() == 0:
           button_handler()

    oled.fill(0)
    oled.show()
    clear_matrix_cars()
    return


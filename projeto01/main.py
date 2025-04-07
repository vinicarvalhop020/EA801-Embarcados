def game_vars():
    global oled, np, button_b, button_a, i2c, joy_button, joy_x, joy_y, utime, random, math
    global last_joystick_check, joystick_interval, last_x, last_y, threshold
    global game_state, effect_start_time, effect_step, dificuldade, last_score
    global win, reset, win_state, MATRIX_MAP, snake_pos, direction, food, score
    global game_speed, brightness, cor_fruta_atual, sound_queue, sound_start_time
    global current_sound, aumenta_dificuldade, lose_state, running, buzzer
    global COUNTDOWN_PATTERNS_snake, WIN_PATTERNS_snake, LOSE_PATTERNS_snake
    
    from machine import Pin, SoftI2C, ADC, PWM
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
    BUTTON_A = 5
    OLED_SDA = 14      # GPIO14 (SDA do OLED)
    OLED_SCL = 15      # GPIO15 (SCL do OLED)

    # --- Inicialização dos componentes ---
    np = neopixel.NeoPixel(Pin(LED_PIN), 25)  # Matriz 5x5
    button_b = Pin(BUTTON_B, Pin.IN, Pin.PULL_UP)
    button_a = Pin(BUTTON_A, Pin.IN, Pin.PULL_UP)
    i2c = SoftI2C(scl=Pin(OLED_SCL), sda=Pin(OLED_SDA))
    oled = SSD1306_I2C(128, 64, i2c)
    joy_button = Pin(22, Pin.IN, Pin.PULL_UP) 
    joy_x = ADC(Pin(27))  # Joystick X
    joy_y = ADC(Pin(26))  # Joystick Y

    # Variáveis globais para armazenar o último estado do joystick
    last_joystick_check = 0
    joystick_interval = 50  # ms (mesmo intervalo do timer anterior)
    last_x = 32768
    last_y = 32768
    threshold = 10000
    game_state = None  # Pode ser: "RUNNING", "LOSE", "START"
    effect_start_time = 0
    effect_step = 0
    dificuldade = 1
    last_score = -1
    win = False 
    reset = False
    win_state = 0

        # --- Mapeamento FÍSICO da matriz (conforme manual) ---
    MATRIX_MAP = [  
        [24, 23, 22, 21, 20],  # Linha 0 (topo)
        [15, 16, 17, 18, 19],  # Linha 1
        [14, 13, 12, 11, 10],  # Linha 2
        [5, 6, 7, 8, 9],       # Linha 3
        [4, 3, 2, 1, 0]        # Linha 4 (base)
    ]

    # --- Variáveis do jogo ---
    snake_pos = [(2, 2)]    # Cobra inicia no centro
    direction = "RIGHT"  # Direção inicial
    food = (0, 0)       # Posição da comida
    score = 0           # Pontuação
    game_speed = 0.9    # Velocidade 
    brightness = 0.1
    cor_fruta_atual = [255,0,0]
    sound_queue = []
    sound_start_time = 0
    current_sound = None
    aumenta_dificuldade = False
    lose_state = False
    running = True
    buzzer = PWM(Pin(21))

        # Adicione no início do código (com as outras variáveis globais)
    COUNTDOWN_PATTERNS_snake = {
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

    WIN_PATTERNS_snake = {
        'W': [
            [1, 0, 0, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 1, 0, 1, 1],
            [1, 0, 0, 0, 1]
        ],
        'I': [
            [0, 1, 1, 1, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 1, 1, 1, 0]
        ],
        'N': [
            [1, 0, 0, 0, 1],
            [1, 1, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 0, 1, 1],
            [1, 0, 0, 0, 1]
        ]
    }

    LOSE_PATTERNS_snake = {
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

def check_joystick_movement():
    global direction, last_x, last_y, last_joystick_check
    
    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_joystick_check) >= joystick_interval:
        last_joystick_check = now
        
        x = joy_x.read_u16()
        y = joy_y.read_u16()
        
        if abs(x - last_x) > threshold or abs(y - last_y) > threshold:
            new_dir = read_joystick_snake()
            current_dir = direction
            
            if new_dir and new_dir != oposite(current_dir):
                direction = new_dir
        
        last_x, last_y = x, y


def play_tone_non_blocking_snake(frequency, duration):
    """Adiciona um som à fila de reprodução"""
    sound_queue.append((frequency, duration))

def process_sounds_snake():
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
        buzzer.duty_u16(2000)
        sound_start_time = now

def snake_sounds(action):
    """Adiciona sons à fila conforme a ação"""
    if action == "eat":
        play_tone_non_blocking_snake(523, 100)  # Dó (100ms)
        play_tone_non_blocking_snake(659, 100)  # Mi (100ms)

    elif action == "move":
        play_tone_non_blocking_snake(100, 20)  # Som curto de movimento (20ms)

def game_sounds_snake(action):
    if action == "game_start":
        for freq in [392, 349, 330]:
            play_tone_non_blocking_snake(freq, 1000)  # 150ms por nota

    elif action == "game_over":
        if lose_state:  
            # Som descendente (triste)
            play_tone_non_blocking_snake(392, 300)  # Sol
            play_tone_non_blocking_snake(349, 300)  # Fá
            play_tone_non_blocking_snake(330, 300)  # Mi
            play_tone_non_blocking_snake(294, 500)  # Ré (mais longo)
    
    elif action == "WIN":
    # Fanfarra de vitória (notas mais agudas e ritmo animado)
    # Efeito de preparação (opcional)
        for freq in range(200, 600, 50):
            play_tone_non_blocking_snake(freq, 50)
        play_tone_non_blocking_snake(523, 200)  # Dó5
        play_tone_non_blocking_snake(659, 200)  # Mi5
        play_tone_non_blocking_snake(784, 200)  # Sol5
        play_tone_non_blocking_snake(1046, 400) # Dó6 (mais longo)
        play_tone_non_blocking_snake(784, 200)  # Sol5
        play_tone_non_blocking_snake(1046, 800) # Dó6 final (bem longo)
        

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

def start_game_snake():
    global game_state, effect_start_time, effect_step, direction
    game_state = "START"
    effect_start_time = utime.ticks_ms()
    effect_step = 0
    direction = "RIGHT"  # Reset da direção
    game_sounds_snake("game_start")  # Adicione um som específico para início

def lose_game_snake():
    global game_state, effect_start_time, effect_step, lose_state
    if not lose_state:
        lose_state = True
        game_state = "LOSE"
        effect_start_time = utime.ticks_ms()
        effect_step = 0
        game_sounds_snake("game_over")
        show_loose_screen_snake()

def win_game_snake():
    global game_state, effect_start_time, effect_step
    game_state = "WIN"
    effect_start_time = utime.ticks_ms()
    effect_step = 0
    game_sounds_snake("WIN")
    show_win_screen_snake()

def show_pattern_snake(pattern, number, color):
    """Desenha um número na matriz LED"""
    if pattern == "start":
        pattern = COUNTDOWN_PATTERNS_snake.get(number)
        if not pattern:
            return
        
        for y in range(5):
            for x in range(5):
                if pattern[y][x]:
                    set_pixel(x, y, color)
                else:
                    set_pixel(x, y, (0, 0, 0))
        np.write()
    if pattern == "win":
        pattern = WIN_PATTERNS_snake.get(number)
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
        pattern = LOSE_PATTERNS_snake.get(number)
        if not pattern:
            return
        
        for y in range(5):
            for x in range(5):
                if pattern[y][x]:
                    set_pixel(x, y, color)
                else:
                    set_pixel(x, y, (0, 0, 0))
        np.write()
    


def process_game_effects_snake():
    global game_state, effect_start_time, effect_step, win_state,lose_state
    now = utime.ticks_ms()
    
    if game_state == "START":
        if effect_step == 0:  # Mostra "3" (azul)
            show_pattern_snake("start",3, apply_brightness((0, 0, 255), brightness))
     # Som para contagem
            effect_step = 1
            effect_start_time = now
        elif effect_step == 1:  # Espera 1 segundo
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                show_pattern_snake("start",2, apply_brightness((0, 0, 255), brightness))
                effect_step = 2
                effect_start_time = now

        elif effect_step == 2:  # Espera 1 segundo
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                show_pattern_snake("start",1, apply_brightness((0, 0, 255), brightness))
                effect_step = 3
                effect_start_time = now
                
        elif effect_step == 3:  # Espera 1 segundo e inicia
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                clear_matrix()
                reset_game_snake()
                game_state = "RUNNING"

    elif game_state == "LOSE":
        if effect_step == 0:
            show_pattern_snake("lose","L", apply_brightness((255, 0, 0), brightness))
            effect_step = 1
            effect_start_time = now
        elif effect_step == 1 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern_snake("lose","O", apply_brightness((255, 0, 0), brightness))
            effect_step = 2
            effect_start_time = now
        elif effect_step == 2 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern_snake("lose","S", apply_brightness((255, 0, 0), brightness))
            effect_step = 3
            effect_start_time = now
        elif effect_step == 3 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern_snake("lose","E", apply_brightness((255, 0, 0), brightness))
            effect_step = 4
            effect_start_time = now
        elif effect_step == 4 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern_snake("lose","R", apply_brightness((255, 0, 0), brightness))
            effect_step = 5
            effect_start_time = now
        elif effect_step == 5 and utime.ticks_diff(now, effect_start_time) >= 2000:
            clear_matrix()
            reset_game_snake()
            game_state = "RUNNING"

    elif game_state == "WIN":
        if effect_step == 0:  # Mostra "3" (azul)
            show_pattern_snake("win","W", apply_brightness((255, 255, 0), brightness))
     # Som para contagem
            effect_step = 1
            effect_start_time = now
            
        elif effect_step == 1:  # Espera 1 segundo
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                show_pattern_snake("win","I", apply_brightness((255, 255, 0), brightness))
                effect_step = 2
                effect_start_time = now
                
        elif effect_step == 2:  # Espera 1 segundo
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                show_pattern_snake("win","N", apply_brightness((255, 255, 0), brightness))
                effect_step = 3
                effect_start_time = now
                
        elif effect_step == 3:  # Espera 1 segundo e inicia
            if utime.ticks_diff(now, effect_start_time) >= 1000:
                clear_matrix()
                effect_step = 0
                if (win_state == 1):
                    reset_game_snake()
                    game_state = "RUNNING"
                else:
                    win_state += 1
                    win_game_snake()        
        
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

def show_start_screen_snake():
    """Tela inicial no OLED"""
    oled.fill(0)
    oled.text("SNAKE GAME", 30, 20)
    oled.text("Pressione B", 25, 40)
    oled.show()

def show_win_screen_snake():
        oled.fill(0)
        oled.text(f"PARABENS", 0, 0)
        oled.text(f"VOCE GANHOU", 0, 20)
        oled.show()

def show_loose_screen_snake():
        oled.fill(0)
        oled.text(f"QUE PENA", 0, 0)
        oled.text(f"VOCE PERDEU!", 0, 20)
        oled.show()

def update_display_snake():
    global last_score, reset
    if (score != last_score or reset):
        oled.fill(0)
        oled.text(f"Pontos: {score}", 0, 0)
        oled.text(f"Dificulade: {dificuldade}", 0, 20)
        oled.text(f"voltar ao menu:", 0, 30)
        oled.text(f"Pressione A:", 0, 40)
        oled.show()
        last_score = score
        reset = False
    
def read_joystick_snake():
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
        if food not in snake_pos:
            break

def reset_game_snake():
    """Reinicia o jogo"""
    global snake_pos, direction, score, game_speed, dificuldade,win_state,win,reset,lose_state
    snake_pos = [(2, 2)]
    direction = "RIGHT"
    score = 0
    game_speed = 0.9
    dificuldade = 0
    win = False  
    win_state = 0
    reset = True
    lose_state = False  # Adicione esta linha
    place_food()
    update_display_snake()

def update_snake():
    global snake_pos, direction, score, game_speed, dificuldade,win, aumenta_dificuldade, lose_state
    
    head_x, head_y = snake_pos[0]
    
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
    snake_sounds("move")

    # Verifica colisão
    if (head_x, head_y) in snake_pos[:-1] and not lose_state:
        lose_game_snake()
        return
    
    # Insere nova cabeça
    snake_pos.insert(0, (head_x, head_y))
    
    # Verifica se comeu
    if (head_x, head_y) == food and not win:
        snake_sounds("eat")
        if(len(snake_pos) == 25):
            win = True  
            win_game_snake()
        else:
            score += 1
            place_food()
            if (aumenta_dificuldade): #aumenta dificuldade vez sim vez nao
                game_speed = max(0.1, game_speed * 0.95)
                dificuldade +=1
                aumenta_dificuldade = False
            else:
                aumenta_dificuldade = True
    else:
        snake_pos.pop()  # Remove cauda se não comeu

def draw_snake():
    """Desenha a cobra e comida na matriz"""
    clear_matrix()
    draw_snake_color()
    set_pixel(food[0], food[1], apply_brightness((255,255,255), brightness))  # Comida vermelha
    np.write()

def draw_snake_color():
    """Desenha a cobra com cores variadas baseadas no HSL"""
    for i, pixel in enumerate(snake_pos):
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


def snake():
    game_vars()
    global oled, np, button_b, button_a, i2c, joy_button, joy_x, joy_y, utime, random, math
    global last_joystick_check, joystick_interval, last_x, last_y, threshold
    global game_state, effect_start_time, effect_step, dificuldade, last_score
    global win, reset, win_state, MATRIX_MAP, snake_pos, direction, food, score
    global game_speed, brightness, cor_fruta_atual, sound_queue, sound_start_time
    global current_sound, aumenta_dificuldade, lose_state, running, buzzer
    global COUNTDOWN_PATTERNS_snake, WIN_PATTERNS_snake, LOSE_PATTERNS_snake

    # Restante do código permanece igual...
    show_start_screen_snake()
    while button_b.value() == 1:  # Espera pressionar o botão de ação (B)
        utime.sleep_ms(100)

    start_game_snake()
    last_update = utime.ticks_ms()

    
    while True:
        now = utime.ticks_ms()
        process_sounds_snake()
        check_joystick_movement()
        process_game_effects_snake()

        if game_state == "RUNNING":
            if utime.ticks_diff(now, last_update) >= int(game_speed * 1000):
                last_update = now
                update_snake()
                draw_snake()
                update_display_snake()
        
        # Verifica se deve sair para o menu (Botão A)
        if button_a.value() == 0:
            reset_game_snake()
            break
        
        utime.sleep_ms(10)

    oled.fill(0)
    oled.show()
    clear_matrix()
    return


def game_vars_cars():
    global MATRIX_MAP_RACING, COUNTDOWN_PATTERNS_RACING, VICTORY_SOUND, GAMEOVER_SOUND, random, math, utime, np
    global i2c, oled, joy_x, joy_y, JOYSTICK_THRESHOLD_LOW, JOYSTICK_THRESHOLD_HIGH
    global botao_b_dog, player_x, player_y, score, game_active, cars, last_car_move, button_a
    global last_car_generation, should_generate_cars, game_over, BUZZER_PIN, buzzer
    global engine_sound_enabled, last_sound_update, current_frequency, target_frequency
    global engine_rpm, DEBOUNCE_TIME, last_button_time

    from machine import Pin, ADC, SoftI2C, PWM
    from ssd1306 import SSD1306_I2C
    import neopixel
    import utime  # Alterado de time para utime
    import random
    import machine
    import math

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

    # Display OLED
    i2c = SoftI2C(scl=Pin(15), sda=Pin(14))
    oled = SSD1306_I2C(128, 64, i2c)

    # Joystick
    joy_x = ADC(Pin(27))  # Horizontal
    joy_y = ADC(Pin(26))  # Vertical
    JOYSTICK_THRESHOLD_LOW = 12000
    JOYSTICK_THRESHOLD_HIGH = 52000

    # Botões
    botao_b_dog = Pin(6, Pin.IN, Pin.PULL_UP)
    button_a = Pin(5, Pin.IN, Pin.PULL_UP)
    botao_b_dog.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)
    joystick_timer.init(period=100, mode=machine.Timer.PERIODIC, callback=lambda t: joystick_handler(None))
    np = neopixel.NeoPixel(Pin(7), 25)  # Matriz 5x5


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
    np.fill((0, 0, 0))
    for car in cars:
        if 0 <= car[0] < 5:
            np[MATRIX_MAP_RACING[car[0]][car[1]]] = (64, 0, 0)
    np[MATRIX_MAP_RACING[player_y][player_x]] = (0, 0, 64)
    np.write()

def debounce():
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
    oled.fill(0)
    oled.text(f"Pontos: {score}", 0, 0)
    oled.text(f"Para voltar ao menu:", 0, 30)
    oled.text(f"Pressione A:", 0, 40)
    oled.show()

def show_game_over_cars():
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


def cars():

    game_vars_cars()
    show_start_screen_cars()

    while True:
        if game_active:
            move_cars()
        utime.sleep(0.05)  # Alterado de time para utime

        if button_a.value() == 0:
            break

# Configura interrupção do joystick
joystick_timer = machine.Timer()

def clear_matrix_cars():
    """Apaga todos os LEDs"""
    for i in range(25):
        np[i] = (0, 0, 0)

# Função de interrupção do joystick
def joystick_handler(pin):
    global player_x, player_y
    if not game_active:
        return
    
    x_value = joy_x.read_u16()
    y_value = joy_y.read_u16()
    
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



########SPACEINVADERS##
def space_vars():
    global np, joy_x, joy_y, button_b, button_a, i2c, oled, joy_button, buzzer, time, utime, math, random
    global dificuldade, last_score, start_defeat, nave_pos, tiros, inimigos_1, inimigos_2
    global inimigos_3, match, game_state, brightness, direcao_inimigos, score
    global first_move, lose_state, reset, tiro_on, vidas, sound_queue, current_sound
    global sound_start_time, MAX_SOUND_QUEUE, game_over_melody, current_note_index
    global note_start_time, is_playing_melody, COUNTDOWN_PATTERNS, LOSE_PATTERNS,MATRIX_MAP
    global last_enemy_move,last_nave_move, last_tiro_move, last_update, enemy_move_interval, tiro_move_interval, nave_move_interval

    from machine import Pin, SoftI2C, ADC,PWM
    import neopixel
    import utime
    import random
    from ssd1306 import SSD1306_I2C
    import math
    import time
    import utime

        # --- Loop Principal ---
    last_update = utime.ticks_ms()

    last_enemy_move = utime.ticks_ms()
    enemy_move_interval = 2000  # ms (1 segundo para descer)

    last_tiro_move = utime.ticks_ms()
    tiro_move_interval = 200  # ms (mais rápido que o padrão atual)

    last_nave_move = utime.ticks_ms()
    nave_move_interval = 200  # A nave só pode se mover a cada 200 ms


    # --- Configuração dos pinos ---
    LED_PIN = 7        # GPIO7 para a matriz NeoPixel (5x5)
    JOYSTICK_X = 27    # GPIO27 (VRx do joystick)
    JOYSTICK_Y = 26    # GPIO26 (VRy do joystick)
    BUTTON_B = 6       # GPIO6 para o botão B (tiro)
    BUTTON_A = 5
    OLED_SDA = 14      # GPIO14 (SDA do OLED)
    OLED_SCL = 15      # GPIO15 (SCL do OLED)

    # --- Inicialização ---
    np = neopixel.NeoPixel(Pin(LED_PIN), 25)
    joy_x = ADC(Pin(JOYSTICK_X))
    joy_y = ADC(Pin(JOYSTICK_Y))
    button_b = Pin(BUTTON_B, Pin.IN, Pin.PULL_UP)
    button_a = Pin(BUTTON_A, Pin.IN, Pin.PULL_UP)
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
    tiro_on = False
    vidas = 3

    sound_queue = []
    current_sound = None
    sound_start_time = 0
    MAX_SOUND_QUEUE = 3  # Limite máximo de sons na fila

    game_over_melody = [
        (523, 200), (466, 200), (440, 200), (392, 250), (349, 250),
        (330, 300), (294, 350), (262, 400), (247, 450), (220, 500), (196, 600)
    ]
    current_note_index = -1
    note_start_time = 0
    is_playing_melody = False

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

    button_b.irq(trigger=Pin.IRQ_FALLING, handler=lambda p: atirar())

def play_tone_non_blocking_sp(frequency, duration):
    """Adiciona um som à fila de reprodução com limite de tamanho"""
    if len(sound_queue) < MAX_SOUND_QUEUE:
        sound_queue.append((frequency, duration))

def ship_sounds(action):
    """Efeitos sonoros melhorados"""
    if action == "tiro":
        # Laser espacial descendente (mais realista)
        play_tone_non_blocking_sp(1200, 30)  # Frequência alta inicial
        play_tone_non_blocking_sp(900, 30)   # Queda rápida
        play_tone_non_blocking_sp(600, 40)   # Finalização
    
    elif action == "explosao":
        # Explosão com ruído "granulado"
        play_tone_non_blocking_sp(300, 80)
        play_tone_non_blocking_sp(200, 80)
        play_tone_non_blocking_sp(150, 100)
    
    elif action == "movimento":
        # Feedback sutil ao mover nave
        play_tone_non_blocking_sp(500, 15)

def play_game_over_sound():
    """Inicia a melodia de game over (não bloqueante)"""
    global current_note_index, note_start_time, is_playing_melody
    
    buzzer.duty_u16(0)  # Garante que o buzzer está desligado
    current_note_index = 0
    note_start_time = utime.ticks_ms()
    is_playing_melody = True
    
    # Toca a primeira nota
    freq, duration = game_over_melody[current_note_index]
    buzzer.freq(freq)
    buzzer.duty_u16(3000)

def update_melody():
    """Deve ser chamada no loop principal para gerenciar a melodia"""
    global current_note_index, note_start_time, is_playing_melody
    
    if not is_playing_melody:
        return
        
    now = utime.ticks_ms()
    freq, duration = game_over_melody[current_note_index]
    
    # Verifica se a nota atual terminou
    if utime.ticks_diff(now, note_start_time) >= duration:
        buzzer.duty_u16(0)  # Desliga o buzzer
        
        # Pequena pausa entre notas (50ms)
        if utime.ticks_diff(now, note_start_time) < duration + 50:
            return
            
        # Próxima nota ou fim da melodia
        current_note_index += 1
        if current_note_index < len(game_over_melody):
            freq, duration = game_over_melody[current_note_index]
            buzzer.freq(freq)
            buzzer.duty_u16(3000)
            note_start_time = utime.ticks_ms()
        else:
            # Fim da melodia
            is_playing_melody = False
            buzzer.duty_u16(0)

def game_sounds_sp(action):
    """Sons de jogo melhorados"""
    global start_defeat
    
    if action == "game_start":
        # Fanfarra de início (3 notas ascendentes)
        play_tone_non_blocking_sp(523, 150)  # Dó
        play_tone_non_blocking_sp(659, 150)  # Mi
        play_tone_non_blocking_sp(784, 200)  # Sol
    
    elif action == "game_over":
        play_game_over_sound()
    
    elif action == "hit":
        play_tone_non_blocking_sp(130, 300)  # Dó grave

def process_sounds_sp():
    """Gerencia a reprodução dos sons na fila de forma mais eficiente"""
    global current_sound, sound_start_time
    
    now = utime.ticks_ms()

    # Se está tocando um som, verifica se já terminou
    if current_sound is not None:
        elapsed = utime.ticks_diff(now, sound_start_time)
        if elapsed >= current_sound[1]:  # current_sound[1] é a duration
            buzzer.duty_u16(0)  # Desliga o buzzer
            current_sound = None
    
    # Se não está tocando nada e há sons na fila
    if current_sound is None and sound_queue:
        current_sound = sound_queue.pop(0)  # Pega o som mais antigo (FIFO)
        buzzer.freq(current_sound[0])
        buzzer.duty_u16(2000)
        sound_start_time = now

def start_game_sp():
    global game_state, effect_start_time, effect_step, tiro_on
    tiro_on = True
    game_state = "START"
    effect_start_time = utime.ticks_ms()
    effect_step = 0
    game_sounds_sp("game_start")  # Adicione um som específico para início

def lose_game_sp():
    global game_state, effect_start_time, effect_step, lose_state
    lose_state = True
    game_state = "LOSE"
    effect_start_time = utime.ticks_ms()
    effect_step = 0
    show_loose_screen_sp()

def show_pattern_sp(pattern, number, color):
    """Desenha um número na matriz LED"""
    if pattern == "start":
        pattern = COUNTDOWN_PATTERNS.get(number)
        if not pattern:
            return
        
        for y in range(5):
            for x in range(5):
                if pattern[y][x]:
                    set_pixel_sp(x, y, color)
                else:
                    set_pixel_sp(x, y, (0, 0, 0))
        np.write()
    
    if pattern == "lose":
        pattern = LOSE_PATTERNS.get(number)
        if not pattern:
            return
        
        for y in range(5):
            for x in range(5):
                if pattern[y][x]:
                    set_pixel_sp(x, y, color)
                else:
                    set_pixel_sp(x, y, (0, 0, 0))
        np.write()


def process_game_effects_sp():
    global game_state, effect_start_time, effect_step, first_move
    
    now = utime.ticks_ms()
    
    if game_state == "START":
        if effect_step == 0:  # Início da contagem
            show_pattern_sp("start",3, apply_brightness_sp((0, 0, 255), brightness))
            play_tone_non_blocking_sp(784, 150)  # Sol
            effect_step = 1
            effect_start_time = now
            
        elif effect_step == 1 and utime.ticks_diff(now, effect_start_time) >= 1000:
            show_pattern_sp("start",2, apply_brightness_sp((0, 0, 255), brightness))
            play_tone_non_blocking_sp(659, 150)  # Mi
            effect_step = 2
            effect_start_time = now
            
        elif effect_step == 2 and utime.ticks_diff(now, effect_start_time) >= 1000:
            show_pattern_sp("start",1, apply_brightness_sp((0, 0, 255), brightness))
            play_tone_non_blocking_sp(523, 150)  # Dó
            effect_step = 3
            effect_start_time = now
            
        elif effect_step == 3 and utime.ticks_diff(now, effect_start_time) >= 1000:
            clear_matrix_sp()
            play_tone_non_blocking_sp(1046, 200)  # Dó agudo (início)
            game_state = "RUNNING"
    
    elif game_state == "LOSE":
        if effect_step == 0:
            show_pattern_sp("lose","L", apply_brightness_sp((255, 0, 0), brightness))
            effect_step = 1
            effect_start_time = now
        elif effect_step == 1 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern_sp("lose","O", apply_brightness_sp((255, 0, 0), brightness))
            effect_step = 2
            effect_start_time = now
        elif effect_step == 2 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern_sp("lose","S", apply_brightness_sp((255, 0, 0), brightness))
            effect_step = 3
            effect_start_time = now
        elif effect_step == 3 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern_sp("lose","E", apply_brightness_sp((255, 0, 0), brightness))
            effect_step = 4
            effect_start_time = now
        elif effect_step == 4 and utime.ticks_diff(now, effect_start_time) >= 800:
            show_pattern_sp("lose","R", apply_brightness_sp((255, 0, 0), brightness))
            effect_step = 5
            effect_start_time = now
        elif effect_step == 5 and utime.ticks_diff(now, effect_start_time) >= 3000:
            clear_matrix_sp()
            reset_game_sp()
            game_state = "RUNNING"
            first_move = -1


def show_start_screen_sp():
    """Tela inicial no OLED"""
    oled.fill(0)
    oled.text("SPACE INAVADERS", 5, 20)
    oled.text("Pressione B", 25, 40)
    oled.show()

def show_loose_screen_sp():
        oled.fill(0)
        oled.text(f"QUE PENA", 0, 0)
        oled.text(f"VOCE PERDEU!", 0, 20)
        oled.show()

def apply_brightness_sp(color, brightness):
    """Ajusta o brilho de uma cor RGB (0-255)"""
    r, g, b = color
    return (
        int(r * brightness),
        int(g * brightness),
        int(b * brightness)
    )

def set_pixel_sp(x, y, color):
    """Acende o LED na posição (x,y)"""
    if 0 <= x < 5 and 0 <= y < 5:
        np[MATRIX_MAP[y][x]] = color

def clear_matrix_sp():
    """Apaga todos os LEDs"""
    for i in range(25):
        np[i] = (0, 0, 0)

def draw_game_sp():
    global brightness, inimigos_1, inimigos_2, inimigos_3
    """Desenha todos os elementos na matriz"""
    clear_matrix_sp()
    
    # Desenha nave (roxo)
    set_pixel_sp(nave_pos[0], nave_pos[1], apply_brightness_sp((50, 200, 133),brightness))
    
    # Desenha tiros (azul)
    for tiro in tiros:
        set_pixel_sp(tiro[0], tiro[1], apply_brightness_sp((255, 255, 0),brightness))
    
    # Desenha inimigos (vermelho)
    for inimigo in inimigos_1:
        set_pixel_sp(inimigo[0], inimigo[1], apply_brightness_sp((255, 0, 0),brightness))
    
    for inimigo in inimigos_2:
        set_pixel_sp(inimigo[0], inimigo[1], apply_brightness_sp((0, 255, 0),brightness))
    
    for inimigo in inimigos_3:
        set_pixel_sp(inimigo[0], inimigo[1], apply_brightness_sp((0, 0, 255),brightness))
    
    np.write()

def update_display_sp():
    global last_score, reset
    if (score != last_score or reset):
        oled.fill(0)
        oled.text(f"Pontos: {score}", 0, 0)
        oled.text(f"Vidas: {vidas}", 0, 20)
        oled.text(f"Fase {match}", 0, 30)
        oled.text(f"voltar ao menu:", 0, 40)
        oled.text(f"Pressione A:", 0, 50)
        oled.show()
        last_score = score
        reset = False

def atirar():
    """Dispara um novo tiro"""
    if (tiro_on):
        if len(tiros) < 3:  # Limite de 2 tiros simultâneos
            tiros.append([nave_pos[0], nave_pos[1] - 1])
            ship_sounds("tiro")

def mover_tiros():
    """Atualiza posição dos tiros"""
    for tiro in tiros[:]:
        tiro[1] -= 1  # Move para cima
        if tiro[1] < 0:
            tiros.remove(tiro)

def mover_nave_sp():
    """Controla movimento da nave com joystick"""
    x = joy_x.read_u16()
    if x < 15000 and nave_pos[0] > 0:  # Esquerda
        nave_pos[0] -= 1
    elif x > 50000 and nave_pos[0] < 4:  # Direita
        nave_pos[0] += 1

def mover_inimigos_sp():
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
            game_sounds_sp("hit")
            if vidas <= 0:
                game_sounds_sp("game_over")
                lose_game_sp()
            else:
                reset_positions_sp()


def verificar_colisoes_sp():
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


def reset_positions_sp():
    global nave_pos, tiros, inimigos_1, inimigos_2, inimigos_3, match
    nave_pos = [2, 4]
    tiros = []
    
    # Recria os inimigos baseado na fase atual
    inimigos_1 = [[i, 0] for i in range(5)]
    
    if match >= 2:
        inimigos_2 = [[i, -1] for i in range(5)]  # Começa "escondido"
    
    if match >= 3:
        inimigos_3 = [[i, -2] for i in range(5)]  # Começa "escondido


def reset_game_sp():
    global nave_pos, tiros, inimigos_1, inimigos_2, inimigos_3, score, vidas, game_state, match, enemy_move_interval, dificuldade, lose_state, start_defeat, current_sound, tiro_on, reset
    nave_pos = [2, 4]
    tiros = []
    inimigos_1 = [[i, 0] for i in range(5)]
    inimigos_2 = []
    inimigos_3 = []
    enemy_move_interval = 2000
    score = 0
    vidas = 3
    reset = True
    match = 1
    game_state = "START"
    lose_state = False  # Reseta o estado de derrota
    dificuldade = 0
    tiro_on = True
    start_defeat = False

# --- Inicialização ---


def space__invaders():
    space_vars()
    global last_nave_move, last_enemy_move, last_tiro_move, enemy_move_interval
    global nave_move_interval, tiro_move_interval, game_state, now
    global button_b, button_a, nave_pos, tiros, inimigos_1, inimigos_2, inimigos_3
    global match, score, vidas, dificuldade, reset, lose_state, start_defeat
    global current_sound, sound_start_time, sound_queue, current_note_index
    global note_start_time, is_playing_melody, effect_start_time, effect_step

    show_start_screen_sp()
    while button_b.value() == 1:  # Espera pressionar o botão B
        time.sleep(0.1)
    start_game_sp()
    
    show_start_screen_sp()
    while True:
        if button_a.value() == 0:
            reset_game_sp()
            break

        now = utime.ticks_ms()
        process_game_effects_sp()
        update_melody() 
        process_sounds_sp()  
        if game_state == "RUNNING":
            # Movimento da nave
            if utime.ticks_diff(now, last_nave_move) >= nave_move_interval:
                last_nave_move = now
                if joy_x.read_u16() < 15000 or joy_x.read_u16() > 50000:
                    ship_sounds("movimento")
                mover_nave_sp()

            # Movimento dos inimigos
            if utime.ticks_diff(now, last_enemy_move) >= enemy_move_interval:
                last_enemy_move = now
                mover_inimigos_sp()

            # Movimento dos tiros
            if utime.ticks_diff(now, last_tiro_move) >= tiro_move_interval:
                last_tiro_move = now
                verificar_colisoes_sp()
                mover_tiros()
                verificar_colisoes_sp()

            draw_game_sp()
            update_display_sp()
            utime.sleep_ms(10)

            # Verifica se todos inimigos foram destruídos
            if len(inimigos_1) == 0 and len(inimigos_2) == 0 and len(inimigos_3) == 0:
                match += 1
                reset_positions_sp()
                enemy_move_interval = max(300, int(enemy_move_interval * 0.9))
                dificuldade += 1


def vars_menu():
    global np, i2c, oled, joystick_y, button_b, button_a, games, selected, DEBOUNCE_DELAY, last_input_time, utime, time
    
    from machine import Pin, I2C, ADC, Timer, SoftI2C
    import neopixel
    from ssd1306 import SSD1306_I2C
    import time
    import utime

    # --- Hardware Configuration (BitDoglab) ---
    LED_PIN = 7        # GPIO7 para a matriz NeoPixel (5x5)
    JOYSTICK_X = 27    # GPIO27 (VRx do joystick)
    JOYSTICK_Y = 26    # GPIO26 (VRy do joystick)
    BUTTON_B = 6       # GPIO6 para o botão B (reset)
    BUTTON_A = 5
    OLED_SDA = 14      # GPIO14 (SDA do OLED)
    OLED_SCL = 15      # GPIO15 (SCL do OLED)

    np = neopixel.NeoPixel(Pin(LED_PIN), 25)  # Matriz 5x5
    i2c = SoftI2C(scl=Pin(OLED_SCL), sda=Pin(OLED_SDA))
    oled = SSD1306_I2C(128, 64, i2c)
    joystick_y = ADC(Pin(JOYSTICK_Y))  # Pino VRy do joystick (KY023)
    button_b = Pin(BUTTON_B, Pin.IN, Pin.PULL_UP)  # Botão B (GPIO6)
    button_a = Pin(BUTTON_A, Pin.IN, Pin.PULL_UP)  # Botão A (GPIO5)

    # --- Game Menu ---
    games = [
        ("Snake", snake),
        ("Space Invaders", space__invaders),
        ("Racing Cars", cars)
    ]
    selected = 0
    DEBOUNCE_DELAY = 200  # ms
    last_input_time = utime.ticks_ms()

def show_menu(highlight=None):
    oled.fill(0)
    oled.text("BitDoglab Games", 0, 0)
    
    for i, (name, _) in enumerate(games):
        prefix = ">" if i == selected else " "
        y_pos = 15 + i * 12
        if highlight == i:
            oled.fill_rect(0, y_pos-1, 128, 10, 1)
            oled.text(f"{prefix} {name}", 0, y_pos, 0)
        else:
            oled.text(f"{prefix} {name}", 0, y_pos, 1)
    oled.show()

def show_loading(game_name):
    for i in range(3):
        oled.fill(0)
        oled.text(f"Iniciando {'.'*i}", 20, 20)
        oled.text(game_name, 0, 30)
        oled.show()
        utime.sleep_ms(300)

def check_input_menu():
    """Controla a navegação no menu com debounce"""
    global selected, last_input_time
    
    now = utime.ticks_ms()
    if utime.ticks_diff(now, last_input_time) < DEBOUNCE_DELAY:
        return None
    
    y_value = joystick_y.read_u16()
    input_detected = False
    
    if y_value > 50000:  # Para cima
        selected = (selected - 1) % len(games)
        input_detected = True
    elif y_value < 10000:  # Para baixo
        selected = (selected + 1) % len(games)
        input_detected = True
    
    if input_detected:
        last_input_time = now
        show_menu(highlight=selected)
        utime.sleep_ms(100)
        show_menu()
        return None
    
    if button_b.value() == 0:  # Botão B seleciona
        last_input_time = now
        return games[selected][1]  # Retorna a função do jogo
    
    return None

def clear_matrix_menu():
    """Apaga todos os LEDs"""
    for i in range(25):
        np[i] = (0, 0, 0)
    np.write()

def main():
    vars_menu()
    show_menu()
    last_active = utime.ticks_ms()
    
    while True:
        selected_game = check_input_menu()
        if selected_game is not None:
            show_loading(games[selected][0])
            selected_game()  # Executa a função do jogo selecionado
            # Quando o jogo termina, volta para o menu
            clear_matrix_menu()
            buzzer.duty_u16(0)  # Desliga o buzzer
            vars_menu()  # Reinicializa as variáveis do menu
            show_menu()
            last_active = utime.ticks_ms()
    
        # Verifica timeout (5 minutos de inatividade)
        if utime.ticks_diff(utime.ticks_ms(), last_active) > 300000:
            show_menu()
            last_active = utime.ticks_ms()
            
        utime.sleep_ms(50)

# Inicia o menu
main()
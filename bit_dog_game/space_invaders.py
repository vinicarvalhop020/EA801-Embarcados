def space_vars():
    #Variaveis e imports de SPACE_INAVADERS
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
    
    last_update = utime.ticks_ms()
    last_enemy_move = utime.ticks_ms()
    enemy_move_interval = 2000  
    last_tiro_move = utime.ticks_ms()
    tiro_move_interval = 200 
    last_nave_move = utime.ticks_ms()
    nave_move_interval = 200  

    LED_PIN = 7        # GPIO7 para a matriz NeoPixel (5x5)
    JOYSTICK_X = 27    # GPIO27 (VRx do joystick)
    JOYSTICK_Y = 26    # GPIO26 (VRy do joystick)
    BUTTON_B = 6       # GPIO6 para o botão B (tiro)
    BUTTON_A = 5
    OLED_SDA = 14      # GPIO14 (SDA do OLED)
    OLED_SCL = 15      # GPIO15 (SCL do OLED)
    MAX_SOUND_QUEUE = 3  # Limite máximo de sons na fila

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

    MATRIX_MAP = [  
        [24, 23, 22, 21, 20],  # Linha 0 (topo)
        [15, 16, 17, 18, 19],  # Linha 1
        [14, 13, 12, 11, 10],  # Linha 2
        [5, 6, 7, 8, 9],       # Linha 3
        [4, 3, 2, 1, 0]        # Linha 4 (base)
    ]

    #Seta os numeros que aparecem no menu ao iniciar
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

    #Seta a matriz de derrota L-O-S-E-R
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


    nave_pos = [2, 4]
    tiros = []
    inimigos_1 = [[i, 0] for i in range(5)]  # Inimigos vermelhos (linha 0)
    inimigos_2 = []  # Inimigos verdes (aparecem depois)
    inimigos_3 = []  # Inimigos azuis (aparecem depois)
    match = 1
    game_state = "RUNNING"  
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
    current_note_index = -1
    note_start_time = 0
    is_playing_melody = False

    game_over_melody = [
        (523, 200), (466, 200), (440, 200), (392, 250), (349, 250),
        (330, 300), (294, 350), (262, 400), (247, 450), (220, 500), (196, 600)
    ]
    
    #interrupção para o botao b atirar
    button_b.irq(trigger=Pin.IRQ_FALLING, handler=lambda p: atirar())

def play_tone_non_blocking_sp(frequency, duration):
    """Adiciona um som à fila de reprodução com limite de tamanho"""
    if len(sound_queue) < MAX_SOUND_QUEUE:
        sound_queue.append((frequency, duration))

def ship_sounds(action):
    """Efeitos sonoros da nave"""
    if action == "tiro":
        play_tone_non_blocking_sp(1200, 30)  
        play_tone_non_blocking_sp(900, 30)   
        play_tone_non_blocking_sp(600, 40)   
    
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
    
    buzzer.duty_u16(0) 
    current_note_index = 0
    note_start_time = utime.ticks_ms()
    is_playing_melody = True
    
    freq, duration = game_over_melody[current_note_index]
    buzzer.freq(freq)
    buzzer.duty_u16(2000)

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
            buzzer.duty_u16(100)
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
    """função que configura o start do jogo, sons e variaveis"""
    global game_state, effect_start_time, effect_step, tiro_on
    tiro_on = True
    game_state = "START"
    effect_start_time = utime.ticks_ms()
    effect_step = 0
    game_sounds_sp("game_start")  # Adicione um som específico para início

def lose_game_sp():
    """função que configura a derrota do jogo, sons e variaveis"""
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
    """função responsavel por controlar as imagems do jogo de start e lose na matriz"""
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
    """atualiza o display com pontuacao, vidas, fase atual e volta para o menu"""
    global last_score, reset
    if (score != last_score or reset):
        oled.fill(0)
        oled.text(f"Pontos: {score}", 0, 0)
        oled.text(f"Vidas: {vidas}", 0, 20)
        oled.text(f"Fase {match}", 0, 30)
        oled.text(f"Voltar menu (A)",0, 40)
        oled.show()
        last_score = score
        reset = False

def atirar():
    """Dispara um novo tiro"""
    if (tiro_on):
        if len(tiros) < 3:  # Limite de 3 tiros simultâneos
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
    """reseta a posição dos inimigos, e configura para aparecer mais com base na rodada"""
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
    """função que reseta as variaveis do jogo"""
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

def reset_to_menu():
    """função que reseta o jogo caso va para o menu"""
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
    tiro_on = False # Nao saem tiros sem querer ao ir para o menu, ou resetar
    start_defeat = False


#função principal de funcionamento do jogo
def run():
    space_vars()
    global last_nave_move, last_enemy_move, last_tiro_move, enemy_move_interval
    global nave_move_interval, tiro_move_interval, game_state, now
    global button_b, button_a, nave_pos, tiros, inimigos_1, inimigos_2, inimigos_3
    global match, score, vidas, dificuldade, reset, lose_state, start_defeat
    global current_sound, sound_start_time, sound_queue, current_note_index
    global note_start_time, is_playing_melody, effect_start_time, effect_step

    show_start_screen_sp()
    while button_b.value() == 1:  # Espera pressionar o botão B para começar
        time.sleep(0.1)
    start_game_sp()
    
    show_start_screen_sp()
    while True:
        if button_a.value() == 0: # Espera pressionar o botão A quebra o loop e volta para o menu
            reset_to_menu()
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

    oled.fill(0)
    oled.show()
    clear_matrix_sp()
    return

run()
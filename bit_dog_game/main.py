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
BUTTON_B = 6       # GPIO6 para o botão B (seleção)
BUTTON_A = 5       # GPIO5 para o botão A (voltar)
OLED_SDA = 14      # GPIO14 (SDA do OLED)
OLED_SCL = 15      # GPIO15 (SCL do OLED)
BUZZER_PIN = 21    # GPIO21 para o buzzer

# --- Inicialização dos componentes ---
np = neopixel.NeoPixel(Pin(LED_PIN), 25)  # Matriz 5x5
button_b = Pin(BUTTON_B, Pin.IN, Pin.PULL_UP)
button_a = Pin(BUTTON_A, Pin.IN, Pin.PULL_UP)
i2c = SoftI2C(scl=Pin(OLED_SCL), sda=Pin(OLED_SDA))
oled = SSD1306_I2C(128, 64, i2c)
joy_button = Pin(22, Pin.IN, Pin.PULL_UP) 
joy_x = ADC(Pin(JOYSTICK_X))  # Joystick X
joy_y = ADC(Pin(JOYSTICK_Y))  # Joystick Y
buzzer = PWM(Pin(BUZZER_PIN))

# Variáveis globais
current_selection = 0
menu_items = ["snake", "racing_cars", "space_invaders"]  # Substitua pelos nomes reais dos seus jogos
game_modules = ["snake", "racing_cars", "space_invaders"]       # Nomes dos módulos (sem .py)

# --- Mapeamento FÍSICO da matriz (conforme manual) ---
MATRIX_MAP = [  
    [24, 23, 22, 21, 20],  # Linha 0 (topo)
    [15, 16, 17, 18, 19],  # Linha 1
    [14, 13, 12, 11, 10],  # Linha 2
    [5, 6, 7, 8, 9],       # Linha 3
    [4, 3, 2, 1, 0]        # Linha 4 (base)
]

def set_pixel(x, y, color):
    """Acende o LED na posição (x,y) com RGB"""
    if 0 <= x < 5 and 0 <= y < 5:
        np[MATRIX_MAP[y][x]] = color

def clear_matrix():
    """Apaga todos os LEDs"""
    for i in range(25):
        np[i] = (0, 0, 0)
    np.write()

def draw_menu_cursor(position):
    """Desenha um indicador de seleção no menu"""
    clear_matrix()
    set_pixel(0, position, (0, 255, 0))  # LED verde na posição atual
    np.write()

def show_menu():
    """Mostra o menu no display OLED"""
    oled.fill(0)
    oled.text("GAME DOG LAB", 0, 0)
    
    for i, item in enumerate(menu_items):
        y_pos = 15 + i * 10
        prefix = ">" if i == current_selection else " "
        oled.text(f"{prefix} {item}", 0, y_pos)
    
    oled.text("B: Selecionar", 0, 55)
    oled.show()

def play_tone(frequency, duration_ms):
    """Toca um tom no buzzer"""
    buzzer.freq(frequency)
    buzzer.duty_u16(1000)  # 50% duty cycle
    utime.sleep_ms(duration_ms)
    buzzer.duty_u16(0)

def read_joystick():
    """Lê o joystick e retorna a direção"""
    y = joy_y.read_u16()
    if y < 15000: return "DOWN"
    elif y > 50000: return "UP"
    return None

def load_game(game_index):
    """Carrega o jogo selecionado"""
    play_tone(784, 100)  # Tom de confirmação
    
    try:
        # Importa o módulo do jogo
        game_module = __import__(game_modules[game_index])
        
        # Limpa a tela antes de iniciar o jogo
        oled.fill(0)
        oled.show()
        clear_matrix()
        
        # Executa o jogo
        game_module.run()
        
        # Quando o jogo terminar, volta ao menu
        play_tone(523, 100)  # Tom de retorno
        show_menu()
        
    except Exception as e:
        # Em caso de erro, mostra mensagem
        oled.fill(0)
        oled.text("Erro ao carregar:", 0, 0)
        oled.text(game_modules[game_index], 0, 10)
        oled.text(str(e), 0, 30)
        oled.show()
        utime.sleep(3)
        show_menu()


def main():
    global current_selection
    
    # Inicialização
    play_tone(523, 50)  # Tom de inicialização
    play_tone(659, 50)
    show_menu()
    draw_menu_cursor(current_selection)
    
    last_joystick_time = utime.ticks_ms()
    joystick_delay = 200  # ms
    
    while True:
        now = utime.ticks_ms()
        
        # Verifica navegação no menu
        direction = read_joystick()
        if direction and utime.ticks_diff(now, last_joystick_time) > joystick_delay:
            last_joystick_time = now
            
            if direction == "UP":
                current_selection = (current_selection - 1) % len(menu_items)
                play_tone(262, 50)  # Tom de navegação
            elif direction == "DOWN":
                current_selection = (current_selection + 1) % len(menu_items)
                play_tone(262, 50)  # Tom de navegação
            
            show_menu()
            draw_menu_cursor(current_selection)
        
        # Verifica botões
        if button_b.value() == 0:  # Botão B - Selecionar
            play_tone(784, 100)  # Tom de confirmação
            utime.sleep_ms(200)  # Debounce
            load_game(current_selection)
        
        if button_a.value() == 0:  # Botão A - Sair (não faz nada no menu principal)
            play_tone(392, 100)  # Tom de cancelamento
            utime.sleep_ms(200)  # Debounce
        
        utime.sleep_ms(10)

if __name__ == "__main__":
    main()
from machine import Pin, I2C, ADC, Timer, SoftI2C
import neopixel
from ssd1306 import SSD1306_I2C
import time
import gc
import sys

# --- Hardware Configuration (BitDoglab) ---
LED_PIN = 7        # GPIO7 para a matriz NeoPixel (5x5)
JOYSTICK_X = 27    # GPIO27 (VRx do joystick)
JOYSTICK_Y = 26    # GPIO26 (VRy do joystick)
BUTTON_B = 6       # GPIO6 para o botão B (reset)
BUTTON_A = 5
OLED_SDA = 14      # GPIO14 (SDA do OLED)
OLED_SCL = 15      # GPIO15 (SCL do OLED)

np = neopixel.NeoPixel(Pin(LED_PIN), 25)  # Matriz 5x5
i2c = SoftI2C(scl=Pin(15), sda=Pin(14))  # Usando SoftI2C para robustez
oled = SSD1306_I2C(128, 64, i2c)
joystick_y = ADC(Pin(26))  # Pino VRy do joystick (KY023)
button_b = Pin(6, Pin.IN, Pin.PULL_UP)  # Botão B (GPIO6)
button_a = Pin(5, Pin.IN, Pin.PULL_UP)  # Botão A (GPIO5)

# --- Game Menu ---
games = [
    ("Snake", "Snake"),  # Nome exibido + nome do módulo (case-sensitive)
    ("Space Invaders", "spaceInvaders"),
    ("Racing Cars", "Racing_cars")
]
selected = 0
DEBOUNCE_DELAY = 200  # ms
last_input_time = time.ticks_ms()


# --- UI Functions ---
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
        oled.text(game_name, 30, 40)
        oled.show()
        time.sleep_ms(300)

def show_error(message):
    oled.fill(0)
    oled.text("Erro:", 0, 10)
    for i, line in enumerate(message.split('\n')):
        oled.text(line[:16], 0, 20 + i * 10)  # Limita a 16 caracteres/linha
    oled.show()
    time.sleep(3)

# --- Input Handling ---
def check_input():
    """Controla a navegação no menu com debounce"""
    global selected, last_input_time
    
    now = time.ticks_ms()
    if time.ticks_diff(now, last_input_time) < DEBOUNCE_DELAY:
        return None
    
    y_value = joystick_y.read_u16()
    input_detected = False
    
    if y_value < 10000:  # Para cima
        selected = (selected - 1) % len(games)
        input_detected = True
    elif y_value > 50000:  # Para baixo
        selected = (selected + 1) % len(games)
        input_detected = True
    
    if input_detected:
        last_input_time = now
        show_menu(highlight=selected)
        time.sleep_ms(100)
        show_menu()
        return None
    
    if button_b.value() == 0:  # Botão B seleciona
        last_input_time = now
        return games[selected][1]
    
    return None


def clear_matrix():
    """Apaga todos os LEDs"""
    for i in range(25):
        np[i] = (0, 0, 0)
    np.write()


def cleanup_resources():
    """Limpeza completa de todos os recursos"""
    # Desativa todas as interrupções    
    # Limpa a matriz de LEDs
    clear_matrix()
    
    # Limpa o display
    oled.fill(0)
    oled.show()
    
    # Coleta de lixo agressiva
    gc.collect()
    gc.collect()  # Duas chamadas para garantir

def load_game(game_name):
    try:
        # Limpeza completa antes de carregar novo jogo
        cleanup_resources()
        
        # Mostra tela de loading
        show_loading(games[selected][0])
        
        # Mapeamento de nomes de jogos para módulos
        module_name = {
            "Snake": "Snake",
            "Space Invaders": "spaceInvaders",
            "Racing Cars": "Racing_cars"
        }.get(game_name, game_name)
        
        # Força o recarregamento do módulo
        if module_name in sys.modules:
            del sys.modules[module_name]
            gc.collect()
        
        # Importa dinamicamente com tratamento de erro
        try:
            game_module = __import__(module_name)
            game_module.main(oled, np, button_a, button_b)  # Passa os recursos necessários
        except Exception as e:
            show_error(f"Erro no jogo:\n{str(e)}")
            raise
    except Exception as e:
        show_error(f"Erro ao carregar {game_name}:\n{str(e)}")
    finally:
        cleanup_resources()


# --- Main Loop ---
def main():
    show_menu()
    last_active = time.ticks_ms()
    
    while True:
        selected_game = check_input()
        if selected_game:
            last_active = time.ticks_ms()
            load_game(selected_game)
            show_menu()
        
        # Verifica timeout (5 minutos de inatividade)
        if time.ticks_diff(time.ticks_ms(), last_active) > 300000:
            cleanup_resources()
            show_menu()
            last_active = time.ticks_ms()
            
        time.sleep_ms(50)

if __name__ == "__main__":
    main()
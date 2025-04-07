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


# --- Game Management ---
def load_game(game_name):
    try:
        # Limpa TODAS as interrupções antes de carregar o novo jogo
        for pin in [button_a, button_b]:
            pin.irq(handler=None)
        
        # Limpeza de memória mais agressiva
        gc.collect()
        
        # Mostra tela de loading
        show_loading(games[selected][0])
        
        # Mapeamento de nomes de jogos para módulos
        file_names = {
            "Snake": "Snake",
            "Space Invaders": "spaceInvaders",
            "Racing Cars": "Racing_cars"
        }
        
        module_name = file_names.get(game_name, game_name)
        
        # Força o recarregamento do módulo se já estiver carregado
        if module_name in sys.modules:
            del sys.modules[module_name]
        
        # Importa e executa o jogo
        game_module = __import__(module_name, None, None, ['main'])
        game_module.main(oled, joystick_y, button_b, button_a)
        
    except Exception as e:
        show_error(f"Erro ao carregar {game_name}:\n{str(e)}")
    finally:
        # Garante que as interrupções sejam limpas mesmo em caso de erro
        for pin in [button_a, button_b]:
            pin.irq(handler=None)
        gc.collect()
        oled.fill(0)
        oled.show()

# --- Main Loop ---
def main():
    show_menu()
    while True:
        selected_game = check_input()
        if selected_game:
            load_game(selected_game)
            show_menu()  # Volta ao menu após o jogo
        time.sleep_ms(50)

if __name__ == "__main__":
    main()
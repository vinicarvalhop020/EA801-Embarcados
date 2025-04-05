from machine import Pin, I2C, ADC, Timer
from ssd1306 import SSD1306_I2C
import time
import gc
import sys

# --- Hardware Configuration ---
i2c = I2C(1, scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)
joystick_y = ADC(Pin(26))
button_b = Pin(6, Pin.IN, Pin.PULL_UP)
button_a = Pin(5, Pin.IN, Pin.PULL_UP)  # Botão para voltar ao menu

# --- Game Menu ---
games = [
    ("Snake", "Snake"),
    ("spaceInvaders", "spaceInvaders"),
    ("Racing_cars", "Racing_cars")
]
selected = 0
last_input_time = time.ticks_ms()
DEBOUNCE_DELAY = 200  # ms

# --- UI Functions ---
def show_menu(highlight=None):
    """Mostra o menu com animação de seleção"""
    oled.fill(0)
    oled.text("Selecione o jogo:", 0, 0)
    
    for i, (name, _) in enumerate(games):
        prefix = ">" if i == selected else " "
        y_pos = 15 + i*15
        
        # Efeito de highlight
        if highlight == i:
            oled.fill_rect(0, y_pos-2, 128, 12, 1)
            oled.text(f"{prefix} {name}", 0, y_pos, 0)
        else:
            oled.text(f"{prefix} {name}", 0, y_pos, 1)
    
    oled.show()

def show_loading(game_name):
    """Tela de carregamento animada"""
    for i in range(4):
        oled.fill(0)
        oled.text(f"Carregando{'.'*i}", 20, 20)
        oled.text(game_name, 40, 40)
        oled.show()
        time.sleep_ms(300)

def show_error(message):
    """Mostra mensagem de erro"""
    oled.fill(0)
    oled.text("ERRO:", 0, 10)
    for i, line in enumerate(message.split('\n')):
        oled.text(line[:20], 0, 20 + i*10)
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

# --- Game Management ---
def load_game(game_name):
    """Carrega e executa um jogo"""
    try:
        # Limpa memória antes de carregar
        gc.collect()
        
        # Mostra tela de carregamento
        show_loading(games[selected][0])
        
        # Importa dinamicamente o módulo
        module = __import__(f"games.{game_name}", None, None, ['main'])
        
        # Executa o jogo
        module.main(oled, joystick_y, button_b, button_a)
        
    except ImportError:
        show_error(f"Jogo não encontrado:\n{games[selected][1]}.py")
    except Exception as e:
        show_error(f"Erro no jogo:\n{str(e)}")
    finally:
        # Limpeza pós-jogo
        gc.collect()
        oled.fill(0)
        oled.show()

# --- Main Loop ---
def main():
    # Animação inicial
    for i in range(3):
        show_menu(highlight=selected)
        time.sleep_ms(100)
        show_menu()
        time.sleep_ms(100)
    
    while True:
        show_menu()
        selected_game = check_input()
        
        if selected_game:
            load_game(selected_game)
        
        time.sleep_ms(50)

if __name__ == "__main__":
    main()
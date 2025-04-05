from machine import Pin, I2C, ADC
from ssd1306 import SSD1306_I2C
import time
import sys

# --- Hardware ---
i2c = I2C(1, scl=Pin(15), sda=Pin(14))
oled = SSD1306_I2C(128, 64, i2c)
joystick_y = ADC(Pin(26))
button_b = Pin(6, Pin.IN, Pin.PULL_UP)

# --- Menu ---
games = [
    ("Snake", "snake.py"),
    ("Space Invaders", "space_invaders.py"),
    ("Racing", "racing.py")
]
selected = 0

def show_menu():
    oled.fill(0)
    oled.text("Selecione o jogo:", 0, 0)
    
    for i, (name, _) in enumerate(games):
        prefix = ">" if i == selected else " "
        oled.text(f"{prefix} {name}", 0, 15 + i*15)
    
    oled.show()

# --- Controles ---
def check_input():
    global selected
    y_value = joystick_y.read_u16()
    
    if y_value < 10000:  # Para cima
        selected = (selected - 1) % len(games)
    elif y_value > 50000:  # Para baixo
        selected = (selected + 1) % len(games)
    
    if button_b.value() == 0:  # Botão B seleciona
        return games[selected][1]
    return None

# --- Main Loop ---
while True:
    show_menu()
    selected_game = check_input()
    
    if selected_game:
        oled.fill(0)
        oled.text(f"Iniciando...", 0, 30)
        oled.show()
        time.sleep(1)
        
        # Carrega o jogo selecionado
        with open(f"/games/{selected_game}") as f:
            exec(f.read())
        
        # Volta ao menu após o jogo terminar
        oled.fill(0)
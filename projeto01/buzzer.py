from machine import Pin, PWM
import time

# Configura o buzzer (GPIO21 conforme manual da BitDoglab)
buzzer = PWM(Pin(21))  

def play_tone(frequency, duration=0.1):
    """Toca um tom na frequência especificada"""
    buzzer.freq(frequency)
    buzzer.duty_u16(32768)  # 50% duty cycle
    time.sleep(duration)
    buzzer.duty_u16(0)  # Desliga

# Exemplo de uso:
play_tone(440)  # Toca um Lá (440Hz) por 0.1s
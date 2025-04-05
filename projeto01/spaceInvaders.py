from machine import Pin, ADC, Timer
import neopixel
import time
import random

# --- Hardware ---
np = neopixel.NeoPixel(Pin(7), 25)  # Matriz 5x5
joystick_x = ADC(Pin(27))            # Controle horizontal
botao_tiro = Pin(22, Pin.IN, Pin.PULL_UP)  # Botão de atirar

# --- Variáveis do Jogo ---
player_pos = 2          # Posição inicial da nave (linha 4)
tiro = None             # Posição do tiro (x,y)
inimigos = [[0, i] for i in range(5)]  # Inimigos na linha 0
direcao_inimigos = 1    # 1 = direita, -1 = esquerda
game_speed = 0.5        # Velocidade inicial
brightness = 0.1

# --- Cores ---
COR_NAVE = (0, 0, 255)    # Azul
COR_TIRO = (255, 255, 0)  # Amarelo
COR_INIMIGO = (255, 0, 0) # Vermelho

def atualiza_posicao(timer):
    global player_pos
    x = joystick_x.read_u16()
    if x < 10000: player_pos = max(0, player_pos - 1)
    elif x > 50000: player_pos = min(4, player_pos + 1)

def atira(pin):
    global tiro
    if tiro is None:  # Só atira se não houver tiro ativo
        tiro = [player_pos, 3]  # Sai da linha 4 (posição da nave)

# Configura interrupções
Timer().init(freq=20, mode=Timer.PERIODIC, callback=atualiza_posicao)
botao_tiro.irq(trigger=Pin.IRQ_FALLING, handler=atira)

def move_inimigos():
    global direcao_inimigos, inimigos
    
    # Move todos os inimigos
    for inimigo in inimigos:
        inimigo[1] += direcao_inimigos
    
    # Verifica bordas
    if any(inimigo[1] == 0 or inimigo[1] == 4 for inimigo in inimigos):
        direcao_inimigos *= -1
        for inimigo in inimigos:
            inimigo[0] += 1  # Desce uma linha

def atualiza_tiro():
    global tiro
    if tiro:
        tiro[0] -= 1  # Move o tiro para cima
        if tiro[0] < 0:
            tiro = None  # Saiu da tela

def desenha_cena():
    np.fill((0, 0, 0))  # Limpa a matriz
    
    # Desenha inimigos
    for x, y in inimigos:
        if 0 <= x < 5 and 0 <= y < 5:
            np[y*5 + x] = COR_INIMIGO
    
    # Desenha tiro
    if tiro:
        x, y = tiro
        np[y*5 + x] = COR_TIRO
    
    # Desenha nave (sempre na linha 4)
    np[player_pos + 4*5] = COR_NAVE
    
    np.write()

while True:
    # Lógica
    move_inimigos()
    atualiza_tiro()
    
    # Verifica colisões
    if tiro and tiro in inimigos:
        inimigos.remove(tiro)
        tiro = None
        game_speed *= 0.9  # Aumenta dificuldade
    
    # Render
    desenha_cena()
    time.sleep(game_speed)
    
    # Fim de jogo
    if any(inimigo[0] == 4 for inimigo in inimigos):  # Inimigos chegaram ao fim
        break


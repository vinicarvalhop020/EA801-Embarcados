from servo import Servos
from machine import I2C, Pin, UART
import time
import math

# Configuração inicial
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
i2c = I2C(id=1, sda=Pin(2), scl=Pin(3), freq=100000)
print("Dispositivos I2C encontrados:", i2c.scan())

servo = Servos(i2c=i2c)

# Dicionário de servos
dict_servos = {
    "HeadServo": 1,
    "Leg1F": 2, "Leg1B": 3,
    "Leg2F": 4, "Leg2B": 5,
    "Leg3F": 6, "Leg3B": 7,
    "Leg4F": 8, "Leg4B": 9
}

# Variáveis de estado
maxstep = 0
totalforwardsteps = 50
totalsidesteps = 25
moveforwardsteps = 0
movesidesteps = 0
forwardsteps = 0

stepLeg1F = 0
stepLeg1B = 0
stepLeg2F = 0
stepLeg2B = 0
stepLeg3F = 0
stepLeg3B = 0
stepLeg4F = 0
stepLeg4B = 0

# Tabelas de movimento
walkF = [
    [124, 146, 177, 150, 132, 115, 115],
    [94, 132, 178, 139, 112, 84, 84],
    [37, 112, 179, 139, 95, 42, 42],
    [22, 95, 150, 115, 78, 30, 30],
    [11, 78, 124, 92, 59, 13, 13],
    [13, 59, 92, 58, 36, 2, 2]
]

walkB = [
    [3, 34, 56, 65, 48, 30, 30],
    [2, 48, 86, 96, 68, 41, 41],
    [1, 68, 143, 138, 85, 41, 41],
    [30, 85, 158, 150, 102, 65, 65],
    [56, 102, 169, 167, 121, 88, 88],
    [88, 121, 167, 178, 144, 122, 122]
]

walkH = [3, 4, 5, 6, 7, 8]
Fheight = 5
Bheight = 5
heightchange = 0

walkstep = 1
walkstep2 = 0

Twalkstep = 0
Twalkstep2 = 0

# Variáveis de controle
reccmd = "S"
autorun = False
fromauto = False
smoothrun = True
smoothdelay = 2

# Ângulos atuais dos servos
LALeg1F = 80
LALeg1B = 100
LALeg2F = 100
LALeg2B = 80
LALeg3F = 80
LALeg3B = 100
LALeg4F = 100
LALeg4B = 80
LAHeadservo = 90

# Ângulos alvo dos servos
TOLeg1F = LALeg1F
TOLeg1B = LALeg1B
TOLeg2F = LALeg2F
TOLeg2B = LALeg2B
TOLeg3F = LALeg3F
TOLeg3B = LALeg3B
TOLeg4F = LALeg4F
TOLeg4B = LALeg4B
TOHeadservo = LAHeadservo

# Configuração do sensor de distância
trigPin = Pin('A2', Pin.OUT)  # Substitua 'A2' pelo pino correto no seu hardware
echoPin = Pin('A3', Pin.IN)   # Substitua 'A3' pelo pino correto no seu hardware

def initial_position():
    """Posição inicial do robô"""
    servo.position(index=dict_servos["Leg1F"], degrees=80)
    servo.position(index=dict_servos["Leg1B"], degrees=100)
    servo.position(index=dict_servos["Leg2F"], degrees=100)
    servo.position(index=dict_servos["Leg2B"], degrees=80)
    servo.position(index=dict_servos["Leg3F"], degrees=80)
    servo.position(index=dict_servos["Leg3B"], degrees=100)
    servo.position(index=dict_servos["Leg4F"], degrees=100)
    servo.position(index=dict_servos["Leg4B"], degrees=80) 
    servo.position(index=dict_servos["HeadServo"], degrees=90)
    time.sleep(1)

def sayhai():
    """Animação de saudação"""
    global TOHeadservo, TOLeg1F, TOLeg1B, TOLeg2F, TOLeg2B, TOLeg3F, TOLeg3B, TOLeg4F, TOLeg4B
    
    TOLeg1F = 0
    TOLeg1B = 180
    TOLeg2F = 180
    TOLeg2B = 0
    TOLeg3F = 180
    TOLeg3B = 0
    TOLeg4F = 0
    TOLeg4B = 180
    TOHeadservo = 90
    Servomovement()

    for i in range(1, 6):
        time.sleep_ms(500)
        TOLeg1F = 60
        TOHeadservo = 135
        Servomovement()

        time.sleep_ms(500)
        TOLeg1F = 100
        TOHeadservo = 45
        Servomovement()

    TOLeg1F = 0
    TOHeadservo = 90
    Servomovement()

def selfcheck():
    """Auto-teste dos servos"""
    global smoothdelay, TOHeadservo, TOLeg1F, TOLeg1B, TOLeg2F, TOLeg2B, TOLeg3F, TOLeg3B, TOLeg4F, TOLeg4B
    
    smoothdelay = 8
    TOLeg1F = 0
    TOLeg1B = 180
    TOLeg2F = 180
    TOLeg2B = 0
    TOLeg3F = 0
    TOLeg3B = 180
    TOLeg4F = 180
    TOLeg4B = 0
    TOHeadservo = 90
    Servomovement()

    time.sleep_ms(500)
    TOLeg1F = 180
    TOLeg1B = 0
    Servomovement()

    time.sleep_ms(500)
    TOLeg1F = 0
    TOLeg1B = 180
    Servomovement()

    time.sleep_ms(500)
    TOLeg2F = 0
    TOLeg2B = 180
    Servomovement()

    time.sleep_ms(500)
    TOLeg2F = 180
    TOLeg2B = 0
    Servomovement()

    time.sleep_ms(500)
    TOLeg3F = 180
    TOLeg3B = 0
    Servomovement()

    time.sleep_ms(500)
    TOLeg3F = 0
    TOLeg3B = 180
    Servomovement()

    time.sleep_ms(500)
    TOLeg4F = 0
    TOLeg4B = 180
    Servomovement()

    time.sleep_ms(500)
    TOLeg4F = 180
    TOLeg4B = 0
    Servomovement()

    TOHeadservo = 0
    Servomovement()
    time.sleep_ms(100)
    TOHeadservo = 180
    Servomovement()
    time.sleep_ms(100)
    TOHeadservo = 90
    Servomovement()
    time.sleep_ms(100)
    smoothdelay = 2

def changeheight():
    """Ajusta a altura do robô"""
    global Fheight, Bheight, heightchange, othercmd
    global TOLeg1F, TOLeg1B, TOLeg2F, TOLeg2B, TOLeg3F, TOLeg3B, TOLeg4F, TOLeg4B
    
    if othercmd == "O":
        Fheight = 5
        Bheight = 5
    elif othercmd == "P":
        Fheight = 0
        Bheight = 0

    if othercmd in ["D", "U", "W", "Y"]:
        Fheight += heightchange
        Fheight = max(0, min(5, Fheight))
        
    if othercmd in ["D", "U", "X", "Z"]:
        Bheight += heightchange
        Bheight = max(0, min(5, Bheight))
        
    heightchange = 0

    rotate1 = walkF[Fheight][4]
    rotate2 = walkB[Fheight][4]
    TOLeg1F = rotate1
    TOLeg1B = rotate2
    TOLeg2F = 180 - rotate1
    TOLeg2B = 180 - rotate2

    rotate1 = walkF[Bheight][4]
    rotate2 = walkB[Bheight][4]
    TOLeg3F = rotate1
    TOLeg3B = rotate2
    TOLeg4F = 180 - rotate1
    TOLeg4B = 180 - rotate2
    Servomovement()

def Servomovement():
    """Move os servos suavemente para as posições alvo"""
    global LALeg1F, LALeg1B, LALeg2F, LALeg2B, LALeg3F, LALeg3B, LALeg4F, LALeg4B, LAHeadservo
    global stepLeg1F, stepLeg1B, stepLeg2F, stepLeg2B, stepLeg3F, stepLeg3B, stepLeg4F, stepLeg4B
    
    if smoothrun:
        smoothmove()

    # Atualiza posições atuais
    LALeg1F = TOLeg1F
    LALeg1B = TOLeg1B
    LALeg2F = TOLeg2F
    LALeg2B = TOLeg2B
    LALeg3F = TOLeg3F
    LALeg3B = TOLeg3B
    LALeg4F = TOLeg4F
    LALeg4B = TOLeg4B
    LAHeadservo = TOHeadservo

    # Move os servos para as posições alvo
    servo.position(index=dict_servos["Leg1F"], degrees=TOLeg1F)
    servo.position(index=dict_servos["Leg1B"], degrees=TOLeg1B)
    servo.position(index=dict_servos["Leg2F"], degrees=TOLeg2F)
    servo.position(index=dict_servos["Leg2B"], degrees=TOLeg2B)
    servo.position(index=dict_servos["Leg3F"], degrees=TOLeg3F)
    servo.position(index=dict_servos["Leg3B"], degrees=TOLeg3B)
    servo.position(index=dict_servos["Leg4F"], degrees=TOLeg4F)
    servo.position(index=dict_servos["Leg4B"], degrees=TOLeg4B)
    servo.position(index=dict_servos["HeadServo"], degrees=TOHeadservo)

def smoothmove():
    """Movimento suave entre posições"""
    global maxstep, LALeg1F, LALeg1B, LALeg2F, LALeg2B, LALeg3F, LALeg3B, LALeg4F, LALeg4B, LAHeadservo
    global stepLeg1F, stepLeg1B, stepLeg2F, stepLeg2B, stepLeg3F, stepLeg3B, stepLeg4F, stepLeg4B
    
    maxstep = max(
        abs(LALeg1F - TOLeg1F),
        abs(LALeg1B - TOLeg1B),
        abs(LALeg2F - TOLeg2F),
        abs(LALeg2B - TOLeg2B),
        abs(LALeg3F - TOLeg3F),
        abs(LALeg3B - TOLeg3B),
        abs(LALeg4F - TOLeg4F),
        abs(LALeg4B - TOLeg4B)
    )

    if maxstep > 0:
        stepLeg1F = (TOLeg1F - LALeg1F) / maxstep
        stepLeg1B = (TOLeg1B - LALeg1B) / maxstep
        stepLeg2F = (TOLeg2F - LALeg2F) / maxstep
        stepLeg2B = (TOLeg2B - LALeg2B) / maxstep
        stepLeg3F = (TOLeg3F - LALeg3F) / maxstep
        stepLeg3B = (TOLeg3B - LALeg3B) / maxstep
        stepLeg4F = (TOLeg4F - LALeg4F) / maxstep
        stepLeg4B = (TOLeg4B - LALeg4B) / maxstep

        for i in range(maxstep + 1):
            LALeg1F += stepLeg1F
            LALeg1B += stepLeg1B
            LALeg2F += stepLeg2F
            LALeg2B += stepLeg2B
            LALeg3F += stepLeg3F
            LALeg3B += stepLeg3B
            LALeg4F += stepLeg4F
            LALeg4B += stepLeg4B

            servo.position(index=dict_servos["Leg1F"], degrees=LALeg1F)
            servo.position(index=dict_servos["Leg1B"], degrees=LALeg1B)
            servo.position(index=dict_servos["Leg2F"], degrees=LALeg2F)
            servo.position(index=dict_servos["Leg2B"], degrees=LALeg2B)
            servo.position(index=dict_servos["Leg3F"], degrees=LALeg3F)
            servo.position(index=dict_servos["Leg3B"], degrees=LALeg3B)
            servo.position(index=dict_servos["Leg4F"], degrees=LALeg4F)
            servo.position(index=dict_servos["Leg4B"], degrees=LALeg4B)

            time.sleep_ms(smoothdelay)

    # Movimento suave para a cabeça
    if LAHeadservo > TOHeadservo:
        for i in range(LAHeadservo, TOHeadservo - 1, -1):
            LAHeadservo = i
            servo.position(index=dict_servos["HeadServo"], degrees=LAHeadservo)
            time.sleep_ms(smoothdelay)
    else:
        for i in range(LAHeadservo, TOHeadservo + 1):
            LAHeadservo = i
            servo.position(index=dict_servos["HeadServo"], degrees=LAHeadservo)
            time.sleep_ms(smoothdelay)

def Distancecal():
    """Calcula a distância usando o sensor ultrassônico"""
    trigPin.value(0)
    time.sleep_us(2)
    trigPin.value(1)
    time.sleep_us(10)
    trigPin.value(0)
    
    # Mede o pulso no pino de eco
    pulse_time = machine.time_pulse_us(echoPin, 1, 30000)  # Timeout de 30ms
    distance = pulse_time * 0.034 / 2 if pulse_time > 0 else 0
    
    return distance

def check_uart():
    """Verifica comandos recebidos pela UART"""
    global reccmd, autorun, autostep, stopcmd, heightchange, othercmd
    
    if uart.any():
        data = uart.read().decode().strip()
        for cmd in data:
            if cmd == 'A':
                autorun = True
                autostep = 0
            elif cmd == 'M':
                autorun = False
            elif not autorun:
                if cmd in ['F', 'B', 'L', 'R', 'G', 'I', 'H', 'J']:
                    reccmd = cmd
                elif cmd == 'S':
                    stopcmd = True
                elif cmd in ['C', 'V']:
                    reccmd = cmd
                elif cmd in ['U', 'O']:
                    othercmd = cmd
                    heightchange = 1
                elif cmd in ['D', 'P']:
                    othercmd = cmd
                    heightchange = -1
                elif cmd in ['W', 'X']:
                    othercmd = cmd
                    heightchange = -1
                elif cmd in ['Y', 'Z']:
                    othercmd = cmd
                    heightchange = 1

def main_loop():
    """Loop principal do robô"""
    global reccmd, autorun, autostep, fromauto, smoothdelay
    global walkstep, walkstep2, Fheight, Bheight, heightchange
    global moveforwardsteps, movesidesteps, forwardsteps, stopcmd
    
    while True:
        check_uart()
        
        if autorun:
            if not fromauto:
                fromauto = True
                
            if autostep == 0:
                Fheight = 5
                Bheight = 5
                autostep = 1
                forwardsteps = 0
                changeheight()
            elif autostep == 1:
                distance = Distancecal()
                if distance < 8:
                    reccmd = "S"
                    autostep = 2
                else:
                    reccmd = "F"

                if Fheight != 5:
                    moveforwardsteps += 1
                    if moveforwardsteps > totalforwardsteps:
                        Fheight = 5
                        Bheight = 5
                        autostep = 1
            elif autostep == 2:
                if Fheight >= 1:
                    Fheight -= 1
                    Bheight -= 1
                    changeheight()
                    distance = Distancecal()
                    if distance >= 5:
                        forwardsteps = 0
                        moveforwardsteps = 0
                        autostep = 1
                else:
                    Fheight = 5
                    Bheight = 5
                    autostep = 3
                    changeheight()
            elif autostep == 3:
                smoothdelay = 8
                TOHeadservo = 0
                Servomovement()
                rightdistance = Distancecal()
                time.sleep_ms(100)
                TOHeadservo = 180
                Servomovement()
                leftdistance = Distancecal()
                time.sleep_ms(100)
                TOHeadservo = 90
                Servomovement()
                smoothdelay = 2
                
                reccmd = "L" if leftdistance > rightdistance else "R"
                movesidesteps = 0
                autostep = 4
            elif autostep == 4:
                movesidesteps += 1
                if movesidesteps > totalsidesteps:
                    autostep = 1
        elif fromauto:
            Fheight = 5
            Bheight = 5
            reccmd = "S"
            changeheight()
            fromauto = False

        if reccmd in ["F", "B", "L", "R", "G", "I", "H", "J"]:
            if reccmd in ["F", "L", "G", "I"]:
                walkstep += 1
                if walkstep > 7:
                    walkstep = 1
                walkstep2 = walkstep + 3
                if walkstep2 > 7:
                    walkstep2 -= 7
            elif reccmd in ["B", "R", "H", "J"]:
                walkstep -= 1
                if walkstep < 1:
                    walkstep = 7
                walkstep2 = walkstep - 4
                if walkstep2 < 1:
                    walkstep2 += 7

            if reccmd in ["F", "B"]:
                # Implementação do movimento para frente/trás
                rotate1 = walkF[Fheight][walkstep - 1]
                rotate2 = walkB[Fheight][walkstep - 1]
                rotate3 = walkF[Bheight][walkstep - 1]
                rotate4 = walkB[Bheight][walkstep - 1]

                TOLeg1F = rotate1
                TOLeg1B = rotate2
                TOLeg4F = 180 - rotate3
                TOLeg4B = 180 - rotate4
                Servomovement()

                rotate1 = walkF[Fheight][walkstep2 - 1]
                rotate2 = walkB[Fheight][walkstep2 - 1]
                rotate3 = walkF[Bheight][walkstep2 - 1]
                rotate4 = walkB[Bheight][walkstep2 - 1]

                TOLeg2F = 180 - rotate1
                TOLeg2B = 180 - rotate2
                TOLeg3F = rotate3
                TOLeg3B = rotate4
                Servomovement()

            elif reccmd in ["G", "I", "H", "J"]:
                # Implementação de movimentos laterais
                if reccmd == "I" and walkstep >= 4:
                    rotate1 = walkF[Fheight][4]
                    rotate2 = walkB[Fheight][4]
                else:
                    rotate1 = walkF[Fheight][walkstep - 1]
                    rotate2 = walkB[Fheight][walkstep - 1]

                if reccmd == "H" and walkstep >= 4:
                    rotate3 = walkF[Bheight][4]
                    rotate4 = walkB[Bheight][4]
                else:
                    rotate3 = walkF[Bheight][walkstep - 1]
                    rotate4 = walkB[Bheight][walkstep - 1]

                TOLeg1F = rotate1
                TOLeg1B = rotate2
                TOLeg4F = 180 - rotate3
                TOLeg4B = 180 - rotate4
                Servomovement()

                if reccmd == "G" and walkstep2 >= 4:
                    rotate1 = walkF[Fheight][4]
                    rotate2 = walkB[Fheight][4]
                else:
                    rotate1 = walkF[Fheight][walkstep2 - 1]
                    rotate2 = walkB[Fheight][walkstep2 - 1]

                if reccmd == "J" and walkstep2 >= 4:
                    rotate3 = walkF[Bheight][4]
                    rotate4 = walkB[Bheight][4]
                else:
                    rotate3 = walkF[Bheight][walkstep2 - 1]
                    rotate4 = walkB[Bheight][walkstep2 - 1]

                TOLeg2F = 180 - rotate1
                TOLeg2B = 180 - rotate2
                TOLeg3F = rotate3
                TOLeg3B = rotate4
                Servomovement()

            elif reccmd in ["L", "R"]:
                # Implementação de giros
                rotate1 = walkF[Fheight][walkstep - 1]
                rotate2 = walkB[Fheight][walkstep - 1]
                rotate3 = walkF[Bheight][walkstep - 1]
                rotate4 = walkB[Bheight][walkstep - 1]

                TOLeg1F = rotate1
                TOLeg1B = rotate2
                TOLeg4F = rotate4
                TOLeg4B = rotate3
                Servomovement()

                rotate1 = walkF[Fheight][(8 - walkstep) - 1]
                rotate2 = walkB[Fheight][(8 - walkstep) - 1]
                rotate3 = walkF[Bheight][(8 - walkstep) - 1]
                rotate4 = walkB[Bheight][(8 - walkstep) - 1]

                TOLeg2F = 180 - rotate1
                TOLeg2B = 180 - rotate2
                TOLeg3F = 180 - rotate4
                TOLeg3B = 180 - rotate3
                Servomovement()

            time.sleep_ms(100)

            if stopcmd:
                if walkstep == 4:
                    reccmd = "S"
                    stopcmd = False
                    
            if heightchange != 0 and walkstep == 4:
                changeheight()
                
        elif heightchange != 0:
            changeheight()
        elif reccmd == "C":
            smoothdelay = 8
            selfcheck()
            smoothdelay = 2
            reccmd = "S"
        elif reccmd == "V":
            sayhai()
            reccmd = "S"

# Inicialização
initial_position()
print("Robô inicializado e pronto para comandos")

# Inicia o loop principal
main_loop()
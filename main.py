from pca9685 import PCA9685
from servo import Servos
from machine import I2C, Pin, UART
from time import sleep
import utime

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
i2c = I2C(id = 1, sda= Pin(2),scl= Pin(3), freq= 100000)
print("Dispositivos I2C encontrados:", i2c.scan())


pca = PCA9685(i2c = i2c)
servo = Servos(i2c = i2c)



print("Teste do HC-05 - BitDogLab")
print("Aguardando dados Bluetooth...")


sevos = [0,1,2,3,4,5,6,7,8,9]

while True:
    if uart.any():
        data = uart.read()
        try:
            if data:
                # Decodifica os dados recebidos
                decoded_data = data.decode('utf-8').strip()
                print("Dados recebidos:", decoded_data)

                # Verifica se o comando é para acender ou apagar o LED
                if decoded_data == 'A':
                    servo.position(index=0,degrees = 180)
                elif decoded_data == 'B':
                    servo.position(index=1,degrees = 180)
                elif decoded_data == 'R':
                    servo.position(index=2,degrees = 180)
                elif decoded_data == 'L':
                    servo.position(index=3,degrees = 180)
                elif decoded_data == 'T':
                    servo.position(index= 4,degrees = 180)
                elif decoded_data == 'X':
                    servo.position(index=5,degrees = 180)
                elif decoded_data == 'C':
                    servo.position(index=6,degrees = 180)
                elif decoded_data == 'S':
                    servo.position(index=7,degrees = 180)
                elif decoded_data == 'P':
                    servo.position(index=8,degrees = 180)
                elif decoded_data == 'F':
                    servo.position(index=9,degrees = 180)
                elif decoded_data == '0':
                    for i in range(10):
                        servo.position(index=i,degrees = 0)

                elif decoded_data == 'RESET':
                    for i in range(10):
                        servo.position(index=i,degrees = 180)
                    sleep(0.5)
                    for i in range(10):
                        servo.position(index=i,degrees = 0)
                    sleep(0.5)

        except UnicodeError:
            print("Dados inválidos recebidos")
    
    # Pequena pausa para evitar sobrecarga
    sleep(0.1)

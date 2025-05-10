from pca9685 import PCA9685
from servo import Servos
from time import sleep
import utime

from machine import I2C, Pin

i2c = I2C(id=1, sda=Pin(2), scl=Pin(3), freq=100000)  # Use I2C1, não I2C0

print("Dispositivos I2C encontrados:", i2c.scan())


pca = PCA9685(i2c=i2c)
servo = Servos(i2c=i2c)


servo.position(index=0, degrees=180)


while True:
    servo.position(index=1, degrees=0)
    sleep(0.5)
    servo.position(index=1, degrees=180)
    sleep(0.5)
    
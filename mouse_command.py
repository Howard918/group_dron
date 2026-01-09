from time import sleep
import pyautogui as pg

width = pg.size().width
height = pg.size().height

while True:
    roll = int((pg.position().x / (width/200) - 100) * 0.3)
    pitch = -int((pg.position().y / (height/200) - 100) * 0.3)
    print(roll, pitch)
    sleep(0.1)
print(pg.size())
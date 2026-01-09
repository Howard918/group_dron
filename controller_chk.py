from time import sleep
from CodingRider.drone import *
from CodingRider.protocol import *

def eventButton(button):
    print(button.button)

drone = Drone()
drone.open('COM6')
drone.setEventHandler(DataType.Button, eventButton)
drone.sendPing(DeviceType.Controller)

while True:
    sleep(0.01)
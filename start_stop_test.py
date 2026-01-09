from time import sleep
from CodingRider.drone import *
from CodingRider.protocol import *

drone = Drone()
drone.open('COM6')

sleep(2)
drone.sendTakeOff()
print("Take Off")
sleep(5)
drone.sendLanding()
print("Landing")

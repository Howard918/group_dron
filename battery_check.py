from time import sleep
from CodingRider.drone import *
from CodingRider.protocol import *

def eventState(state):
    print(state.battery)

drone = Drone()
drone.open('COM6')
drone.setEventHandler(DataType.State, eventState)
drone.sendRequest(DeviceType.Drone, DataType.State)

sleep(1)
from time import *
import keyboard
from CodingRider.drone import *
from CodingRider.protocol import *

BEFORE_FLYING = 0
FLYING = 1
EXIT_FLYING = 2

THROTTLE = 0
PITCH = 0
ROLL = 0
YAW = 0

drone = Drone()
drone.open('COM6')
print("System Starting")
print("Ver 1.0.1")
sleep(3)
print("Drone is Ready\n" \
"Key 'Enter' to Start\n" \
"Key 'c' to Calibration Drone\n" \
"Key 'b' to Check Battery\n" \
"Key 'esc' to Exit Program")
flying_status = BEFORE_FLYING


def batteryState(state):
    print("Battery :",state.battery,"%")    

while flying_status is not EXIT_FLYING:
    if keyboard.is_pressed('esc'):
        if flying_status == FLYING:
            drone.sendLanding()
            print("Stop Flying \nLanding ...")
        flying_status = EXIT_FLYING
        break
    elif keyboard.is_pressed('b'):
        drone.setEventHandler(DataType.State, batteryState)
        drone.sendRequest(DeviceType.Drone, DataType.State)

    if flying_status == FLYING:
        PITCH = 0
        YAW = 0
        ROLL = 0
        THROTTLE = 0
        drone.sendControl(0,0,0,0)

    if flying_status is BEFORE_FLYING:
        if keyboard.is_pressed('enter'):
            drone.sendTakeOff()
            print("Start Take Off ...")
            sleep(5)
            print("Ready To Flying")
            flying_status = FLYING
        elif keyboard.is_pressed('c'):
            print("Put the drone on flat spaces ...")
            sleep(1)
            print("Start Drone Calibration\nDO NOT MOVE the Drone")
            drone.sendClearBias()
            sleep(3)
            print("Calbration Complete")
        elif keyboard.is_pressed('f1'):
            print("======= Key Mapping =======")
            print("Key 'enter' to Start\n" \
                "Key 'c' to Calibration Drone\n" \
                "Key 'b' to Check Battery\n" \
                "Key 'esc' to Exit Program")
            
    if flying_status is FLYING:
        if keyboard.is_pressed('up'):
            THROTTLE = 20
        if keyboard.is_pressed('down'):
            THROTTLE = -40
        if keyboard.is_pressed('w'):
            PITCH = 30
        if keyboard.is_pressed('a'):
            ROLL = -30
        if keyboard.is_pressed('s'):
            PITCH = -30
        if keyboard.is_pressed('d'):
            ROLL = 30
        if keyboard.is_pressed('q'):
            YAW = -30
        if keyboard.is_pressed('e'):
            YAW = 30
        if keyboard.is_pressed('f1'):
            print("======= Key Mapping =======")
            print("Key 'b' to Check Battery\n" \
                "Key 'esc' to Land the Drone\n" \
                "Key 'up' to going Up\n" \
                "Key 'down' to going Down\n" \
                "Key 'w' to move Forward\n" \
                "Key 's' to move Backward\n" \
                "Key 'a' to move Left\n" \
                "Key 'd' to move Right\n" \
                "Key 'q' to turn Left\n" \
                "Key 'e' to turn Right")
    
    if flying_status == FLYING:
        drone.sendControl(ROLL, PITCH, YAW, THROTTLE)
    
    sleep(0.01)
print("<< Program Done >>")
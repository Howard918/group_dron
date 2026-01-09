from time import *
import keyboard
import pyautogui as pg
from CodingRider.drone import *
from CodingRider.protocol import *

BEFORE_FLYING = 0
FLYING = 1
EXIT_FLYING = 2

# 화면 크기를 가져와 마우스 컨트롤에 사용
width = pg.size().width
height = pg.size().height

drone = Drone()
drone.open('COM6')
print("System Starting")
print("Ver 1.0.2")
sleep(3)
print("Drone is Ready\n" \
"Mouse to control Pitch and Roll\n" \
"Key 'Enter' to Start\n" \
"Key 'c' to Calibration Drone\n" \
"Key 'b' to Check Battery\n" \
"Key 'esc' to Exit Program")
flying_status = BEFORE_FLYING


def batteryState(state):
    print("Battery :", state.battery, "%")

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
        # 매 루프마다 키보드 값을 초기화 (키를 떼면 멈추도록)
        THROTTLE = 0
        YAW = 0

        # 마우스 위치에 따라 Roll과 Pitch 값을 계산
        ROLL = int((pg.position().x / (width / 200) - 100) * 0.3)
        PITCH = -int((pg.position().y / (height / 200) - 100) * 0.3)

        # 키보드로 Throttle(고도) 및 Yaw(회전) 제어
        if keyboard.is_pressed('up'):
            THROTTLE = 20
        if keyboard.is_pressed('down'):
            THROTTLE = -45
        if keyboard.is_pressed('q'):
            YAW = -30
        if keyboard.is_pressed('e'):
            YAW = 30
        if keyboard.is_pressed('f1'):
            print("======= Key Mapping =======")
            print("Move Mouse to control Roll and Pitch\n" \
                  "Key 'b' to Check Battery\n" \
                  "Key 'esc' to Land the Drone\n" \
                  "Key 'up' to going Up\n" \
                  "Key 'down' to going Down\n" \
                  "Key 'q' to turn Left\n" \
                  "Key 'e' to turn Right")

        # 계산된 최종 값을 드론으로 전송
        drone.sendControl(ROLL, PITCH, YAW, THROTTLE)

    sleep(0.01)

print("<< Program Done >>")

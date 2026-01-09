from time import *
import keyboard
import pyautogui as pg
from CodingRider.drone import *
from CodingRider.protocol import *

# Application States
LANDED = 0
FLYING = 1
EXITING = 2

# Control Modes
KEYBOARD_MODE = "Keyboard"
MOUSE_MODE = "Mouse"

# Screen size for mouse control
try:
    width, height = pg.size()
except Exception as e:
    width, height = 1920, 1080 
    print(f"Warning: Could not get screen size ({e}). Using default 1920x1080.")

# --- Drone and State Initialization ---
drone = Drone()
drone.open('COM6')

flying_status = LANDED
control_mode = KEYBOARD_MODE  # Default mode

# --- Helper Functions for User Interface ---
def print_landed_help():
    print("\n======= Drone is LANDED ======")
    print(f"       Control Mode: {control_mode}")
    print("===============================")
    print("- 'enter': Start Flying")
    print("- 'm': Change Control Mode")
    print("- 'c': Calibrate Drone")
    print("- 'b': Check Battery")
    print("- 'esc': Exit Program")
    print("- 'f1': Show this help message")

def print_flying_help():
    print(f"\n======= Drone is FLYING | Mode: {control_mode} ======")
    print("- 'esc': Land the Drone")
    print("- 'b': Check Battery")
    if control_mode == KEYBOARD_MODE:
        print("- Arrow Keys: Control altitude (Up/Down)")
        print("- 'w'/'s': Move Forward/Backward")
        print("- 'a'/'d': Move Left/Right")
        print("- 'q'/'e': Turn Left/Right")
    elif control_mode == MOUSE_MODE:
        print("- Mouse: Control Forward/Backward & Left/Right")
        print("- Arrow Keys: Control altitude (Up/Down)")
        print("- 'q'/'e': Turn Left/Right")

def batteryState(state):
    print(f"Battery: {state.battery}%")

# --- Main Program ---
print("System Starting")
print("Unified Controller Ver 2.0.1")
sleep(2)
print("Drone is Ready.")
print_landed_help()

# Main loop
while flying_status is not EXITING:
    # --- Universal Key Presses ---
    # ESC key for landing or exiting
    if keyboard.is_pressed('esc'):
        if flying_status == FLYING:
            print("\nLanding...")
            drone.sendLanding()
            sleep(5)  # Allow time for landing
            flying_status = LANDED
            print("Drone has landed.")
            print_landed_help()
        elif flying_status == LANDED:
            flying_status = EXITING
        
        sleep(0.5)  # Debounce to prevent multiple triggers
        continue

    # Battery check
    if keyboard.is_pressed('b'):
        drone.setEventHandler(DataType.State, batteryState)
        drone.sendRequest(DeviceType.Drone, DataType.State)
        sleep(0.5) # Debounce

    # F1 for help
    if keyboard.is_pressed('f1'):
        if flying_status == LANDED:
            print_landed_help()
        elif flying_status == FLYING:
            print_flying_help()
        sleep(0.5)

    # --- State: LANDED ---
    if flying_status == LANDED:
        # Take off
        if keyboard.is_pressed('enter'):
            print("\nTaking off...")
            drone.sendTakeOff()
            sleep(5)
            print("Ready to fly!")
            flying_status = FLYING
            print_flying_help()
            sleep(0.5)
        
        # Calibration
        elif keyboard.is_pressed('c'):
            print("\nPlace drone on a flat surface for calibration.")
            sleep(1)
            print("Calibrating... DO NOT MOVE the drone.")
            drone.sendClearBias()
            sleep(3)
            print("Calibration complete.")
            sleep(0.5)
        
        # Mode switch
        elif keyboard.is_pressed('m'):
            control_mode = MOUSE_MODE if control_mode == KEYBOARD_MODE else KEYBOARD_MODE
            print(f"\nControl mode changed to: {control_mode}")
            print_landed_help()
            sleep(0.5)
            
        # Keep drone idle
        drone.sendControl(0, 0, 0, 0)

    # --- State: FLYING ---
    elif flying_status == FLYING:
        THROTTLE, PITCH, ROLL, YAW = 0, 0, 0, 0
        
        # -- Keyboard Mode --
        if control_mode == KEYBOARD_MODE:
            if keyboard.is_pressed('up'): THROTTLE = 20
            if keyboard.is_pressed('down'): THROTTLE = -40
            if keyboard.is_pressed('w'): PITCH = 30
            if keyboard.is_pressed('s'): PITCH = -30
            if keyboard.is_pressed('a'): ROLL = -30
            if keyboard.is_pressed('d'): ROLL = 30
            if keyboard.is_pressed('q'): YAW = 30
            if keyboard.is_pressed('e'): YAW = -30

        # -- Mouse Mode --
        elif control_mode == MOUSE_MODE:
            ROLL = int((pg.position().x / (width / 200) - 100) * 0.3)
            PITCH = -int((pg.position().y / (height / 200) - 100) * 0.3)
            
            if keyboard.is_pressed('up'): THROTTLE = 20
            if keyboard.is_pressed('down'): THROTTLE = -45
            if keyboard.is_pressed('q'): YAW = 30
            if keyboard.is_pressed('e'): YAW = -30
            
        # Send control command to drone
        drone.sendControl(ROLL, PITCH, YAW, THROTTLE)
        
    sleep(0.01)

# --- Cleanup ---
print("Closing connection...")
drone.close()
print("<< Program Done >>")

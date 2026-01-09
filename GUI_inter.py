import tkinter as tk
from tkinter import ttk
from time import sleep
import threading

# CodingRider 라이브러리가 설치되어 있어야 합니다.
# pip install CodingRider
from CodingRider.drone import *
from CodingRider.protocol import *

# ===================================================================
# ==                     APPLICATION GLOBALS                       ==
# ===================================================================

DRONE_IDS = ['D1', 'D2', 'D3']

# --- Drone Data Structures ---
drones = {}
drone_states = {}

# ===================================================================
# ==                       CORE FUNCTIONS                          ==
# ===================================================================

def connect_drone(drone_id):
    if drone_states.get(drone_id, {}).get('connected', False):
        return

    com_port = drone_states[drone_id]['com_port_var'].get()
    if not com_port:
        return
        
    drone_states[drone_id]['com_port'] = com_port
    drone_states[drone_id]['connected'] = 'CONNECTING'
    gui_elements[drone_id]['status_var'].set("Connecting...")
    gui_elements[drone_id]['connect_btn'].config(state=tk.DISABLED)

    try:
        new_drone = Drone()
        new_drone.open(com_port)
        
        handler = lambda state: battery_state_handler(drone_id, state)
        new_drone.setEventHandler(DataType.State, handler)
        drones[drone_id] = new_drone
        
        new_drone.sendRequest(DeviceType.Drone, DataType.State)
        timeout_id = root.after(3000, lambda: connection_timeout(drone_id))
        drone_states[drone_id]['timeout_id'] = timeout_id
        
    except Exception as e:
        connection_failed(drone_id, str(e))

def connection_timeout(drone_id):
    if drone_states.get(drone_id, {}).get('connected') == 'CONNECTING':
        connection_failed(drone_id, "Timeout")

def connection_failed(drone_id, reason="Failed"):
    if drone_id in drones:
        drones[drone_id].close()
        del drones[drone_id]

    drone_states[drone_id]['connected'] = False
    gui_elements[drone_id]['status_var'].set(f"Failed: {reason}")
    gui_elements[drone_id]['connect_btn'].config(state=tk.NORMAL)

def finalize_connection_gui(drone_id):
    drone_states[drone_id]['connected'] = True
    gui_elements[drone_id]['status_var'].set("Connected")
    gui_elements[drone_id]['connect_btn'].config(text="Disconnect", state=tk.NORMAL)
    gui_elements[drone_id]['com_entry'].config(state=tk.DISABLED)
    gui_elements[drone_id]['individual_cmds_frame'].pack(fill="x", pady=5)
    print(f"Drone {drone_id} on {drone_states[drone_id]['com_port']} handshake successful.")

def disconnect_drone(drone_id):
    if drone_states.get(drone_id, {}).get('connected') == 'CONNECTING':
        timeout_id = drone_states[drone_id].get('timeout_id')
        if timeout_id:
            root.after_cancel(timeout_id)

    if drone_id in drones:
        if drone_states[drone_id]['flying_status'] == 'FLYING':
            drones[drone_id].sendLanding()
            sleep(3)
        drones[drone_id].close()
        del drones[drone_id]
    
    drone_states[drone_id]['connected'] = False
    drone_states[drone_id]['flying_status'] = 'LANDED'
    
    gui_elements[drone_id]['status_var'].set("Disconnected")
    gui_elements[drone_id]['batt_var'].set("Battery: N/A")
    gui_elements[drone_id]['connect_btn'].config(text="Connect", state=tk.NORMAL)
    gui_elements[drone_id]['com_entry'].config(state=tk.NORMAL)
    gui_elements[drone_id]['individual_cmds_frame'].pack_forget()

    print(f"Drone {drone_id} disconnected.")

def battery_state_handler(drone_id, state):
    if drone_id in drone_states:
        if drone_states[drone_id].get('connected') == 'CONNECTING':
            timeout_id = drone_states[drone_id].get('timeout_id')
            if timeout_id:
                root.after_cancel(timeout_id)
            finalize_connection_gui(drone_id)

        drone_states[drone_id]['battery'] = state.battery
        root.after(0, lambda: gui_elements[drone_id]['batt_var'].set(f"Battery: {state.battery}%"))

def update_flying_status(drone_id, status):
    drone_states[drone_id]['flying_status'] = status
    display_status = "Flying" if status == "FLYING" else "Landed"
    gui_elements[drone_id]['status_var'].set(display_status)
    
    take_off_btn = gui_elements[drone_id]['takeoff_btn']
    if status == 'FLYING':
        take_off_btn.config(text="Land")
        enable_movement_controls(drone_id, True)
    else:
        take_off_btn.config(text="Take Off")
        enable_movement_controls(drone_id, False)

def connect_disconnect_command(drone_id):
    if not drone_states[drone_id]['connected']:
        connect_drone(drone_id)
    else:
        disconnect_drone(drone_id)

def set_panel_enabled(drone_id, is_enabled):
    """특정 드론 패널의 모든 버튼을 활성화/비활성화합니다."""
    state = tk.NORMAL if is_enabled else tk.DISABLED
    frame = gui_elements[drone_id]['individual_cmds_frame']
    for widget in frame.winfo_children():
        # container frames
        if isinstance(widget, (ttk.Frame, ttk.LabelFrame)):
            for sub_widget in widget.winfo_children():
                 if isinstance(sub_widget, ttk.Button):
                    sub_widget.config(state=state)
        # direct buttons
        elif isinstance(widget, ttk.Button):
            widget.config(state=state)

# ===================================================================
# ==                   INDIVIDUAL & SWARM COMMANDS                 ==
# ===================================================================

def take_off_land_individual(drone_id):
    if not drone_states.get(drone_id, {}).get('connected'): return

    is_landed = drone_states[drone_id]['flying_status'] == 'LANDED'
    
    # Disable panel during transition
    set_panel_enabled(drone_id, False)
    
    if is_landed:
        gui_elements[drone_id]['status_var'].set("Taking Off...")
        drones[drone_id].sendTakeOff()
        # After 5s, update status and re-enable panel
        root.after(5000, lambda: (update_flying_status(drone_id, "FLYING"), set_panel_enabled(drone_id, True)))
    else:
        gui_elements[drone_id]['status_var'].set("Landing...")
        drones[drone_id].sendLanding()
        # After 5s, update status and re-enable panel
        root.after(5000, lambda: (update_flying_status(drone_id, "LANDED"), set_panel_enabled(drone_id, True)))

def calibrate_individual(drone_id):
    if not drone_states.get(drone_id, {}).get('connected'): return
    drones[drone_id].sendClearBias()
    gui_elements[drone_id]['status_var'].set("Calibrating...")
    root.after(1000, lambda: update_flying_status(drone_id, drone_states[drone_id]['flying_status']))

def check_battery_individual(drone_id):
    if not drone_states.get(drone_id, {}).get('connected'): return
    drones[drone_id].sendRequest(DeviceType.Drone, DataType.State)

def take_off_all():
    print("Command: SWARM TAKE OFF")
    for drone_id in DRONE_IDS:
        if drone_states.get(drone_id, {}).get('connected') and drone_states[drone_id]['flying_status'] == 'LANDED':
            take_off_land_individual(drone_id)
            sleep(0.1)
    root.after(6000, check_battery_all)

def land_all():
    print("Command: SWARM LAND")
    for drone_id in DRONE_IDS:
        if drone_states.get(drone_id, {}).get('connected') and drone_states[drone_id]['flying_status'] == 'FLYING':
            take_off_land_individual(drone_id)
            sleep(0.1)
    root.after(6000, check_battery_all)

def calibrate_all():
    print("Command: SWARM CALIBRATE")
    for drone_id in DRONE_IDS:
        if drone_states.get(drone_id, {}).get('connected'):
            calibrate_individual(drone_id)
            sleep(0.05)
    root.after(1000, check_battery_all)
    
def check_battery_all():
    print("Command: SWARM BATTERY CHECK")
    for drone_id in DRONE_IDS:
        if drone_states.get(drone_id, {}).get('connected'):
            check_battery_individual(drone_id)
            sleep(0.05)

# ===================================================================
# ==                     MANUAL MOVEMENT                           ==
# ===================================================================

def start_move(drone_id, direction):
    state = drone_states[drone_id]
    if not state.get('connected') or state.get('flying_status') != "FLYING": return

    speeds = {"power": 35, "lift": 40, "turn": 50}
    if direction == 'forward': state['pitch_speed'] = speeds["power"]
    elif direction == 'backward': state['pitch_speed'] = -speeds["power"]
    elif direction == 'left': state['roll_speed'] = -speeds["power"]
    elif direction == 'right': state['roll_speed'] = speeds["power"]
    elif direction == 'up': state['throttle_speed'] = speeds["lift"]
    elif direction == 'down': state['throttle_speed'] = -speeds["lift"]
    elif direction == 'turn_left': state['yaw_speed'] = -speeds["turn"]
    elif direction == 'turn_right': state['yaw_speed'] = speeds["turn"]

    if not state.get('movement_job'):
        update_movement(drone_id)

def stop_move(drone_id, direction):
    state = drone_states[drone_id]
    if not state.get('connected'): return

    if direction in ['forward', 'backward']: state['pitch_speed'] = 0
    elif direction in ['left', 'right']: state['roll_speed'] = 0
    elif direction in ['up', 'down']: state['throttle_speed'] = 0
    elif direction in ['turn_left', 'turn_right']: state['yaw_speed'] = 0

    if all(v == 0 for v in [state['roll_speed'], state['pitch_speed'], state['yaw_speed'], state['throttle_speed']]):
        if state.get('movement_job'):
            root.after_cancel(state['movement_job'])
            state['movement_job'] = None
        if state['flying_status'] == "FLYING":
            drones[drone_id].sendControl(0, 0, 0, 0)

def update_movement(drone_id):
    state = drone_states[drone_id]
    if state.get('connected') and state.get('flying_status') == "FLYING":
        drones[drone_id].sendControl(
            state['roll_speed'], state['pitch_speed'], 
            state['yaw_speed'], state['throttle_speed']
        )
        state['movement_job'] = root.after(50, lambda: update_movement(drone_id))
    else:
        state['movement_job'] = None
        
def enable_movement_controls(drone_id, enabled):
    state = tk.NORMAL if enabled else tk.DISABLED
    for frame_name in ['pr_frame', 'yt_frame']:
        if frame_name in gui_elements.get(drone_id, {}):
            for widget in gui_elements[drone_id][frame_name].winfo_children():
                if isinstance(widget, ttk.Button):
                    widget.config(state=state)

# ===================================================================
# ==                           GUI SETUP                           ==
# ===================================================================

def on_closing():
    print("Closing application...")
    land_all()
    sleep(4)
    for drone_id in DRONE_IDS:
        if drone_states.get(drone_id, {}).get('connected'):
            disconnect_drone(drone_id)
    root.destroy()

root = tk.Tk()
root.title("Swarm Drone Control Panel")
root.protocol("WM_DELETE_WINDOW", on_closing)

style = ttk.Style()
style.theme_use('clam')
style.configure("TButton", padding=5)
style.configure("TLabel", background="white")
style.configure("TFrame", background="white")
style.configure("TLabelframe", padding=5, background="white")
style.configure("TLabelframe.Label", font=("Helvetica", 11, "bold"), background="white")

main_frame = ttk.Frame(root, padding=10)
main_frame.pack(fill="both", expand=True)

global_controls_frame = ttk.LabelFrame(main_frame, text="Global Controls", padding=10)
global_controls_frame.pack(pady=5, padx=5, fill="x")
ttk.Button(global_controls_frame, text="Take Off All", command=take_off_all).pack(side="left", padx=5, expand=True)
ttk.Button(global_controls_frame, text="Land All", command=land_all).pack(side="left", padx=5, expand=True)
ttk.Button(global_controls_frame, text="Calibrate All", command=calibrate_all).pack(side="left", padx=5, expand=True)
ttk.Button(global_controls_frame, text="Check Battery All", command=check_battery_all).pack(side="left", padx=5, expand=True)

drone_panels_frame = ttk.Frame(main_frame)
drone_panels_frame.pack(pady=5, padx=5, fill="both", expand=True)

gui_elements = {'D1': {}, 'D2': {}, 'D3': {}}

def create_movement_button(parent, text, direction, row, col, drone_id):
    button = ttk.Button(parent, text=text, width=8)
    button.grid(row=row, column=col, padx=5, pady=5, ipady=10)
    button.bind('<ButtonPress-1>', lambda event, d=direction, i=drone_id: start_move(i, d))
    button.bind('<ButtonRelease-1>', lambda event, d=direction, i=drone_id: stop_move(i, d))

for i, drone_id in enumerate(DRONE_IDS):
    # --- Data Structure Init ---
    drone_states[drone_id] = {
        'com_port_var': tk.StringVar(value=f'COM{6+i}'), 'connected': False, 
        'flying_status': 'LANDED', 'battery': 0, 'com_port': '',
        'roll_speed': 0, 'pitch_speed': 0, 'yaw_speed': 0, 'throttle_speed': 0,
        'movement_job': None
    }

    # --- Panel Frame ---
    activation_frame = ttk.LabelFrame(drone_panels_frame, text=f"Drone {i+1}", borderwidth=2, padding=5)
    activation_frame.pack(fill="x", pady=4, padx=4)
    gui_elements[drone_id]['activation_frame'] = activation_frame
    
    # --- Top Section ---
    top_frame = ttk.Frame(activation_frame, padding=5)
    top_frame.pack(fill="x")
    
    com_entry = ttk.Entry(top_frame, textvariable=drone_states[drone_id]['com_port_var'], width=10)
    com_entry.pack(side="left", padx=5)
    gui_elements[drone_id]['com_entry'] = com_entry
    
    connect_btn = ttk.Button(top_frame, text="Connect", command=lambda i=drone_id: connect_disconnect_command(i))
    connect_btn.pack(side="left", padx=5)
    gui_elements[drone_id]['connect_btn'] = connect_btn

    gui_elements[drone_id]['batt_var'] = tk.StringVar(value="Battery: N/A")
    gui_elements[drone_id]['status_var'] = tk.StringVar(value="Disconnected")
    ttk.Label(top_frame, textvariable=gui_elements[drone_id]['status_var']).pack(side="left", padx=5, expand=True, fill="x")
    ttk.Label(top_frame, textvariable=gui_elements[drone_id]['batt_var']).pack(side="left", padx=10)

    # --- Bottom Section (Initially Hidden) ---
    cmds_frame = ttk.Frame(activation_frame, padding=5)
    gui_elements[drone_id]['individual_cmds_frame'] = cmds_frame
    
    ind_cmds_group = ttk.Frame(cmds_frame)
    ind_cmds_group.pack(side="left", padx=10, anchor="n")
    
    takeoff_btn = ttk.Button(ind_cmds_group, text="Take Off", width=12, command=lambda i=drone_id: take_off_land_individual(i))
    takeoff_btn.pack(pady=4, fill="x")
    gui_elements[drone_id]['takeoff_btn'] = takeoff_btn

    ttk.Button(ind_cmds_group, text="Calibrate", width=12, command=lambda i=drone_id: calibrate_individual(i)).pack(pady=4, fill="x")
    ttk.Button(ind_cmds_group, text="Check Battery", width=12, command=lambda i=drone_id: check_battery_individual(i)).pack(pady=4, fill="x")
    
    move_frame = ttk.Frame(cmds_frame)
    move_frame.pack(side="left", padx=10)
    
    pr_frame = ttk.LabelFrame(move_frame, text="Pitch/Roll")
    pr_frame.pack(side="left", padx=5)
    gui_elements[drone_id]['pr_frame'] = pr_frame
    create_movement_button(pr_frame, "▲\n(Fwd)", 'forward', 0, 1, drone_id)
    create_movement_button(pr_frame, "◄\n(Left)", 'left', 1, 0, drone_id)
    create_movement_button(pr_frame, "►\n(Right)", 'right', 1, 2, drone_id)
    create_movement_button(pr_frame, "▼\n(Back)", 'backward', 2, 1, drone_id)

    yt_frame = ttk.LabelFrame(move_frame, text="Yaw/Throttle")
    yt_frame.pack(side="left", padx=5)
    gui_elements[drone_id]['yt_frame'] = yt_frame
    create_movement_button(yt_frame, "Up", 'up', 0, 1, drone_id)
    create_movement_button(yt_frame, "↰\n(Turn L)", 'turn_left', 1, 0, drone_id)
    create_movement_button(yt_frame, "↱\n(Turn R)", 'turn_right', 1, 2, drone_id)
    create_movement_button(yt_frame, "Down", 'down', 2, 1, drone_id)
    
    cmds_frame.pack_forget()
    enable_movement_controls(drone_id, False)

if __name__ == "__main__":
    root.mainloop()
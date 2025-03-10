import tkinter as tk
from tkinter import messagebox, ttk
from mcp2210_wrapper import MCP2210
import constants
import time
from collections import deque
import threading
from collections import deque
from Switchboard_18GHz import Switchboard_18GHz

mcp = MCP2210()
quanity = mcp.get_connected_device_count()

swb = Switchboard_18GHz()

Serial_no_list = []
for i in range (0, quanity, 1):
    handle = mcp.open_device_by_index(index = i)
    Serial_no = mcp.get_serial_number(handle)
    Serial_no_list.append(Serial_no)
    mcp.close_device(handle)
print(Serial_no_list)



def toggle_button_color(button):
    current_color = button.cget("bg")
    new_color = "red" if current_color == "green" else "green"
    button.config(bg=new_color)


def on_button_click(button, text):
    #toggle_button_color(button)
    if text == "mech_sw_1":
        swb.Mech_sw_1.toggle_state()
    if text == "mech_sw_2":
        swb.Mech_sw_2.toggle_state()
    if text == "mech_sw_3":
        swb.Mech_sw_3.toggle_state()
    if text == "mech_sw_4":
        swb.Mech_sw_4.toggle_state()
    if text == "mech_sw_5":
        swb.Mech_sw_5.toggle_state()          

def on_dropdown_select(event):
    selected_option = event.widget.get()
    messagebox.showinfo("Dropdown Selected", f"You selected: {selected_option}")


def on_slider_change(value, slider_name):
    """Handles the slider value change event."""
    print(f"{slider_name} changed to {value}")  # Debugging output
    
    # Example: if var_x controls a voltage on AD5726
    if "var_" in slider_name:
        channel = int(slider_name.split("_")[1])  # Extract channel number
        match channel:
            case 1:
                swb.AD5726_2.set_output_voltage(3, value)
            case 2:
                swb.AD5726_2.set_output_voltage(2, value)
            case 3:
                swb.AD5726_2.set_output_voltage(1, value)
            case 4:
                swb.AD5726_2.set_output_voltage(0, value)
            case 5:
                swb.AD5726_1.set_output_voltage(3, value)
            case 6:
                swb.AD5726_1.set_output_voltage(2, value)  
            case 7:
                swb.AD5726_1.set_output_voltage(1, value) 
            case 8:
                swb.AD5726_1.set_output_voltage(0, value)

def on_popup_button_click(action):
    if action == "Connect":
        Serial_no = dropdown_var.get()
        swb.connect(Serial_no)

    if action == "Disconnect":
        swb.CloseDevice()

    if action == "Reset":
        swb.reset_PCB()
    else:
        messagebox.showinfo("Action", f"You selected: {action}")


# Инициализация основного окна
root = tk.Tk()
root.title("Compact UI with Dropdown")
root.geometry("1000x600")

# Верхняя панель с dropdown и кнопками
top_frame = ttk.Frame(root)
top_frame.grid(row=0, column=0, columnspan=10, padx=10, pady=10, sticky="ew")

# Dropdown
dropdown_label = ttk.Label(top_frame, text="Dropdown:")
dropdown_label.grid(row=0, column=0, padx=5, pady=5)

dropdown_var = tk.StringVar()
dropdown = ttk.Combobox(top_frame, textvariable=dropdown_var, state="readonly", width=15)
dropdown['values'] = Serial_no_list  # Установите список значений
dropdown.current(0)  # Установите первый элемент по умолчанию
dropdown_var.set(dropdown['values'][0])  # Принудительно синхронизируем переменную
dropdown.grid(row=0, column=1, padx=5, pady=5)

print(f"Dropdown value: {dropdown_var.get()}")

# Кнопки Connect, Disconnect, Reset
btn_connect = tk.Button(top_frame, text="Connect", width=10, command=lambda: on_popup_button_click("Connect"))
btn_connect.grid(row=0, column=2, padx=5, pady=5)

btn_disconnect = tk.Button(top_frame, text="Disconnect", width=10, command=lambda: on_popup_button_click("Disconnect"))
btn_disconnect.grid(row=0, column=3, padx=5, pady=5)

btn_reset = tk.Button(top_frame, text="Reset", width=10, command=lambda: on_popup_button_click("Reset"))
btn_reset.grid(row=0, column=4, padx=5, pady=5)

# Кнопки "mech_sw_x"
for x in range(1, 6):
    button = tk.Button(root, text=f"mech_sw_{x}", bg="green", width=10, height=2)
    button.grid(row=x, column=0, padx=5, pady=5)
    button.config(command=lambda btn=button, x=x: on_button_click(btn, f"mech_sw_{x}"))

# Кнопки "sw_x"
for x in range(1, 13):
    button = tk.Button(root, text=f"sw_{x}", bg="green", width=10, height=2)
    button.grid(row=(x - 1) % 6 + 1, column=1 + (x - 1) // 6, padx=5, pady=5)
    button.config(command=lambda btn=button, x=x: on_button_click(btn, f"sw_{x}"))

# Кнопки "ttl_x"
for x in range(1, 3):
    button = tk.Button(root, text=f"ttl{x}", bg="green", width=10, height=2)
    button.grid(row=x, column=4, padx=5, pady=5)
    button.config(command=lambda btn=button, x=x: on_button_click(btn, f"ttl{x}"))

# Кнопка "S-param_SW"
btn_s_param = tk.Button(root, text="S-param_SW", bg="green", width=10, height=2)
btn_s_param.grid(row=3, column=4, padx=5, pady=5)
btn_s_param.config(command=lambda: on_button_click(btn_s_param, "S-param_SW"))

# Кнопки "IQ-ATT_x"
for x in range(1, 9):
    button = tk.Button(root, text=f"IQ-ATT_{x}", bg="green", width=10, height=2)
    button.grid(row=(x - 1) % 4 + 1, column=5 + (x - 1) // 4, padx=5, pady=5)
    button.config(command=lambda btn=button, x=x: on_button_click(btn, f"IQ-ATT_{x}"))

# "var_x" sliders
for x in range(1, 9):
    slider_label = f"var_{x}"
    tk.Label(root, text=slider_label).grid(row=x - 1, column=8, padx=5, pady=5, sticky=tk.W)
    
    slider = tk.Scale(root, from_=-1.1, to=1.1, resolution=0.01, orient=tk.HORIZONTAL, length=150,
                      command=lambda value, name=slider_label: on_slider_change(value, name))
    slider.grid(row=x - 1, column=9, padx=5, pady=5)

# Ползунки "Mech_att_x"
for x in range(1, 8):
    tk.Label(root, text=f"Mech_att_{x}").grid(row=x - 1, column=10, padx=5, pady=5, sticky=tk.W)
    slider = tk.Scale(root, from_=0, to=70, resolution=10, orient=tk.HORIZONTAL, length=150)
    slider.grid(row=x - 1, column=11, padx=5, pady=5)

root.mainloop()

import tkinter as tk
from tkinter import messagebox, ttk
from mcp2210_wrapper import MCP2210
import constants
import time
import matplotlib.pyplot as plt
from collections import deque
import threading
import matplotlib.pyplot as plt
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
    """
    Меняет цвет кнопки при нажатии.
    Если цвет зеленый, меняется на красный, и наоборот.
    """
    current_color = button.cget("bg")
    new_color = "red" if current_color == "green" else "green"
    button.config(bg=new_color)

def on_button_click(button, text):
    if "mech_sw" in text:
        messagebox.showinfo("Action", f"Executing action for {text}")
    elif "sw" in text:
        messagebox.showinfo("Action", f"Switch action for {text}")
        # Добавьте вашу функцию для sw кнопок здесь
    elif "ttl" in text:
        messagebox.showinfo("Action", f"TTL action for {text}")
        # Добавьте вашу функцию для ttl кнопок здесь
    elif "IQ-ATT" in text:
        messagebox.showinfo("Action", f"Adjusting IQ ATT for {text}")
        # Добавьте вашу функцию для IQ-ATT кнопок здесь
    elif "S-param_SW" in text:
        messagebox.showinfo("Action", "Executing S-parameter action")
        # Добавьте вашу функцию для S-param_SW здесь
    toggle_button_color(button)
    messagebox.showinfo("Button Clicked", f"You clicked: {text}")

def on_dropdown_select(event):
    """
    Обработчик выбора в выпадающем списке.
    """
    selected_option = event.widget.get()
    messagebox.showinfo("Dropdown Selected", f"You selected: {selected_option}")


def on_popup_button_click(action, swb):
    """
    Функция вызывается при нажатии кнопок Connect, Disconnect, Reset.
    """
    if action == "Connect":
        Serial_no = dropdown_var.get()
        swb.connect(Serial_no)

    if action == "Disconnect":
        swb.CloseDevice()

    if action == "Reset":
        swb.reset_PCB()
    else:
        messagebox.showinfo("Action", f"You selected: {action}")

# Создаем главное окно
root = tk.Tk()
root.title("Custom UI")
root.geometry("1400x700")  # Размер окна

# Создаем верхний фрейм для dropdown и кнопок
top_frame = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

# Добавляем выпадающий список
dropdown_label = tk.Label(top_frame, text="Dropdown:")
dropdown_label.pack(side=tk.LEFT, padx=5)

dropdown_var = tk.StringVar()
dropdown = ttk.Combobox(top_frame, textvariable=dropdown_var, state="readonly")
dropdown['values'] = Serial_no_list
dropdown.current(0)  # Устанавливаем первый элемент как выбранный по умолчанию

dropdown.bind("<<ComboboxSelected>>", on_dropdown_select)
dropdown.pack(side=tk.LEFT, padx=10)

# Добавляем кнопки Connect, Disconnect, Reset
btn_connect = tk.Button(top_frame, text="Connect", command=lambda: on_popup_button_click("Connect", swb))
btn_connect.pack(side=tk.LEFT, padx=10)

btn_disconnect = tk.Button(top_frame, text="Disconnect", command=lambda: on_popup_button_click("Disconnect", swb))
btn_disconnect.pack(side=tk.LEFT, padx=10)

btn_reset = tk.Button(top_frame, text="Reset", command=lambda: on_popup_button_click("Reset", swb))
btn_reset.pack(side=tk.LEFT, padx=10)

# Создаем фреймы для кнопок и ползунков
frame1 = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
frame1.pack(side=tk.LEFT, padx=20, pady=20)

frame2 = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
frame2.pack(side=tk.LEFT, padx=20, pady=20)

frame3 = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
frame3.pack(side=tk.LEFT, padx=20, pady=20)

frame4 = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
frame4.pack(side=tk.LEFT, padx=20, pady=20)

frame5 = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
frame5.pack(side=tk.LEFT, padx=20, pady=20)

frame6 = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
frame6.pack(side=tk.LEFT, padx=20, pady=20)

slider_frame_var = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
slider_frame_var.pack(side=tk.RIGHT, padx=20, pady=20)

slider_frame_mech = tk.Frame(root, relief=tk.GROOVE, borderwidth=2)
slider_frame_mech.pack(side=tk.RIGHT, padx=20, pady=20)

# Первый столбик с кнопками mech_sw_x
for x in range(1, 6):
    button = tk.Button(frame1, text=f"mech_sw_{x}", bg="green")
    button.config(command=lambda btn=button, x=x: on_button_click(btn, f"mech_sw_{x}"))
    button.pack(pady=5, padx=10, fill=tk.X)

# Второй столбик с кнопками sw_x
for x in range(1, 13):
    button = tk.Button(frame2, text=f"sw_{x}", bg="green")
    button.config(command=lambda btn=button, x=x: on_button_click(btn, f"sw_{x}"))
    button.pack(pady=5, padx=10, fill=tk.X)

# Третий столбик с кнопками ttlx
for x in range(1, 3):
    button = tk.Button(frame3, text=f"ttl{x}", bg="green")
    button.config(command=lambda btn=button, x=x: on_button_click(btn, f"ttl{x}"))
    button.pack(pady=5, padx=10, fill=tk.X)

# Четвертый столбик с кнопкой S-param_SW
btn_s_param = tk.Button(frame4, text="S-param_SW", bg="green", command=lambda: on_button_click(btn_s_param, "S-param_SW"))
btn_s_param.pack(pady=20, padx=10, fill=tk.X)

# Пятый столбик с кнопками IQ-ATT_x
for x in range(1, 9):
    button = tk.Button(frame5, text=f"IQ-ATT_{x}", bg="green")
    button.config(command=lambda btn=button, x=x: on_button_click(btn, f"IQ-ATT_{x}"))
    button.pack(pady=5, padx=10, fill=tk.X)

# Добавляем 8 ползунков var_x
for x in range(1, 9):
    tk.Label(slider_frame_var, text=f"var_{x}").pack(pady=5)
    slider = tk.Scale(slider_frame_var, from_=-1.1, to=1.1, resolution=0.01, orient=tk.HORIZONTAL)
    slider.set(0)  # Устанавливаем ползунок по центру
    slider.pack(pady=5, fill=tk.X)

# Добавляем 7 ползунков Mech_att_x
for x in range(1, 8):
    tk.Label(slider_frame_mech, text=f"Mech_att_{x}").pack(pady=5)
    slider = tk.Scale(slider_frame_mech, from_=0, to=70, resolution=10, orient=tk.HORIZONTAL)
    slider.set(35)  # Устанавливаем ползунок по центру
    slider.pack(pady=5, fill=tk.X)

# Запускаем главное окно
root.mainloop()

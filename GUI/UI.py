import tkinter as tk
from tkinter import messagebox, ttk

from instrumentation.PCBs.Switchboard_18GHz import Switchboard_18GHz

# DAC slider -> (DAC attribute on the switchboard, DAC channel)
SLIDER_DAC_CHANNELS = {
    1: ("AD5726_2", 3),
    2: ("AD5726_2", 2),
    3: ("AD5726_2", 1),
    4: ("AD5726_2", 0),
    5: ("AD5726_1", 3),
    6: ("AD5726_1", 2),
    7: ("AD5726_1", 1),
    8: ("AD5726_1", 0),
}


def list_serial_numbers(mcp):
    """Serial numbers of all connected MCP2210 devices."""
    serials = []
    for index in range(mcp.get_connected_device_count()):
        handle = mcp.open_device_by_index(index=index)
        try:
            serials.append(mcp.get_serial_number(handle))
        finally:
            mcp.close_device(handle)
    return serials


class SwitchboardApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("18GHz Switchboard")
        self.geometry("1000x600")
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.swb = Switchboard_18GHz()
        serials = list_serial_numbers(self.swb.mcp)
        print(serials)

        self._build_ui(serials)
        if not serials:
            messagebox.showwarning("No device", "No MCP2210 device found. Plug in the switchboard and restart.")

    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_ui(self, serials):
        # Top panel: device selection and Connect / Disconnect / Reset
        top_frame = ttk.Frame(self)
        top_frame.grid(row=0, column=0, columnspan=12, padx=10, pady=10, sticky="ew")

        ttk.Label(top_frame, text="Serial:").grid(row=0, column=0, padx=5, pady=5)
        self.serial_var = tk.StringVar(value=serials[0] if serials else "")
        dropdown = ttk.Combobox(top_frame, textvariable=self.serial_var, state="readonly", width=15)
        dropdown["values"] = serials
        dropdown.grid(row=0, column=1, padx=5, pady=5)

        for column, (text, action) in enumerate(
                [("Connect", self.on_connect), ("Disconnect", self.on_disconnect), ("Reset", self.on_reset)], start=2):
            tk.Button(top_frame, text=text, width=10, command=self._safe(action)).grid(row=0, column=column, padx=5, pady=5)

        self.status_var = tk.StringVar(value="Not connected")
        self.status_label = ttk.Label(top_frame, textvariable=self.status_var, foreground="red")
        self.status_label.grid(row=0, column=5, padx=10, pady=5)

        # Mechanical switches
        for x in range(1, 6):
            button = tk.Button(self, text=f"mech_sw_{x}", bg="green", width=10, height=2,
                               command=self._safe(lambda x=x: self.on_mech_switch(x)))
            button.grid(row=x, column=0, padx=5, pady=5)

        # Not wired to hardware yet: shown disabled
        for x in range(1, 13):
            self._placeholder_button(f"sw_{x}", row=(x - 1) % 6 + 1, column=1 + (x - 1) // 6)
        for x in range(1, 3):
            self._placeholder_button(f"ttl{x}", row=x, column=4)
        self._placeholder_button("S-param_SW", row=3, column=4)
        for x in range(1, 9):
            self._placeholder_button(f"IQ-ATT_{x}", row=(x - 1) % 4 + 1, column=5 + (x - 1) // 4)

        # DAC outputs
        for x in range(1, 9):
            tk.Label(self, text=f"var_{x}").grid(row=x, column=8, padx=5, pady=5, sticky=tk.W)
            slider = tk.Scale(self, from_=-1.1, to=1.1, resolution=0.01, orient=tk.HORIZONTAL, length=150,
                              command=self._safe(lambda value, x=x: self.on_slider_change(x, value)))
            slider.grid(row=x, column=9, padx=5, pady=5)

        # Mechanical attenuators, not wired to hardware yet
        for x in range(1, 8):
            tk.Label(self, text=f"Mech_att_{x}").grid(row=x, column=10, padx=5, pady=5, sticky=tk.W)
            slider = tk.Scale(self, from_=0, to=70, resolution=10, orient=tk.HORIZONTAL, length=150,
                              state="disabled")
            slider.grid(row=x, column=11, padx=5, pady=5)

    def _placeholder_button(self, text, row, column):
        button = tk.Button(self, text=text, bg="green", width=10, height=2, state="disabled")
        button.grid(row=row, column=column, padx=5, pady=5)

    def _safe(self, callback):
        """Wrap a Tk callback so errors show up in a dialog instead of only the console."""
        def wrapper(*args):
            try:
                callback(*args)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        return wrapper

    def _set_status(self):
        if self.swb.is_connected:
            self.status_var.set(f"Connected: {self.swb.serial_no}")
            self.status_label.configure(foreground="green")
        else:
            self.status_var.set("Not connected")
            self.status_label.configure(foreground="red")

    def _require_connection(self):
        if not self.swb.is_connected:
            messagebox.showwarning("Not connected", "Connect to the switchboard first.")
            return False
        return True

    # ------------------------------------------------------------------ #
    # Callbacks
    # ------------------------------------------------------------------ #
    def on_connect(self):
        serial = self.serial_var.get()
        if not serial:
            messagebox.showwarning("No device", "No MCP2210 device selected.")
            return
        try:
            self.swb.connect(serial)
        finally:
            self._set_status()

    def on_disconnect(self):
        self.swb.CloseDevice()
        self._set_status()

    def on_reset(self):
        if self._require_connection():
            self.swb.reset_PCB()

    def on_mech_switch(self, x):
        if self._require_connection():
            getattr(self.swb, f"Mech_sw_{x}").toggle_state()

    def on_slider_change(self, x, value):
        print(f"var_{x} changed to {value}")
        if not self.swb.is_connected:
            return  # sliders only move the DACs once connected
        dac_name, channel = SLIDER_DAC_CHANNELS[x]
        getattr(self.swb, dac_name).set_output_voltage(channel, value)

    def on_close(self):
        try:
            self.swb.CloseDevice()
        finally:
            self.destroy()


if __name__ == "__main__":
    SwitchboardApp().mainloop()

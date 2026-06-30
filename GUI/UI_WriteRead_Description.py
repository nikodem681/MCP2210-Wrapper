import os
import sys

# Make the project root importable so `instrumentation` resolves regardless of cwd.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import tkinter as tk
from tkinter import messagebox, ttk
from instrumentation.PCBs.mcp2210_wrapper import MCP2210


DEFAULT_VID = 0x4D8
DEFAULT_PID = 0xDE
 
 
class Mcp2210App(tk.Tk):
    def __init__(self):
        super().__init__()
 
        self.title("MCP2210 Configurator")
        self.geometry("800x600")
        self.resizable(False, False)
 
        self.mcp = None          # MCP2210 instance (DLL wrapper)
        self.handle = None       # Currently open device handle
 
        self._build_ui()
 
    # ------------------------------------------------------------------ #
    # UI construction
    # ------------------------------------------------------------------ #
    def _build_ui(self):
        pad = {"padx": 10, "pady": 6}
 
        # --- Connection frame ---
        conn_frame = ttk.LabelFrame(self, text="Connection")
        conn_frame.pack(fill="x", **pad)
 
        ttk.Label(conn_frame, text="VID (hex):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.vid_var = tk.StringVar(value=f"{DEFAULT_VID:04X}")
        ttk.Entry(conn_frame, textvariable=self.vid_var, width=10).grid(row=0, column=1, padx=5, pady=5)
 
        ttk.Label(conn_frame, text="PID (hex):").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.pid_var = tk.StringVar(value=f"{DEFAULT_PID:04X}")
        ttk.Entry(conn_frame, textvariable=self.pid_var, width=10).grid(row=0, column=3, padx=5, pady=5)
 
        ttk.Button(conn_frame, text="Count Devices", command=self.on_count_devices)\
            .grid(row=1, column=0, columnspan=2, sticky="we", padx=5, pady=5)
 
        self.count_var = tk.StringVar(value="Devices found: -")
        ttk.Label(conn_frame, textvariable=self.count_var).grid(row=1, column=2, columnspan=2, sticky="w", padx=5, pady=5)
 
        ttk.Button(conn_frame, text="Open First Device", command=self.on_open_device)\
            .grid(row=2, column=0, columnspan=2, sticky="we", padx=5, pady=5)
 
        self.status_var = tk.StringVar(value="Not connected")
        ttk.Label(conn_frame, textvariable=self.status_var, foreground="blue")\
            .grid(row=2, column=2, columnspan=2, sticky="w", padx=5, pady=5)
 
        # --- Read frame ---
        read_frame = ttk.LabelFrame(self, text="Device Strings (read)")
        read_frame.pack(fill="x", **pad)
 
        ttk.Label(read_frame, text="Manufacturer:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.mfg_read_var = tk.StringVar(value="-")
        ttk.Label(read_frame, textvariable=self.mfg_read_var, relief="sunken", width=35)\
            .grid(row=0, column=1, padx=5, pady=5, sticky="w")
 
        ttk.Label(read_frame, text="Product:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.prod_read_var = tk.StringVar(value="-")
        ttk.Label(read_frame, textvariable=self.prod_read_var, relief="sunken", width=35)\
            .grid(row=1, column=1, padx=5, pady=5, sticky="w")
 
        ttk.Button(read_frame, text="Refresh Strings", command=self.on_read_strings)\
            .grid(row=2, column=0, columnspan=2, sticky="we", padx=5, pady=8)
 
        # --- Write frame ---
        write_frame = ttk.LabelFrame(self, text="Device Strings (write to NVRAM)")
        write_frame.pack(fill="x", **pad)
 
        ttk.Label(write_frame, text="New Manufacturer (max 29 chars):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.mfg_write_var = tk.StringVar()
        ttk.Entry(write_frame, textvariable=self.mfg_write_var, width=35)\
            .grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(write_frame, text="Write", command=self.on_write_manufacturer)\
            .grid(row=0, column=2, padx=5, pady=5)
 
        ttk.Label(write_frame, text="New Product (max 29 chars):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.prod_write_var = tk.StringVar()
        ttk.Entry(write_frame, textvariable=self.prod_write_var, width=35)\
            .grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(write_frame, text="Write", command=self.on_write_product)\
            .grid(row=1, column=2, padx=5, pady=5)
 
        ttk.Label(
            write_frame,
            text="Note: writes persist to NVRAM and survive power cycles.",
            foreground="gray"
        ).grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=(2, 8))
 
        # --- Log frame ---
        log_frame = ttk.LabelFrame(self, text="Log")
        log_frame.pack(fill="both", expand=True, **pad)
 
        self.log_text = tk.Text(log_frame, height=8, state="disabled", wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
 
    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
 
    def _get_vid_pid(self):
        try:
            vid = int(self.vid_var.get(), 16)
            pid = int(self.pid_var.get(), 16)
            return vid, pid
        except ValueError:
            messagebox.showerror("Invalid input", "VID/PID must be valid hexadecimal numbers.")
            return None, None
 
    def _ensure_mcp(self):
        if self.mcp is None:
            try:
                self.mcp = MCP2210()
                self._log("DLL loaded successfully.")
            except Exception as e:
                messagebox.showerror("DLL Error", f"Could not load MCP2210 DLL:\n{e}")
                self.mcp = None
        return self.mcp
 
    def _ensure_open_device(self):
        if self.handle is None:
            messagebox.showwarning("No device", "Please open a device first.")
            return False
        return True
 
    # ------------------------------------------------------------------ #
    # Button callbacks
    # ------------------------------------------------------------------ #
    def on_count_devices(self):
        vid, pid = self._get_vid_pid()
        if vid is None:
            return
        mcp = self._ensure_mcp()
        if mcp is None:
            return
        try:
            count = mcp.get_connected_device_count(vid=vid, pid=pid)
            self.count_var.set(f"Devices found: {count}")
            self._log(f"Found {count} device(s) for VID=0x{vid:04X}, PID=0x{pid:04X}.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self._log(f"Error counting devices: {e}")
 
    def on_open_device(self):
        vid, pid = self._get_vid_pid()
        if vid is None:
            return
        mcp = self._ensure_mcp()
        if mcp is None:
            return
        try:
            self.handle = mcp.open_device_by_index(vid=vid, pid=pid, index=0)
            self.status_var.set("Connected")
            self._log("Device opened successfully (index 0).")
            # Auto-refresh strings on open
            self.on_read_strings()
        except Exception as e:
            self.status_var.set("Not connected")
            messagebox.showerror("Error opening device", str(e))
            self._log(f"Error opening device: {e}")
 
    def on_read_strings(self):
        if not self._ensure_open_device():
            return
        try:
            mfg = self.mcp.get_manufacturer_string(self.handle)
            self.mfg_read_var.set(mfg if mfg else "(empty)")
        except Exception as e:
            self.mfg_read_var.set("Error")
            self._log(f"Error reading manufacturer string: {e}")
 
        try:
            prod = self.mcp.get_product_string(self.handle)
            self.prod_read_var.set(prod if prod else "(empty)")
        except Exception as e:
            self.prod_read_var.set("Error")
            self._log(f"Error reading product string: {e}")
 
    def on_write_manufacturer(self):
        if not self._ensure_open_device():
            return
        text = self.mfg_write_var.get()
        if not text:
            messagebox.showwarning("Empty value", "Please enter a manufacturer string to write.")
            return
        try:
            self.mcp.set_manufacturer_string(self.handle, text)
            self._log(f"Manufacturer string written: '{text}'")
            self.on_read_strings()
        except Exception as e:
            messagebox.showerror("Write failed", str(e))
            self._log(f"Error writing manufacturer string: {e}")
 
    def on_write_product(self):
        if not self._ensure_open_device():
            return
        text = self.prod_write_var.get()
        if not text:
            messagebox.showwarning("Empty value", "Please enter a product string to write.")
            return
        try:
            self.mcp.set_product_string(self.handle, text)
            self._log(f"Product string written: '{text}'")
            self.on_read_strings()
        except Exception as e:
            messagebox.showerror("Write failed", str(e))
            self._log(f"Error writing product string: {e}")
 
    def on_close(self):
        if self.mcp is not None and self.handle is not None:
            try:
                self.mcp.close_device(self.handle)
            except Exception:
                pass
        self.destroy()
 
 
if __name__ == "__main__":
    app = Mcp2210App()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
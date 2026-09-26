import ctypes
import os

# Default DLL location: resolved relative to this file so it works from any cwd.
_DEFAULT_DLL_PATH = os.path.join(os.path.dirname(__file__), "MCP2210", "mcp2210_dll_um_x64.dll")

# Error codes from mcp2210_dll_um.h
_ERROR_DESCRIPTIONS = {
    0: "E_SUCCESS: Successful API call",
    -1: "E_ERR_UNKOWN_ERROR: Unexpected error, likely caused by communication issues",
    -2: "E_ERR_INVALID_PARAMETER: Invalid API parameter",
    -3: "E_ERR_BUFFER_TOO_SMALL: Buffer provided is too small",
    -10: "E_ERR_NULL: NULL pointer parameter",
    -20: "E_ERR_MALLOC: Memory allocation error",
    -30: "E_ERR_INVALID_HANDLE_VALUE: Invalid device handle usage",
    -100: "E_ERR_FIND_DEV: Error while searching for devices",
    -101: "E_ERR_NO_SUCH_INDEX: Invalid device index",
    -103: "E_ERR_DEVICE_NOT_FOUND: Device not found with the given VID:PID",
    -104: "E_ERR_INTERNAL_BUFFER_TOO_SMALL: Internal DLL buffer is too small",
    -105: "E_ERR_OPEN_DEVICE_ERROR: Failed to open device",
    -106: "E_ERR_CONNECTION_ALREADY_OPENED: Device is already open",
    -107: "E_ERR_CLOSE_FAILED: Failed to close the connection",
    -108: "E_ERR_NO_SUCH_SERIALNR: No device found with the given serial number",
    -110: "E_ERR_HID_RW_TIMEOUT: HID file operation timeout, device may be disconnected",
    -111: "E_ERR_HID_RW_FILEIO: HID file operation unknown error, device may be disconnected",
    -200: "E_ERR_CMD_FAILED: Unexpected device reply to command",
    -201: "E_ERR_CMD_ECHO: Command code mismatch",
    -202: "E_ERR_SUBCMD_ECHO: Subcommand code mismatch",
    -203: "E_ERR_SPI_CFG_ABORT: SPI configuration change refused, transfer in progress",
    -204: "E_ERR_SPI_EXTERN_MASTER: SPI bus is owned by an external master",
    -205: "E_ERR_SPI_TIMEOUT: SPI transfer attempts exceeded",
    -206: "E_ERR_SPI_RX_INCOMPLETE: SPI received bytes less than configured",
    -207: "E_ERR_SPI_XFER_ONGOING: SPI transfer still in progress",
    -300: "E_ERR_BLOCKED_ACCESS: Device settings are password protected or permanently locked",
    -301: "E_ERR_EEPROM_WRITE_FAIL: EEPROM write failure",
    -350: "E_ERR_NVRAM_LOCKED: NVRAM is permanently locked",
    -351: "E_ERR_WRONG_PASSWD: Password mismatch, less than 5 attempts",
    -352: "E_ERR_ACCESS_DENIED: Password mismatch, exceeded 5 attempts, access denied until reset",
    -353: "E_ERR_NVRAM_PROTECTED: NVRAM access control protection already enabled",
    -354: "E_ERR_PASSWD_CHANGE: Password change not allowed without enabling access control",
    -400: "E_ERR_STRING_DESCRIPTOR: Invalid NVRAM string descriptor",
    -401: "E_ERR_STRING_TOO_LARGE: Input string size exceeds the limit",
}

_INVALID_HANDLE = ctypes.c_void_p(-1).value

MCP2210_GPIO_NR = 9  # number of GPIO pins


class MCP2210:
    def __init__(self, dll_path=None):
        """
        Initialize and load the DLL.
        """
        if dll_path is None:
            dll_path = _DEFAULT_DLL_PATH
        self.dll = ctypes.WinDLL(dll_path)
        self._setup_functions()
        version = self.get_library_version()
        print("DLL version: " + str(version))

    def _setup_functions(self):
        """
        Set up the DLL function signatures, following mcp2210_dll_um.h.

        Every function gets explicit argtypes: without them ctypes passes Python
        ints as 32-bit C ints, which truncates 64-bit device handles.
        """
        c_void_p = ctypes.c_void_p
        c_ubyte = ctypes.c_ubyte
        c_ushort = ctypes.c_ushort
        c_uint = ctypes.c_uint
        c_int = ctypes.c_int
        c_wchar_p = ctypes.c_wchar_p
        P = ctypes.POINTER

        signatures = {
            # Library / device access
            "Mcp2210_GetLibraryVersion": (c_int, [c_wchar_p]),
            "Mcp2210_GetLastError": (c_int, []),
            "Mcp2210_GetConnectedDevCount": (c_int, [c_ushort, c_ushort]),
            "Mcp2210_OpenByIndex": (c_void_p, [c_ushort, c_ushort, c_uint, c_wchar_p, P(ctypes.c_ulong)]),
            "Mcp2210_OpenBySN": (c_void_p, [c_ushort, c_ushort, c_wchar_p, c_wchar_p, P(ctypes.c_ulong)]),
            "Mcp2210_Close": (c_int, [c_void_p]),
            "Mcp2210_Reset": (c_int, [c_void_p]),

            # USB settings (NVRAM)
            "Mcp2210_GetUsbKeyParams": (c_int, [c_void_p, P(c_ushort), P(c_ushort), P(c_ubyte), P(c_ubyte), P(c_ushort)]),
            "Mcp2210_SetUsbKeyParams": (c_int, [c_void_p, c_ushort, c_ushort, c_ubyte, c_ubyte, c_ushort]),
            "Mcp2210_GetManufacturerString": (c_int, [c_void_p, c_wchar_p]),
            "Mcp2210_SetManufacturerString": (c_int, [c_void_p, c_wchar_p]),
            "Mcp2210_GetProductString": (c_int, [c_void_p, c_wchar_p]),
            "Mcp2210_SetProductString": (c_int, [c_void_p, c_wchar_p]),
            "Mcp2210_GetSerialNumber": (c_int, [c_void_p, c_wchar_p]),

            # GPIO
            "Mcp2210_GetGpioPinDir": (c_int, [c_void_p, P(c_uint)]),
            "Mcp2210_SetGpioPinDir": (c_int, [c_void_p, c_uint]),
            "Mcp2210_GetGpioPinVal": (c_int, [c_void_p, P(c_uint)]),
            "Mcp2210_SetGpioPinVal": (c_int, [c_void_p, c_uint, P(c_uint)]),
            "Mcp2210_GetGpioConfig": (c_int, [c_void_p, c_ubyte, P(c_ubyte), P(c_uint), P(c_uint),
                                              P(c_ubyte), P(c_ubyte), P(c_ubyte)]),
            "Mcp2210_SetGpioConfig": (c_int, [c_void_p, c_ubyte, P(c_ubyte), c_uint, c_uint,
                                              c_ubyte, c_ubyte, c_ubyte]),

            # SPI
            "Mcp2210_GetSpiConfig": (c_int, [c_void_p, c_ubyte, P(c_uint), P(c_uint), P(c_uint), P(c_uint),
                                             P(c_uint), P(c_uint), P(c_uint), P(c_ubyte)]),
            "Mcp2210_SetSpiConfig": (c_int, [c_void_p, c_ubyte, P(c_uint), P(c_uint), P(c_uint), P(c_uint),
                                             P(c_uint), P(c_uint), P(c_uint), P(c_ubyte)]),
            "Mcp2210_xferSpiData": (c_int, [c_void_p, P(c_ubyte), P(c_ubyte), P(c_uint), P(c_uint), c_uint]),
            "Mcp2210_xferSpiDataEx": (c_int, [c_void_p, P(c_ubyte), P(c_ubyte), P(c_uint), P(c_uint), c_uint,
                                              P(c_uint), P(c_uint), P(c_uint), P(c_uint), P(c_uint), P(c_ubyte)]),
        }
        for name, (restype, argtypes) in signatures.items():
            func = getattr(self.dll, name)
            func.restype = restype
            func.argtypes = argtypes

    @staticmethod
    def _is_invalid_handle(handle):
        return handle is None or handle == _INVALID_HANDLE

    def _open_error(self):
        error_code = self.dll.Mcp2210_GetLastError()
        return RuntimeError(f"Error opening the device: {self.describe_mcp2210_error(error_code)}")

    def get_library_version(self):
        """
        Get the library version.
        """
        buffer = ctypes.create_unicode_buffer(64)
        result = self.dll.Mcp2210_GetLibraryVersion(buffer)
        if result < 0:
            raise RuntimeError(f"Error getting the DLL version: {self.describe_mcp2210_error(result)}")
        return buffer.value

    def get_connected_device_count(self, vid=0x4D8, pid=0xDE):
        """
        Get the number of connected MCP2210 devices by VID and PID.

        Args:
            vid (int): Vendor ID (e.g., 0x4D8 for Microchip).
            pid (int): Product ID (e.g., 0xDE for MCP2210).

        Returns:
            int: Number of connected devices.

        Raises:
            RuntimeError: If the function call fails.
        """
        device_count = self.dll.Mcp2210_GetConnectedDevCount(vid, pid)
        if device_count < 0:
            raise RuntimeError(f"Mcp2210_GetConnectedDevCount failed: {self.describe_mcp2210_error(device_count)}")
        return device_count

    def open_device_by_sn(self, serial_no, vid=0x4D8, pid=0xDE):
        """
        Open an MCP2210 device by serial number.

        Args:
            serial_no (str): Serial number of the device.
            vid (int): Vendor ID of the device.
            pid (int): Product ID of the device.

        Returns:
            int: Device handle.

        Raises:
            RuntimeError: If the device could not be opened.
        """
        dev_path_size = ctypes.c_ulong(256)
        dev_path_buffer = ctypes.create_unicode_buffer(dev_path_size.value)
        handle = self.dll.Mcp2210_OpenBySN(vid, pid, serial_no, dev_path_buffer, ctypes.byref(dev_path_size))
        if self._is_invalid_handle(handle):
            raise self._open_error()
        return handle

    def open_device_by_index(self, vid=0x4D8, pid=0xDE, index=0):
        """
        Open an MCP2210 device by index.

        Args:
            vid (int): Vendor ID of the device.
            pid (int): Product ID of the device.
            index (int): Index of the device among the connected ones.

        Returns:
            int: Device handle.

        Raises:
            RuntimeError: If the device could not be opened.
        """
        dev_path_size = ctypes.c_ulong(256)
        dev_path_buffer = ctypes.create_unicode_buffer(dev_path_size.value)
        handle = self.dll.Mcp2210_OpenByIndex(vid, pid, index, dev_path_buffer, ctypes.byref(dev_path_size))
        if self._is_invalid_handle(handle):
            raise self._open_error()
        return handle

    def close_device(self, handle):
        """
        Close the connection to an MCP2210 device.

        Args:
            handle (int): Device handle obtained when opening.

        Raises:
            RuntimeError: If the connection could not be closed.
        """
        result = self.dll.Mcp2210_Close(handle)
        if result != 0:
            raise RuntimeError(f"Error closing the device: {self.describe_mcp2210_error(result)}")

    def reset_device(self, handle):
        """
        Reset the MCP2210 device.

        Args:
            handle (int): Device handle.

        Raises:
            ValueError: If the handle is invalid.
            RuntimeError: If the device reset failed.
        """
        if self._is_invalid_handle(handle):
            raise ValueError("Invalid device handle.")
        result = self.dll.Mcp2210_Reset(handle)
        if result != 0:
            raise RuntimeError(f"Error resetting the device: {self.describe_mcp2210_error(result)}")
        print("Device reset successfully.")

    def get_serial_number(self, handle):
        """
        Get the serial number of an MCP2210 device.

        Args:
            handle (int): Device handle.

        Returns:
            str: Device serial number.

        Raises:
            RuntimeError: If the function returns a negative code.
        """
        serial_str = ctypes.create_unicode_buffer(64)
        result = self.dll.Mcp2210_GetSerialNumber(handle, serial_str)
        if result < 0:
            raise RuntimeError(f"Error getting the serial number: {self.describe_mcp2210_error(result)}")
        return serial_str.value

    # ------------------------------------------------------------------ #
    # USB string descriptors (NVRAM): manufacturer / product strings.    #
    # Max length is 29 UTF-16 chars (MCP2210_DESCRIPTOR_STR_MAX_LEN).     #
    # ------------------------------------------------------------------ #
    DESCRIPTOR_STR_MAX_LEN = 29

    def get_manufacturer_string(self, handle):
        """Read the manufacturer string descriptor from NVRAM."""
        buf = ctypes.create_unicode_buffer(self.DESCRIPTOR_STR_MAX_LEN + 1)
        result = self.dll.Mcp2210_GetManufacturerString(handle, buf)
        if result < 0:
            raise RuntimeError(f"GetManufacturerString failed: {self.describe_mcp2210_error(result)}")
        return buf.value

    def set_manufacturer_string(self, handle, text):
        """Write the manufacturer string descriptor to NVRAM (persists)."""
        if len(text) > self.DESCRIPTOR_STR_MAX_LEN:
            raise ValueError(f"String too long ({len(text)} > {self.DESCRIPTOR_STR_MAX_LEN}).")
        buf = ctypes.create_unicode_buffer(text, self.DESCRIPTOR_STR_MAX_LEN + 1)
        result = self.dll.Mcp2210_SetManufacturerString(handle, buf)
        if result < 0:
            raise RuntimeError(f"SetManufacturerString failed: {self.describe_mcp2210_error(result)}")
        return result

    def get_product_string(self, handle):
        """Read the product string descriptor from NVRAM."""
        buf = ctypes.create_unicode_buffer(self.DESCRIPTOR_STR_MAX_LEN + 1)
        result = self.dll.Mcp2210_GetProductString(handle, buf)
        if result < 0:
            raise RuntimeError(f"GetProductString failed: {self.describe_mcp2210_error(result)}")
        return buf.value

    def set_product_string(self, handle, text):
        """Write the product string descriptor to NVRAM (persists)."""
        if len(text) > self.DESCRIPTOR_STR_MAX_LEN:
            raise ValueError(f"String too long ({len(text)} > {self.DESCRIPTOR_STR_MAX_LEN}).")
        buf = ctypes.create_unicode_buffer(text, self.DESCRIPTOR_STR_MAX_LEN + 1)
        result = self.dll.Mcp2210_SetProductString(handle, buf)
        if result < 0:
            raise RuntimeError(f"SetProductString failed: {self.describe_mcp2210_error(result)}")
        return result

    def get_usb_key_params(self, handle):
        """Read USB key params (VID/PID/power source/remote wakeup/current) from NVRAM."""
        vid = ctypes.c_ushort()
        pid = ctypes.c_ushort()
        pwr_src = ctypes.c_ubyte()
        rmt_wkup = ctypes.c_ubyte()
        current_ld = ctypes.c_ushort()
        result = self.dll.Mcp2210_GetUsbKeyParams(
            handle, ctypes.byref(vid), ctypes.byref(pid),
            ctypes.byref(pwr_src), ctypes.byref(rmt_wkup), ctypes.byref(current_ld)
        )
        if result < 0:
            raise RuntimeError(f"GetUsbKeyParams failed: {self.describe_mcp2210_error(result)}")
        return {
            "vid": vid.value,
            "pid": pid.value,
            "power_source": pwr_src.value,
            "remote_wakeup": rmt_wkup.value,
            "current_load": current_ld.value,
        }

    def set_usb_key_params(self, handle, vid, pid, power_source, remote_wakeup, current_load):
        """Write USB key params to NVRAM (persists). Changing VID/PID changes how the
        device enumerates — handle with care."""
        result = self.dll.Mcp2210_SetUsbKeyParams(handle, vid, pid, power_source, remote_wakeup, current_load)
        if result < 0:
            raise RuntimeError(f"SetUsbKeyParams failed: {self.describe_mcp2210_error(result)}")
        return result

    def get_gpio_pin_dir(self, handle):
        """
        Get the GPIO pin direction of the device.

        Args:
            handle (int): Device handle.

        Returns:
            list: List of 9 values (0 - output, 1 - input) for each GPIO.

        Raises:
            RuntimeError: If the function returns an error.
        """
        gpio_dir = ctypes.c_uint()
        result = self.dll.Mcp2210_GetGpioPinDir(handle, ctypes.byref(gpio_dir))
        if result != 0:
            raise RuntimeError(f"Error getting the GPIO pin direction: {self.describe_mcp2210_error(result)}")
        return [(gpio_dir.value >> i) & 1 for i in range(MCP2210_GPIO_NR)]

    def set_gpio_pin_dir(self, handle, gpioSetDir):
        """
        Set the GPIO pin direction of the MCP2210 device.

        Args:
            handle (int): Device handle.
            gpioSetDir (int): New GPIO pin direction bitmap (1 - input, 0 - output).

        Raises:
            ValueError: If the DLL function call fails.
        """
        result = self.dll.Mcp2210_SetGpioPinDir(handle, gpioSetDir)
        if result != 0:
            raise ValueError(f"Error setting GPIO pin direction: {self.describe_mcp2210_error(result)}")

    def get_gpio_pin_val(self, handle):
        """
        Retrieve the current GPIO values of the MCP2210 device.

        Args:
            handle (int): Device handle.

        Returns:
            tuple: (result_code, gpio_pin_val); result_code is always 0 on return.

        Raises:
            ValueError: If the DLL function call fails.
        """
        gpio_pin_val = ctypes.c_uint()
        result = self.dll.Mcp2210_GetGpioPinVal(handle, ctypes.byref(gpio_pin_val))
        if result != 0:
            raise ValueError(f"Error getting GPIO pin values: {self.describe_mcp2210_error(result)}")
        return result, gpio_pin_val.value

    def set_gpio_pin_val(self, handle, gpio_set_val):
        """
        Set the GPIO output values.

        Args:
            handle (int): Device handle.
            gpio_set_val (int): New GPIO values.

        Returns:
            tuple: (result_code, gpio_pin_val), where gpio_pin_val is the GPIO
            value reported back by the device.

        Raises:
            ValueError: If the handle is invalid.
            RuntimeError: If the call fails.
        """
        if self._is_invalid_handle(handle):
            raise ValueError("Invalid handle provided")
        gpio_pin_val = ctypes.c_uint()
        result_code = self.dll.Mcp2210_SetGpioPinVal(handle, gpio_set_val, ctypes.byref(gpio_pin_val))
        if result_code < 0:
            raise RuntimeError(f"Error in Mcp2210_SetGpioPinVal: {self.describe_mcp2210_error(result_code)}")
        return result_code, gpio_pin_val.value

    def get_gpio_config(self, handle, cfgSelector):
        """
        Retrieve the GPIO configuration of the MCP2210 device.

        Args:
            handle (int): Device handle.
            cfgSelector (int): Current (volatile memory) or power-up (NVRAM) configuration.

        Returns:
            dict: A dictionary containing the following keys:
                - "gpio_pin_des" (list[int]): GPIO pin designation array.
                - "dflt_gpio_output" (int): Default GPIO output values.
                - "dflt_gpio_dir" (int): Default GPIO direction.
                - "rmt_wkup_en" (int): Remote wake-up enable/disable status.
                - "int_pin_md" (int): Interrupt pin mode.
                - "spi_bus_rel_en" (int): SPI bus release enable/disable status.

        Raises:
            ValueError: If the DLL function call fails.
        """
        gpio_pin_des = (ctypes.c_ubyte * MCP2210_GPIO_NR)()
        dflt_gpio_output = ctypes.c_uint()
        dflt_gpio_dir = ctypes.c_uint()
        rmt_wkup_en = ctypes.c_ubyte()
        int_pin_md = ctypes.c_ubyte()
        spi_bus_rel_en = ctypes.c_ubyte()

        result = self.dll.Mcp2210_GetGpioConfig(
            handle,
            cfgSelector,
            gpio_pin_des,
            ctypes.byref(dflt_gpio_output),
            ctypes.byref(dflt_gpio_dir),
            ctypes.byref(rmt_wkup_en),
            ctypes.byref(int_pin_md),
            ctypes.byref(spi_bus_rel_en)
        )
        if result != 0:
            raise ValueError(f"Error getting GPIO config: {self.describe_mcp2210_error(result)}")

        return {
            "gpio_pin_des": list(gpio_pin_des),
            "dflt_gpio_output": dflt_gpio_output.value,
            "dflt_gpio_dir": dflt_gpio_dir.value,
            "rmt_wkup_en": rmt_wkup_en.value,
            "int_pin_md": int_pin_md.value,
            "spi_bus_rel_en": spi_bus_rel_en.value
        }

    def Set_Gpio_Config(self, handle, cfgSelector, pGpioPinDes, dfltGpioOutput, dfltGpioDir, rmtWkupEn, intPinMd,
                        spiBusRelEn):
        """
        Set the current GPIO configuration or the power-up default (NVRAM) GPIO configuration.

        Args:
            handle (int): Device handle.
            cfgSelector (int): Selection for current or power-up chip settings.
            pGpioPinDes (list): GPIO pin designation array (9 entries).
            dfltGpioOutput (dict | int): GPIO output values, as {"GPIO0": 0/1, ...} or a bitmap.
            dfltGpioDir (dict | int): GPIO directions, as {"GPIO0": 0/1, ...} or a bitmap.
            rmtWkupEn (int): Remote wake-up setting.
            intPinMd (int): Interrupt pulse count mode.
            spiBusRelEn (int): SPI bus release option.

        Returns:
            int: 0 on success.

        Raises:
            ValueError: If pGpioPinDes does not have 9 entries.
            RuntimeError: If the DLL call fails.
        """
        if len(pGpioPinDes) != MCP2210_GPIO_NR:
            raise ValueError(f"pGpioPinDes must have {MCP2210_GPIO_NR} entries, got {len(pGpioPinDes)}.")
        if isinstance(dfltGpioOutput, dict):
            dfltGpioOutput = self.dictionary_to_binary_number(dfltGpioOutput)
        if isinstance(dfltGpioDir, dict):
            dfltGpioDir = self.dictionary_to_binary_number(dfltGpioDir)

        pin_des = (ctypes.c_ubyte * MCP2210_GPIO_NR)(*pGpioPinDes)
        result = self.dll.Mcp2210_SetGpioConfig(
            handle, cfgSelector, pin_des, dfltGpioOutput, dfltGpioDir, rmtWkupEn, intPinMd, spiBusRelEn
        )
        if result != 0:
            raise RuntimeError(f"Error setting GPIO config: {self.describe_mcp2210_error(result)}")
        return result

    @staticmethod
    def describe_mcp2210_error(error_code):
        """
        Provide a description for the given MCP2210 DLL error code.

        Args:
            error_code (int): The error code returned by the MCP2210 DLL.

        Returns:
            str: A description of the error.
        """
        return _ERROR_DESCRIPTIONS.get(error_code, f"Unknown error (code: {error_code})")

    def get_spi_config(self, handle, cfgSelector):
        """
        Get the SPI settings for the current (VM) configuration or the default (NVRAM) configuration.

        Args:
            handle (int): Device handle.
            cfgSelector (int): MCP2210_VM_CONFIG (current) or MCP2210_NVRAM_CONFIG (power-up).

        Returns:
            dict: Dictionary containing the SPI settings:
                - baudRate: Transfer rate.
                - idleCsVal: Chip Select value when idle.
                - activeCsVal: Chip Select value when active.
                - csToDataDly: Delay from Chip Select to data transmission.
                - dataToCsDly: Delay from the last byte to Chip Select.
                - dataToDataDly: Delay between bytes.
                - txferSize: Transfer size in bytes.
                - spiMd: SPI mode.

        Raises:
            ValueError: If the DLL function call fails.
        """
        baudRate = ctypes.c_uint()
        idleCsVal = ctypes.c_uint()
        activeCsVal = ctypes.c_uint()
        csToDataDly = ctypes.c_uint()
        dataToCsDly = ctypes.c_uint()
        dataToDataDly = ctypes.c_uint()
        txferSize = ctypes.c_uint()
        spiMd = ctypes.c_ubyte()

        result = self.dll.Mcp2210_GetSpiConfig(
            handle,
            cfgSelector,
            ctypes.byref(baudRate),
            ctypes.byref(idleCsVal),
            ctypes.byref(activeCsVal),
            ctypes.byref(csToDataDly),
            ctypes.byref(dataToCsDly),
            ctypes.byref(dataToDataDly),
            ctypes.byref(txferSize),
            ctypes.byref(spiMd)
        )
        if result != 0:
            raise ValueError(f"Error getting SPI configuration: {self.describe_mcp2210_error(result)}")

        return {
            "baudRate": baudRate.value,
            "idleCsVal": idleCsVal.value,
            "activeCsVal": activeCsVal.value,
            "csToDataDly": csToDataDly.value,
            "dataToCsDly": dataToCsDly.value,
            "dataToDataDly": dataToDataDly.value,
            "txferSize": txferSize.value,
            "spiMd": spiMd.value
        }

    def set_spi_config(self, handle, cfgSelector, baudRate, idleCsVal, activeCsVal,
                       csToDataDly, dataToCsDly, dataToDataDly, txferSize, spiMd):
        """
        Configure the SPI settings for either the current (VM) configuration
        or the default startup (NVRAM) configuration.

        Args:
            handle (int): Device handle.
            cfgSelector (int): MCP2210_VM_CONFIG (current) or MCP2210_NVRAM_CONFIG (power-up).
            baudRate (int): SPI clock speed in bits per second.
            idleCsVal (int): Chip Select (CS) values when idle, one bit per GPIO.
            activeCsVal (int): Chip Select (CS) values when active, one bit per GPIO.
            csToDataDly (int): Delay from CS assertion to first data byte (in 100 µs units).
            dataToCsDly (int): Delay from last data byte to CS deassertion (in 100 µs units).
            dataToDataDly (int): Delay between consecutive data bytes (in 100 µs units).
            txferSize (int): Number of bytes per SPI transaction.
            spiMd (int): SPI Mode (0-3):
                        - 0 = SPI Mode 0 (CPOL=0, CPHA=0)
                        - 1 = SPI Mode 1 (CPOL=0, CPHA=1)
                        - 2 = SPI Mode 2 (CPOL=1, CPHA=0)
                        - 3 = SPI Mode 3 (CPOL=1, CPHA=1)

        Raises:
            ValueError: If the DLL function returns an error.
        """
        baudRate_c = ctypes.c_uint(baudRate)
        idleCsVal_c = ctypes.c_uint(idleCsVal)
        activeCsVal_c = ctypes.c_uint(activeCsVal)
        csToDataDly_c = ctypes.c_uint(csToDataDly)
        dataToCsDly_c = ctypes.c_uint(dataToCsDly)
        dataToDataDly_c = ctypes.c_uint(dataToDataDly)
        txferSize_c = ctypes.c_uint(txferSize)
        spiMd_c = ctypes.c_ubyte(spiMd)

        result = self.dll.Mcp2210_SetSpiConfig(
            handle,
            cfgSelector,
            ctypes.byref(baudRate_c),
            ctypes.byref(idleCsVal_c),
            ctypes.byref(activeCsVal_c),
            ctypes.byref(csToDataDly_c),
            ctypes.byref(dataToCsDly_c),
            ctypes.byref(dataToDataDly_c),
            ctypes.byref(txferSize_c),
            ctypes.byref(spiMd_c)
        )
        if result != 0:
            raise ValueError(f"Failed to set SPI configuration: {self.describe_mcp2210_error(result)}")

        print("SPI configuration successfully applied.")

    def xfer_spi_data(self, handle, data_tx, baud_rate, transfer_size, cs_mask):
        """
        Wrapper for the Mcp2210_xferSpiData function.

        Args:
            handle (int): Device handle.
            data_tx (list[int]): Data to transmit over SPI.
            baud_rate (int): SPI transfer rate (in Hz). If 0, the current rate is used.
            transfer_size (int): Number of bytes per transfer. If 0, no transfer is performed, only a configuration change.
            cs_mask (int): Bit mask of GPIO pins used for Chip Select.

        Returns:
            dict: SPI transfer results:
                - "data_rx" (list[int]): Received data.
                - "baud_rate" (int): Accepted SPI transfer rate.
                - "transfer_size" (int): Actual transfer size.

        Raises:
            ValueError: If data_tx is longer than transfer_size, or the DLL call fails.
        """
        if len(data_tx) > transfer_size:
            raise ValueError(f"data_tx has {len(data_tx)} bytes, more than transfer_size={transfer_size}.")
        data_tx_buffer = (ctypes.c_ubyte * transfer_size)(*data_tx)
        data_rx_buffer = (ctypes.c_ubyte * transfer_size)()
        c_baud_rate = ctypes.c_uint(baud_rate)
        c_transfer_size = ctypes.c_uint(transfer_size)

        result = self.dll.Mcp2210_xferSpiData(
            handle,
            data_tx_buffer,
            data_rx_buffer,
            ctypes.byref(c_baud_rate),
            ctypes.byref(c_transfer_size),
            cs_mask
        )
        if result != 0:
            raise ValueError(f"SPI transfer error: {self.describe_mcp2210_error(result)}")

        return {
            "data_rx": list(data_rx_buffer),
            "baud_rate": c_baud_rate.value,
            "transfer_size": c_transfer_size.value
        }

    def mcp2210_xfer_spi_data_ex(self, handle, data_tx, baud_rate=10000000, txfer_size=None, csmask=4,
                                 idle_cs_val=1, active_cs_val=0, cs_to_data_dly=0,
                                 data_to_cs_dly=0, data_to_data_dly=0, spi_mode=0):
        """
        Configure and perform an SPI data transfer with the MCP2210 device.

        :param handle: Device handle.
        :param data_tx: Data to transmit (list of ints or bytes).
        :param baud_rate: SPI transfer rate (int).
        :param txfer_size: Number of bytes to transfer; defaults to len(data_tx).
        :param csmask: Chip-select bit mask (int).
        :param idle_cs_val: Chip-select value when idle (int).
        :param active_cs_val: Active chip-select value (int).
        :param cs_to_data_dly: Delay from CS assertion to data start (int).
        :param data_to_cs_dly: Delay from the last byte to CS deassertion (int).
        :param data_to_data_dly: Delay between bytes (int).
        :param spi_mode: SPI mode (MCP2210_SPI_MODE0-3).
        :return: Tuple (return code, received data).
        """
        if txfer_size is None:
            txfer_size = len(data_tx)
        buffer_size = max(len(data_tx), txfer_size)
        pdata_tx = (ctypes.c_ubyte * buffer_size)(*data_tx)
        pdata_rx = (ctypes.c_ubyte * buffer_size)()

        baud_rate_c = ctypes.c_uint(baud_rate)
        txfer_size_c = ctypes.c_uint(txfer_size)
        idle_cs_val_c = ctypes.c_uint(idle_cs_val)
        active_cs_val_c = ctypes.c_uint(active_cs_val)
        cs_to_data_dly_c = ctypes.c_uint(cs_to_data_dly)
        data_to_cs_dly_c = ctypes.c_uint(data_to_cs_dly)
        data_to_data_dly_c = ctypes.c_uint(data_to_data_dly)
        spi_mode_c = ctypes.c_ubyte(spi_mode)

        ret = self.dll.Mcp2210_xferSpiDataEx(
            handle,
            pdata_tx,
            pdata_rx,
            ctypes.byref(baud_rate_c),
            ctypes.byref(txfer_size_c),
            csmask,
            ctypes.byref(idle_cs_val_c),
            ctypes.byref(active_cs_val_c),
            ctypes.byref(cs_to_data_dly_c),
            ctypes.byref(data_to_cs_dly_c),
            ctypes.byref(data_to_data_dly_c),
            ctypes.byref(spi_mode_c)
        )
        return ret, list(pdata_rx)

    @staticmethod
    def dictionary_to_binary_number(gpio_dict):
        """Convert {"GPIO0": bit, ..., "GPIO8": bit} into a bitmap (GPIO0 = bit 0)."""
        value = 0
        for key, bit in gpio_dict.items():
            pin = int(key[4:])
            if int(bit) not in (0, 1):
                raise ValueError(f"{key} must be 0 or 1, got {bit}.")
            value |= int(bit) << pin
        return value

    @staticmethod
    def decode_temperature(result):
        """Decode a 13-bit two's complement temperature reading (0.0625 °C/LSB, TC77-style)."""
        raw_data = result['data_rx']
        raw_data = (raw_data[0] << 8) | raw_data[1]
        # Drop the 3 least significant bits
        temperature_raw = raw_data >> 3
        # Sign bit is bit 12
        if temperature_raw & 0x1000:
            temperature_raw -= 0x2000
        return temperature_raw * 0.0625

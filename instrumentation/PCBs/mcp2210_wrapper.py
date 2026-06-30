import ctypes
import os
from . import constants

#Used constants

# Default DLL location: resolved relative to this file so it works from any cwd.
_DEFAULT_DLL_PATH = os.path.join(os.path.dirname(__file__), "MCP2210", "mcp2210_dll_um_x64.dll")

class MCP2210:
    def __init__(self, dll_path=None):
        """
        Initialize and load the DLL.
        """
        if dll_path is None:
            dll_path = _DEFAULT_DLL_PATH
        self.dll = ctypes.WinDLL(dll_path)
        version = self.get_library_version()
        print("DLL version: " + str(version))
        self._setup_functions()

    def _setup_functions(self):
        """
        Set up the DLL function signatures.
        """
        self.dll.Mcp2210_SetGpioPinVal.argtypes = [
            ctypes.c_void_p,        # Pointer to the device handle
            ctypes.c_uint,          # GPIO value
            ctypes.POINTER(ctypes.c_uint)  # Pointer for the returned GPIO value
        ]
        self.dll.Mcp2210_SetGpioPinVal.restype = ctypes.c_int  # Result code


        # Configure Mcp2210_GetConnectedDevCount
        self.dll.Mcp2210_GetConnectedDevCount.argtypes = [ctypes.c_ushort, ctypes.c_ushort]
        self.dll.Mcp2210_GetConnectedDevCount.restype = ctypes.c_int

        # Configure Mcp2210_GetSerialNumber
        self.dll.Mcp2210_GetSerialNumber.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        self.dll.Mcp2210_GetSerialNumber.restype = ctypes.c_int

        # Configure Mcp2210_OpenByIndex
        self.dll.Mcp2210_OpenByIndex.argtypes = [
            ctypes.c_ushort,  # vid
            ctypes.c_ushort,  # pid
            ctypes.c_uint,  # index
            ctypes.c_wchar_p,  # devPath
            ctypes.POINTER(ctypes.c_ulong)  # devPathsize
        ]
        self.dll.Mcp2210_OpenByIndex.restype = ctypes.c_void_p

        # Configure Mcp2210_Close
        self.dll.Mcp2210_Close.argtypes = [ctypes.c_void_p]  # Takes handle
        self.dll.Mcp2210_Close.restype = ctypes.c_int        # Returns int

        # Configure Mcp2210_OpenBySN
        self.dll.Mcp2210_OpenBySN.argtypes = [
            ctypes.c_ushort,        # vid
            ctypes.c_ushort,        # pid
            ctypes.c_wchar_p,       # serialNo
            ctypes.c_wchar_p        # devPath
        ]
        self.dll.Mcp2210_OpenBySN.restype = ctypes.c_void_p  # Returns the device handle (IntPtr in C#)

        # Configure Mcp2210_GetGpioPinDir
        self.dll.Mcp2210_GetGpioPinDir.argtypes = [
            ctypes.c_void_p,                # handle
            ctypes.POINTER(ctypes.c_uint)  # pgpioDir
        ]
        self.dll.Mcp2210_GetGpioPinDir.restype = ctypes.c_int  # Returns result code

        # Configure Mcp2210_SetGpioPinDir
        self.dll.Mcp2210_SetGpioPinDir.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint     # gpioDir
        ]
        self.dll.Mcp2210_SetGpioPinDir.restype = ctypes.c_int  # Returns result code

        # Configure Mcp2210_GetGpioPinVal
        self.dll.Mcp2210_GetGpioPinVal.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(ctypes.c_uint)  # pGPIOVal
        ]
        self.dll.Mcp2210_GetGpioPinVal.restype = ctypes.c_int  # Returns result code

        # Configure Mcp2210_SetGpioConfig
        self.dll.Mcp2210_SetGpioConfig.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_ubyte,  # cfgSelector
            ctypes.POINTER(ctypes.c_ubyte),  # pGpioPinDes (pointer to array)
            ctypes.c_uint,  # dfltGpioOutput
            ctypes.c_uint,  # dfltGpioDir
            ctypes.c_ubyte,  # rmtWkupEn
            ctypes.c_ubyte,  # intPinMd
            ctypes.c_ubyte  # spiBusRelEn
        ]
        self.dll.Mcp2210_SetGpioConfig.restype = ctypes.c_int  # Returns result code

        # Configure Mcp2210_Reset
        self.dll.Mcp2210_Reset.argtypes = [ctypes.c_void_p]  # handle
        self.dll.Mcp2210_Reset.restype = ctypes.c_int  # Returns result code

        # Configure Mcp2210_GetGpioConfig
        self.dll.Mcp2210_GetGpioConfig.argtypes = [
            ctypes.c_void_p,                        # void* handle
            ctypes.c_ubyte,                         # unsigned char cfgSelector
            ctypes.POINTER(ctypes.c_ubyte),         # unsigned char* pGpioPinDes
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pdfltGpioOutput
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pdfltGpioDir
            ctypes.POINTER(ctypes.c_ubyte),         # unsigned char* prmtWkupEn
            ctypes.POINTER(ctypes.c_ubyte),         # unsigned char* pintPinMd
            ctypes.POINTER(ctypes.c_ubyte)          # unsigned char* pspiBusRelEn
        ]
        self.dll.Mcp2210_GetGpioConfig.restype = ctypes.c_int  # Return type is int

        ################################################################################################################
        # Temporary settings start
        # Set up the function signature
        self.dll.Mcp2210_GetGpioConfig.argtypes = [
            ctypes.c_void_p,                        # void* handle
            ctypes.c_ubyte,                         # unsigned char cfgSelector
            ctypes.POINTER(ctypes.c_ubyte),         # unsigned char* pGpioPinDes
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pdfltGpioOutput
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pdfltGpioDir
            ctypes.POINTER(ctypes.c_ubyte),         # unsigned char* prmtWkupEn
            ctypes.POINTER(ctypes.c_ubyte),         # unsigned char* pintPinMd
            ctypes.POINTER(ctypes.c_ubyte)          # unsigned char* pspiBusRelEn
        ]
        self.dll.Mcp2210_GetGpioConfig.restype = ctypes.c_int  # Return type is int

        self.dll.Mcp2210_SetGpioPinDir.argtypes = [
            ctypes.c_void_p,                        # void* handle
            ctypes.c_uint                           # unsigned int gpioSetDir
        ]
        self.dll.Mcp2210_SetGpioPinDir.restype = ctypes.c_int  # Return type is int

        self.dll.Mcp2210_GetGpioPinVal.argtypes = [
            ctypes.c_void_p,                        # void* handle
            ctypes.POINTER(ctypes.c_uint)           # unsigned int* pgpioPinVal
        ]
        self.dll.Mcp2210_GetGpioPinVal.restype = ctypes.c_int  # Return type is int

        self.dll.Mcp2210_SetGpioConfig.argtypes = [
            ctypes.c_void_p,                        # void* handle
            ctypes.c_ubyte,                         # unsigned char cfgSelector
            ctypes.POINTER(ctypes.c_ubyte),         # unsigned char* pGpioPinDes
            ctypes.c_uint,                          # unsigned int dfltGpioOutput
            ctypes.c_uint,                          # unsigned int dfltGpioDir
            ctypes.c_ubyte,                         # unsigned char rmtWkupEn
            ctypes.c_ubyte,                         # unsigned char intPinMd
            ctypes.c_ubyte                          # unsigned char spiBusRelEn
        ]
        self.dll.Mcp2210_SetGpioConfig.restype = ctypes.c_int

        self.dll.Mcp2210_SetSpiConfig.argtypes = [
            ctypes.c_void_p,                        # void* handle (Device handle)
            ctypes.c_ubyte,                         # unsigned char cfgSelector (VM or NVRAM config)
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pbaudRate (SPI clock speed)
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pidleCsVal (CS idle value)
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pactiveCsVal (CS active value)
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pCsToDataDly (CS to first data delay)
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pdataToCsDly (Last data byte to CS delay)
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* pdataToDataDly (Inter-byte delay)
            ctypes.POINTER(ctypes.c_uint),          # unsigned int* ptxferSize (Number of bytes per SPI transfer)
            ctypes.POINTER(ctypes.c_ubyte)          # unsigned char* pspiMd (SPI mode selection)
        ]

        # USB string descriptors (stored in NVRAM)
        self.dll.Mcp2210_GetManufacturerString.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        self.dll.Mcp2210_GetManufacturerString.restype = ctypes.c_int
        self.dll.Mcp2210_SetManufacturerString.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        self.dll.Mcp2210_SetManufacturerString.restype = ctypes.c_int
        self.dll.Mcp2210_GetProductString.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        self.dll.Mcp2210_GetProductString.restype = ctypes.c_int
        self.dll.Mcp2210_SetProductString.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        self.dll.Mcp2210_SetProductString.restype = ctypes.c_int

        # USB key params (VID/PID/power source/remote wakeup/current, stored in NVRAM)
        self.dll.Mcp2210_GetUsbKeyParams.argtypes = [
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ushort),   # vid
            ctypes.POINTER(ctypes.c_ushort),   # pid
            ctypes.POINTER(ctypes.c_ubyte),    # power source
            ctypes.POINTER(ctypes.c_ubyte),    # remote wakeup
            ctypes.POINTER(ctypes.c_ushort)    # current load
        ]
        self.dll.Mcp2210_GetUsbKeyParams.restype = ctypes.c_int
        self.dll.Mcp2210_SetUsbKeyParams.argtypes = [
            ctypes.c_void_p,
            ctypes.c_ushort, ctypes.c_ushort,
            ctypes.c_ubyte, ctypes.c_ubyte, ctypes.c_ushort
        ]
        self.dll.Mcp2210_SetUsbKeyParams.restype = ctypes.c_int

        ################################################################################################################
        # Temporary settings end

    def get_library_version(self):
        """
        Get the library version.
        """
        buffer = ctypes.create_unicode_buffer(64)
        result = self.dll.Mcp2210_GetLibraryVersion(buffer)
        if result < 0:
            raise RuntimeError(f"Error getting the DLL version. Error code: {result}")
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

        # Call the DLL function
        device_count = self.dll.Mcp2210_GetConnectedDevCount(vid, pid)

        # Check the result
        if device_count < 0:
            raise RuntimeError(f"Error calling Mcp2210_GetConnectedDevCount. Error code: {device_count}")

        return device_count

    def open_device_by_sn(self, serial_no, vid=0x4D8, pid=0xDE):
        """
        Open an MCP2210 device by serial number.

        Args:
            vid (int): Vendor ID of the device.
            pid (int): Product ID of the device.
            serial_no (str): Serial number of the device.

        Returns:
            tuple: Device handle and device path (str).

        Raises:
            RuntimeError: If the device could not be opened.
        """
        # Buffer for the device path
        dev_path_buffer = ctypes.create_unicode_buffer(256)  # Maximum path length is 256 characters

        # Call the DLL function
        handle = self.dll.Mcp2210_OpenBySN(
            ctypes.c_ushort(vid),
            ctypes.c_ushort(pid),
            serial_no,
            dev_path_buffer
        )

        # Check the result
        if handle is None or handle == ctypes.c_void_p(-1).value:
            error_code = self.dll.Mcp2210_GetLastError()  # Get the last error code
            raise RuntimeError(f"Error opening the device. Error code: {error_code}")

        # Return the device handle and path
        return handle

    def get_serial_number(self, handle):
        """
        Get the serial number of an MCP2210 device.

        Args:
            handle (ctypes.c_void_p): Device handle.

        Returns:
            str: Device serial number.

        Raises:
            RuntimeError: If the function returns a negative code.
        """
        # Create a buffer for the serial number
        serial_str = ctypes.create_unicode_buffer(64)  # Buffer for a string up to 64 characters

        # Call the DLL function
        result = self.dll.Mcp2210_GetSerialNumber(handle, serial_str)

        # Check the result
        if result < 0:
            raise RuntimeError(f"Error getting the serial number. Error code: {result}")

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
        result = self.dll.Mcp2210_SetUsbKeyParams(
            handle, ctypes.c_ushort(vid), ctypes.c_ushort(pid),
            ctypes.c_ubyte(power_source), ctypes.c_ubyte(remote_wakeup),
            ctypes.c_ushort(current_load)
        )
        if result < 0:
            raise RuntimeError(f"SetUsbKeyParams failed: {self.describe_mcp2210_error(result)}")
        return result

    def open_device_by_index(self, vid=0x4D8, pid=0xDE, index=0):
        """
        Open an MCP2210 device by index.

        Args:
            vid: VID of the device
            pid: PID of the device
            index (int): Index of the device among the connected ones.

        Returns:
            tuple: Device handle and device path (str).

        Raises:
            RuntimeError: If the device could not be opened.
        """
        # Buffer for the device path
        dev_path_buffer_size = ctypes.c_ulong(256)  # Device path size
        dev_path_buffer = ctypes.create_unicode_buffer(dev_path_buffer_size.value)  # Buffer for the string

        # Call the DLL function
        handle = self.dll.Mcp2210_OpenByIndex(
            ctypes.c_ushort(vid),
            ctypes.c_ushort(pid),
            ctypes.c_uint(index),
            dev_path_buffer,
            ctypes.byref(dev_path_buffer_size)
        )

        # Check the result
        if handle is None or handle == ctypes.c_void_p(-1).value:
            error_code = self.dll.Mcp2210_GetLastError()  # Get the last error code
            raise RuntimeError(f"Error opening the device. Error code: {error_code}")

        # Return the device handle and path
        return handle

    def close_device(self, handle):
        """
        Close the connection to an MCP2210 device.

        Args:
            handle (ctypes.c_void_p): Device handle obtained when opening.

        Returns:
            None

        Raises:
            RuntimeError: If the connection could not be closed.
        """
        result = self.dll.Mcp2210_Close(handle)
        if result != 0:
            raise RuntimeError(f"Error closing the device. Error code: {result}")

    def get_gpio_pin_dir(self, handle):
        """
        Get the GPIO pin direction of the device.

        Args:
            handle (ctypes.c_void_p): Device handle.

        Returns:
            list: List of 9 values (0 - input, 1 - output) for each GPIO.

        Raises:
            RuntimeError: If the function returns an error.
        """
        # Variable to hold the result (pin directions)
        gpio_dir = ctypes.c_uint()

        # Call the DLL function
        result = self.dll.Mcp2210_GetGpioPinDir(handle, ctypes.byref(gpio_dir))

        # Check the result
        if result != 0:
            raise RuntimeError(f"Error getting the GPIO pin direction. Error code: {result}")

        # Convert the bit value into a list of directions
        gpio_directions = [(gpio_dir.value >> i) & 1 for i in range(9)]

        return gpio_directions

    def set_gpio_pin_dir(self, handle, gpioSetDir):
        """
        Sets the GPIO pin direction of the MCP2210 device.

        Args:
            handle (int): A handle to the MCP2210 device.
            gpioSetDir (int): New GPIO pin direction configuration.

        Returns:
            None

        Raises:
            ValueError: If the DLL function call fails (non-zero return value).
        """
        # Call the DLL function
        result = self.dll.Mcp2210_SetGpioPinDir(
            ctypes.c_void_p(handle),
            ctypes.c_uint(gpioSetDir)
        )

        if result != 0:
            raise ValueError(f"Error setting GPIO pin direction: {result}")

    def get_gpio_config(self, handle, cfgSelector):
        """
        Retrieves the GPIO configuration of the MCP2210 device.

        Args:
            handle (int): A handle to the MCP2210 device.
            cfgSelector (int): Selector for current (volatile memory) or power-up (NVRAM) configuration.

        Returns:
            dict: A dictionary containing the following keys:
                - "gpio_pin_des" (list[int]): GPIO pin designation array.
                - "dflt_gpio_output" (int): Default GPIO output values.
                - "dflt_gpio_dir" (int): Default GPIO direction.
                - "rmt_wkup_en" (int): Remote wake-up enable/disable status.
                - "int_pin_md" (int): Interrupt pin mode.
                - "spi_bus_rel_en" (int): SPI bus release enable/disable status.

        Raises:
            ValueError: If the DLL function call fails (non-zero return value).
        """
        # Prepare the output variables
        gpio_pin_des = (ctypes.c_ubyte * 9)()  # Assuming MCP2210_GPIO_NR is 9
        dflt_gpio_output = ctypes.c_uint()
        dflt_gpio_dir = ctypes.c_uint()
        rmt_wkup_en = ctypes.c_ubyte()
        int_pin_md = ctypes.c_ubyte()
        spi_bus_rel_en = ctypes.c_ubyte()

        # Call the DLL function
        result = self.dll.Mcp2210_GetGpioConfig(
            ctypes.c_void_p(handle),
            ctypes.c_ubyte(cfgSelector),
            gpio_pin_des,
            ctypes.byref(dflt_gpio_output),
            ctypes.byref(dflt_gpio_dir),
            ctypes.byref(rmt_wkup_en),
            ctypes.byref(int_pin_md),
            ctypes.byref(spi_bus_rel_en)
        )

        if result != 0:
            raise ValueError(f"Error getting GPIO config: {result}")

        # Return the output values as a dictionary
        return {
            "gpio_pin_des": list(gpio_pin_des),
            "dflt_gpio_output": dflt_gpio_output.value,
            "dflt_gpio_dir": dflt_gpio_dir.value,
            "rmt_wkup_en": rmt_wkup_en.value,
            "int_pin_md": int_pin_md.value,
            "spi_bus_rel_en": spi_bus_rel_en.value
        }
        # Convert into a readable format

    def Set_Gpio_Config(self, handle, cfgSelector, pGpioPinDes, dfltGpioOutput, dfltGpioDir, rmtWkupEn, intPinMd,
                              spiBusRelEn):
        """
        Set the current GPIO configuration or the power-up default (NVRAM) GPIO configuration.

        Parameters:
        handle (object): The pointer to the device handle. Cannot be NULL.
        cfgSelector (int): Selection for current or power-up chip settings.
        pGpioPinDes (list): GPIO Pin Designation array. Cannot be NULL.
        dfltGpioOutput (int): GPIO pin output values.
        dfltGpioDir (int): GPIO pin direction.
        rmtWkupEn (int): Remote wake-up setting.
        intPinMd (int): Interrupt pulse count mode.
        spiBusRelEn (int): SPI Bus Release option.

        Returns:
        int: 0 for success or a negative error code.
        """
        dfltGpioOutput = self.dictionary_to_binary_number(dfltGpioOutput)
        dfltGpioDir = self.dictionary_to_binary_number(dfltGpioDir)

        # Prepare ctypes arguments
        c_handle = ctypes.c_void_p(handle)
        c_cfgSelector = ctypes.c_ubyte(cfgSelector)
        c_pGpioPinDes = (ctypes.c_ubyte * len(pGpioPinDes))(*pGpioPinDes)
        c_dfltGpioOutput = ctypes.c_uint(dfltGpioOutput)
        c_dfltGpioDir = ctypes.c_uint(dfltGpioDir)
        c_rmtWkupEn = ctypes.c_ubyte(rmtWkupEn)
        c_intPinMd = ctypes.c_ubyte(intPinMd)
        c_spiBusRelEn = ctypes.c_ubyte(spiBusRelEn)

        # Call the DLL function
        try:
            result = self.dll.Mcp2210_SetGpioConfig(
                c_handle,
                c_cfgSelector,
                c_pGpioPinDes,
                c_dfltGpioOutput,
                c_dfltGpioDir,
                c_rmtWkupEn,
                c_intPinMd,
                c_spiBusRelEn
            )
            return result
        except Exception as e:
            print(f"Error calling DLL function: {e}")
            return -1  # E_ERR_UNKOWN_ERROR

    def reset_device(self, handle):
        """
        Reset the MCP2210 device.

        Args:
            handle (ctypes.c_void_p): Device handle.

        Returns:
            None

        Raises:
            RuntimeError: If the device reset failed.
        """
        if not handle or handle == ctypes.c_void_p(-1).value:
            raise ValueError("Invalid device handle.")

        # Call the reset function
        result = self.dll.Mcp2210_Reset(handle)

        # Check the result
        if result != 0:
            error_buffer = ctypes.create_unicode_buffer(256)
            self.dll.Mcp2210_GetLastErrorText(error_buffer, 256)
            raise RuntimeError(f"Error resetting the device. Error code: {result}, Description: {error_buffer.value}")

        print("Device reset successfully.")


    def set_gpio_pin_val(self, handle, gpio_set_val):
        """
        Wrapper for the Mcp2210_SetGpioPinVal function.

        Args:
            handle (ctypes.c_void_p): Pointer to the device.
            gpio_set_val (int): New GPIO values.

        Returns:
            tuple: (result_code, gpio_pin_val), where:
                - result_code (int): Result code (0 - success, negative - errors).
                - gpio_pin_val (int): Current GPIO value returned by the function.

        Raises:
            ValueError: If handle is None.
            RuntimeError: If the call result is negative (error).
        """
        if handle is None or handle == ctypes.c_void_p(-1).value:
            raise ValueError("Invalid handle provided")

        # Buffer for the returned GPIO pin values
        gpio_pin_val = ctypes.c_uint()

        # Call the DLL function
        result_code = self.dll.Mcp2210_SetGpioPinVal(
            ctypes.c_void_p(handle),
            ctypes.c_uint(gpio_set_val),
            ctypes.byref(gpio_pin_val)
        )

        # Handle the result
        if result_code < 0:
            raise RuntimeError(f"Error in Mcp2210_SetGpioPinVal: code {result_code}")

        return result_code, gpio_pin_val.value


    def describe_mcp2210_error(self, error_code):
        """
        Provides a description for the given MCP2210 DLL error code.

        Args:
            error_code (int): The error code returned by the MCP2210 DLL.

        Returns:
            str: A description of the error.
        """
        error_descriptions = {
            0: "E_SUCCESS: Successful API call",
            -1: "E_ERR_UNKOWN_ERROR: Unexpected error, likely caused by communication issues",
            -2: "E_ERR_INVALID_PARAMETER: Invalid API parameter",
            -3: "E_ERR_BUFFER_TOO_SMALL: Buffer provided is too small",
            -10: "E_ERR_NULL: NULL pointer parameter",
            -20: "E_ERR_MALLOC: Memory allocation error",
            -30: "E_ERR_INVALID_HANDLE_VALUE: Invalid device handle usage",
            -101: "E_ERR_NO_SUCH_INDEX: Invalid device index",
            -103: "E_ERR_DEVICE_NOT_FOUND: Device not found with the given VID:PID",
            -105: "E_ERR_OPEN_DEVICE_ERROR: Failed to open device",
            -106: "E_ERR_CONNECTION_ALREADY_OPENED: Device is already open",
            -107: "E_ERR_CLOSE_FAILED: Failed to close the connection",
            -108: "E_ERR_NO_SUCH_SERIALNR: No device found with the given serial number",
            -110: "E_ERR_HID_RW_TIMEOUT: HID file operation timeout, device may be disconnected",
            -111: "E_ERR_HID_RW_FILEIO: HID file operation unknown error, device may be disconnected",
            -200: "E_ERR_CMD_FAILED: Unexpected device reply to command",
            -201: "E_ERR_CMD_ECHO: Command code mismatch",
            -203: "E_ERR_SPI_CFG_ABORT: SPI configuration change refused",
            -204: "E_ERR_SPI_EXTERN_MASTER: SPI bus is owned by an external master",
            -205: "E_ERR_SPI_TIMEOUT: SPI transfer attempts exceeded",
            -206: "E_ERR_SPI_RX_INCOMPLETE: SPI received bytes less than configured",
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
        return error_descriptions.get(error_code, f"Unknown error (code: {error_code})")

        ################################################################################################################
        # Temporary settings start

    def get_gpio_config(self, handle, cfgSelector):
        """
        Retrieves the GPIO configuration of the MCP2210 device.

        Args:
            handle (int): A handle to the MCP2210 device.
            cfgSelector (int): Selector for current (volatile memory) or power-up (NVRAM) configuration.

        Returns:
            dict: A dictionary containing the following keys:
                - "gpio_pin_des" (list[int]): GPIO pin designation array.
                - "dflt_gpio_output" (int): Default GPIO output values.
                - "dflt_gpio_dir" (int): Default GPIO direction.
                - "rmt_wkup_en" (int): Remote wake-up enable/disable status.
                - "int_pin_md" (int): Interrupt pin mode.
                - "spi_bus_rel_en" (int): SPI bus release enable/disable status.

        Raises:
            ValueError: If the DLL function call fails (non-zero return value).
        """
        # Prepare the output variables
        gpio_pin_des = (ctypes.c_ubyte * 9)()  # Assuming MCP2210_GPIO_NR is 9
        dflt_gpio_output = ctypes.c_uint()
        dflt_gpio_dir = ctypes.c_uint()
        rmt_wkup_en = ctypes.c_ubyte()
        int_pin_md = ctypes.c_ubyte()
        spi_bus_rel_en = ctypes.c_ubyte()

        # Call the DLL function
        result = self.dll.Mcp2210_GetGpioConfig(
            ctypes.c_void_p(handle),
            ctypes.c_ubyte(cfgSelector),
            gpio_pin_des,
            ctypes.byref(dflt_gpio_output),
            ctypes.byref(dflt_gpio_dir),
            ctypes.byref(rmt_wkup_en),
            ctypes.byref(int_pin_md),
            ctypes.byref(spi_bus_rel_en)
        )

        if result != 0:
            raise ValueError(f"Error getting GPIO config: {result}")

        # Return the output values as a dictionary
        return {
            "gpio_pin_des": list(gpio_pin_des),
            "dflt_gpio_output": dflt_gpio_output.value,
            "dflt_gpio_dir": dflt_gpio_dir.value,
            "rmt_wkup_en": rmt_wkup_en.value,
            "int_pin_md": int_pin_md.value,
            "spi_bus_rel_en": spi_bus_rel_en.value
        }

    def get_gpio_pin_val(self, handle):
        """
        Retrieves the current GPIO values of the MCP2210 device.

        Args:
            handle (int): A handle to the MCP2210 device.

        Returns:
            int: Current GPIO pin values.

        Raises:
            ValueError: If the DLL function call fails (non-zero return value).
        """
        gpio_pin_val = ctypes.c_uint()

        # Call the DLL function
        result = self.dll.Mcp2210_GetGpioPinVal(
            ctypes.c_void_p(handle),
            ctypes.byref(gpio_pin_val)
        )

        if result != 0:
            raise ValueError(f"Error getting GPIO pin values: {result}")

        return result, gpio_pin_val.value

    def get_spi_config(self, handle, cfgSelector):
        """
        Get the SPI settings for the current (VM) configuration or the default (NVRAM) configuration.

        Args:
            handle (ctypes.c_void_p): Device handle.
            cfgSelector (int): Selects the current or startup configuration.
                            Possible values:
                            - MCP2210_VM_CONFIG (current configuration)
                            - MCP2210_NVRAM_CONFIG (startup configuration)

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
        # Prepare the output variables
        baudRate = ctypes.c_uint()
        idleCsVal = ctypes.c_uint()
        activeCsVal = ctypes.c_uint()
        csToDataDly = ctypes.c_uint()
        dataToCsDly = ctypes.c_uint()
        dataToDataDly = ctypes.c_uint()
        txferSize = ctypes.c_uint()
        spiMd = ctypes.c_ubyte()

        # Call the DLL function
        result = self.dll.Mcp2210_GetSpiConfig(
            ctypes.c_void_p(handle),
            ctypes.c_ubyte(cfgSelector),
            ctypes.byref(baudRate),
            ctypes.byref(idleCsVal),
            ctypes.byref(activeCsVal),
            ctypes.byref(csToDataDly),
            ctypes.byref(dataToCsDly),
            ctypes.byref(dataToDataDly),
            ctypes.byref(txferSize),
            ctypes.byref(spiMd)
        )

        # Check the result
        if result != 0:
            raise ValueError(f"Error getting SPI configuration. Error code: {result}")

        # Return the data as a dictionary
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

    def xfer_spi_data(self, handle, data_tx, baud_rate, transfer_size, cs_mask):

        """
        Wrapper for the Mcp2210_xferSpiData function.

        Args:
            handle (ctypes.c_void_p): MCP2210 device handle.
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
            ValueError: If the DLL function call fails.
        """
        # Prepare the data to transmit
        data_tx_buffer = (ctypes.c_ubyte * transfer_size)(*data_tx)
        data_rx_buffer = (ctypes.c_ubyte * transfer_size)()  # Receive buffer of the same size
        c_baud_rate = ctypes.c_uint(baud_rate)
        c_transfer_size = ctypes.c_uint(transfer_size)
        # Call the DLL function (cs_mask is honored as passed by the caller)
        result = self.dll.Mcp2210_xferSpiData(
            ctypes.c_void_p(handle),
            data_tx_buffer,
            data_rx_buffer,
            ctypes.byref(c_baud_rate),
            ctypes.byref(c_transfer_size),
            ctypes.c_uint(cs_mask)
        )

        # Check the result
        if result != 0:
            raise ValueError(f"SPI transfer error. Error code: {result}")

        # Convert the data from the receive buffer into a list
        data_rx = list(data_rx_buffer)

        # Return the results
        return {
            "data_rx": data_rx,
            "baud_rate": c_baud_rate.value,
            "transfer_size": c_transfer_size.value
        }


    def mcp2210_xfer_spi_data_ex(self, handle = 1368, data_tx = [255, 255], baud_rate = 10000000, txfer_size = 2, csmask = 4,
                                idle_cs_val = 1, active_cs_val= 0, cs_to_data_dly = 0,
                                data_to_cs_dly = 0, data_to_data_dly = 0, spi_mode = 0):
        """
        Configures and performs an SPI data transfer with the MCP2210 device.

        :param handle: Pointer to the device handle (ctypes void pointer).
        :param data_tx: Byte array of data to transmit (list or bytes).
        :param baud_rate: SPI transfer rate (int).
        :param txfer_size: Size of the data to transmit (int).
        :param csmask: Chip-select bit mask (int).
        :param idle_cs_val: Chip-select value when idle (int).
        :param active_cs_val: Active chip-select value (int).
        :param cs_to_data_dly: Delay from CS assertion to data start (int).
        :param data_to_cs_dly: Delay from the last byte to CS deassertion (int).
        :param data_to_data_dly: Delay between bytes (int).
        :param spi_mode: SPI mode (MCP2210_SPI_MODE0-3).
        :return: Tuple (return code, received data).
        """

        # Convert the input data to ctypes
        pdata_tx = (ctypes.c_ubyte * len(data_tx))(*data_tx)
        pdata_rx = (ctypes.c_ubyte * len(data_tx))()  # Receive buffer

        # Convert variables for passing by pointer
        baud_rate_c = ctypes.c_uint(baud_rate)
        txfer_size_c = ctypes.c_uint(txfer_size)
        idle_cs_val_c = ctypes.c_uint(idle_cs_val)
        active_cs_val_c = ctypes.c_uint(active_cs_val)
        cs_to_data_dly_c = ctypes.c_uint(cs_to_data_dly)
        data_to_cs_dly_c = ctypes.c_uint(data_to_cs_dly)
        data_to_data_dly_c = ctypes.c_uint(data_to_data_dly)
        spi_mode_c = ctypes.c_ubyte(spi_mode)

        # Call the library function
        ret = self.dll.Mcp2210_xferSpiDataEx(
            handle,
            ctypes.byref(pdata_tx),
            ctypes.byref(pdata_rx),
            ctypes.byref(baud_rate_c),
            ctypes.byref(txfer_size_c),
            ctypes.c_uint(csmask),
            ctypes.byref(idle_cs_val_c),
            ctypes.byref(active_cs_val_c),
            ctypes.byref(cs_to_data_dly_c),
            ctypes.byref(data_to_cs_dly_c),
            ctypes.byref(data_to_data_dly_c),
            ctypes.byref(spi_mode_c)
        )

        # Convert the buffer into a Python list
        received_data = list(pdata_rx)

        return ret, received_data










    def dictionary_to_binary_number(self, gpio_dict):
        sorted_keys = sorted(gpio_dict.keys(), key=lambda x: int(x[4:]), reverse=True)
        binary_string = ''.join(str(int(gpio_dict[key])) for key in sorted_keys)
        return int(binary_string, 2)

    def decode_temperature(self, result):
        # Combine the bytes
        raw_data = result['data_rx']
        raw_data = (raw_data[0] << 8) | raw_data[1]
        # Drop the 3 least significant bits
        temperature_raw = raw_data >> 3
        # Check the sign
        if temperature_raw & 0x1000:  # If bit 12 is set
            temperature_raw -= 0x2000
        # Convert to temperature
        return temperature_raw * 0.0625


    def set_spi_config(self, handle, cfgSelector, baudRate, idleCsVal, activeCsVal,
                    csToDataDly, dataToCsDly, dataToDataDly, txferSize, spiMd):
        """
        Configures SPI settings for MCP2210 for either the current (VM) configuration
        or the default startup (NVRAM) configuration.

        Args:
            handle (ctypes.c_void_p): Device handle.
            cfgSelector (int): Selects current or startup configuration.
                            Possible values:
                            - MCP2210_VM_CONFIG (current configuration)
                            - MCP2210_NVRAM_CONFIG (startup configuration)
            baudRate (int): SPI clock speed in bits per second.
            idleCsVal (int): Chip Select (CS) value when idle.
            activeCsVal (int): Chip Select (CS) value when active.
            csToDataDly (int): Delay from CS assertion to first data transmission (in 100 µs units).
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
        # Prepare input variables
        baudRate_c = ctypes.c_uint(baudRate)
        idleCsVal_c = ctypes.c_uint(idleCsVal)
        activeCsVal_c = ctypes.c_uint(activeCsVal)
        csToDataDly_c = ctypes.c_uint(csToDataDly)
        dataToCsDly_c = ctypes.c_uint(dataToCsDly)
        dataToDataDly_c = ctypes.c_uint(dataToDataDly)
        txferSize_c = ctypes.c_uint(txferSize)
        spiMd_c = ctypes.c_ubyte(spiMd)

        # Call the DLL function to set SPI configuration
        result = self.dll.Mcp2210_SetSpiConfig(
            ctypes.c_void_p(handle),
            ctypes.c_ubyte(cfgSelector),
            ctypes.byref(baudRate_c),
            ctypes.byref(idleCsVal_c),
            ctypes.byref(activeCsVal_c),
            ctypes.byref(csToDataDly_c),
            ctypes.byref(dataToCsDly_c),
            ctypes.byref(dataToDataDly_c),
            ctypes.byref(txferSize_c),
            ctypes.byref(spiMd_c)
        )

        # Check the result and raise an exception if an error occurs
        if result != 0:
            raise ValueError(f"Failed to set SPI configuration, error code: {result}")

        print("SPI configuration successfully applied.")

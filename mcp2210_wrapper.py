import ctypes
import constants

#Used constants

class MCP2210:
    def __init__(self):
        """
        Инициализация и загрузка DLL.
        """
        dll_path = "MCP2210/mcp2210_dll_um_x64.dll"
        self.dll = ctypes.WinDLL(dll_path)
        version = self.get_library_version()
        print("Версия dll: " + str(version))
        self._setup_functions()

    def _setup_functions(self):
        """
        Настройка функций DLL.
        """
        self.dll.Mcp2210_SetGpioPinVal.argtypes = [
            ctypes.c_void_p,        # Указатель на handle устройства
            ctypes.c_uint,          # Значение GPIO
            ctypes.POINTER(ctypes.c_uint)  # Указатель для возвращаемого значения GPIO
        ]
        self.dll.Mcp2210_SetGpioPinVal.restype = ctypes.c_int  # Код результата


        # Настройка Mcp2210_GetConnectedDevCount
        self.dll.Mcp2210_GetConnectedDevCount.argtypes = [ctypes.c_ushort, ctypes.c_ushort]
        self.dll.Mcp2210_GetConnectedDevCount.restype = ctypes.c_int

        # Настройка Mcp2210_GetSerialNumber
        self.dll.Mcp2210_GetSerialNumber.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p]
        self.dll.Mcp2210_GetSerialNumber.restype = ctypes.c_int

        # Настройка Mcp2210_OpenByIndex
        self.dll.Mcp2210_OpenByIndex.argtypes = [
            ctypes.c_ushort,  # vid
            ctypes.c_ushort,  # pid
            ctypes.c_uint,  # index
            ctypes.c_wchar_p,  # devPath
            ctypes.POINTER(ctypes.c_ulong)  # devPathsize
        ]
        self.dll.Mcp2210_OpenByIndex.restype = ctypes.c_void_p

        # Настройка Mcp2210_Close
        self.dll.Mcp2210_Close.argtypes = [ctypes.c_void_p]  # Принимает handle
        self.dll.Mcp2210_Close.restype = ctypes.c_int        # Возвращает int

        # Настройка Mcp2210_OpenBySN
        self.dll.Mcp2210_OpenBySN.argtypes = [
            ctypes.c_ushort,        # vid
            ctypes.c_ushort,        # pid
            ctypes.c_wchar_p,       # serialNo
            ctypes.c_wchar_p        # devPath
        ]
        self.dll.Mcp2210_OpenBySN.restype = ctypes.c_void_p  # Возвращает дескриптор устройства (IntPtr в C#)

        # Настройка M_Mcp2210_GetGpioPinDir
        self.dll.Mcp2210_GetGpioPinDir.argtypes = [
            ctypes.c_void_p,                # handle
            ctypes.POINTER(ctypes.c_uint)  # pgpioDir
        ]
        self.dll.Mcp2210_GetGpioPinDir.restype = ctypes.c_int  # Возвращает код результата

        # Настройка Mcp2210_SetGpioPinDir
        self.dll.Mcp2210_SetGpioPinDir.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_uint     # gpioDir
        ]
        self.dll.Mcp2210_SetGpioPinDir.restype = ctypes.c_int  # Возвращает код результата

        # Настройка Mcp2210_GetGpioPinVal
        self.dll.Mcp2210_GetGpioPinVal.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.POINTER(ctypes.c_uint)  # pGPIOVal
        ]
        self.dll.Mcp2210_GetGpioPinVal.restype = ctypes.c_int  # Возвращает код результата

        # Настройка Mcp2210_SetGpioConfig
        self.dll.Mcp2210_SetGpioConfig.argtypes = [
            ctypes.c_void_p,  # handle
            ctypes.c_ubyte,  # cfgSelector
            ctypes.POINTER(ctypes.c_ubyte),  # pGpioPinDes (указатель на массив)
            ctypes.c_uint,  # dfltGpioOutput
            ctypes.c_uint,  # dfltGpioDir
            ctypes.c_ubyte,  # rmtWkupEn
            ctypes.c_ubyte,  # intPinMd
            ctypes.c_ubyte  # spiBusRelEn
        ]
        self.dll.Mcp2210_SetGpioConfig.restype = ctypes.c_int  # Возвращает код результата

        # Настройка Mcp2210_Reset
        self.dll.Mcp2210_Reset.argtypes = [ctypes.c_void_p]  # handle
        self.dll.Mcp2210_Reset.restype = ctypes.c_int  # Возвращает код результата

        # Настройка Mcp2210_GetGpioConfig
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
        #Временные настройки начались
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

        ################################################################################################################
        #Временные настройки закончились

    def get_library_version(self):
        """
        Получение версии библиотеки.
        """
        buffer = ctypes.create_unicode_buffer(64)
        result = self.dll.Mcp2210_GetLibraryVersion(buffer)
        if result < 0:
            raise RuntimeError(f"Ошибка при получении версии DLL. Код ошибки: {result}")
        return buffer.value

    def get_connected_device_count(self, vid=0x4D8, pid=0xDE):
        """
        Получает количество подключённых устройств MCP2210 по VID и PID.

        Args:
            vid (int): Vendor ID (например, 0x4D8 для Microchip).
            pid (int): Product ID (например, 0xDE для MCP2210).

        Returns:
            int: Количество подключённых устройств.

        Raises:
            RuntimeError: Если произошла ошибка при вызове функции.
        """

        # Вызов функции DLL
        device_count = self.dll.Mcp2210_GetConnectedDevCount(vid, pid)

        # Проверка результата
        if device_count < 0:
            raise RuntimeError(f"Ошибка при вызове Mcp2210_GetConnectedDevCount. Код ошибки: {device_count}")

        return device_count

    def open_device_by_sn(self, serial_no, vid=0x4D8, pid=0xDE):
        """
        Открытие устройства MCP2210 по серийному номеру.

        Args:
            vid (int): Vendor ID устройства.
            pid (int): Product ID устройства.
            serial_no (str): Серийный номер устройства.

        Returns:
            tuple: Дескриптор устройства (handle) и путь устройства (str).

        Raises:
            RuntimeError: Если не удалось открыть устройство.
        """
        # Буфер для пути устройства
        dev_path_buffer = ctypes.create_unicode_buffer(256)  # Максимальная длина пути — 256 символов

        # Вызов функции DLL
        handle = self.dll.Mcp2210_OpenBySN(
            ctypes.c_ushort(vid),
            ctypes.c_ushort(pid),
            serial_no,
            dev_path_buffer
        )

        # Проверка результата
        if handle is None or handle == ctypes.c_void_p(-1).value:
            error_code = self.dll.Mcp2210_GetLastError()  # Получаем последний код ошибки
            raise RuntimeError(f"Ошибка при открытии устройства. Код ошибки: {error_code}")

        # Возвращаем дескриптор и путь устройства
        return handle

    def get_serial_number(self, handle):
        """
        Получение серийного номера устройства MCP2210.

        Args:
            handle (ctypes.c_void_p): Дескриптор устройства.

        Returns:
            str: Серийный номер устройства.

        Raises:
            RuntimeError: Если функция возвращает отрицательный код.
        """
        # Создание буфера для серийного номера
        serial_str = ctypes.create_unicode_buffer(64)  # Буфер для строки до 64 символов

        # Вызов функции DLL
        result = self.dll.Mcp2210_GetSerialNumber(handle, serial_str)

        # Проверка результата
        if result < 0:
            raise RuntimeError(f"Ошибка при получении серийного номера. Код ошибки: {result}")

        return serial_str.value

    def open_device_by_index(self, vid=0x4D8, pid=0xDE, index=0):
        """
        Открытие устройства MCP2210 по индексу.

        Args:
            vid: VID устройства
            pid: PID устройства
            index (int): Индекс устройства среди подключённых.

        Returns:
            tuple: Дескриптор устройства (handle) и путь устройства (str).

        Raises:
            RuntimeError: Если не удалось открыть устройство.
        """
        # Буфер для пути устройства
        dev_path_buffer_size = ctypes.c_ulong(256)  # Размер пути устройства
        dev_path_buffer = ctypes.create_unicode_buffer(dev_path_buffer_size.value)  # Буфер для строки

        # Вызов функции DLL
        handle = self.dll.Mcp2210_OpenByIndex(
            ctypes.c_ushort(vid),
            ctypes.c_ushort(pid),
            ctypes.c_uint(index),
            dev_path_buffer,
            ctypes.byref(dev_path_buffer_size)
        )

        # Проверка результата
        if handle is None or handle == ctypes.c_void_p(-1).value:
            error_code = self.dll.Mcp2210_GetLastError()  # Получаем последний код ошибки
            raise RuntimeError(f"Ошибка при открытии устройства. Код ошибки: {error_code}")

        # Возвращаем дескриптор устройства и путь
        return handle

    def close_device(self, handle):
        """
        Закрытие соединения с устройством MCP2210.

        Args:
            handle (ctypes.c_void_p): Дескриптор устройства, полученный при открытии.

        Returns:
            None

        Raises:
            RuntimeError: Если не удалось закрыть соединение.
        """
        result = self.dll.Mcp2210_Close(handle)
        if result != 0:
            raise RuntimeError(f"Ошибка при закрытии устройства. Код ошибки: {result}")

    def get_gpio_pin_dir(self, handle):
        """
        Получение направления GPIO пинов устройства.

        Args:
            handle (ctypes.c_void_p): Дескриптор устройства.

        Returns:
            list: Список из 9 значений (0 - вход, 1 - выход) для каждого GPIO.

        Raises:
            RuntimeError: Если функция возвращает ошибку.
        """
        # Переменная для хранения результата (направления пинов)
        gpio_dir = ctypes.c_uint()

        # Вызов функции DLL
        result = self.dll.Mcp2210_GetGpioPinDir(handle, ctypes.byref(gpio_dir))

        # Проверка результата
        if result != 0:
            raise RuntimeError(f"Ошибка при получении направления GPIO пинов. Код ошибки: {result}")

        # Преобразуем битовое значение в список направлений
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
        # Преобразование в читаемый формат

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
            return self.E_ERR_UNKNOWN_ERROR
        
    def reset_device(self, handle):
        """
        Сброс устройства MCP2210.

        Args:
            handle (ctypes.c_void_p): Дескриптор устройства.

        Returns:
            None

        Raises:
            RuntimeError: Если сброс устройства завершился с ошибкой.
        """
        if not handle or handle == ctypes.c_void_p(-1).value:
            raise ValueError("Недействительный дескриптор устройства.")

        # Вызов функции сброса
        result = self.dll.Mcp2210_Reset(handle)

        # Проверка результата
        if result != 0:
            error_buffer = ctypes.create_unicode_buffer(256)
            self.dll.Mcp2210_GetLastErrorText(error_buffer, 256)
            raise RuntimeError(f"Ошибка при сбросе устройства. Код ошибки: {result}, Описание: {error_buffer.value}")

        print("Устройство успешно сброшено.")


    def set_gpio_pin_val(self, handle, gpio_set_val):
        """
        Обёртка для функции Mcp2210_SetGpioPinVal.

        Args:
            handle (ctypes.c_void_p): Указатель на устройство.
            gpio_set_val (int): Новые значения GPIO.

        Returns:
            tuple: (result_code, gpio_pin_val), где:
                - result_code (int): Код результата (0 - успех, отрицательные - ошибки).
                - gpio_pin_val (int): Текущее значение GPIO, возвращаемое функцией.

        Raises:
            ValueError: Если handle равен None.
            RuntimeError: Если результат вызова отрицательный (ошибка).
        """
        if handle is None or handle == ctypes.c_void_p(-1).value:
            raise ValueError("Invalid handle provided")

        # Буфер для возвращаемого значения GPIO pin values
        gpio_pin_val = ctypes.c_uint()

        # Вызов функции DLL
        result_code = self.dll.Mcp2210_SetGpioPinVal(
            ctypes.c_void_p(handle),
            ctypes.c_uint(gpio_set_val),
            ctypes.byref(gpio_pin_val)
        )

        # Обработка результата
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
        #Временные настройки начались
   
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
        Получение настроек SPI для текущей (VM) конфигурации или конфигурации по умолчанию (NVRAM).

        Args:
            handle (ctypes.c_void_p): Дескриптор устройства.
            cfgSelector (int): Выбор текущей или начальной конфигурации.
                            Возможные значения:
                            - MCP2210_VM_CONFIG (текущая конфигурация)
                            - MCP2210_NVRAM_CONFIG (начальная конфигурация)

        Returns:
            dict: Словарь, содержащий настройки SPI:
                - baudRate: Скорость передачи.
                - idleCsVal: Значение Chip Select в состоянии ожидания.
                - activeCsVal: Значение Chip Select в активном состоянии.
                - csToDataDly: Задержка от Chip Select до передачи данных.
                - dataToCsDly: Задержка от последнего байта до Chip Select.
                - dataToDataDly: Задержка между байтами.
                - txferSize: Размер передачи в байтах.
                - spiMd: Режим SPI.
        Raises:
            ValueError: Если вызов функции DLL завершился с ошибкой.
        """
        # Подготовка выходных переменных
        baudRate = ctypes.c_uint()
        idleCsVal = ctypes.c_uint()
        activeCsVal = ctypes.c_uint()
        csToDataDly = ctypes.c_uint()
        dataToCsDly = ctypes.c_uint()
        dataToDataDly = ctypes.c_uint()
        txferSize = ctypes.c_uint()
        spiMd = ctypes.c_ubyte()

        # Вызов функции DLL
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

        # Проверка результата
        if result != 0:
            raise ValueError(f"Ошибка при получении конфигурации SPI. Код ошибки: {result}")

        # Возврат данных в виде словаря
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
        Обертка для вызова функции Mcp2210_xferSpiData.

        Args:
            handle (ctypes.c_void_p): Дескриптор устройства MCP2210.
            data_tx (list[int]): Данные для передачи через SPI.
            baud_rate (int): Скорость передачи SPI (в Гц). Если 0, используется текущая скорость.
            transfer_size (int): Количество байт на передачу. Если 0, передача не выполняется, только изменение конфигурации.
            cs_mask (int): Битовая маска GPIO пинов для Chip Select.

        Returns:
            dict: Результаты SPI передачи:
                - "data_rx" (list[int]): Принятые данные.
                - "baud_rate" (int): Принятая скорость передачи SPI.
                - "transfer_size" (int): Фактический размер передачи.

        Raises:
            ValueError: Если вызов функции DLL завершился с ошибкой.
        """
        # Подготовка данных для передачи
        data_tx_buffer = (ctypes.c_ubyte * transfer_size)(*data_tx)
        data_rx_buffer = (ctypes.c_ubyte * transfer_size)()  # Буфер для приёма данных того же размера
        c_baud_rate = ctypes.c_uint(baud_rate)
        c_transfer_size = ctypes.c_uint(transfer_size)

        # Вызов функции DLL
        result = self.dll.Mcp2210_xferSpiData(
            ctypes.c_void_p(handle),
            data_tx_buffer,
            data_rx_buffer,
            ctypes.byref(c_baud_rate),
            ctypes.byref(c_transfer_size),
            ctypes.c_uint(cs_mask)
        )

        # Проверка результата
        if result != 0:
            raise ValueError(f"Ошибка SPI передачи. Код ошибки: {result}")

        # Преобразование данных из буфера приёма в список
        data_rx = list(data_rx_buffer)

        # Возврат результатов
        return {
            "data_rx": data_rx,
            "baud_rate": c_baud_rate.value,
            "transfer_size": c_transfer_size.value
        }

    def dictionary_to_binary_number(self, gpio_dict):
        sorted_keys = sorted(gpio_dict.keys(), key=lambda x: int(x[4:]), reverse=True)
        binary_string = ''.join(str(int(gpio_dict[key])) for key in sorted_keys)
        return int(binary_string, 2)
    
    def decode_temperature(self, result):
        # Объединяем байты
        raw_data = result['data_rx'] 
        raw_data = (raw_data[0] << 8) | raw_data[1]
        # Отбрасываем младшие 3 бита
        temperature_raw = raw_data >> 3
        # Проверяем знак
        if temperature_raw & 0x1000:  # Если бит 12 установлен
            temperature_raw -= 0x2000
        # Преобразуем в температуру
        return temperature_raw * 0.0625

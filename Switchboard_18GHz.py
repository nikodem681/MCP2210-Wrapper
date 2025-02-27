from mcp2210_wrapper import MCP2210
import constants
import time

class Switchboard_18GHz:
    def __init__(self):
        self.mcp = MCP2210()
        self.cs_mask = 0b000010000
        self.default_baud_rate = 1000000

    def connect(self, serial_no):
        self.serial_no = serial_no
        self._setup_PCB(self.serial_no)

    def _setup_PCB(self, serial_no):
        self.handle = self.mcp.open_device_by_sn(serial_no, vid=0x4D8, pid=0xDE)
        print("18GHz switchboard has opened succesfully, handle is: " + str(self.handle))
        print("Starting initializating of MCP...")

        gpio_pins = [
            constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # GPIO0  MUX
            constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # GPIO1  MUX
            constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # GPIO2  MUX
            constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO3
            constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO4
            constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # GPIO5 reset
            constants.pGpioPinDes.MCP2210_PIN_DES_GPIO,  # GPIO6 (DAC LDAC)
            constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO7
            constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO8
        ]
        default_output = {
            "GPIO0": constants.dfltGpioOutput.MCP2210_LOW,
            "GPIO1": constants.dfltGpioOutput.MCP2210_LOW,
            "GPIO2": constants.dfltGpioOutput.MCP2210_LOW,
            "GPIO3": constants.dfltGpioOutput.MCP2210_HIGH,
            "GPIO4": constants.dfltGpioOutput.MCP2210_HIGH,
            "GPIO5": constants.dfltGpioOutput.MCP2210_LOW,
            "GPIO6": constants.dfltGpioOutput.MCP2210_HIGH,
            "GPIO7": constants.dfltGpioOutput.MCP2210_HIGH,
            "GPIO8": constants.dfltGpioOutput.MCP2210_HIGH
        }
        default_direction = {
            "GPIO0": constants.dfltGpioDir.MCP2210_OUPTUT,
            "GPIO1": constants.dfltGpioDir.MCP2210_OUPTUT,
            "GPIO2": constants.dfltGpioDir.MCP2210_OUPTUT,
            "GPIO3": constants.dfltGpioDir.MCP2210_OUPTUT,
            "GPIO4": constants.dfltGpioDir.MCP2210_OUPTUT,
            "GPIO5": constants.dfltGpioDir.MCP2210_OUPTUT,
            "GPIO6": constants.dfltGpioDir.MCP2210_OUPTUT,
            "GPIO7": constants.dfltGpioDir.MCP2210_OUPTUT,
            "GPIO8": constants.dfltGpioDir.MCP2210_OUPTUT
        }
        # Remote wakeup enabled
        remote_wakeup = constants.rmtWkupEn.MCP2210_REMOTE_WAKEUP_DISABLED
        # Interrupt mode set to detect high pulses
        interrupt_mode = constants.intPinMd.MCP2210_INT_MD_CNT_NONE
        # SPI bus release disabled
        spi_bus_release = constants.spiBusRelEn.MCP2210_SPI_BUS_RELEASE_DISABLED
        # Set the GPIO configuration
        result = self.mcp.Set_Gpio_Config(
            self.handle,
            0,  # Volatile Memory
            gpio_pins,
            default_output,
            default_direction,
            remote_wakeup,
            interrupt_mode,
            spi_bus_release
        )

        self.mcp.set_spi_config(
        self.handle,
        0,  # Volatile Memory,
        30000000,
        0x111111111,
        0x000000000, 
        1,
        1,
        1,
        2,
        3)


        if result == 0:
            print("MCP has initializied succesfully...")
        
        self.reset_PCB()
        print("Initializating MCP23S17SO...")
        self.set_MUX_channel(0)

        for i in range (0,5,1):
            self.init_MCP23S17(i)
        
        self.Mech_sw_1 = MechanicalSwitcher(swb = self, address = "MCPIO5Q0")
        self.Mech_sw_2 = MechanicalSwitcher(swb = self, address = "MCPIO5Q1")
        self.Mech_sw_3 = MechanicalSwitcher(swb = self, address = "MCPIO5Q2")
        self.Mech_sw_4 = MechanicalSwitcher(swb = self, address = "MCPIO5Q3")
        self.Mech_sw_5 = MechanicalSwitcher(swb = self, address = "MCPIO5Q4")

        self.AD5726_1 = AD5726(swb = self, spichannel = 2)
        self.AD5726_2 = AD5726(swb = self, spichannel = 3)

    def __del__(self):
        try:
            self.CloseDevice()
        except Exception:
            pass

    def init_MCP23S17(self, MUX_address):
        if MUX_address not in range(6):  # 0-5 включительно
            raise ValueError("MUX address must be between 0 and 5.")
        transfer_size = 3          
        control_byte = 0b01000000 | (MUX_address << 1) # Сдвиг MUX_address на 1 бит влево и объединение с базовым значением
        iocon_address = 0x0A  # Адрес IOCON
        data = 0x80 
        data_tx = [control_byte, iocon_address, data]
        self.SPI_send_command(data_tx, transfer_size, self.cs_mask)
        # Настроить IODIRA
        data_tx_a = [control_byte, 0x00, 0x00]  # PORTA все как выходы
        self.SPI_send_command(data_tx_a, transfer_size, self.cs_mask)
        # Настроить IODIRB
        data_tx_b = [control_byte, 0x10, 0x00]  # PORTB все как выходы
        self.SPI_send_command(data_tx_b, transfer_size, self.cs_mask)
        # Установить OLATA
        data_tx_a = [control_byte, 0x0A, 0x00]  # PORTA = лог. 0
        self.SPI_send_command(data_tx_a, transfer_size, self.cs_mask)
        # Установить OLATB
        data_tx_b = [control_byte, 0x1A, 0x00]  # PORTB = лог. 0
        self.SPI_send_command(data_tx_b, transfer_size, self.cs_mask)
        
    def set_MUX_channel(self, channel_N):
        if channel_N not in range(8):
            raise ValueError("Channel_N must be between 0 and 7")
        result, current_val = self.mcp.get_gpio_pin_val(self.handle)
        current_val = current_val & ~0b111
        if result != 0:
            raise RuntimeError("Failed to get GPIO pin value.")
        current_val = current_val | (channel_N & 0b111)
        result, gpio_pin_val = self.mcp.set_gpio_pin_val(self.handle, current_val)
        if (result == 0 ): 
            print('set_MUX_channel: ' + str(channel_N) + ', current GPIO_val: ' + (bin(gpio_pin_val)))

    def reset_PCB(self):
        RESET_MASK = 0b000100000
        result, current_val = self.mcp.get_gpio_pin_val(self.handle)
        if result != 0:
            raise RuntimeError("Failed to get GPIO pin value.")
        current_val = current_val  | RESET_MASK
        self.mcp.set_gpio_pin_val(self.handle, current_val)
        current_val = current_val  & ~RESET_MASK  #CHATGPT - что делает тильда знак?
        self.mcp.set_gpio_pin_val(self.handle, current_val)
        print("reset_PCB function succesfully done.")

    def CloseDevice(self):
        self.mcp.close_device(self.handle)

    def SPI_send_command (self, data_tx, transfer_size, cs_mask):
        results = self.mcp.xfer_spi_data(self.handle, data_tx, self.default_baud_rate, transfer_size, cs_mask)
        #print ('Responce is: ' + str(results))
        return results

    def MCP23S17_Send_SPI_command(self, device_address, rw_mode, register, data_to_send):

        if rw_mode not in ('r', 'w'):
            raise ValueError(f"Invalid rw_mode: {rw_mode}. Must be 'r' or 'w'.")
        # Проверка device_address
        if device_address not in range(6):
            raise ValueError(f"Invalid device_address: {device_address}. Must be 0-5.")
        # Проверка data
        if not (0x00 <= data_to_send <= 0xFF):
            raise ValueError(f"Invalid data: {data_to_send}. Must be between 0x00 and 0xFF.")
        if register not in [0x0A, 0x1A]:
            raise ValueError(f"Invalid data: {register}. Must be 0x0A, 0x1A")

        rw_bit = 0x01 if rw_mode == 'r' else 0x00        
        data = 0b01000000 | (device_address << 1) | rw_bit # Сдвиг MUX_address на 1 бит влево и объединение с базовым значением
        
        data_tx = [data, register, data_to_send]
        results = self.SPI_send_command(data_tx, 3, self.cs_mask)
        return results

    def MCP23S17_set_output(self, device_address, output_value):
        if device_address not in range(6):
            raise ValueError(f"Invalid device_address: {device_address}. Must be 0-5.") 
        if not (0x00 <= output_value <= 0xFFFF):
            raise ValueError(f"Invalid data: {output_value}. Must be between 0x00 and 0xFFFF.")
        
        if output_value > 0xFF:
            output_value_low_byte = output_value & 0x00FF
            output_value_high_byte = (output_value & 0xFF00) >> 8
            result1 = self.MCP23S17_Send_SPI_command(device_address, 'w', 0x0A, output_value_low_byte)
            result2 = self.MCP23S17_Send_SPI_command(device_address, 'w', 0x1A, output_value_high_byte)
        elif output_value <= 0xff:
            result1 = self.MCP23S17_Send_SPI_command(device_address, 'w', 0x0A, output_value)

    def MCP23S17_get_output(self, device_address):
        if device_address not in range(6):
            raise ValueError(f"Invalid device_address: {device_address}. Must be 0-5.") 
         # Чтение двух регистров
        result1 = self.MCP23S17_Send_SPI_command(device_address, 'r', 0x0A, 0x00)
        result2 = self.MCP23S17_Send_SPI_command(device_address, 'r', 0x1A, 0x00)
        
        # Извлечение значений
        result1 = result1['data_rx'][2]  # Младший байт
        result2 = result2['data_rx'][2]  # Старший байт
        
        # Сдвиг и сложение
        result = result1 + (result2 << 8)  # Сдвиг result2 на 8 бит влево и сложение с result1
        print(f"Вернулось значение: {bin(result)}")  # Двоичное представление результата

        return result


class MechanicalSwitcher:
    def __init__(self, swb, address, state="NC"):
        """
        Конструктор класса MechanicalSwitcher.
        :param swb: объект свитчборда.
        :param address: Уникальный адрес переключателя.
        :param state: Состояние переключателя, может быть 'NO' или 'NC'.
        """
        self.address = address
        self.device_address = None 
        self.GPIO_mask = None 
        self.swb = swb
        if state not in ["NO", "NC"]:
            raise ValueError(f"Invalid state: {state}. Must be 'NO' or 'NC'.")
        self.state = state
        self.configure_by_address()

    def toggle_state(self):
        """
        Переключает состояние между 'NO' и 'NC'.
        """
        current_state = self.get_state()
        self.set_state("NO") if current_state == "NC" else self.set_state("NC")
        

    def get_state(self):
        """
        Возвращает текущее состояние переключателя.
        """
        self.swb.set_MUX_channel(0)
        response = self.swb.MCP23S17_get_output(self.device_address)
        self.state = "NO" if response & self.GPIO_mask else "NC"
        return self.state

    def set_state(self, state):
        """
        Устанавливает состояние переключателя.
        :param state: Новое состояние ('NO' или 'NC').
        """
        self.swb.set_MUX_channel(0)
        if state not in ["NO", "NC"]:
            raise ValueError("Состояние может быть только 'NO' или 'NC'.")
        current_state = self.get_state()
        if current_state == state:
            print ("Needed value is already set")
        else:
            self.state = state
            current_output = self.swb.MCP23S17_get_output(self.device_address)
            if self.state == "NO":
                new_output = current_output | self.GPIO_mask
            else:
                new_output = current_output & ~self.GPIO_mask
            self.swb.MCP23S17_set_output(self.device_address, new_output)

    def configure_by_address(self):
        address_map = {
            "MCPIO5Q0": (5, 0b00000001),
            "MCPIO5Q1": (5, 0b00000010),
            "MCPIO5Q2": (5, 0b00000100),
            "MCPIO5Q3": (5, 0b00001000),
            "MCPIO5Q4": (5, 0b00010000),
            "MCPIO5Q5": (5, 0b00100000),
        }
        if self.address not in address_map:
            raise ValueError(f"Unknown address: {self.address}")
        self.device_address, self.GPIO_mask = address_map[self.address]

    def __repr__(self):
        """
        Возвращает строковое представление объекта.
        """
        return f"MechanicalSwitcher(address={self.address}, state={self.state})"
    
class Var:
    def __init__(self, address, value=0.0):
        """
        Конструктор класса Var.
        :param address: Уникальный адрес переменной.
        :param value: Значение переменной в диапазоне от -1.1 до 1.1.
        """
        self.address = address
        self.set_current_value(value)

    def get_current_value(self):
        """
        Возвращает текущее значение переменной.
        """
        return self.value

    def set_current_value(self, value):
        """
        Устанавливает значение переменной.
        :param value: Новое значение в диапазоне от -1.1 до 1.1.
        """
        if not -1.1 <= value <= 1.1:
            raise ValueError("Значение должно быть в диапазоне от -1.1 до 1.1.")
        self.value = value

class AD5726:
    def __init__(self, swb, spichannel, LDAC_pin = 6, vref_P=1.5, vref_N=-1.5):
        """
        Конструктор класса AD5726.
        :param swb: это класс switchboard 18GHz и никакой другой
        :param spichannel: Уникальный адрес SPI, задается с помощью MUX функции.
        :param vref_P: Референсное напряжение на vref_P.
        :param vref_N: Референсное напряжение на vref_N.
        :param LDAC_pin: Пин с MCP, который подключен.
        """
        if not isinstance(swb, Switchboard_18GHz):
            raise TypeError(f"swb должен быть экземпляром класса Switchboard_18GHz, а не {type(swb).__name__}.")
        self.swb = swb
        self.spichannel = spichannel
        self.LDAC_pin = LDAC_pin
        self.vref_P = vref_P
        self.vref_N = vref_N
    
    def set_output_voltage(self, channel, value):
        """
        Метод, который выставляет выходное напряжение
        :param channel: Канал, который может быть 1, 2, 3, 4 
        :param value: значение напряжение, которое мы хотим получить
        """
        value = float(value)
        if not (-1.5 < value < 1.5):
            raise ValueError(f"Значение {value} выходит за пределы диапазона (-1.5, 1.5).")
        data = int(((value - self.vref_N) * 4096) / (self.vref_P - self.vref_N))
        lo_byte = data & 0xff
        hi_byte= (channel << 6) | (data >> 8)
        data_tx = [hi_byte, lo_byte]
        print(f"hi: {bin(hi_byte)} lo: {bin(lo_byte)}")
        transfer_size = 2
        self.swb.set_MUX_channel(self.spichannel)
        result = self.swb.mcp.get_gpio_pin_val(self.swb.handle)
        self.swb.mcp.set_gpio_pin_val(self.swb.handle, result[1] | (1<<self.LDAC_pin))
        self.swb.SPI_send_command (data_tx, transfer_size, self.swb.cs_mask)
        self.swb.mcp.set_gpio_pin_val(self.swb.handle, result[1] & ~(1<<self.LDAC_pin))
        self.swb.mcp.set_gpio_pin_val(self.swb.handle, result[1] | (1<<self.LDAC_pin))
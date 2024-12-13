from mcp2210_wrapper import MCP2210
import constants

class Switchboard_18GHz:
    def __init__(self):
        self.mcp = MCP2210()
        self.cs_mask = 0b000010000
        self.default_baud_rate = 10000000
        

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
            constants.pGpioPinDes.MCP2210_PIN_DES_CS,  # GPIO6
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
        if result == 0:
            print("MCP has initializied succesfully...")
        
        self.reset_PCB()
        print("Initializating MCP23S17SO...")
        self.set_MUX_channel(0)

        for i in range (0,5,1):
            self.init_MCP23S17(i)

    def __del__(self):
        a = 1

#############################################################

#############################################################
    def init_MCP23S17(self, MUX_address):
        if MUX_address not in range (0, 5):
            print('Mistake. MUX address suppose to be 0, 1, 2, 3, 4, 5 and that it is')
            raise ValueError('Mistake. MUX address suppose to be 0, 1, 2, 3, 4, 5 and that it is')
        transfer_size = 3
        base = 0b01000000            
        control_byte = base | (MUX_address << 1) # Сдвиг MUX_address на 1 бит влево и объединение с базовым значением
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
        data_tx_a = [control_byte, 0x0A, 0xFF]  # PORTA = лог. 1
        self.SPI_send_command(data_tx_a, transfer_size, self.cs_mask)
        # Установить OLATB
        data_tx_b = [control_byte, 0x1A, 0xFF]  # PORTB = лог. 1
        self.SPI_send_command(data_tx_b, transfer_size, self.cs_mask)
        
    def set_MUX_channel(self, channel_N):
        if channel_N not in [0,1,2,3,4,5,6,7]:
            raise ValueError("Channel_N must be between 0 and 8")
        current_val = self.mcp.get_gpio_pin_val(self.handle) & ~0b111
        current_val = current_val | (channel_N & 0b111)
        result, gpio_pin_val = self.mcp.set_gpio_pin_val(self.handle, current_val)
        if (result == 0 ): 
            print('set_MUX_channel: ' + str(channel_N) + 'current GPIO_val: ' + (bin(gpio_pin_val)))

    def SPI_send_command (self, data_tx, transfer_size, cs_mask):
        results = self.mcp.xfer_spi_data(self.handle, data_tx, self.default_baud_rate, transfer_size, cs_mask)
        print ('Responce is: ' + str(results))

    def reset_PCB(self):
        current_val = self.mcp.get_gpio_pin_val(self.handle)
        current_val = current_val  | 0b000100000
        result, gpio_pin_val = self.mcp.set_gpio_pin_val(self.handle, current_val)
        current_val = current_val  & 0b111011111
        result, gpio_pin_val = self.mcp.set_gpio_pin_val(self.handle, current_val)
        print("reset_PCB function succesfully done.")

    def CloseDevice(self):
        self.mcp.close_device(self.handle)
        
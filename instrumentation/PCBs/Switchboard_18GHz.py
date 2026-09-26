from .mcp2210_wrapper import MCP2210
from . import constants

MUX_MASK = 0b000000111    # GPIO0-2 select the SPI MUX channel
RESET_MASK = 0b000100000  # GPIO5 resets the PCB (active high pulse)
ALL_CS_IDLE_HIGH = 0x1FF  # one bit per GPIO: every chip select idles high


class Switchboard_18GHz:
    def __init__(self):
        self.mcp = MCP2210()
        self.cs_mask = 0b000010000  # GPIO4 is the SPI chip select
        self.default_baud_rate = 1000000
        self.handle = None

    def connect(self, serial_no):
        if self.handle is not None:
            self.CloseDevice()
        self.serial_no = serial_no
        try:
            self._setup_PCB(self.serial_no)
        except Exception:
            self.CloseDevice()  # don't leave a half-initialized board looking connected
            raise

    @property
    def is_connected(self):
        return self.handle is not None

    def _require_connection(self):
        if self.handle is None:
            raise RuntimeError("18GHz switchboard is not connected.")

    def _setup_PCB(self, serial_no):
        self.handle = self.mcp.open_device_by_sn(serial_no, vid=0x4D8, pid=0xDE)
        print("18GHz switchboard has opened successfully, handle is: " + str(self.handle))
        print("Starting initialization of MCP...")

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
            "GPIO0": constants.dfltGpioDir.MCP2210_OUTPUT,
            "GPIO1": constants.dfltGpioDir.MCP2210_OUTPUT,
            "GPIO2": constants.dfltGpioDir.MCP2210_OUTPUT,
            "GPIO3": constants.dfltGpioDir.MCP2210_OUTPUT,
            "GPIO4": constants.dfltGpioDir.MCP2210_OUTPUT,
            "GPIO5": constants.dfltGpioDir.MCP2210_OUTPUT,
            "GPIO6": constants.dfltGpioDir.MCP2210_OUTPUT,
            "GPIO7": constants.dfltGpioDir.MCP2210_OUTPUT,
            "GPIO8": constants.dfltGpioDir.MCP2210_OUTPUT
        }
        self.mcp.Set_Gpio_Config(
            self.handle,
            constants.cfgSelector.MCP2210_VM_CONFIG,
            gpio_pins,
            default_output,
            default_direction,
            constants.rmtWkupEn.MCP2210_REMOTE_WAKEUP_DISABLED,
            constants.intPinMd.MCP2210_INT_MD_CNT_NONE,
            constants.spiBusRelEn.MCP2210_SPI_BUS_RELEASE_DISABLED,
        )

        self.mcp.set_spi_config(
            self.handle,
            constants.cfgSelector.MCP2210_VM_CONFIG,
            30000000,          # baud rate (each transfer overrides it with default_baud_rate)
            ALL_CS_IDLE_HIGH,  # idle CS values
            0x000,             # active CS values
            1,                 # CS to data delay
            1,                 # data to CS delay
            1,                 # data to data delay
            2,                 # transfer size
            3)                 # SPI mode

        print("MCP has initialized successfully...")

        self.reset_PCB()
        print("Initializing MCP23S17SO...")
        self.set_MUX_channel(0)

        # Devices 0-4 only. Device 5 (the mechanical switches) is intentionally
        # left out of this init; the switches work as is.
        for i in range(0, 5, 1):
            self.init_MCP23S17(i)

        self.Mech_sw_1 = MechanicalSwitcher(swb=self, address="MCPIO5Q0")
        self.Mech_sw_2 = MechanicalSwitcher(swb=self, address="MCPIO5Q1")
        self.Mech_sw_3 = MechanicalSwitcher(swb=self, address="MCPIO5Q2")
        self.Mech_sw_4 = MechanicalSwitcher(swb=self, address="MCPIO5Q3")
        self.Mech_sw_5 = MechanicalSwitcher(swb=self, address="MCPIO5Q4")

        self.AD5726_1 = AD5726(swb=self, spichannel=2)
        self.AD5726_2 = AD5726(swb=self, spichannel=3)

    def __del__(self):
        try:
            self.CloseDevice()
        except Exception:
            pass

    def init_MCP23S17(self, MUX_address):
        if MUX_address not in range(6):  # 0-5 inclusive
            raise ValueError("MUX address must be between 0 and 5.")
        transfer_size = 3
        control_byte = 0b01000000 | (MUX_address << 1)  # opcode 0100 A2 A1 A0 W
        iocon_address = 0x0A  # IOCON
        data = 0x80  # IOCON.BANK = 1
        data_tx = [control_byte, iocon_address, data]
        self.SPI_send_command(data_tx, transfer_size, self.cs_mask)
        # IODIRA: PORTA all outputs
        data_tx_a = [control_byte, 0x00, 0x00]
        self.SPI_send_command(data_tx_a, transfer_size, self.cs_mask)
        # IODIRB: PORTB all outputs
        data_tx_b = [control_byte, 0x10, 0x00]
        self.SPI_send_command(data_tx_b, transfer_size, self.cs_mask)
        # OLATA: PORTA = 0
        data_tx_a = [control_byte, 0x0A, 0x00]
        self.SPI_send_command(data_tx_a, transfer_size, self.cs_mask)
        # OLATB: PORTB = 0
        data_tx_b = [control_byte, 0x1A, 0x00]
        self.SPI_send_command(data_tx_b, transfer_size, self.cs_mask)

    def set_MUX_channel(self, channel_N):
        if channel_N not in range(8):
            raise ValueError("Channel_N must be between 0 and 7")
        self._require_connection()
        _, current_val = self.mcp.get_gpio_pin_val(self.handle)
        new_val = (current_val & ~MUX_MASK) | channel_N
        result, gpio_pin_val = self.mcp.set_gpio_pin_val(self.handle, new_val)
        if result == 0:
            print('set_MUX_channel: ' + str(channel_N) + ', current GPIO_val: ' + bin(gpio_pin_val))

    def reset_PCB(self):
        self._require_connection()
        _, current_val = self.mcp.get_gpio_pin_val(self.handle)
        self.mcp.set_gpio_pin_val(self.handle, current_val | RESET_MASK)
        self.mcp.set_gpio_pin_val(self.handle, current_val & ~RESET_MASK)
        print("reset_PCB function successfully done.")

    def CloseDevice(self):
        if self.handle is None:
            return
        try:
            self.mcp.close_device(self.handle)
        finally:
            self.handle = None

    def SPI_send_command(self, data_tx, transfer_size, cs_mask):
        self._require_connection()
        return self.mcp.xfer_spi_data(self.handle, data_tx, self.default_baud_rate, transfer_size, cs_mask)

    def MCP23S17_Send_SPI_command(self, device_address, rw_mode, register, data_to_send):
        if rw_mode not in ('r', 'w'):
            raise ValueError(f"Invalid rw_mode: {rw_mode}. Must be 'r' or 'w'.")
        if device_address not in range(6):
            raise ValueError(f"Invalid device_address: {device_address}. Must be 0-5.")
        if not (0x00 <= data_to_send <= 0xFF):
            raise ValueError(f"Invalid data: {data_to_send}. Must be between 0x00 and 0xFF.")
        if register not in [0x0A, 0x1A]:
            raise ValueError(f"Invalid register: {register}. Must be 0x0A or 0x1A.")

        rw_bit = 0x01 if rw_mode == 'r' else 0x00
        opcode = 0b01000000 | (device_address << 1) | rw_bit  # 0100 A2 A1 A0 R/W
        return self.SPI_send_command([opcode, register, data_to_send], 3, self.cs_mask)

    def MCP23S17_set_output(self, device_address, output_value):
        if device_address not in range(6):
            raise ValueError(f"Invalid device_address: {device_address}. Must be 0-5.")
        if not (0x00 <= output_value <= 0xFFFF):
            raise ValueError(f"Invalid data: {output_value}. Must be between 0x00 and 0xFFFF.")

        # Always write both ports so the high byte (OLATB) is never left stale
        # when stepping down from a >0xFF value to a small one.
        self.MCP23S17_Send_SPI_command(device_address, 'w', 0x0A, output_value & 0x00FF)
        self.MCP23S17_Send_SPI_command(device_address, 'w', 0x1A, (output_value & 0xFF00) >> 8)

    def MCP23S17_get_output(self, device_address):
        if device_address not in range(6):
            raise ValueError(f"Invalid device_address: {device_address}. Must be 0-5.")
        low = self.MCP23S17_Send_SPI_command(device_address, 'r', 0x0A, 0x00)['data_rx'][2]   # OLATA
        high = self.MCP23S17_Send_SPI_command(device_address, 'r', 0x1A, 0x00)['data_rx'][2]  # OLATB
        result = low | (high << 8)
        print(f"MCP23S17 {device_address} output: {bin(result)}")
        return result


class MechanicalSwitcher:
    def __init__(self, swb, address, state="NC"):
        """
        :param swb: switchboard object.
        :param address: switch address, a key of the address map below.
        :param state: switch state, 'NO' or 'NC'.
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
        Switch between 'NO' and 'NC'.
        """
        if self.get_state() == "NC":
            self.set_state("NO")
        else:
            self.set_state("NC")

    def get_state(self):
        """
        Read the current switch state from the MCP23S17.
        """
        self.swb.set_MUX_channel(0)
        response = self.swb.MCP23S17_get_output(self.device_address)
        self.state = "NO" if response & self.GPIO_mask else "NC"
        return self.state

    def set_state(self, state):
        """
        :param state: new state, 'NO' or 'NC'.
        """
        if state not in ["NO", "NC"]:
            raise ValueError(f"Invalid state: {state}. Must be 'NO' or 'NC'.")
        self.swb.set_MUX_channel(0)
        current_output = self.swb.MCP23S17_get_output(self.device_address)
        current_state = "NO" if current_output & self.GPIO_mask else "NC"
        if current_state == state:
            print("Needed value is already set")
            self.state = state
            return
        if state == "NO":
            new_output = current_output | self.GPIO_mask
        else:
            new_output = current_output & ~self.GPIO_mask
        self.swb.MCP23S17_set_output(self.device_address, new_output)
        self.state = state

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
        return f"MechanicalSwitcher(address={self.address}, state={self.state})"


class Var:
    def __init__(self, address, value=0.0):
        """
        :param address: variable address.
        :param value: value in the range -1.1 to 1.1.
        """
        self.address = address
        self.set_current_value(value)

    def get_current_value(self):
        return self.value

    def set_current_value(self, value):
        """
        :param value: new value in the range -1.1 to 1.1.
        """
        if not -1.1 <= value <= 1.1:
            raise ValueError("Value must be in the range -1.1 to 1.1.")
        self.value = value


class AD5726:
    def __init__(self, swb, spichannel, LDAC_pin=6, vref_P=1.5, vref_N=-1.5):
        """
        Quad 12-bit DAC behind the SPI MUX.

        :param swb: the Switchboard_18GHz instance the DAC sits on.
        :param spichannel: SPI MUX channel of the DAC.
        :param LDAC_pin: MCP2210 GPIO wired to the DAC's LDAC pin.
        :param vref_P: voltage on VREFP.
        :param vref_N: voltage on VREFN.
        """
        if not isinstance(swb, Switchboard_18GHz):
            raise TypeError(f"swb must be a Switchboard_18GHz instance, not {type(swb).__name__}.")
        self.swb = swb
        self.spichannel = spichannel
        self.LDAC_pin = LDAC_pin
        self.vref_P = vref_P
        self.vref_N = vref_N

    def set_output_voltage(self, channel, value):
        """
        Set the output voltage of one DAC channel.

        :param channel: DAC channel, 0-3 (A-D).
        :param value: output voltage, strictly between vref_N and vref_P.
        """
        if channel not in range(4):
            raise ValueError(f"Channel {channel} must be 0-3.")
        value = float(value)
        if not (self.vref_N < value < self.vref_P):
            raise ValueError(f"Value {value} is outside the range ({self.vref_N}, {self.vref_P}).")
        data = int(((value - self.vref_N) * 4096) / (self.vref_P - self.vref_N))
        lo_byte = data & 0xff
        hi_byte = (channel << 6) | (data >> 8)
        data_tx = [hi_byte, lo_byte]
        print(f"hi: {bin(hi_byte)} lo: {bin(lo_byte)}")
        transfer_size = 2
        self.swb.set_MUX_channel(self.spichannel)
        _, gpio_val = self.swb.mcp.get_gpio_pin_val(self.swb.handle)
        ldac = 1 << self.LDAC_pin
        self.swb.mcp.set_gpio_pin_val(self.swb.handle, gpio_val | ldac)
        self.swb.SPI_send_command(data_tx, transfer_size, self.swb.cs_mask)
        self.swb.mcp.set_gpio_pin_val(self.swb.handle, gpio_val & ~ldac)
        self.swb.mcp.set_gpio_pin_val(self.swb.handle, gpio_val | ldac)

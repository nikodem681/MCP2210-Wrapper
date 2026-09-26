"""List the connected MCP2210 serial numbers, connect to the first switchboard and reset it."""
import sys

from instrumentation.PCBs.Switchboard_18GHz import Switchboard_18GHz


def main():
    swb = Switchboard_18GHz()
    mcp = swb.mcp

    serial_numbers = []
    for i in range(mcp.get_connected_device_count()):
        handle = mcp.open_device_by_index(index=i)
        try:
            serial_numbers.append(mcp.get_serial_number(handle))
        finally:
            mcp.close_device(handle)
    print(serial_numbers)
    if not serial_numbers:
        sys.exit("No MCP2210 device found.")

    swb.connect(serial_numbers[0])
    try:
        swb.reset_PCB()
    finally:
        swb.CloseDevice()
    print('The end')


if __name__ == "__main__":
    main()

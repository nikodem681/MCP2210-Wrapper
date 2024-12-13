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

Serial_no_list = []
for i in range (0, quanity, 1):
    handle = mcp.open_device_by_index(index = i)
    Serial_no = mcp.get_serial_number(handle)
    Serial_no_list.append(Serial_no)
    mcp.close_device(handle)
print(Serial_no_list)

swb = Switchboard_18GHz(Serial_no_list[0])
swb.reset_PCB()
print('The end')
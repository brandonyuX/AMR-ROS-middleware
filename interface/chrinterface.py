#Interface for charging station

import time
from pymodbus.client import ModbusTcpClient

chargerip='192.168.1.105'
chargerport=502

client = ModbusTcpClient(chargerip,chargerport)
client.connect()




def extend():
    client.write_coil(0,1,3)
    time.sleep(20)
    client.write_coil(0,0,3)

def retract():
    client.write_coil(1,1,3)
    time.sleep(20)
    client.write_coil(1,0,3)

while True:
    choice=input("1 - Extend, 2 - Retract\n")
    match choice:
        case '1':
            extend()
        case '2':
            retract()
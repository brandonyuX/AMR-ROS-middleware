#Interface for charging station

import time,sys
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadDecoder,Endian

sys.path.append('../Middleware Development')
import interface.dbinterface as dbinterface

chargerip='192.168.0.91'
chargerport=502

client = ModbusTcpClient(chargerip,chargerport)
client.connect()




def extend():
    client.write_coil(0,1,3)
    time.sleep(15)
    client.write_coil(0,0,3)

def retract():
    client.write_coil(1,1,3)
    time.sleep(15)
    client.write_coil(1,0,3)

def start():
    client.write_coil(4,0,3)
    client.write_coil(2,1,3)
    time.sleep(1)
    

def stop():
    dbinterface.writeLog(msg='<CHR> Stopping charger')
    client.write_coil(2,0,3)
    client.write_coil(4,1,3)
    time.sleep(1)
    client.write_coil(4,0,3)

def reset():
    client.write_coil(7,1,3)
    time.sleep(1)
    client.write_coil(7,0,3)
    

def gocharge():
    dbinterface.insertRbtTask('CHR',3,'CHARGE',reqid=1001)

def stopcharge():
    stop()
    time.sleep(5)
    retract()
    dbinterface.updateRbtCharge(rbtid=1,state=0)
# def read():
#     rr = client.read_holding_registers(3x13,1,unit=3)
#     print(rr.registers)
#     decoder = BinaryPayloadDecoder.fromRegisters(rr.registers, byteorder=Endian.Little)
#     print(decoder)
#     decoded=(decoder.decode_16bit_int())
#     print(decoded)
#     bit_2 = (decoded & (1 << 0)) >> 0
#     print(bit_2)

# while True:
#     choice=input("1 - Extend, 2 - Retract 3 - Start 4 - Stop 5 - Reset\n")
#     match choice:
#         case '1':
#             extend()
#         case '2':
#             retract()
#         case '3':
#             start()
#         case '4':
#             stop()
#         case '5':
#             reset()
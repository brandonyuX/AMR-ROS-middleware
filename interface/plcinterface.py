#This file provides interface with the PLC and update the database
#Will use opcua in this example
from opcua import Client
from opcua import ua

def pullreq():

    client = Client("opc.tcp://192.168.1.109:49320")
    # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        print("Objects node is: ", root)

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        print("Children of root are: ", root.get_children())

    
        while True:
            
                
            path="ns=2;s=TwincatTest.SeletarDeparture.GVL_MDS.HMI.STATE.{ConveyorName}".format(ConveyorName=conv)
            state = client.get_node(path)
            path2="ns=2;s=TwincatTest.SeletarDeparture.GVL_MDS.HMI.STATUS.{ConveyorName}".format(ConveyorName=conv)
            state2 = client.get_node(path2)
            
            #print(conv)
            
            datavalue = ua.DataValue(ua.Variant(statevalue, ua.VariantType.Int16))
            datavalue2 = ua.DataValue(ua.Variant(statusvalue, ua.VariantType.Int16))
            state.set_value(datavalue)
            state2.set_value(datavalue2)
            #print(conv,":",state.get_value(),":",convmap.get(i+1,"No Value"))
            time.sleep(testtime)

            

        
            
            
            #time.sleep(testtime)           
        #Query Tag





       

    finally:
        client.disconnect()
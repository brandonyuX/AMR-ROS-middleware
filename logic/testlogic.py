import sys
sys.path.append('../Middleware Development')

import interface.dbinterface as dbinterface

while(True):
    x=input('Enter to continue')
    dbinterface.setExecute(0,1027)
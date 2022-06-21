import interface.dbinterface as dbinterface


dbinterface.startup()
for i in range(1,6):

    print('Pushing {} to station {}'.format(dbinterface.getWOQ(i),i))


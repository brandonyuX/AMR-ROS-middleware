testmsg='000100290012STN01;STN02;STN03adfdfdsfsd'

tasktype={'0001': 'CreateTask','0002':'MoveStn','0003':'Custom Command'}

rcvtsk=testmsg[0:4]
rcvlen=testmsg[4:8]
rcvseq=testmsg[8:12]

print('Task Type: {} -> {}'.format(rcvtsk,tasktype[rcvtsk]))
print('Message Length: {}'.format(rcvlen))
print('Message Sequence Number: {}'.format(rcvseq))

msglen=int(rcvlen)


splitmsg=testmsg[12:msglen].split(';')
print('The extracted stations are: ')
for msg in splitmsg:
    print(msg)

asgrbt=input('Enter robot to assign to: ')
asgtid=input('Enter task ID: ')

asgrbt=asgrbt.zfill(4)
asgtid=asgtid.zfill(4)
print('Task assigned to robot {} with Task ID {}'.format(asgrbt,asgtid))
totallen=str(len(rcvtsk)+len(rcvseq)+len(asgrbt)+len(asgtid)+4)
totallen=totallen.zfill(4)
response=rcvtsk+totallen+rcvseq+asgrbt+asgtid
print('Reponse to PLC: {}'.format(response))






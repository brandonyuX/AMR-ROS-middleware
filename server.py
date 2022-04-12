from cgi import test
from flask import Flask, render_template,request,session
import interface.dbinterface as dbinterface
import main
from mwclass.testclass import testclass
from mwclass.robotconfig import RobotConfig
from mwclass.subtask import SubTask
from flask_socketio import SocketIO, emit
from threading import Lock

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask('testapp')
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
actiondict={'0':'Move','1':'Unload','2':'Load','3':'Custom Command'}
subtasklist=[]
tclist=[]
tc=testclass(0,0,0)

#Background activity to perform
def background_thread():
    """Example of how to send server generated events to clients."""
    count = 0
    
    while True:
        socketio.sleep(3)
        count += 1
        tc.x=count
        tc.y=count+1
        tc.z=count+2
        forjson=tc.toJSON()
        socketio.emit('my_response',
                      {'data': count, 'count': count,'class':forjson})

#Define homepage 
@app.route('/')
def index():
    tsklist=dbinterface.getTaskList()
    rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
    return render_template('index.html',tsklist=tsklist,reqlist=req_list, async_mode=async_mode)

@app.route('/', methods=['POST'])
def indexpost():
    #Read the type of request and process
    posttype=request.form['type']
    print(posttype)
    tsklist=dbinterface.getTaskList()
    return render_template('index.html',tsklist=tsklist, async_mode=async_mode)
#Define configuration page
@app.route('/configuration')
def config():
    
    rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
    return render_template('configuration.html',rbtlist=rc_list)

@app.route('/taskmodelquery')
def taskmodelconfig():
    return render_template('taskmodelquery.html')

@app.route('/taskmodelquery', methods=['POST'])
def taskmodelconfigget():
    text = request.form['text']
    subtsklist=dbinterface.getSubTaskListByID(text)
    return render_template('taskmodelquery.html',subtsklist=subtsklist,subtsklen=len(subtsklist))

@app.route('/taskmodelcreate')
def taskmodelcreate():
    return render_template('taskmodelcreate.html')





# Routes for task create
@app.route('/taskmodelcreate', methods=['POST'])
def taskmodelcreatepost():
    #Read the type of request and process
    posttype=request.form['type']
    print(posttype)
    
    if(posttype=='createtm'):
        print('Create task model')
        tskmodno=request.form['tskmodno']
        print(tskmodno)
        querysublist=dbinterface.getSubTaskListByID(int(tskmodno))
        print(len(querysublist))
        #Check if task model id exist
        if(len(querysublist)==0):
            dbinterface.writeSubTask(subtasklist)
            print('Task Model created!')
        else:
            print('Task Model already exist, please delete old task model to create new task model')
        return render_template('taskmodelcreate.html')

    if(posttype=="clear"):
        print('Run clear routine')
        subtasklist.clear()
        return render_template('taskmodelcreate.html')
    if posttype=="addstep":
        tskmodno=request.form['tskmodno']
        sel=request.form['gridRadios']
        if(sel=='CustomCommand'):
            cmd=request.form['custcmd']
            print(cmd)
            print(len(subtasklist))
            st=SubTask(tskmodno,sel,str(len(subtasklist)+1),cmd)
            subtasklist.append(st)
        else:
            print(tskmodno)
            print(sel)
            print(len(subtasklist))
            st=SubTask(tskmodno,sel,str(len(subtasklist)+1),'')
            subtasklist.append(st)

        return render_template('taskmodelcreate.html',subtsklist=subtasklist,tskmod=tskmodno)

@socketio.event
def my_event(message):
    session['receive_count'] = session.get('receive_count', 0) + 1
    forjson=tc.toJSON()
    emit('my_response',
         {'data': message['data'], 'count': session['receive_count'],'class': forjson})

# Receive the test request from client and send back a test response
@socketio.on('test_message')
def handle_message(data):
    print('received message: ' + str(data))
    emit('test_response', {'data': 'Test response sent'})

# Broadcast a message to all clients
@socketio.on('broadcast_message')
def handle_broadcast(data):
    print('received: ' + str(data))
    emit('broadcast_response', {'data': 'Broadcast sent'}, broadcast=True)

@socketio.event
def connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)
    emit('my_response', {'data': 'Connected', 'count': 0})

if __name__ == '__main__':
    app.run()
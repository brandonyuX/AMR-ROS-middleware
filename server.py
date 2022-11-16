from cgi import test
from flask import Flask, render_template,request,session,make_response,redirect,url_for,jsonify
import interface.dbinterface as dbinterface
import main
import test_wo
from mwclass.workorder import WO
from mwclass.robotconfig import RobotConfig
import interface.robotinterface as robotinterface
from mwclass.subtask import SubTask
from flask_socketio import SocketIO, emit
from threading import Lock
import json
from flask import Blueprint, render_template, flash
from flask_simplelogin import SimpleLogin
from flask_login import login_required, current_user,LoginManager,login_user,logout_user,UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from flask_sqlalchemy import SQLAlchemy
import schedulers.rbtscheduler as masterscheduler
from wtforms.validators import InputRequired, Length, ValidationError
import threading
from flask_bcrypt import Bcrypt
import time

import logging
import os.path
import json






# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask("RMS-Server")
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
actiondict={'0':'Move','1':'Unload','2':'Load','3':'Custom Command'}
subtasklist=[]
tclist=[]

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'thisisasecretkey'

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            raise ValidationError(
                'That username already exists. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField(validators=[
                           InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField(validators=[
                             InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

    submit = SubmitField('Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('index'))
    return render_template('login.html', form=form)

@ app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))

    return render_template('register.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/navbar', methods=['GET'])
@login_required
def nav():
    return render_template('navbar.html')

 
#Define homepage 
@app.route('/')
@login_required
def index():
    tsklist=dbinterface.getTaskList()
    rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
    return render_template('index-test.html',tsklist=tsklist,reqlist=req_list,rbtlist=rbt_list, async_mode=async_mode)

@app.route('/', methods=['POST'])
@login_required
def indexpost():
    #Read the type of request and process
    posttype=request.form['type']
    print(posttype)
    if(posttype=='simulate'):
        main.run()
        
    if(posttype=="cleartask"):
        dbinterface.updateRbtStatus(True,1)
        dbinterface.updateReqStatus('NEW',1)
        dbinterface.updateRbtMsg(1,'Task cancelled')
        dbinterface.deltask(1)
    if(posttype=="stn1"):
        dbinterface.updateReqDest('Station 1',1)
        dbinterface.deltask(1)
    if(posttype=="stn2"):
        dbinterface.updateReqDest('Station 2',1)
        dbinterface.deltask(1)
    if(posttype=="localize"):
        robotinterface.localize(1)
    if(posttype=='abort'):
        robotinterface.abort()
        
        
    tsklist=dbinterface.getTaskList()
    rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
    return render_template('index-test.html',tsklist=tsklist,reqlist=req_list,rbtlist=rbt_list, async_mode=async_mode)

#Define configuration page
@app.route('/configuration')
@login_required
def config():
    
    rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
    return render_template('configuration.html',rbtlist=rc_list)

@app.route('/taskmodelquery')
@login_required
def taskmodelconfig():
    return render_template('taskmodelquery.html')

@app.route('/taskmodelquery', methods=['POST'])
@login_required
def taskmodelconfigget():
    text = request.form['text']
    subtsklist=dbinterface.getSubTaskListByID(text)
    return render_template('taskmodelquery.html',subtsklist=subtsklist,subtsklen=len(subtsklist))

@app.route('/taskmodelcreate')
@login_required
def taskmodelcreate():
    return render_template('taskmodelcreate.html')

@app.route('/amr-control')
@login_required
def amrcontrol():
    return render_template('amr-control.html')


#Try getting list test
@app.route("/get_list")
@login_required
def get_list():
    rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
    tsk_list=dbinterface.getTaskList()
    result={}
    result['rbtinfo']=[]
    #Convert python object to json
    for rbt in rbt_list:
        rbt_info={}
        rbt_info['x']=rbt.x
        rbt_info['y']=rbt.y
        rbt_info['r']=rbt.r
        rbt_info['msg']=rbt.msg
        rbt_info['rid']=rbt.rid
        rbt_info['avail']=rbt.avail
        rbt_info['currloc']=rbt.currloc
        result['rbtinfo'].append(rbt_info)
    
    #Convert task table information to json
    result2={}
    result2['taskinfo']=[]
    #Convert python object to json
    for tsk in tsk_list:
        tsk_info={}
        tsk_info['tid']=tsk.tid
        tsk_info['rid']=tsk.rid
        tsk_info['reqid']=tsk.reqid
        tsk_info['currstep']=tsk.currstep
        tsk_info['endstep']=tsk.endstep
        if tsk.comp==1: 
            tsk_info['completed']='Completed Task' 
        else:
            tsk_info['completed']='Active Task'
       
        result2['taskinfo'].append(tsk_info)

    #Convert plc request table information to json
    result3={}
    result3['reqinfo']=[]
    #Convert python object to json
    for req in req_list:
        req_info={}
        req_info['plcid']=req.plcid
        req_info['reqid']=req.reqid
        req_info['destloc']=req.destloc
        req_info['tskmodno']=req.tskmodno
        req_info['status']=req.status

        
       
        result3['reqinfo'].append(req_info)
    
    msinfo=dbinterface.readLog('ms')
    #print(msinfo)


    
    
    #print(result)
    return make_response({"rbtarr": json.dumps(result),"taskarr":json.dumps(result2),"reqarr":json.dumps(result3),"msinfo":msinfo})


# Routes for task create
@app.route('/taskmodelcreate', methods=['POST'])
@login_required
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

    elif(posttype=="clear"):
        print('Run clear routine')
        subtasklist.clear()
        return render_template('taskmodelcreate.html')
    elif (posttype=="addstep"):
        print('enter add step')
        tskmodno=request.form['tskmodno']
        sel=request.form['gridRadios']
        print(tskmodno+' '+sel)
        if(sel=='CustomCommand'):
            cmd=request.form['custcmd']
            print(cmd)
            print(len(subtasklist))
            st=SubTask(1,tskmodno,sel,str(len(subtasklist)+1),len(subtasklist),cmd)
            subtasklist.append(st)
        else:
            print(tskmodno)
            print(sel)
            print(len(subtasklist))
            st=SubTask(1,tskmodno,sel,str(len(subtasklist)+1),len(subtasklist),'')
            subtasklist.append(st)

        return render_template('taskmodelcreate.html',subtsklist=subtasklist,tskmod=tskmodno)


#API Section
#API for MES communication

#Ingress 

#Route to create work order 
@app.route('/syngenta/rm/production/createwo',methods=['POST'])
def createWOTask():
    #Receive body information
    recv=request.get_data()
    #Parse to json object from string
    parsedJSON= json.loads(recv)
    #Send information to database
    wolist=[]
    for item in parsedJSON:
        msg='Word Order ID:{}\nBatch ID:{}\nRequired Quantity:{}\nFill Volume:{}ml\nPriority:{}\n'.format(item['wo_id'],item['details']['batch_id'],item['details']['req_qty'],item['details']['fill_vol'],item['details']['priority'])
        print(msg)
        wo=WO(item['wo_id'],item['details']['batch_id'],item['details']['fill_vol'])
        wolist.append(wo)

    #Write to Work Order Table in database
    dbinterface.writeWO(wolist)
    response = make_response("Work Order Generated", 200)
    response.mimetype = "text/plain"
    return response

#Route for information carton completion status
@app.route('/syngenta/rm/production/cartonready',methods=['POST'])
def cartonReady():
    woid=request.values.get('woid')

    print(woid)
    response = make_response("WMS Creation", 200)
    response.mimetype = "text/plain"
    return response

#Egress





#API to communicate with WMS
#Main Controller to RMS API


#Ingress
@app.route('/syngenta/rm/wms/taskstatus',methods=['POST'])
def queryTaskStatus():
    woid=request.values.get('woid')

    print(woid)
    response = make_response("WMS Creation", 200)
    response.mimetype = "text/plain"
    return response

@app.route('/syngenta/rm/wms/customrequest',methods=['POST'])
def createCustomReq():
    woid=request.values.get('woid')

    print(woid)
    response = make_response("WMS Creation", 200)
    response.mimetype = "text/plain"
    return response

@app.route('/syngenta/rm/wms/taskcreated',methods=['POST'])
def createWMSTask():
    woid=request.values.get('woid')

    print(woid)
    response = make_response("WMS Creation", 200)
    response.mimetype = "text/plain"
    return response
    
@app.route('/syngenta/rm/wms/manualtask',methods=['POST'])
def createManualTask():
    woid=request.values.get('woid')

    print(woid)
    response = make_response("WMS Creation", 200)
    response.mimetype = "text/plain"
    return response




    
# @socketio.event
# def connect():
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = socketio.start_background_task(background_thread)
#     emit('my_response', {'data': 'Connected', 'count': 0})

#Initialze all interfaces
dbinterface.startup()
masterscheduler.startup()
robotinterface.startup()

#threading.Thread(target=lambda: app.run())

#app.run()

t1=threading.Thread(target=app.run(),daemon=True)
t1.start()
#t1.join()

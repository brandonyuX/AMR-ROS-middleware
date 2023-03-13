# from cgi import test
from flask import Flask, render_template,request,session,make_response,redirect,url_for,jsonify
import interface.dbinterface as dbinterface
import schedulers.woscheduler as woscheduler
import main
from mwclass.workorder import WO
from mwclass.robotconfig import RobotConfig
import interface.robotinterface as robotinterface
import interface.wmsinterface as wmsinterface
import interface.chrinterface as chrinterface
from mwclass.subtask import SubTask
import interface.plcinterface as plcinterface
from flask_socketio import SocketIO, emit
from threading import Lock
import json
from flask import Blueprint, render_template, flash
from flask_simplelogin import SimpleLogin
from flask_login import login_required, current_user,LoginManager,login_user,logout_user,UserMixin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, validators
from flask_sqlalchemy import SQLAlchemy
import schedulers.rbtscheduler as rbtscheduler
from wtforms.validators import InputRequired, Length, ValidationError
import threading
from flask_bcrypt import Bcrypt
import time
import requests
import yaml
import re
import sys
from datetime import datetime
import logging
import os.path
import json,os,random








# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask("RMS-Server")
log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)
app.debug=False

# socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()
actiondict={'0':'Move','1':'Unload','2':'Load','3':'Custom Command'}
subtasklist=[]
tclist=[]



with open('server-config.yaml', 'r') as f:
    doc = yaml.safe_load(f)

wmsip=doc['SERVER']['WMSIP']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'thisisasecretkey'

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("rms-message.log", "a")
   
    def write(self, message):
        self.terminal.write(message)
        
        self.log.write('{} {}'.format(datetime.now(),message))  

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass    

sys.stdout = Logger()







class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"



# @app.before_first_request
# def create_tables():
#     db.create_all()

@login_manager.user_loader
def load_user(user_id):
    
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
                           InputRequired(message='Input a username.'), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

    password = PasswordField("Password", validators=[validators.DataRequired(),
                            validators.EqualTo("confirm_password", message='Passwords must match'),
                            InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "New Password"})

    confirm_password = PasswordField("Confirm Password", validators=[
                             InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": "Confirm Password"})

    submit = SubmitField('Register')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(
            username=username.data).first()
        if existing_user_username:
            # raise ValidationError(
            #     'That username already exists. Please choose a different one.')
            return False
        return True


# class LoginForm(FlaskForm):
#     username = StringField(validators=[
#                            InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Username"})

#     password = PasswordField(validators=[
#                              InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})

#     submit = SubmitField('Login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        if len(request.form.get("username", "")) != 0 and len(request.form.get("password", "")) != 0:
            username = request.form["username"]
            password = request.form["password"]
            account = dbinterface.getAccount(username)
            if account:
                if bcrypt.check_password_hash(account.password, password):
                    session['loggedin'] = True
                    session['id'] = account[0]  #account[0] referring to first column of user table which is "id"
                    session['username'] = account[1]    #account[0] referring to first column of user table which is "username"
                    # Redirect to home page
                    print('{0} (id:{1}) successfully login to M8M RMS!'.format(account[1], account[0]))
                    return redirect(url_for('/'))
                else:
                    # Account doesnt exist or username/password incorrect
                    return 'Incorrect username or password!'
            else:
                return 'Username not found!'
        else: 
            return 'Kindly fill up your username and password!'
    else:
        msg = request.args.get('msg')
        return render_template('login-new.html', msg=msg)
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.username.data).first()
    #     if user:
    #         if bcrypt.check_password_hash(user.password, form.password.data):
    #             login_user(user)
    #             return redirect(url_for('index'))
    # return render_template('login-new.html', form=form)

@ app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST" and 'username' in request.form and 'password' in request.form and 'confirmPassword' in request.form:
        if len(request.form.get("username", "")) != 0 and len(request.form.get("password", "")) != 0 and len(request.form.get("confirmPassword", "")) != 0:
            username = request.form['username']
            password = request.form['password']
            confirmPassword = request.form['confirmPassword']
            # Check if account exists using MySQL
            userExist = dbinterface.userExist(username)
            # If account exists show error and validation checks
            if userExist:
                return 'Account already exists!'
            elif not re.match(r'^[a-zA-Z0-9]{4,20}$', username):
                return 'Invalid username. Please enter a username consisting of only alphabets and numbers with a length between 4 and 20 characters.'
            elif password != confirmPassword:
                return 'Confirm password not match with Password'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                hashed_password = bcrypt.generate_password_hash(password)
                dbinterface.addUser(username,hashed_password)            
                return 'Account successfully registered!'
        else:
            return 'Kindly fill up all the field!'
    else:
        return render_template('register-new.html')

    # form = RegisterForm()

    # if request.method == 'GET':
    #     print('I receive get request')
    #     return render_template('register-new.html', form=form)

    # if request.method == 'POST':
    #     print('I receive post request')
    #     if form.validate_on_submit():
    #         hashed_password = bcrypt.generate_password_hash(form.password.data)
    #         new_user = User(username=form.username.data, password=hashed_password)
    #         db.session.add(new_user)
    #         db.session.commit()
    #         return redirect(url_for('login'))
        
        # if form.validate_username(form.username) == False:
        #     error_message = 'Username already exist. Please change to another username.'
        #     print(error_message)
        #     return render_template('register-new.html', error=error_message)

        # error_message = 'There is error in information provided'
        # print(error_message)
        # return render_template('register-new.html', error=error_message)

        # else:
        #     error = 'Username or password not match!'
        #     return 
        # print('I am outside')
    

@app.route('/logout', methods=['GET', 'POST'])
# @login_required
def logout():
    if 'loggedin' in session:
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)
        
    # Redirect to login page
    return redirect(url_for('login'))
    
    # logout_user()
    # return redirect(url_for('login'))


@app.route('/navbar', methods=['GET'])
# @login_required
def nav():
    if 'loggedin' in session:
        return render_template('navbar.html')

#Reset function for amr
@app.route('/amr/action/<act>')
def action(act):
    if 'loggedin' in session:
        match act:
            case 'reset':
                robotinterface.reset_motor()
            case 'tocharge':
                chrinterface.gocharge()
            case 'stopcharge':
                chrinterface.stopcharge()
            case 'cancelnav':
                robotinterface.cancelnav()

        response = make_response("Command sent to AMR", 200)
        response.mimetype = "text/plain"
        return response

#Save point function for amr
@app.route('/amr/save/<stn>')
def savepoint(stn):
    if 'loggedin' in session:
        #Save point code
        robotinterface.save_point(stn=stn)
        response = make_response("Command sent to AMR", 200)
        response.mimetype = "text/plain"
        return response
 #Move function for amr
@app.route('/amr/move/<stn>')
def move(stn):
    if 'loggedin' in session:
        robotinterface.publish_cmd(rid=1,stn=stn)
        while  os.environ['reached'] != 'True':
            pass
        dbinterface.updateRbtLoc(rbtid=1,currloc=stn)

        response = make_response("Command sent to AMR", 200)
        response.mimetype = "text/plain"
        return response
#Define homepage 
# @app.route('/')
# # @login_required
# def index():
#     # Check if user is loggedin
#     if 'loggedin' in session:
#         # User is loggedin show them the home page
#         tsklist=dbinterface.getProductionTaskList()
#         rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
#         return render_template('index.html',tsklist=tsklist,reqlist=req_list,rbtlist=rbt_list, async_mode=async_mode)
#     # User is not loggedin redirect to login page
#     return redirect(url_for('login'))

@app.route('/')
# @login_required
def index():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
       
        return render_template('index-new.html', username=session['username'], async_mode=async_mode)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/', methods=['POST'])
# @login_required
def indexpost():
    if 'loggedin' in session:
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
            
        tsklist=dbinterface.getProductionTaskList()
        rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
        cus_tsk_list=dbinterface.getCustomTaskList()
        return render_template('index-new.html',tsklist=tsklist,reqlist=req_list,rbtlist=rbt_list, cus_tsk_list=cus_tsk_list, async_mode=async_mode)
    
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))   

#Define configuration page
@app.route('/configuration', methods=['GET', 'POST'])
# @login_required
def config():
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == "POST":
            if len(request.form.get("rip", "")) != 0 and len(request.form.get("rid", "")) != 0:
                dbinterface.updateRip(request.form['rip'], request.form['rid'])
                return "Robot IP updated successfully"
            elif "regRbtForm"in request.form:
                status=dbinterface.registerRbt(request.form['rbtID'],request.form['rbtAlias'],request.form['tskAccpThres'],
                request.form['defLoc'],request.form['rbtIP'],request.form['chrgThres'],request.form['idleTime'])
                response_data = {
                    'rbtInfo': request.form.to_dict(),
                    'message': status
                }
                return jsonify(response_data)
        else:
            rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()
            return render_template('configuration-new.html',rbtlist=rc_list, username=session['username'])        

@app.route('/taskmodelquery', methods=['POST','GET'])
# @login_required
def taskmodelconfig():
    # Check if user is loggedin
    if 'loggedin' in session:
        if request.method == 'POST':
            queryID = request.form['queryID']
            subtsklist=dbinterface.getSubTaskListByID(queryID)
            sbList={}
            sbList['sbList']=[]
            for st in subtsklist:
                sbList['sbList'].append(st.__dict__)
            jsonString = json.dumps(sbList)
            return jsonify(jsonString)
            # return render_template('taskmodelquery-new.html',subtsklist=subtsklist,subtsklen=len(subtsklist), username=session['username'])
        else:
            return render_template('taskmodelquery-new.html', username=session['username'])

@app.route('/taskmodelcreate')
# @login_required
def taskmodelcreate():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('taskmodelcreate-new.html', username=session['username'])

@app.route('/amr-control')
# @login_required
def amrcontrol():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('amr-control.html',username=session['username'], async_mode=async_mode)


@app.route('/amr-control', methods=['POST'])
# @login_required
def amrcontrolpost():
    if 'loggedin' in session:
        #Read the type of request and process
        posttype=request.form['type']
        print(posttype)
        match posttype:
            case 'charge':
                chrinterface.gocharge()    
            case 'stopcharge':
                chrinterface.stopcharge()    
        return redirect(request.url)
        return render_template('amr-control.html',username=session['username'], async_mode=async_mode)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))   

@app.route('/amr-settings')
# @login_required
def amrsettings():
    # Check if user is loggedin
    if 'loggedin' in session:
        return render_template('amr-settings.html')


#Try getting list test
@app.route("/get_list")
# @login_required
def get_list():
    # Check if user is loggedin
    if 'loggedin' in session:
        rc_list,sm_list,req_list,rbt_list=dbinterface.getBundleInfo()

        result={}
        result['rbtinfo']=[]
        #Convert python object to json
        for rbt in rbt_list:
            # rbt_info={}
            # rbt_info['x']=rbt.x
            # rbt_info['y']=rbt.y
            # rbt_info['r']=rbt.r
            # rbt_info['msg']=rbt.msg
            # rbt_info['rid']=rbt.rid
            # rbt_info['avail']=rbt.avail
            # rbt_info['currloc']=rbt.currloc
            result['rbtinfo'].append(rbt.__dict__)
        
        tsk_list=dbinterface.getProductionTaskList()
        #Convert task table information to json
        result2={}
        result2['taskinfo']=[]
        #Convert python object to json
        for tsk in tsk_list:
            result2['taskinfo'].append(tsk.to_dict())
            # tsk_info={}
            # tsk_info['tid']=tsk.tid
            # tsk_info['rid']=tsk.rid
            # tsk_info['reqid']=tsk.reqid
            # tsk_info['currstep']=tsk.currstep
            # tsk_info['endstep']=tsk.endstep
            # if tsk.comp==1: 
            #     tsk_info['completed']='Completed Task' 
            # else:
            #     tsk_info['completed']='Active Task'
            
        # print(len(result2['taskinfo']))

        #Convert plc request table information to json
        result3={}
        result3['reqinfo']=[]
        #Convert python object to json
        for req in req_list:
            # req_info={}
            # req_info['plcid']=req.plcid
            # req_info['reqid']=req.reqid
            # req_info['destloc']=req.destloc
            # req_info['tskmodno']=req.tskmodno
            # req_info['status']=req.status

            result3['reqinfo'].append(req.__dict__)
        
        #Get Custom Task List & Convert to json
        cus_tsk_list=dbinterface.getCustomTaskList()
        result4={}
        result4['custskarr']=[]
        #Convert python object to json
        for cus_tsk in cus_tsk_list:
            result4['custskarr'].append(cus_tsk.to_dict())

        #Get Custom Request List & Convert to json
        cus_req_list=dbinterface.getCustomRequestList()
        result5={}
        result5['cusreqarr']=[]
        #Convert python object to json
        for cus_req in cus_req_list:
            result5['cusreqarr'].append(cus_req.__dict__)

        #Get WO List & Convert to json
        WOStn = request.args.get('WOStn')
        wo_per_stn_list=dbinterface.getWOList(WOStn)
        result6={}
        result6['woperstnarr']=[]
        #Convert python object to json
        for wo_line in wo_per_stn_list:
            result6['woperstnarr'].append(wo_line.__dict__)
        
        msinfo=dbinterface.readLog('ms')

        return make_response({"rbtarr": json.dumps(result),"taskarr":json.dumps(result2),"reqarr":json.dumps(result3),"custskarr":json.dumps(result4),"cusreqarr":json.dumps(result5),"woperstnarr":json.dumps(result6),"msinfo":msinfo})


# Routes for task create
@app.route('/taskmodelcreate', methods=['POST'])
# @login_required
def taskmodelcreatepost():
    # Check if user is loggedin
    if 'loggedin' in session:
        #Read the type of request and process
        posttype=request.form['actionTrigger']
        print("Button Listener: " + posttype + " (Triggered)")
        
        if (posttype == "defineST"):
            print('Start defining Sub Task')
            tskmodno=request.form['tskmodno']
            sel=request.form['gridRadios']
            print("Task Model (ID:" + tskmodno + ') Action: '+sel)
            if(sel=='Custom Command'):
                cmd=request.form['custCmd']
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

            return render_template('taskmodelcreate-new.html',subtsklist=subtasklist,tskmod=tskmodno, username=session['username'])
        
        elif (posttype == "clearST"):
            print('Run clear routine')
            subtasklist.clear()
            return render_template('taskmodelcreate-new.html', username=session['username'])
        
        elif (posttype=='registerTM'):
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
            return render_template('taskmodelcreate-new.html', username=session['username'])


#API Section
#API for MES communication

#Ingress 

#Route to create work order 
#{"Batch ID": String, "Init SN": String, "Manufacture Date": String, "Fill and Pack Date": String, "Fill Volume": Number, "Target Torque": Number, "Work Orders": [String, String, String, ...]}

@app.route('/syngenta/rm/production/createwo',methods=['POST'])
def createWOTask():

    avail=True
    for i in range(1,7):
        #Set avaialability to false if any station is not available
        stnstate,wowstate=plcinterface.checkStnStatus(i)
        if stnstate in [4,5] or wowstate in [2,3]:
            avail=False

    #Check if station available
    if avail:
        #Receive body information
        recv=request.get_data()
        
        # for item in parsedJSON:
        #     # msg='Batch ID:{}\nInit SN:{}\nManufacture Date:{}\nFill and Pack Date:{}ml\nFill Volume:{}\nTarget Torque:{}\nWork Orders:{}\n'.format(item['Batch ID'],item['Init SN'],item['Manufacture Date'],item['Fill and Pack Date'],item['Fill Volume'],item['Target Torque'],item['Work Orders'][0])
        #     # print(msg)
        try:
            #print(len(parsedJSON['Work Orders']))
            dbinterface.voidWO()
            plcinterface.initTag()
            #plcinterface.setNewBatch()
            print(recv)
        #Parse to json object from string
            parsedJSON= json.loads(recv)
            #Send information to database
            print(parsedJSON)
            #
            wolist=[]
            for i in range(len(parsedJSON['Work Orders'])):
                
                wo=WO(parsedJSON['Batch ID'],parsedJSON['Init SN'],parsedJSON['Manufacture Date'],parsedJSON['Fill and Pack Date'],parsedJSON['Fill Volume'],parsedJSON['Target Torque'],parsedJSON['Work Orders'][i],expdate=parsedJSON['Expiry Date'],ordernum=i,itemtype=parsedJSON['Item Type'])
                wolist.append(wo)
            os.environ['currentBatch']=parsedJSON['Item Type']
            
             #Write to Work Order Table in database
            dbinterface.writeWO(wolist)
            #time.sleep(1)
            
            response = make_response("Work Order Received", 200)
            response.mimetype = "text/plain"
            return response
        except Exception as e:
            print(e)
            response = make_response("Invalid JSON format", 400)
            response.mimetype = "text/plain"
            return response

        #Tell MES station not ready if state is not 1


       
    else:
        print('<SVR> Station not ready')
        response = make_response("Stations not ready", 400)
        response.mimetype = "text/plain"
        return response 
#Route for information carton completion status
@app.route('/syngenta/rm/production/cartonready',methods=['POST'])
def cartonReady():
    #Call WMS to receive item
    rand_batch=random.randrange(100000,999999)
    wmsinterface.reqsfc(rand_batch)
    #Signal wait complete
    os.environ['waitcomplete'] = 'True'
    #print('print carton ready')
    response = make_response("Carton Ready Received", 200)
    response.mimetype = "text/plain"
    return response

#Signal from wms to indicate that bin is ready and scanned
@app.route('/syngenta/rm/wms/stationoutready',methods=['POST'])
def binReady():
    
    #Signal wait complete
    os.environ['wmsrdy'] = 'True'
    
    #print('print carton ready')
    response = make_response("Bin ready acknowledged", 200)
    response.mimetype = "text/plain"
    return response

#Custom request from wms
@app.route('/syngenta/rm/wms/customrequest',methods=['POST'])
def createCReq():
    os.environ['creqack']='False'
    #Receive body information
    recv=request.get_data()
    print('Message custom request:{}'.format(recv))
    #Parse to json object from string
    parsedJSON= json.loads(recv)
    #Send information to database
    # for item in parsedJSON:
    reqid=parsedJSON['WMSRequestID']
    priority=parsedJSON['Priority']
    dbinterface.writeCustomReq(reqid,priority)
    response = make_response("Custom Request Received", 200)
    response.mimetype = "text/plain"
    return response
 
       
#Acknowledgement from WMS that the custom request is received
@app.route('/syngenta/rm/wms/customreqack',methods=['POST'])
def CreqACK():
    os.environ['creqack']='True'
    response = make_response("Custom Request ACK Received", 200)
    response.mimetype = "text/plain"
    return response

 #WMS task for custom request from WMS (Legacy API)
# @app.route('/syngenta/rm/wms/taskcreated',methods=['POST'])
# def createWMSTask():
#     #Receive body information
#     recv=request.get_data()
#     #Parse to json object from string
#     parsedJSON= json.loads(recv)
#     #Send information to database
#     print(parsedJSON)
#     wolist=[]
#     for item in parsedJSON:
#         reqid=item['WMSRequestID']
#         tskid=item['WMSTaskID']
#         action=item['Action']
#         dest=item['Destination']
        
#         match action:
#             case '1':
#                 print('<SVR> Write retrieval action to custom task table')
#                 dbinterface.insertCustomTask('WH;{}'.format(dest),7,reqid,tskid)
#                 pass
#             case '2':
#                 print('<SVR> Write store action to custom task table')
#                 dbinterface.insertCustomTask('{};WH'.format(dest),8,reqid,tskid)
#                 pass
#             case '3':
#                 print('<SVR> Write custom action to db')
#                 dbinterface.insertCustomTask(dest,9,reqid,tskid)
#                 pass
#             case '4':
#                 print('<SVR> Write manual task to db')
#                 pass
    #Determine action
    # 1. Retrieve
    # 2. Store
    # 3. Custom
    # 4. Manual
    
    
        
              
    # response = make_response("Task Accepted", 200)
    # response.mimetype = "text/plain"
    # return response

#Next action from WMS
#Default amr not in motion
os.environ['reached'] = 'True'
@app.route('/syngenta/rm/wms/nextaction',methods=['POST'])
def nextAction():
    if os.environ['reached'] != 'True':
        response = make_response("AMR still in motion!", 200)
        response.mimetype = "text/plain"
        return response
    else:
    #Receive body information
        recv=request.get_data()
        #Parse to json object from string
        parsedJSON= json.loads(recv)
        #Send information to database
        
        print(recv)
        
        os.environ['waitcustom'] = parsedJSON['NextAction']
        
        if(os.environ.get('waitcustom')=='Continue'):
            ioc=robotinterface.itemOnConveyor()
            if(ioc=='EMPTY' ):
                print('<MS> Detected no tote when asked to continue')
                #Tell WMS no tote on AMR
                response = make_response("Detected no tote when asked to continue", 200)
                response.mimetype = "text/plain"
                return response 
               
            else:
                os.environ['waitcustom']='Continue-Confirm'
                
        elif(os.environ.get('waitcustom')=='Cancel'):
            ioc=robotinterface.itemOnConveyor()
            if ioc=="BLOCKED" or ioc=='OK' or ioc=='ALL OCCUPIED':
                #Tell WMS got tote on AMR
                print('<MS> Detected tote when asked to cancel')
                response = make_response("Detected tote when asked to cancel", 200)
                response.mimetype = "text/plain"
                return response 
                
                
              
            else:
                
                os.environ['waitcustom']='Cancel-Confirm'
            
            #os.environ['waitcustom']='Confirmed'
        #print('<SVR> Next action from WMS: {}'.format(parsedJSON['NextAction']))
        
        response = make_response("Ok", 200)
        response.mimetype = "text/plain"
        return response      
#Item ready for custom location
@app.route('/syngenta/mc/amr/custom/ItemReady',methods=['POST'])
def informItemRdy():
    
    response = make_response("Acknowledged Item Ready", 200)
    response.mimetype = "text/plain"
    return response
 
#Item removed for custom location
@app.route('/syngenta/mc/amr/custom/ItemRemoved',methods=['POST'])
def informItemRemoved():
    
    response = make_response("Acknowledged Item Removed", 200)
    response.mimetype = "text/plain"
    return response     


#Egress

   




#API to communicate with WMS
#Main Controller to RMS API


#Ingress
@app.route('/syngenta/rm/wms/taskstatus',methods=['POST'])
def queryTaskStatus():
    
    #woid=request.values.get('woid')
    #Receive body information
    recv=request.get_data()
    #Parse to json object from string
    parsedJSON= json.loads(recv)
    #Send information to database
    
    wmstid=parsedJSON['WMSTaskID']
    tstatus=parsedJSON['TaskStatus']
    
    if(tstatus=='Completed'):
        os.environ['manualtask']='False'

    
    response = make_response("Completed signal acknowledged", 200)
    response.mimetype = "text/plain"
    return response

@app.route('/syngenta/rm/wms/customrequest',methods=['POST'])
def createCustomReq():
    
    response = make_response("WMS Creation", 200)
    response.mimetype = "text/plain"
    return response

@app.route('/syngenta/rm/wms/taskcreated',methods=['POST'])
def createTask():
   
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


#Query if station is empty (Detect head and tail sensor)
@app.route('/syngenta/rm/wms/stationempty',methods=['POST'])
def checkEmpty():
    
    if plcinterface.checkEmpty("WH"):
        dictToSend = {'Status':'Empty'}
    else:
        dictToSend = {'Status':'Occupied'}
    response = make_response(dictToSend, 200)
    response.mimetype = "application/json"
    return response

# #To Be Deleted
# @app.route('/amrcontrolpanel')
# def amrcontrolpanel():
#     return render_template("amr-controlpanel-nelson.html")


# @socketio.on('connect')
# def test_connect():
#     print('Client connected')
#     emit('update_table', rows)

# @socketio.on('disconnect')
# def test_disconnect():
#     print('Client disconnected')

# @socketio.on('update_database')
# def update_database(data):
#     name = data['name']
#     emit('update_table', rows, broadcast=True)


# @socketio.event
# def connect():
#     global thread
#     with thread_lock:
#         if thread is None:
#             thread = socketio.start_background_task(background_thread)
#     emit('my_response', {'data': 'Connected', 'count': 0})



#threading.Thread(target=lambda: app.run())


#Initialize all interfaces
dbinterface.startup()

robotinterface.startup()
plcinterface.startup()

rbtscheduler.startup()
woscheduler.startup()

# time.sleep(10)
app.run(host='0.0.0.0',debug=False)
# app.run(host='0.0.0.0',debug=False)

# t1=threading.Thread(target=app.run(),daemon=True)
# t1.start()
#t1.join()

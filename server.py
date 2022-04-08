from flask import Flask, render_template,request
import interface.dbinterface as dbinterface
from mwclass.subtask import SubTask

app = Flask('testapp')
actiondict={'0':'Move','1':'Unload','2':'Load','3':'Custom Command'}
subtasklist=[]


@app.route('/')
def index():
    tsklist=dbinterface.getTaskList()
    return render_template('index.html',tsklist=tsklist)

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

@app.route("/clearsubtask/", methods=['POST'])
def clear():
    print('Run clear routine')
    subtasklist.clear()
    return render_template('taskmodelcreate.html')

@app.route("/createtm/", methods=['POST'])
def createtm():
    print('Create task model')
    tskmodno=request.form['tskmodno']
    querysublist=dbinterface.getSubTaskListByID(int(tskmodno))
    #print(len(querysublist))
    #Check if task model id exist
    if(len(querysublist)==0):
        dbinterface.writeSubTask(subtasklist)
        print('Task Model created!')
    else:
        print('Task Model already exist, please delete old task model to create new task model')
    return render_template('taskmodelcreate.html')


@app.route('/taskmodelcreate', methods=['POST'])
def taskmodelcreatepost():
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
    
    # st=SubTask(tskmodno,sel,cmd,len(subtasklist+1))
    # subtasklist.append(st)

    return render_template('taskmodelcreate.html',subtsklist=subtasklist,tskmod=tskmodno)


if __name__ == '__main__':
    app.run()
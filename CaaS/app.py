import time

import torch
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit, rooms, join_room, close_room
from flaskext.mysql import MySQL
from transformers import *

################## SERVER SETUP ######################

app = Flask(__name__)
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'nervaidb'
app.config['SECRET_KEY'] = 'secret!'

serverhost = '127.0.0.1'
serverport = 8082

CORS(app)
mysql = MySQL(app)
db = mysql.connect().cursor()
socketio = SocketIO(app, cors_allowed_origins="*")

################## CHATBOT ######################

def Replier(para, ques):
    st = time.time()

    input_text = ques + " [SEP] " + para
    input_ids = tokenizer.encode(input_text)
    start_scores, end_scores = model(torch.tensor([input_ids]).to(device))
    all_tokens = tokenizer.convert_ids_to_tokens(input_ids)
    ans = ' '.join(all_tokens[torch.argmax(start_scores): torch.argmax(end_scores) + 1])
    ans = ans.replace(' ##', "")

    # input_text = "[CLS] " + question + " [SEP] " + text + " [SEP]"
    # input_ids = tokenizer.encode(input_text)
    # token_type_ids = [0 if i <= input_ids.index(102) else 1 for i in range(len(input_ids))]
    # start_scores, end_scores = model(torch.tensor([input_ids]).to(device), token_type_ids=torch.tensor([token_type_ids]).to(device))
    # all_tokens = tokenizer.convert_ids_to_tokens(input_ids)
    # ans = ' '.join(all_tokens[torch.argmax(start_scores): torch.argmax(end_scores) + 1])
    # ans = ans.replace(' ##', "")

    time_taken = time.time() - st
    print('[=>] Answer: ', ans, " Time:", time_taken)
    return ans

################## Admin Manager ######################

current_admins = []

def getRoomName(sid, botid):
    return str(sid) + "-" + str(botid)

def addAdmin(sid, botid):
    current_admins.append({
        "sid": sid,
        "botid": botid,
        "available": True,
        "room": ""
    })

def isAdmin(sid):
    for admin in current_admins:
        if sid == admin["sid"]:
            return True
    return False

def availableAdmin(botid):
    for admin in current_admins:
        if botid == admin["botid"] and admin["available"]:
            return admin["sid"]
    return None

def removeAdmin(sid):
    for admin in current_admins:
        if sid == admin["sid"]:
            current_admins.remove(admin)
            break

def adminJoinRoom(sid, room):
    for admin in current_admins:
        if sid == admin["sid"] and admin["available"]:
            admin["room"] = room
            admin["available"] = False
            break

def adminLeaveRoom(sid):
    for admin in current_admins:
        if sid == admin["sid"]:
            admin["room"] = ""
            admin["available"] = True
            break

def getAdminRoom(sid):
    for admin in current_admins:
        if sid == admin["sid"]:
            return admin["room"]
    return ""

def getRoomAdmin(room):
    for admin in current_admins:
        if room == admin["room"]:
            return admin["sid"]
    return None

def joinQueryRoom(clientSid, botId):
    adminSid = availableAdmin(botId)
    if adminSid is not None:
        # New Room
        new_Room = getRoomName(clientSid, botId)
        # Admin
        join_room(new_Room, sid=adminSid)
        adminJoinRoom(adminSid, new_Room)
        emit("joinroom", {"msg": "Hey we got client query, We are Switching you to Client", "room": new_Room},
             room=new_Room, skip_sid=request.sid)
        # Client
        join_room(new_Room, sid=request.sid)
        emit("joinroom", {"msg": "Sorry, I don't understand, We are Switching you to Our Admin"},
             room=new_Room, skip_sid=adminSid)
        return True
    else:
        return False

def getClientRoom(clientSid):
    rlist = rooms(sid=clientSid)
    if len(rlist) > 1:
        return rlist[1]
    return None

def getRoomClient(room):
    return room.split("-")[0]

def whenAdminDisconnect(adminSid):
    adminRoom = getAdminRoom(adminSid)
    if adminRoom is not "":
        roomClientSid = getRoomClient(adminRoom)
        emit("leaveroom", "Client Got Disconnected", room=adminRoom, skip_sid=roomClientSid)
        emit("leaveroom", "You Got Disconnected From Admin", room=adminRoom, skip_sid=adminSid)
        close_room(adminRoom)

def whenClientDisconnect(clientSid):
    clientRoom = getClientRoom(clientSid)
    if clientRoom is not None:
        roomAdminSid = getRoomAdmin(clientRoom)
        if roomAdminSid is not None:
            emit("leaveroom", "Client Got Disconnected", room=clientRoom, skip_sid=clientSid)
            emit("leaveroom", "You Got Disconnected From Admin", room=clientRoom, skip_sid=roomAdminSid)
            adminLeaveRoom(roomAdminSid)
            close_room(clientRoom)

################## Admin Sockets ######################

@socketio.on('adminConnect')
def adminConnect(req):
    if req["Admin"] == 1:
        addAdmin(request.sid, req["BotId"])
        print('[=>] Admin Connected: {}'.format(request.sid))

@socketio.on('disconnect')
def disconnect():
    if isAdmin(request.sid):
        whenAdminDisconnect(request.sid)
        removeAdmin(request.sid)
        print('[=>] Admin Disconnected: {}'.format(request.sid))
    else:
        whenClientDisconnect(request.sid)
        print('[=>] Client Disconnected: {}'.format(request.sid))

@socketio.on('greetingsAdmins')
def greetingsAdmins():
    return {
        "len": 3,
        "msgs": [
            {"msg": "Hey there!", "delay": 1000},
            {"msg": "Welcome Admin😁, Clients are Waiting for you.", "delay": 1700},
            {"msg": "We will Connect you to them Soon.", "delay": 2300}
        ]
    }

@socketio.on('adminQues')
def adminQues(msg):
    emit("adminQues", msg["Question"], room=getRoomName(request.sid, msg["BotId"]))

@socketio.on('adminAns')
def adminAns(res):
    emit("adminAns", res["Ans"], room=res["Room"])

#################### Bot Sockets ########################

# ** TODO **
# Load Greeting Message for custom
# else assign default ones
# **********
@socketio.on('greetings')
def greetings(req):
    res = {
        "len": 2,
        "msgs": [
            {"msg": "Hey there!", "delay": 1000},
            {"msg": "Welcome, Feel free to ask me any question.😁", "delay": 1700}
        ]
    }
    return res

@socketio.on('chatbot')
def chatbot(req):
    db.execute("SELECT paragraph,is_deployed from userpanel_bot where id={}".format(req["BotId"]))
    para = db.fetchone()
    if para and (para[1] or req['Previewbot'] is 1):
        ans = Replier(para[0], req['Question'])
        if '[SEP]' in ans:
            if joinQueryRoom(request.sid, req["BotId"]):
                return {'answer': "[NIL]"}
            else:
                return {'answer': "Sorry, I don't understand"}
        else:
            return {'answer': ans}
    elif para and not para[1]:
        return {'answer': "Bot is under maintenance"}
    else:
        return {'answer': "Bot does not exist"}


@socketio.on('oldhomebot')
def oldhomebot(req):
    ans = Replier(req['Paragraph'], req['Question'])
    return {'answer': ans}

################## APIS ######################

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/old')
def oldhome():
    return render_template('index-old.html')

@app.route('/templatebot')
def templatebot():
    return render_template('get.js', loadurl='http://{}:{}'.format(serverhost, serverport))

@app.route('/admintemplate')
def admintemplate():
    return render_template('get2.js', loadurl='http://{}:{}'.format(serverhost, serverport))

@app.route('/adminbot/<bot_id>')
def adminbot(bot_id):
    return render_template('admin.html', loadurl='http://{}:{}'.format(serverhost, serverport), botid=bot_id)

@app.route('/previewbot/<bot_id>')
def previewbot(bot_id):
    return render_template('preview.html', loadurl='http://{}:{}'.format(serverhost, serverport), botid=bot_id)

################## SERVER RUN ######################

if __name__ == '__main__':
    print('[=>] CaaS Chatbot Server Starting')
    print('[=>] Loading Database...')

    if not mysql:
        print('[!] Error to Connnect Database')
        exit(0)

    print('[=>] Database Loaded!')
    print('[=>] Loading Models...')

    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased-distilled-squad')
    model = DistilBertForQuestionAnswering.from_pretrained('distilbert-base-uncased-distilled-squad')
    # tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    # model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')

    print('[=>] Model Loaded!')

    # device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    device = torch.device('cpu')
    print('[=>] Currently Using Device:', device)

    model.to(device)
    if device.type == 'cuda':
        print(torch.cuda.get_device_name(0))
        print('[=>] Memory Usage:')
        print('[=>] Allocated:', round(torch.cuda.memory_allocated(0) / 1024 ** 3, 1), 'GB')
        print('[=>] Cached:   ', round(torch.cuda.memory_cached(0) / 1024 ** 3, 1), 'GB')

    print('[=>] Service Running on http://{}:{}'.format(serverhost, serverport))
    socketio.run(app, host=serverhost, port=serverport, debug=False)

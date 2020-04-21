import time

import torch
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from flaskext.mysql import MySQL
from flask_socketio import SocketIO, emit
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
socketio = SocketIO(app)


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

################## Sockets ######################

#
# ** TODO **
# Load Greeting Message for custom
# else assign default ones
# **********
@socketio.on('greetings')
def greetings(req):
    data = {
        "len": 2,
        "msgs": [
            {"msg": "Hey there!", "delay": 1000},
            {"msg": "Welcome, Feel free to ask me any question.😁", "delay": 2000}
        ]
    }
    return data

@socketio.on('chatbot')
def chatbot(req):
    db.execute("SELECT paragraph,is_deployed from userpanel_bot where id={}".format(req["BotId"]))
    para = db.fetchone()
    if para and (para[1] or req['Previewbot'] is 1):
        ans = Replier(para[0], req['Question'])
        if '[SEP]' in ans:
            return {'answer': ans}
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

@app.route('/previewbot/<bot_id>', methods=['GET'])
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

import time

import torch
from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
from flask_mysqldb import MySQL
from transformers import *

app = Flask(__name__)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'nervaidb'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306

serverhost = '127.0.0.1'
serverport = 3232

CORS(app)
mysql = MySQL(app)


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


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/old')
def oldhome():
    return render_template('index-old.html')


# @app.route('/templatebot')
# def templatebot():
#     return render_template('index-template.html', loadurl='http://{}:{}'.format(serverhost, serverport))


@app.route('/templatebot')
def templatebot():
    return render_template('get.js', loadurl='http://{}:{}'.format(serverhost, serverport))


@app.route('/chat/<bot_id>', methods=['GET', 'POST'])
def chat(bot_id):

    if request.method == 'POST' and request.get_json()['question']:
        db = mysql.connection.cursor()
        db.execute("SELECT paragraph,is_deployed from userpanel_bot where id={}".format(bot_id))
        para = db.fetchone()
        print(para)

        if para and para[1]:
            response = request.get_json()
            ans = Replier(para[0], response['question'])
            j_ans = jsonify({'answer': ans})
            j_ans.headers.add('Access-Control-Allow-Origin', '*')
            return j_ans
        # elif request.method == 'GET':
        #     return send_file('./static/get.js', as_attachment=True, attachment_filename='get.js')
        elif para and not para[1]:
            j_ans = jsonify({'answer': "Bot is under maintenance"})
            j_ans.headers.add('Access-Control-Allow-Origin', '*')
            return j_ans
        else:
            j_ans = jsonify({'answer': "Bot does not exist"})
            j_ans.headers.add('Access-Control-Allow-Origin', '*')
            return j_ans


@app.route('/api/', methods=['POST'])
def answerapi():
    req = request.get_json()
    ans = Replier(req['paragraph'], req['question'])
    return jsonify({'answer': ans})


def get_gpu_status(gpudevice):
    if gpudevice.type == 'cuda':
        print(torch.cuda.get_device_name(0))
        print('[=>] Memory Usage:')
        print('[=>] Allocated:', round(torch.cuda.memory_allocated(0) / 1024 ** 3, 1), 'GB')
        print('[=>] Cached:   ', round(torch.cuda.memory_cached(0) / 1024 ** 3, 1), 'GB')


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
    get_gpu_status(device)

    print('[=>] Service Running on http://{}:{}'.format(serverhost, serverport))
    app.run(host=serverhost, port=serverport,debug=True)

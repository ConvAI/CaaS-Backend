import time

import requests
import torch
from flask import Flask, request, render_template, jsonify, send_file
from flask_cors import CORS
from transformers import *
from flask_mysqldb import MySQL


app = Flask(__name__)
CORS(app)
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'test'
app.config['MYSQL_DB'] = 'nervaidb'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3306

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('index copy.html')

    
@app.route('/templatebot')
def templatebot():
    with open("./templates/index.html","r") as f:
        return f.read()
    return ""

@app.route('/chat/<bot_id>',methods=['GET', 'POST'])
def chat(bot_id):
    cursor =mysql.connection.cursor()

    cursor.execute("SELECT paragraph from userpanel_bot where id={}".format(bot_id))
    data = cursor.fetchone()
    print(data)
    if request.method == 'POST':
        # if bot_id in table:
        
        
        if data:
            response = request.get_json()
            question = response['question']
            # text = response['paragraph']
            text = data[0]
            st = time.time()

            input_text = question + " [SEP] " + text
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
            print('answer: ', ans)

            j_ans = jsonify({'answer': ans})
            j_ans.headers.add('Access-Control-Allow-Origin', '*')
            return j_ans
    if request.method == 'GET':
        return send_file('./static/get.js',as_attachment=True,attachment_filename='get.js')


		# if bot_id not in table:
        # if True:
        #     bot_id = "Oops! Bot not found!"
        #     bot_im = ""
        # # else:
		# 	# bot_im = table[bot_id]["im_url"]
        # return render_template('index.html',bot=bot_id,bot_im=bot_im)

@app.route('/api/', methods=['POST'])
def answer():
    response = request.get_json()

    question = response['question']
    text = response['paragraph']
    st = time.time()

    input_text = question + " [SEP] " + text
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
    print('answer: ', ans)

    j_ans = {'answer': ans}
    return jsonify(j_ans)


def get_gpu_status(conndevice):
    if conndevice.type == 'cuda':
        print(torch.cuda.get_device_name(0))
        print('Memory Usage:')
        print('Allocated:', round(torch.cuda.memory_allocated(0) / 1024 ** 3, 1), 'GB')
        print('Cached:   ', round(torch.cuda.memory_cached(0) / 1024 ** 3, 1), 'GB')


if __name__ == '__main__':
    with app.app_context():
        cursor =mysql.connection.cursor()

        cursor.execute("SELECT paragraph from userpanel_bot where id={}".format(int(6)))
        data = cursor.fetchone()
        print('data',data[0])
    print('Loading models...')
    tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased-distilled-squad')
    model = DistilBertForQuestionAnswering.from_pretrained('distilbert-base-uncased-distilled-squad')
    # tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    # model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    print('Model loaded!')

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)

    model.to(device)
    get_gpu_status(device)

    app.run(host='0.0.0.0',port='3232',debug=True)

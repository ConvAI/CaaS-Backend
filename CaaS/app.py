import time

import requests
import torch
from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from transformers import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/', methods=['POST'])
def answer():
    response = request.get_json()

    question = response['question']
    text = response['paragraph']
    st = time.time()

    '''input_text = question + " [SEP] " + text
    input_ids = tokenizer.encode(input_text)
    start_scores, end_scores = model(torch.tensor([input_ids]).to(device))
    all_tokens = tokenizer.convert_ids_to_tokens(input_ids)
    ans = ' '.join(all_tokens[torch.argmax(start_scores): torch.argmax(end_scores) + 1])
    ans = ans.replace(' ##', "")'''

    input_text = "[CLS] " + question + " [SEP] " + text + " [SEP]"
    input_ids = tokenizer.encode(input_text)
    token_type_ids = [0 if i <= input_ids.index(102) else 1 for i in range(len(input_ids))]
    start_scores, end_scores = model(torch.tensor([input_ids]).to(device), token_type_ids=torch.tensor([token_type_ids]).to(device))
    all_tokens = tokenizer.convert_ids_to_tokens(input_ids)
    ans = ' '.join(all_tokens[torch.argmax(start_scores): torch.argmax(end_scores) + 1])
    ans = ans.replace(' ##', "")

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
    print('Loading models...')
    # tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased-distilled-squad')
    # model = DistilBertForQuestionAnswering.from_pretrained('distilbert-base-uncased-distilled-squad')
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForQuestionAnswering.from_pretrained('bert-large-uncased-whole-word-masking-finetuned-squad')
    print('Model loaded!')

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('Using device:', device)

    model.to(device)
    get_gpu_status(device)

    app.run(host='0.0.0.0')

import requests
import json

from flask import Flask, request, redirect, url_for, flash, jsonify

url = 'http://127.0.0.1:5000/api/'

data = {
    'paragraph':'Established in 2010 as a Center for Excellence, R. N. G. Patel Institute of Technology [RNGPIT] is recognized by All India Council for Technical Education (AICTE), New Delhi and Gujarat Technological University (GTU), Ahmadabad.The institute is situated near Isroli-Afwa in Bardoli taluka of Surat District, about 4 KMs away from Bardoli Town. The institute provides students all possible infrastructure and educational facilities such as neat and airy classrooms, tutorial rooms, fully equipped laboratories, language lab to empower them in communicative English, computer center, library, workshop, playground and canteen. The institute has emerged as forerunner in the field of imparting quality education by touching peak heights of result by falling under state level university ranking in top 10, professional training and development and good placements in multinational companies.',
    'question':'Who recognizes RNGPIT?'
}

j_data = json.dumps(data)

headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

r = requests.post(url, data=j_data, headers=headers)

print(r, r.text)


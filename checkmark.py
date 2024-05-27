import sys
sys.dont_write_bytecode = True
from flask import Flask, request, jsonify, redirect
from nltk.corpus import stopwords
from GoogleCSE import searchAPI
import re

app = Flask(__name__)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', 'https://netclips-soft.000webhostapp.com')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route("/")
def homePage():
    return redirect("https://netclips-soft.000webhostapp.com/")

def findSimilarity(text, key):
    queries = []
    for i in re.compile("[?!.:\"']").split(text):
        x = re.compile(r'\W+', re.UNICODE).split(i)
        x = [ele for ele in x if ele != '']
        l = len(x)
        if l > 9:
            l = int(l/9)
            index = 0
            for _ in range(0, l):
                queries.append(x[index:index+9])
                index += 8
                if index+9 > l:
                    index = l-8
            if index != len(x):
                queries.append(x[len(x)-index:len(x)])
        elif l > 4:
            queries.append(x)

    q = [' '.join(d) for d in queries]
    output = {}
    c = {}
    while("" in q):
        q.remove("")
    count = min(len(q), 100)
    for s in q[0:count]:
        output, c, errorCount = searchAPI(s, output, c, key) ###виклик searchweb
        print(errorCount)
        count -= errorCount
        sys.stdout.flush()
    totalPercent = 0
    outputLink = {}
    for link in output:
        percentage = (output[link]*c[link]*100)/count
        if percentage > 10:
            totalPercent += percentage
            prevlink = link
            outputLink[link] = percentage
        elif len(prevlink) != 0:
            totalPercent += percentage
            outputLink[prevlink] += percentage
        elif c[link] == 1:
            totalPercent += percentage
    return jsonify({
        'error': 0,
        'data': text,
        'score': totalPercent,
        'links': list(outputLink.keys())
    }), 200


@app.route('/api/submitText', methods=['POST'])
def submitText():
    text = request.get_json().get('text')
    key = request.get_json().get('key')
    if text:
        return findSimilarity(text, key)
    return jsonify({'error': 'Data was not received.'}), 400


if __name__ == '__main__':
    app.run(debug = True)

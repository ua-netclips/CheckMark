import sys
sys.dont_write_bytecode = True
from flask import Flask, request, jsonify, redirect
from collections import Counter
from googleapiclient.discovery import build
import math
import re

app = Flask(__name__)

@app.route("/")
def homePage():
    return redirect("https://netclips-soft.000webhostapp.com/")

def searchAPI(text, output, c, keyApi):
    try:
        resource = build("customsearch", 'v1', developerKey=keyApi).cse()
        result = resource.list(q=text, cx='8136307ac04924a5f').execute()
        searchInfo = result['searchInformation']
        if(int(searchInfo['totalResults']) > 0):
            maxSim = 0
            itemLink = ''
            numList = len(result['items'])
            min(numList, 5)
            for i in range(0, numList):
                item = result['items'][i]

                n1 = Counter(re.compile(r'\w+').findall(text.lower()))
                n2 = Counter(re.compile(r'\w+').findall(item['snippet'].lower()))
                intersection = set(n1.keys()) & set(n2.keys())
                matchWords = {}
                for j in intersection:
                    if(n1[j] > n2[j]):
                        matchWords[j] = n2[j]
                    else:
                        matchWords[j] = n1[j]
                numerator = sum([n1[x] * matchWords[x] for x in intersection])
                sum1 = sum([n1[x]**2 for x in n1.keys()])
                sum2 = sum([matchWords[x]**2 for x in matchWords.keys()])
                denominator = math.sqrt(sum1) * math.sqrt(sum2)
                simValue = float(numerator) / denominator if (math.sqrt(sum1) * math.sqrt(sum2)) > 0 else 0.0


                if simValue > maxSim:
                    maxSim, itemLink = simValue, item['link']
                if item['link'] in output:
                    itemLink = item['link']
                    break
            if itemLink in output:
                output[itemLink] = output[itemLink] + 1
                c[itemLink] = ((c[itemLink] * (output[itemLink]-1) + maxSim)/(output[itemLink]))
            else:
                output[itemLink] = 1
                c[itemLink] = maxSim
    except Exception as e:
        return output, c, 1
    return output, c, 0

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
        'links': list(outputLink.keys()),
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

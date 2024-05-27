import re
import math
from collections import Counter
from googleapiclient.discovery import build
# searchEngine_API = 'AIzaSyDy8KWEz3iDy3RUeJuE8ly8uYc1nPWgAto'
# searchEngine_API = 'AIzaSyBbMfadbDuyV4vuNqPU4MDq_6KwFQqeeDg'
#searchEngine_API = 'AIzaSyCLf7qR669Zu3CjhhmRrLx3Mnp7lTw80QA'


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

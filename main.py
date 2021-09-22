import requests
from hashlib import sha1
import os
import webbrowser

def logEvent(category = "Executable", action = None):
    # send google analytics data
    cid = sha1(os.getlogin().encode()).hexdigest()[:10]
    event = {
        "v": 1,
        "tid": "UA-140457323-1",
        "cid": cid,
        "t": "event",
        "ec": category,
        "ea": action
    }
    req = requests.post("https://www.google-analytics.com/collect", event)
    # print(req.text)

# response = requests.get('https://storage.googleapis.com/omsistuff-cdn/images/614218f349df0.jpg')
# file = open("sample_image.jpg", "wb")
# file.write(response.content)
# file.close()

webbrowser.open('https://omsistuff.fr/mercedes-benz-citaro-gc2/navette-disney-keolis-cif/360?ref=&ref_label=&ref_value=&tdl=true')

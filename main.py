import requests
from hashlib import sha1
import os
import webbrowser
import websockets
import asyncio
import time
import sys
import zipfile

steam_folder = r"C:\Program Files (x86)\Steam\steamapps\common"

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

async def time(websocket, path):
    while True:
        await websocket.send('tld:request_download_link')
        download_link = await websocket.recv()
        await websocket.send('tld:download:started')
        response = requests.get(download_link)
        file_name = os.path.join(steam_folder, 'fr.omsistuff.tdl.tmp.zip')

        if download_link.startswith("https://storage.googleapis.com/omsistuff-cdn/"):
            with open(file_name, "wb") as f:
                response = requests.get(download_link, stream=True)
                total_length = response.headers.get('content-length')

                if total_length is None: # no content length header
                    f.write(response.content)
                else:
                    dl = 0
                    total_length = int(total_length)
                    for data in response.iter_content(chunk_size=1024):
                        dl += len(data)
                        f.write(data)
                        done = int(100 * dl / total_length)
                        await websocket.send("tld:download:progress={}".format(done))
            await websocket.send('tld:download:done')

            await websocket.send('tld:archive:start')
            with zipfile.ZipFile(file_name, 'r') as zf:
                # Get a list of all archived file names from the zip
                listOfFileNames = zf.namelist()
                # Iterate over the file names
                for fileName in listOfFileNames:
                    # try to extract
                    try:
                        zf.extract(fileName, steam_folder)
                    except:
                        await websocket.send('tld:archive:error_file')
            # remove tmp archive
            os.remove(file_name)
            await websocket.send('tld:archive:done')
            logEvent(action="download")
            
            # await order from webpage to close script
            await websocket.send('tld:request_close_app')
            await websocket.recv()
        else:
            webbrowser.open('https://omsistuff.fr/autodl?e=invalid_link')

        # force close the script
        # TODO: break loop and execute and end script function
        sys.exit(0)

start_server = websockets.serve(time, '127.0.0.1', 5300)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

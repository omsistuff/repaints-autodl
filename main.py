import requests
from hashlib import sha1
import os
import webbrowser
import websockets
import asyncio
import time
import sys
import zipfile
# from win10toast import ToastNotifier

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
        program_path = os.path.join(steam_folder, 'OMSI 2', '.omsistuff', 'autodl')

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
            try:
                os.remove(file_name)
            except:
                webbrowser.open('https://omsistuff.fr/autodl?e=archive_error')
                sys.exit(0)

            # repaint successfully installed
            # toaster = ToastNotifier()
            # toaster.show_toast("OmsiStuff", "Le repaint a correctement été installé")
            await websocket.send('tld:archive:done')
            logEvent(action="download")
            
            # await order from webpage to close script
            await websocket.send('tld:request_close_app')
            await websocket.recv()
        else:
            webbrowser.open('https://omsistuff.fr/autodl?e=invalid_link')

        # download selfupdate exe (installer)
        # retrieve last release of git repo
        response = requests.get("https://api.github.com/repos/omsistuff/repaints-autodl/releases/latest")
        browser_download_url = response.json()["assets"][0]["browser_download_url"]
        tag_name = response.json()["tag_name"]

        # read lasest version file
        version_txt = os.path.join(program_path, 'version.txt')
        if not os.path.exists(version_txt):
            f = open(version_txt, 'w')
            f.close()

        tag_file = open(version_txt, "r+")
        tag_from_file = tag_file.readline()

        # detect if actual version is already installed
        if tag_name != tag_from_file:
            file = requests.get(browser_download_url, stream=True)
            self_update_exe_name = os.path.join(program_path, 'self.update.fr.omsistuff.autodl.exe')
            with open(self_update_exe_name, "wb") as f:
                f.write(file.content)

            # write new tag to file
            tag_file.seek(0)
            tag_file.write(tag_name)
            tag_file.truncate()

        # launch selfupdate exe
        os.startfile(self_update_exe_name)

        # force close the script
        # TODO: break loop and execute and end script function
        sys.exit(0)

start_server = websockets.serve(time, '127.0.0.1', 5300)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

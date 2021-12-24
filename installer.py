import os
import requests
from tkinter import *
from tkinter.ttk import *
import zipfile
import time
import winreg
import ctypes, sys

if __name__ == "__main__":
    program_path = r"C:\Program Files (x86)\Steam\steamapps\common\OMSI 2\.omsistuff"
    autodl_path = os.path.join(program_path, "autodl")
    md5file = os.path.join(program_path, "autodl.md5")
    tmp_loc = os.path.join(program_path, "autodl.tmp.zip")
    bucket_url = "https://firebasestorage.googleapis.com/v0/b/objects-omsistuff.appspot.com/o/programs%2Fautodl%2F"
    build_url = bucket_url + "build.zip"
    download_link = build_url + "?alt=media"
    reg_path = os.path.join(autodl_path, 'url_protocol.reg')
    metadata = requests.get(build_url).json()

    def resourcePath(relative_path):
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relative_path)
        return os.path.join(os.path.abspath("."), relative_path)

    path = winreg.HKEY_CLASSES_ROOT
    autodl_path_reg = r"autodlomsistuff\\shell\\open\\command"
    def read_reg(k=''):
        try:
            key = winreg.OpenKeyEx(path, autodl_path_reg)
            value = winreg.QueryValueEx(key,k)
            if key:
                winreg.CloseKey(key)
            return value[0]
        except Exception as e:
            print(e)
        return None

    def save_reg(v=0, p=""):
        try:
            key = winreg.CreateKey(path, p)
            winreg.SetValueEx(key, '', 0, winreg.REG_SZ, str(v))
            if key:
                winreg.CloseKey(key)
            return True
        except Exception as e:
            raise e

    # not working actually
    # return file not found error in admin mode
    def save_or_fail_reg():
        if read_reg() is None:
            try:
                save_reg(p=r"autodlomsistuff")
                save_reg(p=r"autodlomsistuff\\shell")
                save_reg(p=r"autodlomsistuff\\shell\\open")
                save_reg(p=autodl_path ,v='c:\Program Files (x86)\Steam\steamapps\common\OMSI 2\.omsistuff\autodl\main.exe "%1"')
            except:
                print('restart in admin mode')
                ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

    reg_attemps = 0
    def open_reg_file():
        global reg_attemps
        reg_attemps+=1
        if reg_attemps < 3:
            try:
                os.startfile(reg_path)
            except:
                message = "Veuillez accepter les droits a cette étape.\nCeci permet au logiciel de s'ouvrir depuis le navigateur.\n(nouvel essai dans 5s)"
                currentTask.set(message)
                window.update()
                time.sleep(5)
                open_reg_file()

    def main():

        # create .omsistuff dir if not exists
        if not os.path.exists(program_path):
            os.makedirs(program_path)

        # read lasest hash file
        if not os.path.exists(md5file):
            f = open(md5file, 'w')
            f.close()

        hash_file = open(md5file, "r+")
        hash_from_file = hash_file.readline()

        if hash_from_file != metadata["md5Hash"]:
            currentTask.set("Téléchargement de la nouvelle version")
            window.update()
            with open(tmp_loc, "wb") as f:
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
                        bar['value'] = int(100 * dl / total_length)
                        window.update()

            # extarct zip
            currentTask.set("Extraction de l'archive")
            window.update()
            with zipfile.ZipFile(tmp_loc, 'r') as zf:
                # Get a list of all archived file names from the zip
                listOfFileNames = zf.namelist()
                # Iterate over the file names
                for fileName in listOfFileNames:
                    # try to extract
                    try:
                        zf.extract(fileName, autodl_path)
                    except:
                        pass
            # remove tmp archive
            try:
                os.remove(tmp_loc)
            except:
                pass

            # open registry file
            if read_reg() is None:
                reg_file = requests.get(bucket_url + "url_protocol.reg?alt=media")
                with open(reg_path, 'wb') as f:
                    f.write(reg_file.content)
                open_reg_file()

            # write new hash to file
            hash_file.seek(0)
            hash_file.write(metadata["md5Hash"])
            hash_file.truncate()

        else:
            currentTask.set("Programme deja à jour")
            window.update()
            time.sleep(2)

        # close window
        window.destroy()

    # interface
    window = Tk()
    window.title("omsistuff autodl - mise a jour")
    window.geometry("320x100+0+0")
    window.resizable(False, False)
    window.iconbitmap(resourcePath("icon.ico"))

    currentTask = StringVar()

    bar = Progressbar(window,orient=HORIZONTAL,length=300)
    bar.pack(pady=15)
    currentTaskLabel = Label(window,textvariable=currentTask).pack()
    # button = Button(window,text="Installer",command=main).pack()

    window.after_idle(main)
    window.mainloop()

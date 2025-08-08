import shutil,random
from mainlib import *
from flask import *
from threading import Thread
from time import sleep

filetypes = {"jpg": "image", "jpeg": "image", "webp": "image", "png": "image", "gif": "image", "bmp": "image",
          "txt": "text", "yml": "config", "toml": "config", "json": "config", "properties": "config",
          "sk": "script", "java": "script", "py": "script", "jar": "java",
          "folder": "folder"
          }

def removeWithDelay(files: list, delay: float):
    sleep(delay)
    for file in files:
        if os.path.exists(file):
            os.remove(file)
def explorerPage(request, id):
    return render_template("explorer.html", id=id)

def editorPage(request, id):
    if request.args.get('path')[1:] == "/":
        path = f"servers/{id}{request.args.get('path')}"
    else:
        path = f"servers/{id}/{request.args.get('path')}"
    file = {"type": "none"}
    if os.path.exists(path):
        file = get_file(path)
        file["path"] = path
        try:
            if filetypes[file["ext"]] == "image":
                file["type"] = "image"
                shutil.copy(f"{path}", f"static/temp/{file['name']}")
                Thread(target=lambda: removeWithDelay([f"static/temp/{file['name']}"], delay=10)).start()
            elif filetypes[file["ext"]] == "text" or filetypes[file["ext"]] == "script" or filetypes[file["ext"]] == "config":
                file["type"] = "text"
                try:
                    if request.method == 'POST':
                        with open(f"{path}", "w", encoding="utf-8") as f:
                            f.write(request.form.get("content"))
                        file["data"] = request.form.get("content")
                    else:
                        with open(f"{path}", encoding="utf-8") as f:
                            file["data"] = f.read()
                except:
                    file["type"] = "none"
        except KeyError:
            file["type"] = "none"

    return render_template("editor.html", file=file, id=id)
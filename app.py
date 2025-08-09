from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from pages import *
from time import sleep
from colorama import Back, Fore
import psutil, random, base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

start_command = {
    "minecraft": "java -Xms4096M -Xmx4096M -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1 -Dusing.aikars.flags=https://mcflags.emc.gs -Daikars.new.flags=true -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -jar server.jar",
    "python": "python3 app.py"
}

tempdata = {}
@app.route('/')
def index():
    return serversPage(request)
@app.route('/explorer/<id>')
def explorer(id):
    return explorerPage(request, id)
@app.route('/editor/<id>', methods=['GET', 'POST'])
def editor(id):
    return editorPage(request, id)
@app.route('/terminal/<id>')
def terminal(id):
    return terminalPage(request, id)
@app.route('/download/<fileid>')
def downloadfile(fileid):
    global tempdata
    if fileid not in tempdata.keys():
        return "Ошибка загрузки файла!"
    path = tempdata[fileid]
    return send_file(path)
#Веб сокеты -------------------------------------------------------------------------------
@socketio.on('connect')
def handle_connect():
    print('> Client connected!')
@socketio.on('term-init')
def handle_term_init(id):
    viewed_logs = -1
    while True:
        emit("term-server-info", get_info(id))
        if is_running(id):
            while len(logs[id]) > viewed_logs + 1:
                viewed_logs += 1
                emit("term-server-msg", {"id": id, "message": str(logs[id][viewed_logs])})
        else:
            viewed_logs = -1
            emit("term-server-info", get_info(id))
        socketio.sleep(0)
@socketio.on('term-client-history')
def handle_history(id):
    global containers
    #console = containers[id]["console"]
    #emit("term-server-history", console)

@socketio.on('term-client-info')
def handle_info(id):
    global containers
    #console = containers[id]["console"]
    emit("term-server-info", get_info(id))

@socketio.on('term-client-msg')
def handle_message(data):
    command = data['data']
    send_command(data['id'], command)
    #socketio.emit("term-server-msg", {"id": data["id"], "message": f"$ {command}"})

@socketio.on('term-client-run')
def handle_run_server(id):
    if not is_running(id):
        #path = f"servers/{id}/server.properties"
        #with open("servers.json") as f:
        #    server = loads(f.read())[id]
        #if os.path.exists(path):
        #    with open(path, "r") as f:
        #        sprop = load_properties(f.read())
        #    sprop["server-port"] = server["port"]
        #    with open(path, "w") as f:
        #        f.write(dump_properties(sprop))
        #else:
        #    with open(path, "w") as f:
        #        f.write(f"server-port={server['port']}")
        socketio.emit("term-server-msg", {"id": id, "message": f"{Fore.GREEN}Включение процесса {id}..."})
        run_server(id)
        Thread(target=terminal_logger, args=[id]).start()
    else:
        send_command(id, "stop")
@socketio.on('term-client-kill')
def handle_kill(id):
    socketio.emit("term-server-msg", {"id": id, "message": f"{Fore.RED}Экстренное выключение процесса {id}..."})
    kill_server(id)
def terminal_logger(id: str):
    conn = socket_connections.get(id)
    if not conn:
        return
    
    sock = conn['socket']
    logs[id] = []
    while is_running(id):
        try:
            ready, _, _ = select.select([sock], [], [], 0.1)
            if ready:
                data = sock.recv(4096)
                if data:
                    conn['buffer'] += data
                    msg = data.decode('utf-8', errors='replace')
                    logs[id].append(msg)
                    print(msg)
                else:
                    break
        except (ConnectionResetError, BrokenPipeError, socket.error):
            break
    
    sock.close()
    if id in socket_connections:
        del socket_connections[id]
def get_info(id):
    memory = psutil.virtual_memory()
    cpu = psutil.cpu_percent(interval=1, percpu=True)
    globalcpu, cores = 0, 0
    for core in cpu:
        globalcpu += core
        cores += 100
    mem = f_size(psutil.disk_usage(f'servers/{id}/').used)
    totalmem = f_size(psutil.disk_usage(f'servers/{id}/').total)
    return {"cpu": f"{round(globalcpu, 10)}%/{cores}%", "ram": f"{f_size(memory.used)}/{f_size(memory.total)}", "mem": f"{mem}/{totalmem}", "status": is_running(id)}

#ОПАСНАЯ ЗОНА ---------------------------
@socketio.on('exp-client-tools')
def handle_files(data):
    if data["mode"] == "list":
        path = f"servers/{data['id']}"
        path = f"{path}/{data['path']}"
        out = get_files(path)
        files = []
        filesimages = []
        for file in out:
            try:
                if filetypes[file["ext"]] == "image":
                    file["image"] = f"/static/temp/{file['name']}"
                    filesimages.append(f"static/temp/{file['name']}")
                    shutil.copy(f"{path}/{file['name']}", f"static/temp/{file['name']}")
                else:
                    file["image"] = f"/static/images/explorer/{filetypes[file['ext']]}.webp"
            except KeyError:
                file["image"] = f"/static/images/explorer/file.webp"
            files.append(file)
        Thread(target=lambda: removeWithDelay(filesimages, delay=10)).start()
        path = data['path']
        if not path: path = ""
        pathsplit = path.split("/")
        paths = []
        temppath = ""
        paths.append({"name": "home", "path": ""})
        for path in pathsplit:
            if path != "":
                temppath += f"/{path}"
                paths.append({"name": path, "path": temppath})
        emit("exp-server-files", {"paths": paths, "files": files})
        return
    if data['file'][0] == "/":
        path = f"servers/{data['id']}{data['file']}"
    else:
        path = f"servers/{data['id']}/{data['file']}"
    match data["mode"]:
        case "delete":
            if os.path.isdir(path):
                shutil.rmtree(path)
            else:
                os.remove(path)
            filename = data["file"].split("/")[-1]
            temppath = data["file"].split("/")[:-1]
            path = ""
            for el in temppath:
                if el != "": path += f"/{el}"
            socketio.emit("exp-server-rmfile", {"path": path, "filename": filename})
        case "rename":
            os.rename(path, f"servers/{data['id']}/{data['name']}")
            temppath = data["file"].split("/")[:-1]
            path = ""
            for el in temppath:
                if el != "": path += f"/{el}"
            socketio.emit("exp-server-refresh", path)
        case "download":
            fileid = f"{random.randint(1000000000, 9999999999)}"
            tempdata[fileid] = path
            socketio.emit("redirect", f"/download/{fileid}")
        case "mkdir":
            if os.path.exists(f"servers/{data['id']}/{data['file']}"):
                emit("message", "Ошибка создания папки она уже существует")
            else:
                os.mkdir(f"servers/{data['id']}/{data['file']}")
            temppath = data["file"].split("/")[:-1]
            path = ""
            for el in temppath:
                if el != "": path += f"/{el}"
            socketio.emit("exp-server-refresh", path)
        case "mkfile":
            if os.path.exists(f"servers/{data['id']}/{data['file']}"):
                emit("message", "Ошибка создания файла он уже существует")
            else:
                with open(f"servers/{data['id']}/{data['file']}", "w") as f:
                    f.write("")
            temppath = data["file"].split("/")[:-1]
            path = ""
            for el in temppath:
                if el != "": path += f"/{el}"
            socketio.emit("exp-server-refresh", path)
        case "archive":
            pass

@socketio.on('exp-client-upload-chunk')
def handle_file_upload_chunk(data):
    try:
        base_path = f"servers/{data['id']}"
        if data['path']:
            save_path = f"{base_path}/{data['path']}/{data['filename']}"
        else:
            save_path = f"{base_path}/{data['filename']}"

        # Декодируем чанк данных
        file_data = data['data'].split(',')[1]
        file_content = base64.b64decode(file_data)

        # Режим записи (первый чанк - 'wb', последующие - 'ab')
        mode = 'ab' if data['currentChunk'] > 0 else 'wb'

        with open(save_path, mode) as f:
            f.write(file_content)

        # Отправляем прогресс
        emit("exp-server-upload-progress", {
            "filename": data['filename'],
            "currentChunk": data['currentChunk'],
            "totalChunks": data['totalChunks'],
            "success": True
        })

        # Запрашиваем следующий чанк или завершаем загрузку
        print(data['currentChunk'], data['totalChunks'])
        if data['currentChunk'] < data['totalChunks'] - 1:
            emit("exp-server-upload-next-chunk", {
                "filename": data['filename'],
                "success": True
            })
        else:
            # Загрузка завершена
            path = data['path'] if data['path'] else ""
            socketio.emit("exp-server-refresh", path)
            emit("exp-server-upload", {
                "success": True,
                "message": "Файл успешно загружен"
            })

    except Exception as e:
        emit("exp-server-upload", {
            "success": False,
            "message": str(e)
        })
#def removeFile(file):
#Включение ------------------------------------------------------------------------------
if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)
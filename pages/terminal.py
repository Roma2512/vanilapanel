from mainlib import *
from flask import *

def terminalPage(request, id):
    with open("servers.json", "r") as f:
        servers = loads(f.read())
    with open("config.json", "r") as f:
        config = loads(f.read())
    return render_template("terminal.html", id=id, config=config, server=servers[id])
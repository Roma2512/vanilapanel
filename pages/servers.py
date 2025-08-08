from mainlib import *
from flask import *

def serversPage(request):
    with open("servers.json", "r") as f:
        servers_read = loads(f.read())
    servers = []
    for key in servers_read.keys():
        servers_read[key]["id"] = key
        servers.append(servers_read[key])
    with open("config.json", "r") as f:
        config = loads(f.read())
    return render_template("servers.html", servers=servers, config=config)
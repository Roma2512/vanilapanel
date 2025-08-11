from mainlib import *
from flask import *

def panelPage(request, mode):
	if mode == "settings":
		return render_template("panel/settings.html")
	elif mode == "servers":
		return render_template("panel/servers.html")
	
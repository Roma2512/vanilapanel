from mainlib import *
from flask import *

def authPage(request):
	message = ""
	if request.method == "POST":
		out = loginuser(request.form.get("username"), request.form.get("password"))
		if out["code"]:
			res = make_response(redirect("/"))
			res.set_cookie('token', out["token"])
			return res
		else:
			message = out["message"]
	return render_template("auth.html", error=message)
	
import web
web.config.debug = False
import os
from discord_webhook import DiscordWebhook
from replit import db
import json
import reflux
import base64
import cloudinary
import cloudinary.api
import cloudinary.uploader
import os
import random
import requests

cloudinary.config(
	cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"),
	api_key = os.getenv("CLOUDINARY_API_KEY"),
	api_secret = os.getenv("CLOUDINARY_API_SECRET")
)

render = web.template.render('templates/')

urls = (
	'/', 'index',
	'/add', 'add',
	'/apiv1', 'apiv1',
	'/apiv2', 'apiv2',
	'/login', 'login',
	'/admin', 'admin',
	'/admin/delete', 'delete',
	'/admin/verify', 'verify',
	'/api', 'api',
	'/generator', 'generator',
	'/admin/edit', 'edit',
	'/admin/code', 'code',
	"/callback", "callback",
	'/login/admin', 'adminlogin',
	'/login/replit/callback', 'replitcallback'
	)
app = web.application(urls, locals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

class replitcallback:
	def GET(self):
		i = web.input()
		token = i.id
		r = requests.post("https://replauth.coolcodersj.repl.co", data={"id": token})
		user = r.text
		session.user = user
		raise web.seeother("/")

class code:
	def POST(self):
		i = web.input()
		id = int(i.id)
		db[id] = {
			"code": i.code,
			"imgurl": db[id]['imgurl'],
			"creator": db[id]['creator'],
			"description": db[id]['description'],
			"name": db[id]['name'],
			"verified": db[id]['verified']
		}

		raise web.seeother('/admin')

class edit:
	def POST(self):
		i = web.input(myfile={})
		id = i.id
		if i.myfile != "":
			filedir = 'static/images'
			fileext = i.myfile.filename.split('.')[-1]
			myfilepath = filedir + '/' + str(id) + "." + fileext
			fout = open(myfilepath, "wb")
			fout.write(i.myfile.file.read())
			fout.close()
			r = cloudinary.uploader.upload(filedir + '/' + str(id) + "." + fileext,
				folder = "rmarketplace/",
				public_id = str(id),
				overwrite = True,
				resource_type = "auto"
			)
			os.remove(filedir + '/' + str(id) + "." + fileext)
			imgurl = r['url']
		else:
			imgurl = db[int(id)]['imgurl']


		db[int(id)] = {
			"code": db[int(id)]['code'],
			"imgurl": imgurl,
			"creator": i.creator,
			"description": i.desc,
			"name": i.name,
			"verified": db[int(id)]['verified']
		}

		raise web.seeother('/admin')

class generator:
	def GET(self):
		if not session.get("user"):
			raise web.seeother("/login")
		return render.generator(session.get("user").strip())
	def POST(self):
		i = web.input()
		t = reflux.Theme({
			"name": i.name,
			"author": i.person,
			"description": i.desc,
			"default": "dark"
		})
		t.set_colors({
			"border": i.bg_1,

			"control-1": i.control_2,
			"control-2": i.control_2, #Run button border
			"control-3": i.control_3, #Run button fill, lang icon fill, share button fill, sidebar icon hover fill, file hover fill, start thread border

			"primary-1": i.primary, #Current file fill, sidebar icon outline
			"primary-2": i.primary,
			"primary-3": i.primary,
			"primary-4": i.primary,

			"background-1": i.bg_1, #File bar, sidebar, console/shell (active) tab fill, top bar
			"background-2": i.bg_2, #console/shell (passive) tab fill
			"background-3": i.bg_3, #space between the sidebar/filebar, editor, and console/shell
			"background-4": i.bg_3
		})
		ids = [0]
		for key in db:
			ids.append(int(key))
		ids.sort()
		id = ids[-1] + 1
		t.build(f"theme{str(id)}.min.js", "w+")
		f = open(f"theme{str(id)}.min.js")
		code = f.read()
		os.remove(f"theme{str(id)}.min.js")
		db[id] = {
			"code": code,
			"imgurl": "",
			"creator": i.person,
			"description": i.desc,
			"name": i.name,
			"verified": False
		}
		raise web.seeother("/?code=2")




class api:
	def GET(self):
		return render.api()

class delete:
	def POST(self):
		i = web.input()
		del db[int(i.id)]
		raise web.seeother("/admin")


class verify:
	def POST(self):
		i = web.input()
		id = int(i.id)
		db[id] = {
			"code": db[id]['code'],
			"imgurl": db[id]['imgurl'],
			"creator": db[id]['creator'],
			"description": db[id]['description'],
			"name": db[id]['name'],
			"verified": True
		}

		if session.get("user"):
			user = "View Admin Panel"
		else:
			user = "False"
		raise web.seeother("/?user="+user)

class admin:
	def GET(self):
		if not "CoolCoderSJ" in session.get("user"):
			return render.errors(4)
		else:
			for key in db:
				print(key, db[key])
			return render.admin(db)

class login:
	def GET(self):
		raise web.seeother("https://replauth.coolcodersj.repl.co")

class adminlogin:
	def GET(self):
		state = ""
		for x in range(15):
			state += random.choice(['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'])
		raise web.seeother(f"https://auth.sjurl.tk/authorize?response-type=code&scopes=username&clientid=5571162301&state={state}&redirect_uri=https://reflux-marketplace.coolcodersj.repl.co/callback")

class callback:
	def GET(self):
		i = web.input()
		code = i.code
		state = i.state
		r = requests.post("https://auth.sjurl.tk/token", data={
			"grant_type": "authorization_code",
			"code": code,
			"clientid": 5571162301,
			"clientsecret": os.environ['CLIENT_SECRET'],
			"redirect_uri": "https://reflux-marketplace.coolcodersj.repl.co/callback",
			"state": state
		})
		token = r.text
		r = requests.get(f"https://auth.sjurl.tk/api/me?Authorization={token}")
		r = r.text
		username = r.replace("'", "").replace(":", "").replace("username", "").replace("{", "").replace("}", "")
		session.user = username
		raise web.seeother("/")

class apiv2:
	def GET(self):
		a = {"theme": []}
		for theme in db:
			themedict = {}
			themedict['id'] = theme
			themedict['user'] = db[theme]['creator']
			themedict['name'] = db[theme]['name']
			themedict['description'] = db[theme]['description']
			themedict['code-jswa'] = db[theme]['code'].replace("%20", " ")
			code = db[theme]['code']
			code = code.split("`")
			code = code[1]
			ts_script = """
			// ==UserScript==
// @name         Reflux -- {{{NAME}}}
// @namespace    http://reflux-marketplace.coolcodersj.repl.co/
// @version      0.1
// @description  {{{DESC}}}
// @author       {{{AUTHOR}}}
// @match        https://*.replit.com/*
// @grant        none
// ==/UserScript==

(
	function () {
		let p1=document.getElementById("reflux-theme");
		let p2=document.getElementById("reflux-display");
		if (p1 && p2) {
			var go=confirm("There is a Reflux theme already running. Would you like to stop it?");
			if (go) {
				p1.remove();p2.remove();alert("This theme has been stopped.");
			} else {alert("This theme will continue running.");
				   }
		}
		else {
			var go2="True"};
		if (go2 === "True") {
			var style=document.createElement("style");
			var head=document.getElementsByTagName("head")[0];
			var target=document.getElementsByClassName("jsx-2607100739")[0];
			style.setAttribute("id", "reflux-theme");
			style.appendChild(document.createTextNode(
				`{{{code}}}`
			)
							 );
			if (true) {
				console.log(true);
			} else {
				alert("Reflux badge could not be applied. This theme will run silently.");
			}
			head.appendChild(style);
		}
		else {
			alert("Reflux operation cancelled.");
		}
	}
)
();
			"""
			ts_script = ts_script.replace("{{{NAME}}}", db[theme]['name'])
			ts_script = ts_script.replace("{{{AUTHOR}}}", db[theme]['creator'])
			ts_script = ts_script.replace("{{{DESC}}}", db[theme]['description'])
			ts_script = ts_script.replace("{{{code}}}", code)
			themedict['code-jswoa'] = ts_script
			themedict['img'] = db[theme]['imgurl']
			a['theme'].append(themedict)
		web.header('Content-Type', 'application/json')
		web.header('Access-Control-Allow-Origin', '*')
		web.header('Access-Control-Allow-Credentials', 'true')
		web.header('Access-Control-Allow-Methods', 'GET')
		web.header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
		return json.dumps(a)

class apiv1:
	def GET(self):
		a = {"theme": []}
		for theme in db:
			themedict = {}
			themedict['id'] = theme
			themedict['user'] = db[theme]['creator']
			themedict['name'] = db[theme]['name']
			themedict['description'] = db[theme]['description']
			themedict['code-jswa'] =db[theme]['code'].replace("%20", " ")
			themedict['img'] = db[theme]['imgurl']
			a['theme'].append(themedict)
		web.header('Content-Type', 'application/json')
		web.header('Access-Control-Allow-Origin', '*')
		web.header('Access-Control-Allow-Credentials', 'true')
		web.header('Access-Control-Allow-Methods', 'GET')
		web.header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
		return json.dumps(a)


class index:
	def GET(self):
		i = web.input(code="0", actualcode="0")
		themes = []
		themes2 = []
		ids = []
		for key in db:
			ids.append(int(key))
		ids.sort()
		ids.reverse()
		for theme in ids:
			if db[theme]['verified']:
				a = {}
				a['id'] = theme
				for val in db[theme]:
					a[val] = db[theme][val]
				themes.append(a)
		for theme in themes:
			code = theme['code']
			code = code.split("`")
			print(code)
			code = code[1]
			ts_script = """
			// ==UserScript==
// @name         Reflux -- {{{NAME}}}
// @namespace    http://reflux-marketplace.coolcodersj.repl.co/
// @version      0.1
// @description  {{{DESC}}}
// @author       {{{AUTHOR}}}
// @match        https://*.replit.com/*
// @grant        none
// ==/UserScript==

(
	function () {
		let p1=document.getElementById("reflux-theme");
		let p2=document.getElementById("reflux-display");
		if (p1 && p2) {
			var go=confirm("There is a Reflux theme already running. Would you like to stop it?");
			if (go) {
				p1.remove();p2.remove();alert("This theme has been stopped.");
			} else {alert("This theme will continue running.");
				   }
		}
		else {
			var go2="True"};
		if (go2 === "True") {
			var style=document.createElement("style");
			var head=document.getElementsByTagName("head")[0];
			var target=document.getElementsByClassName("jsx-2607100739")[0];
			style.setAttribute("id", "reflux-theme");
			style.appendChild(document.createTextNode(
				`{{{code}}}`
			)
							 );
			if (true) {
				console.log(true);
			} else {
				alert("Reflux badge could not be applied. This theme will run silently.");
			}
			head.appendChild(style);
		}
		else {
			alert("Reflux operation cancelled.");
		}
	}
)
();
			"""
			ts_script = ts_script.replace("{{{NAME}}}", theme['name'])
			ts_script = ts_script.replace("{{{AUTHOR}}}", theme['creator'])
			ts_script = ts_script.replace("{{{DESC}}}", theme['description'])
			ts_script = ts_script.replace("{{{code}}}", code)
			theme['js_wa'] = ts_script
			themes2.append(theme)
		if session.get("user"):
			user = session.get("user")
		else:
			user = ""
		return render.index(i.code, themes2, user)

class add:
	def GET(self):
		if not session.get("user"):
			raise web.seeother("/login")
		return render.add(session.get("user"))
	def POST(self):
		i = web.input(myfile={})
		person = i.person
		name = i.name
		desc = i.desc
		code = i.code
		filedir = 'static/images'
		fileext = i.myfile.filename.split('.')[-1]
		ids = [0]
		for id in db:
			ids.append(int(id))
		ids.sort()
		id = ids[-1] + 1
		myfilepath = filedir + '/' + str(id) + "." + fileext
		fout = open(myfilepath, "wb")
		fout.write(i.myfile.file.read())
		fout.close()
		r = cloudinary.uploader.upload(filedir + '/' + str(id) + "." + fileext,
			folder = "rmarketplace/",
			public_id = str(id),
			overwrite = True,
			resource_type = "auto"
		)
		os.remove(filedir + '/' + str(id) + "." + fileext)
		imgurl = r['url']

		db[id] = {
			"code": code,
			"imgurl": imgurl,
			"creator": person,
			"description": desc,
			"name": name,
			"verified": False
		}


		content2 = "PERSON: "+person+"\n\nTHEME NAME: "+name+"\n\nDESCRIPTION: "+desc
		webhook = DiscordWebhook(url="https://canary.discord.com/api/webhooks/806194998549938216/zY_NS1Ezc-e0YcEmlFDhV22yyEQ2XphnCBmyEAMggNht1TGbNPMzEyUlofhofnxCmJIB", content=content2)
		webhook.execute()
		if session.get("user") == "CoolCoderSJ":
			user = "View Admin Panel"
		else:
			user = "False"
		raise web.seeother("/?code=1&user="+user)

if __name__ == "__main__":
	app.run()

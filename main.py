import web
web.config.debug = False
import os
from discord_webhook import DiscordWebhook
import sqlite3
from replit import db
import json
import reflux


render = web.template.render('templates/')

urls = (
	'/', 'index',
	'/add', 'add',
	'/apiv1', 'apiv1',
	'/apiv2', 'apiv2',
	'/login', 'login',
	'/admin', 'admin',
	'/delete', 'delete',
	'/verify', 'verify',
	'/update_code', 'update_code',
	'/api', 'api',
	'/generator', 'generator',
	'/image', 'image'
	)
app = web.application(urls, locals())
session = web.session.Session(app, web.session.DiskStore('sessions'))

db[21] = ""

class image:
	def POST(self):
		i = web.input(myfile={})
		id = i.id
		filedir = 'static/images'
		fileext = i.myfile.filename.split('.')[-1]
		myfilepath = filedir + '/' + str(id) + "." + fileext
		fout = open(myfilepath, "wb") 
		fout.write(i.myfile.file.read()) 
		fout.close() 
		db[int(id)] = myfilepath
		raise web.seeother('/admin')

class generator:
	def GET(self):
		if session.get("user"):
			user = "CoolCoderSJ"
		else:
			user = "CoolCoderSJ"
		return render.generator(user)
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
		conn = sqlite3.connect("database.db")
		db2 = conn.cursor()
		query = db2.execute("SELECT * from themes").fetchall()
		id = query[-1][0]
		id += 1
		t.build(f"theme{str(id)}.min.js", "w+")
		f = open(f"theme{str(id)}.min.js")
		code = f.read()
		os.remove(f"theme{str(id)}.min.js")
		db2.execute(f"INSERT INTO themes (person, name, desc, code_jswa, verified) VALUES ('{i.person}', '{i.name}', '{i.desc}', '{code}',  'False')")
		conn.commit()
		db2 = conn.cursor()
		theme = db2.execute("SELECT * from themes WHERE name = "+"'"+i.name+"'").fetchall()
		db2.close()
		id = theme[0][0]
		db[id] = ""
		raise web.seeother("/?code=2&actualcode="+code)




class api:
	def GET(self):
		return render.api()

class delete:
	def POST(self):
		i = web.input()
		conn = sqlite3.connect("database.db")
		db2 = conn.cursor()
		db2.execute("DELETE FROM themes WHERE id = "+str(i.id))
		conn.commit()
		db2.close()
		del db[int(i.id)]
		raise web.seeother("/admin")

class update_code:
	def POST(self):
		i = web.input()
		print(i)
		conn = sqlite3.connect("database.db")
		db2 = conn.cursor()
		db2.execute("UPDATE themes SET code_jswa = '"+i.code+"' WHERE id = "+i.id)
		conn.commit()
		db2.close()
		raise web.seeother("/admin")

class verify:
	def POST(self):
		i = web.input()
		print(i)
		conn = sqlite3.connect("database.db")
		db2 = conn.cursor()
		db2.execute("UPDATE themes SET verified = 'True' WHERE id = "+i.id)
		conn.commit()
		db2.close()
		if session.get("user"):
			user = "View Admin Panel"
		else:
			user = "False"
		raise web.seeother("/?user="+user)

class admin:
	def GET(self):
		if not session.get("user"):
			return render.errors(4)
		else:
			conn = sqlite3.connect("database.db")
			db2 = conn.cursor()
			themes = db2.execute("SELECT * from themes").fetchall()
			db2.close()
			for theme in themes:
				if theme[0] == 19:
					print(theme)
			return render.admin(themes, db)

class login:
	def GET(self):
		return render.login()
	def POST(self):
		i = web.input()
		import requests
		r = requests.post("https://SJAUTH.coolcodersj.repl.co/apil", data={"user":i.user, "passw":i.passw, "cn":"Reflux Marketplace Admins"})
		if r.text == "True":
			if i.user == "CoolCoderSJ":
				session.user = i.user
				raise web.seeother("/?user="+i.user)
			else:
				return render.errors(4)
		elif r.text == "Wrong auth":
			return render.errors(2)
		elif r.text == "Does not exist":
			return render.errors(3)

class apiv2:
	def GET(self):
		conn = sqlite3.connect("database.db")
		a = {"theme": []}
		db2 = conn.cursor()
		themes = db2.execute("SELECT * from themes").fetchall()
		db2.close()
		for theme in themes:
			themedict = {}
			themedict['id'] = theme[0]
			themedict['user'] = theme[1]
			themedict['name'] = theme[2]
			themedict['desc'] = theme[3]
			themedict['code-jswa'] = theme[4].replace("%20", " ")
			code = theme[-3]
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
			ts_script = ts_script.replace("{{{NAME}}}", theme[2])
			ts_script = ts_script.replace("{{{AUTHOR}}}", theme[1])
			ts_script = ts_script.replace("{{{DESC}}}", theme[3])
			ts_script = ts_script.replace("{{{code}}}", code)
			themedict['code-jswoa'] = ts_script
			themedict['img'] = "https://Reflux-Marketplace.coolcodersj.repl.co/"+db[theme[0]]
			a['theme'].append(themedict)
		web.header('Content-Type', 'application/json')
		web.header('Access-Control-Allow-Origin', '*')
		web.header('Access-Control-Allow-Credentials', 'true')
		web.header('Access-Control-Allow-Methods', 'GET')
		web.header('Access-Control-Allow-Headers', 'Authorization, Content-Type')
		return json.dumps(a)

class apiv1:
	def GET(self):
		conn = sqlite3.connect("database.db")
		a = {"theme": []}
		db2 = conn.cursor()
		themes = db2.execute("SELECT * from themes").fetchall()
		db2.close()
		for theme in themes:
			themedict = {}
			themedict['id'] = theme[0]
			themedict['user'] = theme[1]
			themedict['name'] = theme[2]
			themedict['desc'] = theme[3]
			themedict['code-jswa'] = theme[4].replace("%20", " ")
			themedict['code-jswoa'] = theme[5]
			themedict['img'] = "https://Reflux-Marketplace.coolcodersj.repl.co/"+db[theme[0]]
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
		conn = sqlite3.connect("database.db")
		db2 = conn.cursor()
		themes = db2.execute("SELECT * from themes").fetchall()
		themes.reverse()
		db2.close()
		js_wa = {}
		for theme in themes:
			code = theme[-3]
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
			ts_script = ts_script.replace("{{{NAME}}}", theme[2])
			ts_script = ts_script.replace("{{{AUTHOR}}}", theme[1])
			ts_script = ts_script.replace("{{{DESC}}}", theme[3])
			ts_script = ts_script.replace("{{{code}}}", code)
			js_wa[theme[0]] = ts_script
		if session.get("user"):
			user = "View Admin Panel"
		else:
			user = "False"
		return render.index(i.code, themes, user, db, i.actualcode, js_wa)

class add:
	def GET(self):
		return render.add()
	def POST(self):
		i = web.input(myfile={})
		
		person = i.person
		name = i.name
		desc = i.desc
		code = i.code
		filedir = 'static/images'
		fileext = i.myfile.filename.split('.')[-1]
		conn = sqlite3.connect("database.db")
		db2 = conn.cursor()
		db2.execute(f"INSERT INTO themes (person, name, desc, code_jswa, verified) VALUES ('{person}', '{name}', '{desc}', '{code}',  'False')")
		conn.commit()
		db2.close()
		db2 = conn.cursor()
		theme = db2.execute("SELECT * from themes WHERE name = "+"'"+i.name+"'").fetchall()
		db2.close()
		id = theme[0][0]
		myfilepath = filedir + '/' + str(id) + "." + fileext 
		fout = open(myfilepath, "wb") 
		fout.write(i.myfile.file.read()) 
		fout.close() 
		db[int(id)] = myfilepath
		content2 = "PERSON: "+person+"\n\nTHEME NAME: "+name+"\n\nDESCRIPTION: "+desc
		webhook = DiscordWebhook(url="https://canary.discord.com/api/webhooks/806194998549938216/zY_NS1Ezc-e0YcEmlFDhV22yyEQ2XphnCBmyEAMggNht1TGbNPMzEyUlofhofnxCmJIB", content=content2)
		webhook.execute()
		if session.get("user"):
			user = "View Admin Panel"
		else:
			user = "False"
		raise web.seeother("/?code=1&user="+user)


if __name__ == "__main__":
	app.run()
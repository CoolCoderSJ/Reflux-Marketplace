import discord
import os, os.path
import time
import discord.ext
from discord.utils import get
from discord.ext import commands, tasks
from discord.ext.commands import has_permissions,  CheckFailure, check
import requests
from replit import db
import asyncio
import random
import shutil
import sqlite3
import reflux

client = discord.Client()

client = commands.Bot(command_prefix = ["r!", "reflux!"])
client.remove_command('help')

@client.event
async def on_ready():
	mem = 0
	for guild in client.guilds:
		mem += guild.member_count

	await client.change_presence(status=discord.Status.online, activity = discord.Game(name = 'https://sjurl.tk/ | SnowCoder#5223 | Serving ' + str(mem) + " users in " + str(len(client.guilds)) + " guilds."))
	
	print("Logged in!")

@client.command()
async def all(ctx):
	conn = sqlite3.connect("database.db")
	db2 = conn.cursor()
	themes = db2.execute("SELECT * from themes").fetchall()
	titles = []
	for theme in themes:
		titles.append([theme[0], theme[2]])
	embed=discord.Embed(title="All Themes", url="https://reflux-marketplace.coolcodersj.repl.co", color=0x0080ff)
	embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
	for theme in titles:
		embed.add_field(name=theme[1], value=f"ID = {theme[0]}", inline=False)
	await ctx.send(embed=embed)

@client.command()
async def theme(ctx, id):
	conn = sqlite3.connect("database.db")
	db2 = conn.cursor()
	themes = db2.execute(f"SELECT * from themes WHERE id = {id}").fetchall()
	embed=discord.Embed(title=themes[0][2], url="https://reflux-marketplace.coolcodersj.repl.co", color=0x0080ff)
	embed.set_author(name=themes[0][1])
	embed.add_field(name="Description", value=themes[0][3], inline=False)
	url = f"https://Reflux-Marketplace.coolcodersj.repl.co/{db[int(id)]}"
	# url = "https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Ftse1.mm.bing.net%2Fth%3Fid%3DOIP.Q8xOpKVBy7r0M9QxBHWmVwHaEG%26pid%3DApi%26h%3D160&f=1"
	embed.set_image(url=url)
	await ctx.send(embed=embed)
	msg = await ctx.send("React with a :white_check_mark: to this message to receive the code for this theme. Make sure you have allowed DMs from unkown users or users from this server.")
	await msg.add_reaction("âœ…")
	@client.event
	async def on_reaction_add(reaction, user):
		print(reaction.emoji)
		if reaction.emoji == "âœ…" and reaction.message.id == msg.id and "Reflux Marketplace" not in user.name:
			code = themes[0][-3]
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
			ts_script = ts_script.replace("{{{NAME}}}", themes[0][2])
			ts_script = ts_script.replace("{{{AUTHOR}}}", themes[0][1])
			ts_script = ts_script.replace("{{{DESC}}}", themes[0][3])
			ts_script = ts_script.replace("{{{code}}}", code)
			user = await client.fetch_user(int(user.id))
			f = open("js.txt", "a")
			print(themes[0][-3], file=f)
			f.close()
			file = discord.File("js.txt")
			await user.send(f"""JS CODE: """, file=file)
			os.remove("js.txt")
			f = open("ts.txt", "a")
			print(ts_script, file=f)
			f.close()
			file = discord.File("ts.txt")
			await user.send(f"""TAMPERMONKEY SCRIPT: """, file=file)
			os.remove("ts.txt")

@client.command()
async def generate(ctx, *, args=""):
	if args == "":
		embed=discord.Embed(title="Generate a theme", url="https://reflux-marketplace.coolcodersj.repl.co/generator", color=0x0080ff)
		embed.set_author(name="SnowCoder")
		embed.add_field(name="Syntax", value='` r!generate [name] | [author] | [description] | [controls color 1] | [controls color 2] | [primary color] | [bg color 1] | [bg color 2] | [bg color 3] | mode`\n\nAll values need to be hex colors, except for name, author, and desc (#000000 = black) ', inline=False)
		embed.add_field(name="Controls Color 1", value="This is the run button's border", inline=False)
		embed.add_field(name="Controls Color 2", value="This is the run button's fill color, language icon fill color, share button fill color, sidebar icons fill on hover, Start thread button border.", inline=False)
		embed.add_field(name="Primary Color", value="This is the current file tab fill, and the sidebar icon's outlines.", inline=False)

		embed.add_field(name="Background Color 1", value="This is the file bar's fill color, the sidebar fill, the top bar fill, and current tab for console/shell. (The fill color for the tab you are currently on for console/shell)", inline=False)
		embed.add_field(name="Background Color 2", value="This is the non-current tab for console/shell. (The fill color for the tab you are currently NOT on for console/shell)", inline=False)
		embed.add_field(name="Background Color 3", value="This is the fill color for the space between the editor and top bar, and the space between all of the main elements. (Editor, sidebars, etc.)", inline=False)
		embed.add_field(name="Mode", value="Can either be ` js ` or ` tms `. JS is the JS bookmarklet code, ` tms ` is the Tampermonkey Script.", inline=False)
		await ctx.send(embed=embed)
	else:
		args = args.split(" | ")
		t = reflux.Theme({
			"name": args[0],
			"author": args[1],
			"description": args[2],
			"default": "dark"
		})
		t.set_colors({
			"border": args[7],

			"control-1": args[3],
			"control-2": args[4], #Run button border
			"control-3": args[4], #Run button fill, lang icon fill, share button fill, sidebar icon hover fill, file hover fill, start thread border

			"primary-1": args[5], #Current file fill, sidebar icon outline
			"primary-2": args[5],
			"primary-3": args[5],
			"primary-4": args[5],

			"background-1": args[6], #File bar, sidebar, console/shell (active) tab fill, top bar
			"background-2": args[7], #console/shell (passive) tab fill
			"background-3": args[8], #space between the sidebar/filebar, editor, and console/shell
			"background-4": args[8]
		})
		conn = sqlite3.connect("database.db")
		db2 = conn.cursor()
		query = db2.execute("SELECT * from themes").fetchall()
		id = query[-1][0]
		id += 1
		t.build(f"theme{str(id)}.min.js", "w+")
		if args[9] == "js":
			file=discord.File(f"theme{str(id)}.min.js")
			user = await client.fetch_user(ctx.author.id)
			await user.send(file=file)
			os.remove(f"theme{str(id)}.min.js")
		else:
			code = open(f"theme{str(id)}.min.js").read()
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
			ts_script = ts_script.replace("{{{NAME}}}", args[0])
			ts_script = ts_script.replace("{{{AUTHOR}}}", args[1])
			ts_script = ts_script.replace("{{{DESC}}}", args[2])
			ts_script = ts_script.replace("{{{code}}}", code)
			f = open(f"theme{str(id)}tms.min.js", "w")
			f.write(ts_script)
			file = discord.File(f"theme{str(id)}tms.min.js")
			user = await client.fetch_user(ctx.author.id)
			await user.send(file=file)
			os.remove(f"theme{str(id)}.min.js")
			os.remove(f"theme{str(id)}tms.min.js")

		await ctx.send("The generated code has been DM'd to you.")

@client.command()
async def info(ctx):
	embed=discord.Embed(title="Bot Info", url="https://reflux-marketplace.coolcodersj.repl.co/generator", color=0x0080ff)
	embed.set_author(name="SnowCoder â •", icon_url="https://frissyn.herokuapp.com/main/im_/https://images-ext-2.discordapp.net/external/Z58f6hcmeb6fg-PY4bcuytPov6YLZ900yzxbzGy0_qI/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/744921397582888991/2b1d08bfb5b3b702590b6c1a074636d2.webp?width=300&height=300")
	embed.add_field(name="Github Repo", value="https://github.com/CoolCoderSJ/Reflux-Marketplace")
	embed.add_field(name="Repl Link", value="https://replit.com/@CoolCoderSJ/Reflux-Marketplace")
	embed.add_field(name="Website", value="https://Reflux-Marketplace.coolcodersj.repl.co")
	embed.add_field(name="Bot Invite", value="https://discord.com/api/oauth2/authorize?client_id=826087358096474132&permissions=0&scope=bot")
	await ctx.send(embed=embed)

@client.command()
async def help(ctx):
	embed=discord.Embed(title="Help", url="https://reflux-marketplace.coolcodersj.repl.co/generator", color=0x0080ff)
	embed.set_author(name="SnowCoder â •", icon_url="https://frissyn.herokuapp.com/main/im_/https://images-ext-2.discordapp.net/external/Z58f6hcmeb6fg-PY4bcuytPov6YLZ900yzxbzGy0_qI/%3Fsize%3D1024/https/cdn.discordapp.com/avatars/744921397582888991/2b1d08bfb5b3b702590b6c1a074636d2.webp?width=300&height=300")
	embed.add_field(name="View Bot Info", value="` r!info `")
	embed.add_field(name="Generate a theme", value="Receive either JS code or Tampermonkey script. Use ` r!generate `")
	embed.add_field(name="View all themes", value="` r!all `")
	embed.add_field(name="View a specific theme", value="View the name, author, description, a screenshot, and both JS code and Tampermonkey script (DM'd to you).` r!theme [id] `")
	await ctx.send(embed=embed)


client.run(os.getenv("TOKEN")) 
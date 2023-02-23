#!/usr/bin/env python3

# This bot integrates with an INIM SmartLiving unit and allows full remote administration via Telegram


__author__ = "Michele Lizzit"
__copyright__ = "Copyright 2018"
__credits__ = ["Michele Lizzit"]
__license__ = "AGPLv3"
__version__ = "0.1"
__maintainer__ = "Michele Lizzit"
__email__ = "info@lizzit.it"

import config
import common
import events_notifier

import time
import socket
import traceback
import functools
from telegram.ext import CommandHandler
from telegram.ext import Updater

ADMIN_USERS = [ config.ADMIN_CHAT ]
LOG_FILE = '/tmp/smartliving_bot.log'

# Handle requests from non-whitelisted users
def handleUnauthorized(update, context) :
	if update.effective_user.id not in ADMIN_USERS:
		update.message.reply_text("Unauthorized")
		return True
	return False

# Decorator to check if the user is authorized
def check_auth(f):
	functools.wraps(f)
	def wrapper(update, context):
		if (handleUnauthorized(update, context)):
			return
		return f(update, context)
	return wrapper

updater = Updater(token=config.TOKEN)
dispatcher = updater.dispatcher

# /start command
@check_auth
def start(update, context):
	update.message.reply_text("Hey, I am SmartLivingBot!")

# /activate command
@check_auth
def inserisciCommand(update, context):
	setCentraleStatus(update, context, "activate")

# /deactivate command
@check_auth
def disinserisciCommand(update, context):
	setCentraleStatus(update, context, "deactivate")

# Enable a set Scenario on a SmartLiving unit
def setCentraleStatus(update, context, status):
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.settimeout(2)
			s.connect((config.CENTRALE_HOST, config.CENTRALE_PORT))

			s.send(common.centrale_commands["auth"])
			s.send(common.centrale_commands["postauth"])
			r = s.recv(1024)
			if r != b"\x00\x00\x00":
				raise Exception("Autenticazione fallita")
			s.send(common.centrale_commands["getver"])
			r = s.recv(1024)
			s.send(common.centrale_commands["pre" + status])
			r = s.recv(1024)
			s.send(common.centrale_commands[ status ])
			r = s.recv(1024)
	except Exception as e:
		exc_formatted = traceback.format_exc()
		t = f"""Error while connecting to remote 📡:
		```
		{exc_formatted}
		```"""
		update.message.reply_text(t, disable_notification=config.SILENT_REPLIES, parse_mode=common.PMD)
		return

	t = "OK"
	update.message.reply_text(t, disable_notification=config.SILENT_REPLIES, parse_mode=common.PMD)

# Send the user the current status of remote
@check_auth
def centraleCommand(update, context):
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.settimeout(2)
			s.connect((config.CENTRALE_HOST, config.CENTRALE_PORT))

			s.send(common.centrale_commands["auth"])
			s.send(common.centrale_commands["postauth"])
			r = s.recv(1024)
			if r != b"\x00\x00\x00":
				raise Exception("Authentication failed")
			s.send(common.centrale_commands["getver"])
			r = s.recv(1024)
			centrale_version = r.decode('ascii', 'ignore')
			centrale_version = centrale_version.strip().strip()
			s.send(common.centrale_commands["getstatus"])
			r = s.recv(1024)
			centrale_scenario = r[:-1]
	except Exception as e:
		exc_formatted = traceback.format_exc()
		t = f"""Error while connecting to remote 📡:
		```
		{exc_formatted}
		```"""
		update.message.reply_text(t, disable_notification=config.SILENT_REPLIES, parse_mode=common.PMD)
		return

	centrale_status = "❔"
	# You may need to change these values depending on your configured scenarios
	if centrale_scenario == b"\x00":
		centrale_status = "🔴"
		centrale_scenario = "ACTIVATED"
	elif centrale_scenario == b"\x02":
		centrale_status = "🟢"
		centrale_scenario = "DEACTIVATED"

	t = f"""Centrale `V: {centrale_version}` 📡:
		{centrale_scenario} {centrale_status}"""
	update.message.reply_text(t, disable_notification=config.SILENT_REPLIES, parse_mode=common.PMD)

start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)
centrale_handler = CommandHandler('centrale', centraleCommand)
dispatcher.add_handler(centrale_handler)
centrale_inserisci_handler = CommandHandler('activate', inserisciCommand)
dispatcher.add_handler(centrale_inserisci_handler)
centrale_disinserisci_handler = CommandHandler('deactivate', disinserisciCommand)
dispatcher.add_handler(centrale_disinserisci_handler)

updater.start_polling()

while True:
	try:
		events_notifier.main()
	except Exception as e:
		exc_formatted = traceback.format_exc()
		print(exc_formatted)
		time.sleep(5)
	time.sleep(60)
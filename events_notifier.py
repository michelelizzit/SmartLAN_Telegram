#!/usr/bin/env python3

# This script is used to send a Telegram notification when the SmartLiving unit logs an event
# It's called every 60 seconds by home_bot.py


__author__ = "Michele Lizzit"
__copyright__ = "Copyright 2018"
__credits__ = ["Michele Lizzit"]
__license__ = "AGPLv3"
__version__ = "0.1"
__maintainer__ = "Michele Lizzit"
__email__ = "info@lizzit.it"

import config
import common

import socket
import traceback
from datetime import datetime
import json
import os
import os.path
import hashlib

from telegram import Bot

CACHE_FILE = "/tmp/events.json"
cache = []

# Store the last 5 events in a cache file, so we can avoid sending the same event multiple times
def load_cache():
	global cache
	if not os.path.exists(CACHE_FILE):
		cache = []
		return
	try:
		with open(CACHE_FILE, "r") as fd:
			cache = json.load(fd)
	except json.JSONDecodeError:
		cache = []
		return
def store_cache():
	json.dump(cache, open(CACHE_FILE, "w"))

# This is the main function, it's called every 60 seconds
def main():
	global cache

	load_cache()

	tmp = []
	try:
		with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
			s.settimeout(2)
			# Connect to the centrale
			s.connect((config.CENTRALE_HOST, config.CENTRALE_PORT))

			# Authenticate
			s.send(common.centrale_commands["auth"])
			s.send(common.centrale_commands["postauth"])
			r = s.recv(1024)
			if r != b"\x00\x00\x00":
				raise Exception("Authentication failed")

			# Get the centrale version
			s.send(common.centrale_commands["getver"])
			r = s.recv(1024)
			centrale_version = r.decode('ascii', 'ignore')
			centrale_version = centrale_version.strip()

			# Get the position of the last 5 events in the circular buffer
			eventi = []
			s.send(common.centrale_commands["getloggerpos"])
			r = s.recv(1024)
			if not common.centrale_verify_checksum(r):
				raise Exception("Invalid answer from remote (loggerpos)")
			r = bytes(reversed(r[:2]))
			loggerpos = int.from_bytes(r, "big") - 1

			# Fetch the last 5 events from the circular buffer
			for i in range(5):
				s.send(common.centrale_commands["getevent"]( (loggerpos - i) % 4096 ))
				r = s.recv(1024)
				if not common.centrale_verify_checksum(r):
					raise Exception(f"Invalid answer from remote (log {i})")
				dt = datetime.fromtimestamp(int.from_bytes(r[0:4], "little") + common.CENTRALE_TIMEOFFSET).strftime('%d/%m/%y %H:%M:%S')
				ev = r[6:6+36].decode('ascii', 'ignore')

				# Store an event hash in cache
				ev_hash = hashlib.sha256(r[:6+36]).hexdigest()
				tmp.append(ev_hash)
				if ev_hash not in cache:
					# If the event is not in cache, send it to the admin chat
					eventi.append((ev, dt))

	except Exception as e:
		traceback.print_exc()
		return
	
	if len(eventi) == 0:
		return

	cache = tmp
	store_cache()
	
	# If there are new events, send them to the admin chat
	t = f"""📡📡 *[NEW EVENTS]* 📡📡:"""
	emoji = lambda x : str(x) + "1️⃣ "[1:]
	for e,i in zip(eventi, range(len(eventi))):
		e, ts = e
		e = e.strip()
		t += f"\n{emoji(i)} {ts} `{e}`"
	
	bot = Bot(token=config.TOKEN)
	bot.send_message(chat_id=config.ADMIN_CHAT, text=t, disable_notification=config.SILENT_REPLIES, parse_mode=common.PMD)		

if __name__ == "__main__":
	main()
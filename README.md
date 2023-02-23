# INIM SmartLiving Telegram integration

This repository contains a very simple Telegram bot that integrates with an INIM SmartLiving unit.  
You need to have a SmartLAN/SI or SmartLAN/G module in order to connect the unit to the network.  
The server running this Telegram Bot needs to have direct access to the SmartLAN module and connect on port 5004.  

## Prerequisites
- An installed SmartLiving alarm system
- A SmartLAN/SI (or SmartLAN/G) Ethernet expansion card

## Features
- Fetch status and firmware information
- Send events from the event log via Telegram
- Activate scenarios (activate or deactivate the alarm system)

| ![](https://lizzit.it/dl/github_media/smartliving_1.png) | ![](https://lizzit.it/dl/github_media/smartliving_2.png) |
| -------------- | -------------- |
| Event notifications       | Activate scenarios       |

## Install dependencies
`python3 -m pip install -r requirements.txt`  

## Configure

Edit config.py to match your setup:
```python3
# Address of the SmartLiving unit
CENTRALE_HOST = "192.168.1.92"

# Port, by default it's 5004
CENTRALE_PORT = 5004

# Whether to send silent messages (no notification sound)
SILENT_REPLIES = True

# Chat ID where to send notifications
ADMIN_CHAT = 123456789

# Code of the SmartLiving unit
CODE = 00000

# Telegram bot token
TOKEN = '0000000000:AAAAAAAAAAAAAAAAAAAAAA-AAAAAAAAAAAA'
```

## Run
`python3 home_bot.py`

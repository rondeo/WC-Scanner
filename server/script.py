#!/usr/bin/env python3

# WS server example that synchronizes state across clients

import asyncio
import json
import logging
import os

import websockets
import subprocess

logging.basicConfig()

STATE = {'value': 0}

USERS = set()

def state_event():
    return json.dumps({'type': 'state', **STATE})

def users_event():
    return json.dumps({'type': 'users', 'count': len(USERS)})

async def notify_state():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def notify_users():
    if USERS:       # asyncio.wait doesn't accept an empty list
        message = users_event()
        await asyncio.wait([user.send(message) for user in USERS])

async def register(websocket):
    USERS.add(websocket)
    await notify_users()

async def unregister(websocket):
    USERS.remove(websocket)
    await notify_users()

async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data['action'] == 'minus':
                STATE['value'] -= 1
                await notify_state()
            elif data['action'] == 'plus':
                STATE['value'] += 1
                await notify_state()
            elif data['action'] == 'create_project':
                createProject(data['nameProject'])
            else:
                logging.error(
                    "unsupported event: {}", data)
    finally:
        await unregister(websocket)

async def createProject(message):
    subprocess.Popen('cd && mkdir .wcscanner -m 755 -p && cd .wcscanner && mkdir ' + message + ' -m -755 -p', shell=True)


asyncio.get_event_loop().run_until_complete(
    websockets.serve(counter, '10.154.124.140', 6789))
asyncio.get_event_loop().run_forever()

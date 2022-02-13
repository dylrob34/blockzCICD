from flask import Flask, request
import discord
import threading
from subprocess import call
from multiprocessing import Process
import asyncio
import os
from dotenv import load_dotenv
import sys

load_dotenv()

RUNNING = True

flask = Flask(__name__)

client = discord.Client()

blockz = None
crashes = None

messageQ = asyncio.Queue()

deploy_semaphore = threading.Semaphore()


def redeploy_script():
    deploy_semaphore.acquire()
    client.loop.create_task(blockz.send("Push to blockz...web server redeploying..."))
    call("./redeploy.sh")
    client.loop.create_task(blockz.send("Server Running"))
    deploy_semaphore.release()


def redeploy_thread():
    deploy = threading.Thread(target=redeploy_script)
    deploy.start()


@flask.route("/redeploy", methods=["POST", "GET"])
def redeploy():
    try:
        content = request.get_json()
    except Exception:
        print("didnt get any post data")
    redeploy_thread()
    return "", 200


@flask.route("/notifycrash", methods=["POST"])
def notify():
    content = request.get_json()
    client.loop.create_task(crashes.send(content["message"]))
    return "", 200


@flask.route("/message", methods=["POST"])
def message():
    content = request.get_json()
    client.loop.create_task(blockz.send(content["message"]))
    return "", 200



@flask.route("/stop")
def stop():
    client.loop.create_task((blockz.send("STOP")))
    return "", 200


@client.event
async def on_ready():
    print("ready")
    global blockz
    global crashes
    channels = client.get_all_channels()
    for channel in channels:
        if channel.name == "blockz":
            blockz = channel
            fl = threading.Thread(target=start_flask)
            fl.start()
            redeploy_thread()
        if channel.name == "crashes":
            crashes = channel


async def stop_discord():
    print("waiting")
    while True:
        message = await messageQ.get()
        if message == "STOP":
            break
    client.loop.stop()
    print("done")


async def send_discord():
    while True:
        print("Sending Message to Discord")
        mes = await messageQ.get()
        if mes == "STOP":
            sys.exit(0)
        await blockz.send("Test Message from a discord bot saying there has been a push to git hub and the web server is being redoployed")


def start_discord():
    print("starting discord")
    client.run(os.environ.get("TOKEN"))
    sys.exit(0)


def start_flask():
    flask.run(host="0.0.0.0", port=3435, debug=False)


def main():
    start_discord()


if __name__ == "__main__":
    main()

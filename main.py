from flask import Flask, request
import discord
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

toDo = None

messageQ = asyncio.Queue()


@flask.route("/", methods=["POST", "GET"])
def redeploy():
    try:
        content = request.get_json()
    except Exception:
        print("didnt get any post data")
    os.popen('chmod +x redeploy.sh')
    call("./redeploy.sh")
    client.loop.create_task(toDo.send("Push to toDo...web server redeploying..."))
    return "", 200


@flask.route("/stop")
def stop():
    client.loop.create_task((toDo.send("STOP")))
    return "", 200


@client.event
async def on_ready():
    fl = Process(target=start_flask())
    fl.start()
    print("ready")
    global toDo
    channels = client.get_all_channels()
    for channel in channels:
        if channel.name == "todo":
            toDo = channel


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
            client.loop.stop()
        await toDo.send("Test Message from a discord bot saying there has been a push to git hub and the web server is being redoployed")


def start_discord():
    print("starting discord")
    client.run(os.environ.get("TOKEN"))
    sys.exit(0)


def start_flask():
    flask.run(host="0.0.0.0", port=3435, debug=False)


def main():
    try:
        start_discord()
    except Exception:
        print("Something broke")


if __name__ == "__main__":
    main()

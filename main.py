from flask import Flask, request
import discord
import threading
from subprocess import call
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


@flask.route("/", methods = ["POST"])
def redeploy():
    content = request.get_json()
    call("./subprocess.sj")
    client.loop.create_task(toDo.send("Push to toDo...web server redeploying..."))
    return "", 200


@client.event
async def on_ready():
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
        await messageQ.get()
        await toDo.send("Test Message from a discord bot saying there has been a push to git hub and the web server is being redoployed")


def start_discord():
    print("starting discord")
    client.loop.create_task(stop_discord())
    client.run(os.environ.get("TOKEN"))
    sys.exit(0)


async def main():
    dis = threading.Thread(target=start_discord)
    dis.start()

    try:
        flask.run(host="0.0.0.0", port=3435, debug=True)
    except Exception:
        print("Something broke")
    finally:
        await messageQ.put("STOP")


if __name__=="__main__":
    asyncio.run(main())

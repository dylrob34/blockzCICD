from math import prod
from flask import Flask, request
import discord
import threading
from subprocess import call
import subprocess
from multiprocessing import Process
import asyncio
import os
from dotenv import load_dotenv
import sys
import json

load_dotenv()

RUNNING = True

flask = Flask(__name__)

client = discord.Client()

blockz = None
cicd = None
dev_crashes = None
prod_crashes = None

messageQ = asyncio.Queue()

deploy_semaphore = threading.Semaphore()


def redeploy_dev():
    deploy_semaphore.acquire()
    client.loop.create_task(cicd.send("Push to blockz...dev server redeploying"))
    subprocess.Popen(["chmod", "-x", "redeployDev.sh"])
    subprocess.Popen(["bash", "redeployDev.sh"])
    deploy_semaphore.release()


def redeploy_prod():
    deploy_semaphore.acquire()
    client.loop.create_task(cicd.send("Blockz PR...building new image and redeploying cloud server"))
    subprocess.Popen(["chmod", "-x", "redeployProd.sh"])
    subprocess.Popen(["bash", "redeployProd.sh"])
    client.loop.create_task(cicd.send("Pushed to Docker Hub"))
    deploy_semaphore.release()


def redeploy_thread(func):
    deploy = threading.Thread(target=func)
    deploy.start()


@flask.route("/github", methods=["POST", "GET"])
def github():
    try:
        content = request.get_json()
        branch = str(content["ref"]).split("/")[-1]
        if branch == "dev":
            redeploy_thread(redeploy_dev)
        elif branch == "main":
            redeploy_thread(redeploy_prod)
    except Exception:
        print("didnt get any post data")
    return "", 200


@flask.route("/devcrash", methods=["POST"])
def devcrash():
    content = request.get_json()
    client.loop.create_task(dev_crashes.send(content["message"]))
    return "", 200


@flask.route("/prodcrash", methods=["POST"])
def prodcrash():
    content = request.get_json()
    client.loop.create_task(prod_crashes.send(content["message"]))
    return "", 200


@flask.route("/cicd", methods=["POST"])
def cicd_message():
    content = request.get_json()
    client.loop.create_task(cicd.send(content["message"]))
    return "", 200


@flask.route("/message", methods=["POST"])
def message():
    content = request.get_json()
    client.loop.create_task(blockz.send(content["message"]))
    return "", 200



@flask.route("/stop")
def stop():
    client.loop.create_task((cicd.send("dev server stopping")))
    return "", 200


@client.event
async def on_ready():
    print("ready")
    global blockz
    global cicd
    global prod_crashes
    global dev_crashes
    channels = client.get_all_channels()
    for channel in channels:
        if channel.name == "blockz":
            blockz = channel
        if channel.name == "ci_cd":
            cicd = channel
        if channel.name == "dev_crashes":
            dev_crashes == channel
        if channel.name == "prod_crashes":
            prod_crashes == channel
    fl = threading.Thread(target=start_flask)
    fl.start()
    redeploy_thread(redeploy_dev)


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

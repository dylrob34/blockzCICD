#!/bin/bash

echo "Starting CICD Server"

rm nohup.out

source venv/bin/activate

python main.py
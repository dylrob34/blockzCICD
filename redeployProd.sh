#!/bin/bash

echo "Redeploying Blockz"

cd blockzProd

git pull

docker build -t dylrob34/blockz:latest .

docker push dylrob34/blockz:latest

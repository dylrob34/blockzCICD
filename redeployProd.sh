#!/bin/bash

echo "Redeploying Blockz"

cd blockzProd

git pull

docker buildx build --platform linux/amd64 -t dylrob34/blockz:latest --push .


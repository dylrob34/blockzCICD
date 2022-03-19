#!/bin/bash

echo "Redeploying Blockz"

docker stop $(docker ps -a -q --filter ancestor=dylrob34/blockz:dev --format="{{.ID}}")

docker image rm dylrob34/blockz:dev

cd blockzDev

git pull

cd ./backend

npm install

rm -rf build
mkdir build

cd ../frontend

npm install

npm run build

cd ..

mv ./frontend/build/* ./backend/build

docker build -t dylrob34/blockz:dev .

docker run -p 3001:3001 -d --rm dylrob34/blockz:dev


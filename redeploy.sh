#!/bin/bash

echo "Redeploying Blockz"

pkill "npm start"
pkill "node"

cd toDo

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

cd ./backend

npm start &

curl -fsSL https://deb.nodesource.com/setup_16.14 | sudo -E bash -
sudo apt-get install -y nodejs
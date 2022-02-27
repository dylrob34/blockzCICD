#!/bin/bash

echo "Redeploying Blockz"

pkill "npm start"
pkill "node"

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

cd ./backend

npm start &

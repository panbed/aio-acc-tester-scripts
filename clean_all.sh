#!/bin/bash

echo "Cleaning up..."

rm -R output
rm -R node_modules
rm -R package-lock.json
rm -R package.json
yes | rm -R phpally
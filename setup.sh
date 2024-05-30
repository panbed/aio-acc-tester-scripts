#!/bin/bash

function check_command () {
    if [[ ! $(command -v $1) ]]; then
        echo -e "$1 not found! AHHHHHHH"
        exit 1
    else
        echo -e "✓ Found $1!"
    fi
}

function npm_install () {
    npm --silent install $1
    if [[ $? -ne 0 ]]; then
        echo -e "Failed to install $1! aaaaAAAAAAAAAHHHHHHHHH"
        exit 1
    else
        echo -e "✓ Installed $1!"
    fi
}

echo "Checking for git, composer, node, npm, and php..."
check_command git
check_command node
check_command npm
check_command php
check_command composer

echo "Installing IBM's accessibility-checker..."
npm_install accessibility-checker

echo "Installing Deque System's axe-core..."
npm_install axe-core

echo "Downloading phpally..."
git clone git@github.com:panbed/phpally.git

echo "cd'ing into phpally directory..."
cd phpally
ls -lh

echo "Setting up phpally..."
echo "Running composer update..."
composer -v update
if [[ $? -ne 0 ]]; then
    echo "Composer has fallen! AAAAAAAAAA"
    exit 1
else
    echo -e "✓ composer update completed!"
fi

echo "Generating autoload files (this might take a bit!)"
composer dump-autoload -o

if [[ $? -ne 0 ]]; then
    echo "Failed to generate autoload files! aaaaAAAAAAAAAA"
    exit 1
else
    echo -e "✓ composer autoload files generated!"
fi

echo "Creating some extra folders..."
cd ..
mkdir output
mkdir output/ibm
mkdir output/deque
mkdir output/phpally

echo "✓ Finished setting up!"
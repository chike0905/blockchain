#!/bin/sh
hostname=$(hostname -i)
sudo cp -f blockchain/testscripts/tests_node$NODE.py blockchain/tests.py
python blockchain/tests.py $hostname

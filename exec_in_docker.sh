#!/bin/sh
hostname=$(hostname -i)
python blockchain/tests.py $hostname

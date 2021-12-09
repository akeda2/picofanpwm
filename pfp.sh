#!/bin/bash

[ ! -z "$1" ] && echo "$1" > /dev/ttyACM0 || echo "No value added!"
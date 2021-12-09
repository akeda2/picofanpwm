#!/bin/bash
#
# picofanpwm - control PWM fans with a RPi Pico
# (c) David Åkesso, 2021

# Default PWM value
PWM=60

# Debug mode?
# pfp debug ...
[ "$1" == "debug" ] && DEBUG=1; shift

# Target mode:
# pfp target nn
#
# Manual mode:
# pfp nn
# If debug is given, the program will run the main loop for debugging without changing PWM.
#
if [ ! -z "$1" ]; then
	if [ "$1" == "target" ]; then
		[ ! -z "$2" ] && TARGET="$2" || TARGET=62
	else
		if [ ! -z $DEBUG ]; then
			PWM="$1"
			MANUAL=1
		else
			echo "$1" > /dev/ttyACM0 && exit 0
		fi
	fi
fi
setpwm (){
	[ -z $1 ] && mypwm=60 || mypwm=$1
	[ $1 -le 20 ] && mypwm=20
	echo $mypwm > /dev/ttyACM0
}

# Read GPU-temp from an Nvidia GPU:
# (this is my use-case)
#
readtemp (){
	GPUTEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)
	echo $GPUTEMP
}

# Startup defaults
setpwm 60
lasttemp=50

# The main loop
#
while true; do
	mytemp=$(readtemp)
if [ -z $MANUAL ]; then
	if [ ! -z $TARGET ]; then
		if [ $mytemp -gt $TARGET ]; then
			PWM=$(($TARGET - ($mytemp - $TARGET) + (($mytemp - $lasttemp)*4)))
			UPDOWN=" UP "
		elif [ $mytemp -lt $TARGET ]; then
			PWM=$(($TARGET - ($TARGET - $mytemp) - (($lasttemp - $mytemp) / 4)))
			UPDOWN="DOWN"
		else
			UPDOWN="----"
			PWM=$PWM
		fi
	else
		if [ $mytemp -gt 75 ]; then
			PWM=100
		elif [ $mytemp -ge 65 ]; then
			#PWM=$((PWM + 5))
			PWM=80
		elif [ $mytemp -gt $lasttemp ]; then
			PWM=$((PWM + 2))
			UPDOWN=" UP "
		elif [ $mytemp -lt $lasttemp ]; then
			PWM=$((PWM -2))
			UPDOWN="DOWN"
		else
			#PWM=$((PWM - 1))
			PWM=$PWM
			UPDOWN="----"
		fi
	fi
else
	UPDOWN="MANU"
fi
	# Call the setpwm function
	#
	if [ $PWM -lt 31 ]; then
    		PWM=30
	elif [ $PWM -ge 100 ]; then
		PWM=100
	fi
	setpwm $PWM
	# If in debug mode, print to stdout. >/>> to redirect to logfile, use gnuplot file to view stats.
	#
	[ ! -z $DEBUG ] && echo "$(date +%Y-%m-%d-%H:%M:%S) $UPDOWN Temp: $lasttemp $mytemp  PWM: $PWM"
	lasttemp=$mytemp
	sleep 2

done

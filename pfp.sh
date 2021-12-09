#!/bin/bash

if [ ! -z "$1" ]; then
	if [ "$1" == "debug" ]; then
		DEBUG=1
	else
		echo "$1" > /dev/ttyACM0 && exit 0
	fi
fi
PWM=60

setpwm (){
	[ -z $1 ] && mypwm=60 || mypwm=$1
	[ $1 -le 20 ] && mypwm=20
	echo $mypwm > /dev/ttyACM0
}

readtemp (){
	GPUTEMP=$(nvidia-smi --query-gpu=temperature.gpu --format=csv,noheader)
	echo $GPUTEMP
}

setpwm 60
lasttemp=50
while true; do
	mytemp=$(readtemp)
	if [ $mytemp -gt 75 ]; then
		PWM=100
	elif [ $mytemp -ge 65 ]; then
		#PWM=$((PWM + 5))
		PWM=80
	elif [ $PWM -lt 21 ]; then
		PWM=20
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
	setpwm $PWM
	[ ! -z $DEBUG ] && echo "$UPDOWN Temp: $lasttemp $mytemp  PWM: $PWM"
	lasttemp=$mytemp
	sleep 2
done

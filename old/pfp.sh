#!/bin/bash
#
# picofanpwm - control PWM fans with a RPi Pico
# (c) David Åkesson, 2021

# Default PWM value
PWM=60

# Test
TEMP_MIN=35
TEMP_MAX=70
PWM_MAX=100
PWM_MIN=30


# Debug mode?
# pfp debug ...
[ "$1" == "debug" ] && DEBUG=1 && shift
[ "$1" == "service" ] && SERVICE=1 && shift
# Target mode:
# pfp target nn
#
# Manual mode:
# pfp nn
# If debug is given, the program will run the main loop for debugging without changing PWM.
#
setpwm (){
        [ -z $1 ] && mypwm=60 || mypwm=$1
        [ $1 -le 20 ] && mypwm=20
        TTY="/dev/ttyACM"
        if [ -c "$TTY"0 ]; then
                echo $mypwm > "$TTY"0
        else
                echo $mypwm > "$TTY"1
        fi
}

if [ ! -z "$1" ]; then
	if [ "$1" == "target" ]; then
		[ ! -z "$2" ] && TARGET="$2" || TARGET=62
	else
		if [ ! -z $DEBUG ]; then
			PWM="$1"
			MANUAL=1
		elif [ ! -z $SERVICE ]; then
			echo "(re)starting picofanpwm service with static value: $1"
			while true; do
				setpwm $1
				#echo "$1" > /dev/ttyACM0
				sleep 8
			done
		else
			echo "Sending $1 to ttyACM0"
			setpwm $1 && exit 0
			#echo "$1" > /dev/ttyACM0 && exit 0
		fi
	fi
fi

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
			step=$(((PWM_MAX - PWM_MIN) / (TEMP_MAX - TEMP_MIN)))
			thistemp=$(($myutemp - $TEMP_MIN))
			PWM=$((PWM_MIN + ($thistemp * $step)))
			#PWM=$(($TARGET - ($mytemp - $TARGET) + (($mytemp - $lasttemp)*4)))
			#echo "PWM=(TARGET:$TARGET - (mytemp:$mytemp - TARGET:$TARGET) + ((mytemp:$mytemp - lasttemp:$lasttemp)*4 : PWM=$PWM"
			UPDOWN=" UP "
		#elif [ $mytemp -lt $TARGET ]; then
		#	PWM=$(($TARGET - ($TARGET - $mytemp) - (($lasttemp - $mytemp) / 4)))
                        #echo "PWM=(TARGET:$TARGET - (TARGET:$TARGET - mytemp:$mytemp) - ((lasttemp:$lasttemp - mytemp:$mytemp)) /4) : PWM=$PWM"
		#	UPDOWN="DOWN"
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

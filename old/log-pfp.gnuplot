set term png size 960, 600
set output "plot.png"
set xdata time
set timefmt "%Y-%m-%d-%H:%M:%S"
#set format x "%Y.%m.%d-%H:%M"
set format x "%H:%M"
set yrange [30:80]
set y2range [0:100]
set y2tics 10
set my2tics 1
set grid y2tics
set ylabel "Temperature"
set y2label "PWM"

plot "debug.log" using 1:5 axes x1y1 with lines title 'Temperatur', \
	'' using 1:7 axes x1y2 with lines title 'PWM'

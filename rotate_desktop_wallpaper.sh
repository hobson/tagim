#!/bin/bash 
#/usr/local/bin/rotate_desktop_wallpaper.sh 

function d_start ( ) 
{ 
	echo  "rotate_desktop_wallpaper: starting service" 
	/usr/bin/rotate_desktop_wallpaper
	sleep  5 
	echo  "PID is $ (cat /tmp/rotate_desktop_wallpaper.pid) " 
}
 
function d_stop ( ) 
{ 
	echo  "Deluge: stopping Service (PID = $ (cat /tmp/rotate_desktop_wallpaper.pid) )" 
	kill $ ( cat  /tmp/rotate_desktop_wallpaper.pid ) 
	rm /tmp/rotate_desktop_wallpaper.pid
 }
 
function d_status ( ) 
{ 
	ps  -ef  |  grep rotate_desktop_wallpaper |  grep  -v  grep 
	echo  "PID indicate indication file $ (cat /tmp/rotate_desktop_wallpaper.pid 2&gt; /dev/null) " 
}
 
# Some Things That run always 
touch  /var/lock/rotate_desktop_wallpaper
 
# Management instructions of the service 
box  "$ 1"  in 
	start )
		d_start
		;; 
	Stop )
		d_stop
		;; 
	Reload )
		d_stop
		sleep  1
		d_start
		;; 
	Status )
		d_status
		;; 
	* ) 
	Echo  "Usage: $ 0 {start | stop | reload | status}" 
	exit  1 
	;; 
esac
 
exit  0
#!/bin/bash
# description: Wixeld server


# Start the service node
start() {
    cd /home/edison/Wixel
    ./start.sh &1
    echo "Wixel Dienst wurde gestartet"
    
}
# Restart the service FOO
stop() {
        
    kill $(cat /home/pi/Wixel/pid)
    rm /home/edison/Wixel/pid

    echo "Wixel Dienst wurde beendet"
}
### main logic ###
case "$1" in
start) 
start
    ;;
stop)
    stop
    ;;
status)
    status FOO
    ;;
restart|reload|condrestart)
    stop
    sleep 2
    start
    ;;
*)
    echo $"Usage: $0 {start|stop|restart|reload|status}"
    exit 1
esac
exit 0
										       

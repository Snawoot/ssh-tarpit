#!/usr/bin/python3

import re
import datetime
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: %s <logfilename>"%(sys.argv[0]) )
        sys.exit(0)
    else:
        logfile = sys.argv[1]
    
    regex = r"(\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2})\s([a-zA-Z]+)\s+([a-zA-Z]+):\s([a-zA-Z\s\(\)\'\d\.\,]+)"
    csv_timeformat = '%Y-%m-%d %H:%M:%S'
    csv_field_seperator=','
    
    logfile = open(logfile, 'r')
    connected = []
    connected_num=0
    
    while True:
        line = logfile.readline()
        if not line:
            break
    
        matchObj   = re.match(regex, line, re.M|re.I)
        date       = datetime.datetime.strptime(matchObj.group(1), '%Y-%m-%d %H:%M:%S')
        loglevel   = (matchObj.group(2)).strip()
        sendername = (matchObj.group(3)).strip()
        other      = (matchObj.group(4)).strip()
    
        if sendername == 'MAIN' and other == 'Server startup completed.':
            connected_num = 0
        elif sendername == 'TarpitServer' and other.endswith(' connected'):
            connected_num += 1
            connected.append( {'datetime': date, 'connected': connected_num} )
        elif sendername == 'TarpitServer' and other.endswith(' disconnected'):
            connected_num -= 1
            connected.append( {'datetime': date, 'connected': connected_num} )
    
    logfile.close()
    
    for conn in connected:
        print("%s%s%s"%(conn['datetime'].strftime(csv_timeformat), csv_field_seperator,conn['connected']))

if __name__ == '__main__':
    main()

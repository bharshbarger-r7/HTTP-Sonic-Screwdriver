# HTTP-Sonic-Screwdriver

A general purpose HTTP post timing tool

Takes a username list in a file (users.txt) and an optional password (default is '') and a POST parameter with the username and password values replaced with xux and xpx, respectively. Once run it will return how long each response took for each POST request. 


./HSS.py -h

usage: HSS.py [-h] [-u URL] [-p PASSWORD] [-d DELAY] [-P POSTDATA] [-e ENCODE] [-v]


optional arguments:

  -h, --help            

      show this help message and exit
  
  -u URL, --url URL
  
    The URL you want to test.
  
  -p PASSWORD, --password PASSWORD
  
    The password you want to test, default is null
                        
  -d DELAY, --delay DELAY
  
    Delay in seconds to rate limit requests. Default is 2 seconds
                        
  -P POSTDATA, --postdata POSTDATA
  
    The POST data string to send, contained in single
    quotes. Replace parameter values with a xux for
    username and xpx for password. Example:
                        
    "User=xux&Password=xpx&Lang=en"
                        
  -e ENCODE, --encode ENCODE
  
    Optionally URL encode all POST data
                        
  -v, --verbose         
      enable verbosity

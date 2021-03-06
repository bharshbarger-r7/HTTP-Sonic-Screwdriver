#!/usr/bin/env python

#HSS.py a tool to generically throw usernames at a login or other form to look for timing attacks
#maybe should implement a spider/scraper to find login forms as well to automate some
#probably a good idea to do more than timing attacks. maybe automate user enum on response data as well (forgot pw link, etc)

#By @arbitrary_code
try:
	import argparse, os, requests, signal, ssl, sys, time
	from requests.packages.urllib3.exceptions import InsecureRequestWarning
except Exception as e:
	print('\n  [!] Import(s) failed! ' +str(e))

class Screwdriver():

	def __init__(self):

		#defaults
		self.httpVerbs=['get', 'post', 'put', 'delete']
		self.httpVerb = 'post'
		self.postData=None
		self.cookieInput=None
		self.httpProxy = 'http://localhost:8080'
		self.httpsProxy = 'https://localhost:8080'
		self.userList=[]
		self.userPass=None
		self.postData=None
		self.url=None
		self.verbose=False
		self.encode=False
		self.proxyDict = { 
	              "http"  : self.httpProxy, 
	              "https" : self.httpsProxy}

	def signal_handler(self, signal, frame):
		print('You pressed Ctrl+C! Exiting...')
		sys.exit(0)

	def cls(self):
		os.system('cls' if os.name == 'nt' else 'clear')

	def cmdargs(self):

		parser = argparse.ArgumentParser()
		parser.add_argument('-c', '--cookie', nargs=1, metavar='<cookieInput>', help='Optionally, specify cookie data')
		parser.add_argument('-u', '--url', nargs = 1, metavar='http://www.foo.com/login' ,help = 'The URL you want to test.')
		parser.add_argument('-p', '--password', nargs = 1, metavar='P@55w0rd!',help = 'The password you want to test, default is null')
		parser.add_argument('-d', '--delay', nargs =1, metavar='2',help = 'Optionally set a delay in seconds to rate limit. Default is 2 seconds.')
		parser.add_argument('-P', '--postdata', nargs = 1, metavar="User=xux&Password=xpx&Lang=en",help='The POST data string to send, contained in single quotes.\nReplace parameter values with a xux for username and xpx for password.')
		#parser.add_argument('-G'. '--getdata', nargs = 1, help = 'Data to use in the GET request')
		parser.add_argument('-e', '--encode', help='Optionally URL encode all POST data', action = 'store_true')
		parser.add_argument('-v', '--verbose', help='Optionally enable verbosity', action = 'store_true')
		parser.add_argument('-V', '--verb', nargs=1, metavar='post',help='HTTP Verb to use')
		parser.add_argument('-x', '--proxy', nargs=1, metavar='localhost:8080',help='Optionally specify a proxy')
		parser.add_argument('-f', '--postfile', metavar='postdata.txt', help='POST data contained in a file')
		args = parser.parse_args()

		version='1.0-04202017'

		if self.verbose is True:

			print(
			'''
			 _   _ _____ _____ ____    ____              _ 
			| | | |_   _|_   _|  _ \  / ___|  ___  _ __ (_) ___ 	  
			| |_| | | |   | | | |_) | \___ \ / _ \| '_ \| |/ __|     
			|  _  | | |   | | |  __/   ___) | (_) | | | | | (__        
			|_| |_| |_|   |_| |_|     |____/ \___/|_| |_|_|\___|        
			                                                           
			 ____                            _      _                  
			/ ___|  ___ _ __ _____      ____| |_ __(_)_   _____ _ __  
			\___ \ / __| '__/ _ \ \ /\ / / _` | '__| \ \ / / _ \ '__|   
			 ___) | (__| | |  __/\ V  V / (_| | |  | |\ V /  __/ |      
			|____/ \___|_|  \___| \_/\_/ \__,_|_|  |_| \_/ \___|_|     
																       
			HSS - A Generic HTTP Timing Attack tool					   
																	   
			%s 													   

			''' % version)
			#print args

		print('HSS started at: %s' % (time.strftime("%d/%m/%Y - %H:%M:%S")))


		if args.url is None:
			print('\n[!] Enter a URL to test\n') 
			parser.print_help()
			sys.exit(0)

		if args.verb is None:
			print('[i] Verb not specified, using POST')


		#check for post data in -P arg or file supplied in -f
		#if both are blank
		if args.postdata is None and args.postfile is None:
			#tell the user and exit
			print('\n[-] No POST data entered! Please use -P for inline or -f for a file containing data. Exiting! Use -h for help\n')
			sys.exit(0)
		#otherwise
		else:
			#if -P has data
			if args.postdata is not None:
				#set post data with supplied arg value
				self.postData = ''.join(args.postdata)

			#if -f has data
			if args.postfile is not None:
				#open  to read as object f
				with open(args.postfile,'r') as f: 
					#read the contents into the userList dictionary
					self.postData = ''.join(f.read().splitlines())
					if args.verbose is True:print('postdata: \n %s' % self.postData)

		
			


		if args.password is not None:
			self.userPass = ''.join(args.password)

		if args.delay is None:
			self.delay = float('2')
		else:
			self.delay = float(str(''.join(args.delay)))

		for u in args.url:
			self.url = args.url
			if self.verbose is True:print ('[i] Url entered is: '.join(self.url)+'\n')

		if args.password is None:
			self.userPass = ''

		if args.password is not None:
			self.userPass = ''.join(args.password)

		if args.cookie is not None:
			self.cookieInput = ''.join(args.cookie)
		
			cookieVal = self.cookieInput.split('=')[0]
			cookieData = self.cookieInput.split('=')[1]

			self.cookieData = {str(cookieVal):str(cookieData)}
			print(self.cookieData.items())
		else:
			self.cookieData = ''


		self.verbose=args.verbose

		if args.proxy is not None:
			self.httpProxy = args.proxy
			self.httpsProxy = args.proxy
		else:
			self.httpProxy = ''
			self.httpProxy = ''

		
			

	def request(self):
		#http://docs.python-requests.org/en/master/user/quickstart/

		signal.signal(signal.SIGINT, self.signal_handler)
		
		print('[i] Testing URL: %s ' % ''.join(self.url))
		print('[i] Testing post data of: %s ' % self.postData)
		print('%-8s %-8s %-s'% ('Response', 'Time(ms)','user:pass'))

		#open users.txt to read as object f
		with open('users.txt','r') as f: 
			#read the contents into the userList dictionary
			self.userList =f.read().splitlines()
			#for each line find its index and value
			for i, userID in enumerate(self.userList):

				#finx xux in your string
				if self.postData.find('xux'):
					#replace the string with the user id at the first i value
					self.postData=self.postData.replace('xux', str(self.userList[i]))

				#find xpx in the string
				if self.postData.find('xpx'):
					#replace xpx with the the password specified otherwise its blank
					self.postData=self.postData.replace('xpx', str(self.userPass))
				
				if self.postData.find(str(self.userList[i-1])):
					self.postData=self.postData.replace(str(self.userList[i-1]),str(self.userList[i]))

				if self.encode is True:
					self.postData = urllib.urlencode(str(self.postData))


				#ignore ssl errors
				requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

				#loop through urls as potentially you'd want to test more than 1
				for u in self.url:
					try:
						#set verbosity to print the url
						if self.verbose is True:print ('\n[+] ____Testing____ \n %s'% str(u))
						#record statt time
						startTime=time.time()
						#test for verb. this probably could be done better
						#uses http://docs.python-requests.org/en/master/api/
						if self.httpVerb == 'post':
							response = requests.post(u,str(self.postData),cookies=self.cookieData,verify=False)
						

						if self.httpVerb == 'get':
							response = requests.get(u) #basic auth needs a header Authorization: Basic 
						

						if self.httpVerb == 'put':
							response = requests.put(u)
						

						if self.httpVerb == 'delete':
							response = requests.delete(u)
						
						#record elapsed time
						elapsedTime = str(round((time.time()-startTime)*1000.0))





						#if verbose print the response from the server. probabaly better to write to a file?
						if self.verbose is True:
							print('____SENDING_____\n %s %s \n %s' % (self.httpVerb.upper(),u,str(self.postData)))



							print('____RESPONSE HEADERS____')
							for k in response.headers.items():
								print ('%s : %s' % (k[0], str(k[1].split(';'))+'\n'))
							print('________________________')
							#print(response.text) #dump all response content html

						#return the elapsed time with the user id and password and status code
						#print ('HTTP '+str(response.status_code)+' '+"{:<1}".format(str(elapsedTime))+'ms'+' '+str(userID)+':'+str(self.userPass)+' ')
						print('HTTP %-3s %-8s %s : %s'% (str(response.status_code), str(elapsedTime), str(userID), str(self.userPass)) )

					except requests.exceptions.RequestException as e:
					    print(e)
					    sys.exit(1)



				
				#if verbose print the post data too
				if self.verbose is True: print('[i] POST data: %s' % str(self.postData))
				#throttle based on delay arg
				time.sleep(self.delay)
			

def main():

	run = Screwdriver()
	run.cls()
	run.cmdargs()
	run.request()

if __name__ == '__main__':
    main()

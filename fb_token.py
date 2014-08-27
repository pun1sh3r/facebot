import mechanize
import re
import ConfigParser


'''
Note:

This will not work, the error from facepy is:

facepy.exceptions.OAuthError: [12] (#12) fql is deprecated for versions v2.1 and higher

docs: https://developers.facebook.com/docs/apps/upgrading
	  https://github.com/jgorset/facepy/issues/103


Proposed Fix:
	1 - automate https://github.com/pun1sh3r/facebot/tree/dev-branch#instructions-for-getting-target_mode-to-work
'''

class GetToken:

	def __init__(self, config_file):
		self.config_file = config_file
		global config
		config = ConfigParser.ConfigParser()

	def SetLast(self, access_token):
		config.set('profile-info', 'api_key', '"'+access_token+'"') #I am guessing " is important
		with open(self.config_file, 'w') as configfile:
			config.write(configfile) 


	def GetConfig(self):
		configData = {}
		config.read(self.config_file)
		options = config.options('profile-info')
		for i in options:
			configData[i] = config.get('profile-info', i)

		
		return configData

	
	def browser(self):

		#Keeping things Organized
		fetch = self.GetConfig()
		username = fetch['username'].replace("\"","") # Why is there " in config?????????
		password = fetch['password'].replace("\"","")
		app_id = fetch['app_id'].replace("\"","")
		app_secret = fetch['app_secret'].replace("\"","")


		get_code_url = 'https://www.facebook.com/v2.0/dialog/oauth?client_id=%s&display=popup&response_type=token&redirect_uri=https://www.facebook.com/connect/login_success.html&response_type=code' %app_id
		br = mechanize.Browser()
		br.set_handle_equiv(True)
		br.set_handle_redirect(True)
		br.set_handle_referer(True)
		br.set_handle_robots(False)
		br.set_handle_refresh(False)

		br.open(get_code_url)
		
		last_response = br.response()
		br.form = list(br.forms())[0]
		br['email'] = username
		br['pass'] = password
		r = br.submit()

		regexp = "code=.*"
		regexp = re.compile(regexp, re.IGNORECASE)
		result = regexp.search(br.geturl())

		if (result):
		    code = result.group().split('code=')[1]
		else:
		    pass

		short_life_token_link = 'https://graph.facebook.com/v2.0/oauth/access_token?client_id=%s&client_secret=%s&redirect_uri=https://www.facebook.com/connect/login_success.html&code=%s' %(app_id, app_secret, code)
		#print short_life_token_link
		br.open(short_life_token_link)

		#life = self.tsplit(br.response().read(),('access_token=','&expires='))[2]
		short_life_token=self.tsplit(br.response().read(),('access_token=','&expires='))[1] #Short ttl, around an hour
		long_life_token_link = 'https://graph.facebook.com/v2.0/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' %(app_id, app_secret, short_life_token)
		br.open(long_life_token_link)
		long_life_token=self.tsplit(br.response().read(),('access_token=','&expires='))[1] 

		#return short_life_token #is there diff
		print 'Got Token...'
		#print long_life_token_link
		return long_life_token

	def tsplit(self, string, delimiters):
    
	    delimiters = tuple(delimiters)
	    stack = [string,]
	    
	    for delimiter in delimiters:
	        for i, substring in enumerate(stack):
	            substack = substring.split(delimiter)
	            stack.pop(i)
	            for j, _substring in enumerate(substack):
	                stack.insert(i+j, _substring)
	            
	    return stack

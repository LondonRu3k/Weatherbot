import urllib2
import json
import traceback
import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import re
import sqlite3
from operator import itemgetter 
'''USER CONFIGURATION'''

USERNAME  = "WeatherReportBot"
#This is the bot's Username. In order to send mail, he must have some amount of Karma.
PASSWORD  = "woodeye"
#This is the bot's Password. 
USERAGENT = "LondonRuek"
#This is a short description of what the bot does. For example "/u/GoldenSights' Newsletter bot"
SUBREDDIT = "botwatch+learnpython+flying+goldtesting"
#This is the word you want to put in reply
MAXPOSTS = 100
#This is how many posts you want to retrieve all at once. PRAW can download 100 at a time.
WAIT = 20
#This is how many seconds you will wait between cycles. The bot is completely inactive during this time.


'''All done!'''

try:
    import bot #This is a file in my python library which contains my Bot's username and password. I can push code to Git without showing credentials
    USERNAME = bot.getu()
    PASSWORD = bot.getp()
    USERAGENT = bot.geta()
except ImportError:
    pass

sql = sqlite3.connect('sql.db')
print('Loaded SQL Database')
cur = sql.cursor()

cur.execute('CREATE TABLE IF NOT EXISTS oldposts(ID TEXT)')
print('Loaded Completed table')

sql.commit()

print('Logging in...')
r = praw.Reddit(USERAGENT)
r.login(USERNAME, PASSWORD) 

def scanSub():
    print('Searching '+ SUBREDDIT + '.')
    subreddit = r.get_subreddit(SUBREDDIT)
    posts = subreddit.get_comments(limit=MAXPOSTS)
    for post in posts:
        pid = post.id
        try:
            pauthor = post.author.name
            cur.execute('SELECT * FROM oldposts WHERE ID=?', [pid])
            if not cur.fetchone():
                pbody = post.body.lower()
		searchObj = re.match( r'(?:weather! )(.*)', pbody).group()
		if searchObj:
		  replaceObj = re.sub(r'\s+', '%20', searchObj)
		  print "Post Found"
		  if pauthor.lower() != USERNAME.lower():
			      print ' Replying to comment'
		              try:
					# This is the api connection to wunderground.com
					f = urllib2.urlopen('http://api.wunderground.com/api/0875dc1c4956be3b/geolookup/conditions/q/' + replaceObj + '.json')
					json_string = f.read()
					parsed_json = json.loads(json_string)
					temp = parsed_json['current_observation']['temperature_string']
					location = parsed_json['current_observation']['display_location']['city']
					wind_mph = parsed_json['current_observation']['wind_string']
					icon = parsed_json['current_observation']['icon']
					precip = parsed_json['current_observation']['precip_today_string']
					post.reply( "Current Temperature in " + location + " is " + temp  + " with winds " + wind_mph  + ". It is " + icon + " with " + precip + "rain today so far.")
					f.close()
			      except KeyError:
					pass
					print ' Passing Comment with invalid syntax'
					post.reply("Sorry this place either does not exist or is not available from wunderground.com")
		  if not pauthor.lower() != USERNAME.lower():
				print ' Will not reply to self'
		  cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
	except AttributeError:
		#Author is deleted. We don't care about this
		pass
sql.commit()
	
	

0	

while True:
    try:
        scanSub()
    except Exception as e:
        traceback.print_exc()
    print('Running again in %d seconds \n' % WAIT)
    sql.commit()
    time.sleep(WAIT)

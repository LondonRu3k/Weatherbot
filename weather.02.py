import traceback
import praw # simple interface to the reddit API, also handles rate limiting of requests
import time
import sqlite3
import weatherapi
from operator import itemgetter 
'''USER CONFIGURATION'''

USERNAME  = "WeatherReportBot"
#This is the bot's Username. In order to send mail, he must have some amount of Karma.
PASSWORD  = "woodeye"
#This is the bot's Password. 
USERAGENT = "Weather Report Bot"
#This is a short description of what the bot does. For example "/u/GoldenSights' Newsletter bot"
SUBREDDIT = "GoldTesting"
#This is the sub or list of subs to scan for new posts. For a single sub, use "sub1". For multiple subreddits, use "sub1+sub2+sub3+..."
Pick = itemgetter(2)
#This grabs zipcode
PARENTSTRING = ["Weather!"]
#These are the words you are looking for
REPLYSTRING = ['[Here is your Weather Report](www.thefuckingweather.com/?where=' + search]
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
                search = re.search(?:Weather!(.*))
                    if pauthor.lower() != USERNAME.lower():
                        print('Replying to ' + pid + ' by ' + pauthor)
                        post.reply(REPLYSTRING)
                    else:
                        print('Will not reply to self')
                cur.execute('INSERT INTO oldposts VALUES(?)', [pid])
        except AttributeError:
            #Author is deleted. We don't care about this
            pass
    sql.commit()


while True:
    try:
        scanSub()
    except Exception as e:
        traceback.print_exc()
    print('Running again in %d seconds \n' % WAIT)
    sql.commit()
    time.sleep(WAIT)
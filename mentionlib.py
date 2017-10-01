import json
from twitter_api import apikey, apisecret, token, tokensecret
from twython import Twython

twitter = Twython(apikey, apisecret, token, tokensecret)

# Pull down the most recent twitter mention JSON data
def getlastmentionjson():
    try:
        lastmention = twitter.get_mentions_timeline(count=1)
        return lastmention
    except ValueError:
        print('I could not retrieve my last mention JSON.')


# Parse JSON data into dictionary
def parsementionjson(lastmentionjson):
    try:
        lastmentionparsed = json.dumps(lastmentionjson)
        lastmentiondict = json.loads(lastmentionparsed)[0]
        return lastmentiondict
    except ValueError:
        print('I could not parse the mention JSON received: ' + lastmentionjson)


# Find the screen name of the mentioner
def getmentionscreenname(lastmentiondict):
    try:
        userdict = lastmentiondict['user']
        screen_name = userdict['screen_name']
        return screen_name
    except ValueError:
        print('I could not determine the screen name of the mentioner.')


# Initialize the last mention ID
def initmentionid(lastmentiondict):
    try:
        initmentionid = lastmentiondict['id']
        return initmentionid
    except ValueError:
        print('I could not determine the ID of the last mention.')


# Get the last mention ID
def getlastmentionid(lastmentiondict):
    try:
        lastmentionid = lastmentiondict['id']
        return lastmentionid
    except ValueError:
        print('I could not determine the ID of the last mention.')


# Get the text of the last mention
def getlastmentiontext(lastmentiondict):
    try:
        lastmentiontext = lastmentiondict['text']
        return lastmentiontext
    except ValueError:
        print('I could not determine the text of the last mention.')

def verifymentioner(screenname):
    try:
        if screenname == 'XianClasen':
            return 'Verified'
        else:
            return 'Unverified'
    except ValueError:
        print('I could not verify the screen name.')


# Make sure the mention is new
def verifymentionid(mentionid, initmentionid):
    try:
        if int(mentionid) != int(initmentionid):
            return 'Verified'
        else:
            return 'Unverified'
    except ValueError:
        print('I could not verify the mention ID.')

# Create a tweet with given text
def createtweet(tweetstring):
    try:
        twitter.update_status(status=tweetstring)
    except ValueError:
        print('I failed to create the tweet.')

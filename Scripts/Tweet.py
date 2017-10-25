import re


########################################################
## Define user and tweet's attributes. 
## Full attributes means all atts downloaded. attributes means atts may be used in our method.
## each attri correspondes to a number(attIndex)
userFullAttNames = ["id_str","screen_name","name","description",
"created_at","location","lang",
"statuses_count","favourites_count","listed_count","friends_count","followers_count",
"id","time_zone","utc_offset","is_translator","default_profile","contributors_enabled","protected","geo_enabled","verified","show_all_inline_media",
"profile_link_color","profile_background_color","profile_background_image_url","profile_use_background_image","profile_image_url_https","profile_image_url","profile_text_color","profile_sidebar_border_color","profile_background_image_url_https","default_profile_image","profile_background_tile","profile_sidebar_fill_color"]

tweet_entitiesAttNames = ["media","user_mentions","hashtags","urls"]
tweetFullAttNames = ["id_str","user_id_str","text","created_at",
"user_mentions","hashtags","urls",
"retweet_count","retweeted","favorited",
"in_reply_to_status_id_str", "lang",
"symbols",
"id","entity_linkified_text","media","is_rtl_tweet","truncated","source"]

userAttNames = userFullAttNames[0:12]
tweetAttNames = tweetFullAttNames[0:13]
userAttHash = {} # attName:attIndex_in_userAttNames
tweetAttHash = {} # attName:attIndex_in_tweetAttNames

uAttIndex = 0
for uAtt in userAttNames:
    userAttHash[userAttNames[uAttIndex]] = uAttIndex
    uAttIndex += 1

for tAttIndex in range(len(tweetAttNames)):
    tweetAttHash[tweetAttNames[tAttIndex]] = tAttIndex



########################################################
## Define class user(12) and tweet(10) with all (may) used atts.

class User:
    def __init__(self,userAtts):
        self.id_str = userAtts[userAttHash.get("id_str")]
        self.screen_name = userAtts[userAttHash.get("screen_name")]
        self.name = userAtts[userAttHash.get("name")]
        self.description = userAtts[userAttHash.get("description")]
        self.created_at = userAtts[userAttHash.get("created_at")]
        self.location = userAtts[userAttHash.get("location")]
        self.lang = userAtts[userAttHash.get("lang")]
        self.statuses_count = userAtts[userAttHash.get("statuses_count")]
        self.favourites_count = userAtts[userAttHash.get("favourites_count")]
        self.listed_count = userAtts[userAttHash.get("listed_count")]
        self.friends_count = userAtts[userAttHash.get("friends_count")]
        self.followers_count = userAtts[userAttHash.get("followers_count")]
        

class Tweet:
    def __init__(self,tweetAtts):
        self.id_str = tweetAtts[tweetAttHash.get("id_str")]
        self.user_id_str = tweetAtts[tweetAttHash.get("user_id_str")]
        self.text = tweetAtts[tweetAttHash.get("text")]
        self.created_at = tweetAtts[tweetAttHash.get("created_at")]
        #self.media = tweetAtts[tweetAttHash.get("media")]
        self.user_mentions = tweetAtts[tweetAttHash.get("user_mentions")]
        self.hashtags = tweetAtts[tweetAttHash.get("hashtags")]
        self.urls = tweetAtts[tweetAttHash.get("urls")]
        self.retweet_count = tweetAtts[tweetAttHash.get("retweet_count")]
        #self.is_rtl_tweet = tweetAtts[tweetAttHash.get("is_rtl_tweet")]
        self.retweeted = tweetAtts[tweetAttHash.get("retweeted")]
        self.favorited = tweetAtts[tweetAttHash.get("favorited")]
        self.in_reply_to_status_id_str = tweetAtts[tweetAttHash.get("in_reply_to_status_id_str")]
        self.lang = tweetAtts[tweetAttHash.get("lang")]
        #self.truncated = tweetAtts[tweetAttHash.get("truncated")]

        self.symbols = tweetAtts[tweetAttHash.get("symbols")]
        
    ## feature used
    def setTF_IDF_Vector(self,TF_IDF_Vector):
        self.TF_IDF_Vector = TF_IDF_Vector

## extract a tweet for current tweetLine
def getTweet(jsonObj):
    tweetAtts = []
    if not jsonObj.has_key('id_str'):
        return None
    tweetAtts.append(jsonObj['id_str'])
    tweetAtts.append('user_id_str')# user-id will be assigned later
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'text')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'created_at')
    #tweetAtts = getValue_from2ndLayer_InJson(tweetAtts,jsonObj,'entities','media')
    tweetAtts = getValue_from2ndLayer_InJson(tweetAtts,jsonObj,'entities','user_mentions')
    tweetAtts = getValue_from2ndLayer_InJson(tweetAtts,jsonObj,'entities','hashtags')
    tweetAtts = getValue_from2ndLayer_InJson(tweetAtts,jsonObj,'entities','urls')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'retweet_count')
    #tweetAtts = getValue_InJson(tweetAtts,jsonObj,'is_rtl_tweet')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'retweeted')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'favorited')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'in_reply_to_status_id_str')
    tweetAtts = getValue_InJson(tweetAtts,jsonObj,'lang')
    tweetAtts = getValue_from2ndLayer_InJson(tweetAtts,jsonObj,'entities','symbols')
    
    tweet = Tweet(tweetAtts)
    tweet = textInOneLine(tweet)

    return tweet

## extract an user for current tweetLine
def getUser(jsonObj):
    userAtts = []
    if not jsonObj.has_key('user'):
        return None
    if not jsonObj['user'].has_key('id_str'):
        return None
    
    userAtts.append(jsonObj['user']['id_str'])
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','screen_name')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','name')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','description')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','created_at')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','location')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','lang')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','statuses_count')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','favourites_count')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','listed_count')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','friends_count')
    userAtts = getValue_from2ndLayer_InJson(userAtts,jsonObj,'user','followers_count')
    
    user = User(userAtts)
    return user


# special processing in Tweet.text, replace \n with " "
def textInOneLine(currTweet):
    currTweet.text = re.sub("\n", " ", currTweet.text)
    currTweet.text = re.sub("\s+", " ", currTweet.text).strip()
    return currTweet

def getValue_InJson(attArr, jsonObj, keyword):
    if jsonObj.has_key(keyword):
        attArr.append(jsonObj[keyword])
    else:
        attArr.append(None)
    return attArr
    
def getValue_from2ndLayer_InJson(attArr, jsonObj, keyword1, keyword2):
    if not jsonObj.has_key(keyword1):
        attArr.append(None)
        return attArr
    if jsonObj[keyword1].has_key(keyword2):
            attArr.append(jsonObj[keyword1][keyword2])
    else:
        attArr.append(None)
        #print "Not Found " + keyword1 + " - " + keyword2
        #statistic number of atts missed
        keyword = keyword1 + "-" + keyword2
    return attArr



#Twitter access tutorial from StoryBench
#https://www.storybench.org/how-to-collect-tweets-from-the-twitter-streaming-api-using-python/

#connects to twitter using tweepy API.
#pulls tweets containing hardcoded tags (variable tags)
#run NLP sentiment analysis pipeline using hugging face tranformers API.
#write sentiment, confidence score, and tweet to out.csv file. 
#continues running until cancelled. (CTRL+C in shell)

#TODO: record geo coordinates: in progress
#TODO: Tests with German sentences suggest that Transformers does not work reliably on non-English text. 
#      Use https://pypi.org/project/langdetect/ to detect English and filter out other tweets. DONE! Used languages="en" in stream filter.
#TODO: run sentimental analysis on original tweets only.    
#TODO: Remove userhandles before sentiment analysis. 
#TODO: how to set repeat schedule for pulls?
#TODO: how to set time range for pulls?
#TODO: are tags case sensitive?
#TODO: are these pulls or pushes? REST?


import tweepy
from transformers import pipeline
import time
import pandas as pd

# authorization tokens
df = pd.read_csv('secretKeys.txt')#read access and consumer keys from separate file, not stored on git, for account security
#Use the secretKeysSample.txt file. Place your own keys in the file and rename to secretKeys.txt 
consumer_key    = df.loc[df['keyName'] == "consumer_key"].iloc[0][1]
consumer_secret = df.loc[df['keyName'] == "consumer_secret"].iloc[0][1]
access_key      = df.loc[df['keyName'] == "access_key"].iloc[0][1]
access_secret   = df.loc[df['keyName'] == "access_secret"].iloc[0][1]

# StreamListener class inherits from tweepy.StreamListener and overrides on_status/on_error methods.
class dataWriter(tweepy.Stream):
    def on_status(self, status):
        print(status.id_str)
        # if "retweeted_status" attribute exists, flag this tweet as a retweet.
        is_retweet = hasattr(status, "retweeted_status")

        # check if text has been truncated
        if hasattr(status,"extended_tweet"):
            text = status.extended_tweet["full_text"]
        else:
            text = status.text
        
        # check if this is a quote tweet.
        is_quote = hasattr(status, "quoted_status")
        quoted_text = ""
        if is_quote:
            # check if quoted tweet's text has been truncated before recording it
            if hasattr(status.quoted_status,"extended_tweet"):
                quoted_text = status.quoted_status.extended_tweet["full_text"]
            else:
                quoted_text = status.quoted_status.text
        
        #run sentiment analysis before removing white space and commas
        sentiment = nlp(text)[0]
        sentimentLabel = sentiment['label']
        sentimentScore = round(sentiment['score'], 4)
        
        # remove characters that might cause problems with csv encoding         #Removed: use inverted commas to include commas in CSV.
        #text = ' '.join(text.split())#remove white space
        #text = ' '.join(text.split(',')) # remove commas (breaks CSV) TODO: change code when implementing SQL
        #quoted_text = ' '.join(quoted_text.split())#remove white space
        #quoted_text = ' '.join(quoted_text.split(',')) # remove commas (breaks CSV) TODO: change code when implementing SQL
        
        print("The geo is : " + str(status.geo))
        if (status.geo !=None):
            print("The geo coordinates are : " + str(status.geo.coordinates))
        print("The coordinates are : " + str(status.coordinates))
        if (status.coordinates !=None):
            print("The coordinates are : " + str(status.coordinates.coordinates))
        print("The place is : " + str(status.place))
        if (status.place !=None):
            print("The place coordinates are: " + str(status.place.bounding_box.type))
            print("The place coordinates are: " + str(status.place.bounding_box.coordinates))
            print("The place coordinates are: " + str(status.place.full_name))
        print("The poster's profile name is : " + status.user.screen_name)
        if (status.user.location !=None):
            print("The poster's profile location is : " + status.user.location)


        with open("out.csv", "a", encoding='utf-8') as f:
            f.write("%s,%s,%s,%s,\"%s\",\"%s\",%s,%s\n" % (status.created_at,status.user.screen_name,is_retweet,is_quote,text,quoted_text, sentimentLabel, sentimentScore))        #use inverted commas to include commas in CSV.
                                                    #Note that excel displays in Latin-1 (cp1252) by default.
                                                    #To correctly display utf-8 (inverted commas, emojis etc.) follow these instructions:
                                                    #https://answers.microsoft.com/en-us/msoffice/forum/all/how-to-open-utf-8-csv-file-in-excel-without-mis/1eb15700-d235-441e-8b99-db10fafff3c2

    def on_error(self, status_code):
        print("Encountered streaming error (", status_code, ")")
        sys.exit()

if __name__ == "__main__":
    #initialize sentimental analysis model
    print("loading pipline")
    start = time.time()
    nlp = pipeline("sentiment-analysis")
    end = time.time()
    elapsed = end - start
    print(f"pipeline loaded. Time to complete: {elapsed}")

    # complete authorization and initialize API endpoint
    #auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    #auth.set_access_token(access_key, access_secret)
    #api = tweepy.API(auth)

    # initialize stream
    #streamListener = StreamListener()
    #stream = tweepy.Stream(auth=api.auth, listener=streamListener,tweet_mode='extended')
    
    stream = dataWriter(consumer_key, consumer_secret, access_key, access_secret)#stream call as per Tweepy 4.0
    with open("out.csv", "w", encoding='utf-8') as f:
        f.write("date,user,is_retweet,is_quote,text,quoted_text,sentiment,score\n")
    tags = ["food"]
    stream.filter(languages=["en"], track=tags) # ensures that only English tweets are recorded.


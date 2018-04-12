from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, KafkaClient
import json

access_token = ""
access_token_secret =  ""
consumer_key =  ""
consumer_secret =  ""

class StdOutListener(StreamListener):
    def on_data(self, data):
        producer.send_messages("tweets_name", data.encode('utf-8'))
		all_data = json.loads(data)
		tweet = all_data["text"]
        print (tweet)
        return True
    def on_error(self, status):
        print (status)

kafka = KafkaClient("localhost:9092")
producer = SimpleProducer(kafka)
l = StdOutListener()
auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
stream = Stream(auth, l)
stream.filter(track="errejon")
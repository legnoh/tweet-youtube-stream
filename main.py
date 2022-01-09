import os
import tweepy

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def youtube_search():
  youtube = build(
    serviceName='youtube',
    version='v3',
    developerKey=os.environ.get('YOUTUBE_API_KEY')
  )

  return youtube.search().list(
    channelId=os.environ.get('YOUTUBE_CHANNEL_ID'),
    eventType='live',
    part='id,snippet',
    type='video',
  ).execute()

def tweet(update):
  t = tweepy.Client(
    access_token=os.environ.get('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'),
    consumer_key=os.environ.get('TWITTER_CONSUMER_KEY'),
    consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET')
  )
  t.create_tweet(text=update)

if __name__ == '__main__':
  try:
    lives = youtube_search().get('items', [])
    if len(lives) == 0:
      print('No live events found')
    else:
      print('Live events Found. Good Luck!:')
      for live in lives:
          print('  LIVE: %s (%s)' % (live['snippet']['title'] , live['id']['videoId']))
          tweet( "🔴LIVE: %s\n%s" % (
            live['snippet']['title'] ,
            "https://www.youtube.com/watch?v=" + live['id']['videoId'])
          )
  except HttpError as e:
    print('An HTTP error ', e.resp.status, 'occurred:\n ', e.content)

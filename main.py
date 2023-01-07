import html,os,tweepy
from datetime import datetime

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
    order='date'
  ).execute()

if __name__ == '__main__':
  
  tw = tweepy.Client(
    access_token=os.environ.get('TWITTER_ACCESS_TOKEN'),
    access_token_secret=os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'),
    consumer_key=os.environ.get('TWITTER_CONSUMER_KEY'),
    consumer_secret=os.environ.get('TWITTER_CONSUMER_SECRET'),
  )

  tw2 = tweepy.Client(os.environ.get('TWITTER_BEARER_TOKEN'))

  author=tw.get_me()[0]['username']

  try:
    now = datetime.now()
    lives = youtube_search().get('items', [])
    if len(lives) == 0:
      print('No live events found')
    else:
      print('Live events Found. Good Luck!:')
      for live in lives:
          title = html.unescape(live['snippet']['title'])
          video_id = live['id']['videoId']

          print('  LIVE: {title} (https://www.youtube.com/watch?v={video_id})'.format(title=title, video_id=video_id))

          # calc timedelta
          start_at = datetime.strptime(live['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
          td = now - start_at
          hour=round((td.days * 24) + (td.seconds / 3600), 1)

          # get latest tweet
          tweets = tw2.search_recent_tweets(query="from:{author} https://www.youtube.com/watch?v={video_id}".format(author=author,video_id=video_id))

          # tweet
          text = "🔴LIVE: {title}({hour}h▶️)\nhttps://www.youtube.com/watch?v={video_id}".format(title=title, hour=hour, video_id=video_id)
          
          if type(tweets[0]) == list and len(tweets[0]) != 0:
            tw.create_tweet(text=text, in_reply_to_tweet_id=tweets[0][0]['id'])
          else:
            tw.create_tweet(text=text)

  except HttpError as e:
    print('An HTTP error ', e.resp.status, 'occurred:\n ', e.content)

import tweepy.client
import html,logging,os,tweepy,yaml
from datetime import datetime

from googleapiclient.discovery import build

LIVES_YML = "./lives.yml"

log_format = '%(asctime)s[%(filename)s:%(lineno)d][%(levelname)s] %(message)s'
log_level = os.getenv("LOGLEVEL", logging.INFO)
logging.basicConfig(format=log_format, datefmt='%Y-%m-%d %H:%M:%S%z', level=log_level)

def youtube_search():
  youtube = build(
    serviceName='youtube',
    version='v3',
    developerKey=os.environ['YOUTUBE_API_KEY']
  )

  return youtube.search().list(
    channelId=os.environ['YOUTUBE_CHANNEL_ID'],
    eventType='live',
    part='id,snippet',
    type='video',
    order='date'
  ).execute()

if __name__ == '__main__':
  
  tw = tweepy.Client(
    access_token=os.environ['TWITTER_ACCESS_TOKEN'],
    access_token_secret=os.environ['TWITTER_ACCESS_TOKEN_SECRET'],
    consumer_key=os.environ['TWITTER_CONSUMER_KEY'],
    consumer_secret=os.environ['TWITTER_CONSUMER_SECRET'],
  )
  author=tw.get_me()[0]['username']

  # load prev live datas
  with open(LIVES_YML, encoding='utf-8')as f:
    prev_posts = yaml.safe_load(f)

  latest_posts = []
  lives = youtube_search().get('items', [])
  if len(lives) == 0:
    logging.info('No live events found')
  else:
    logging.info('Live events Found. Good Luck!:')
    for live in lives:
        title = html.unescape(live['snippet']['title'])
        video_id = live['id']['videoId']

        # calc timedelta
        start_at = datetime.strptime(live['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ")
        td = datetime.now() - start_at
        hour=round((td.days * 24) + (td.seconds / 3600), 1)

        # get last post
        prev_post = next((item for item in prev_posts if item["video_id"] == video_id), None)

        text = f"🔴LIVE: {title}({hour}h▶️)\nhttps://www.youtube.com/watch?v={video_id}"
        if prev_post != None:
          post = tw.create_tweet(text=text, in_reply_to_tweet_id=prev_post['post_id'])
        else:
          post = tw.create_tweet(text=text)

        if type(post) == tweepy.client.Response:
          post_id = post.data['id']
          latest_posts.append({"video_id": video_id, "post_id": post_id})
          logging.info(f"--> POSTED: {text} -> https://x.com/{author}/status/{post_id}")
  
  # save live datas
  with open(LIVES_YML,'w')as f:
    yaml.dump(latest_posts, f)

  logging.info("all process finished successfully!")

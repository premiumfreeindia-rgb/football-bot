import time
import feedparser
import tweepy
import requests
import os
import google.generativeai as genai

# --- SECURITY: READ KEYS FROM SERVER (NOT FILE) ---
API_KEY = os.environ.get("API_KEY")
API_SECRET = os.environ.get("API_SECRET")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
ACCESS_SECRET = os.environ.get("ACCESS_SECRET")
GEMINI_KEY = os.environ.get("GEMINI_KEY")

RSS_URL = "https://www.skysports.com/rss/12040"

# --- AUTHENTICATION ---
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
api = tweepy.API(auth)
client = tweepy.Client(consumer_key=API_KEY, consumer_secret=API_SECRET, access_token=ACCESS_TOKEN, access_token_secret=ACCESS_SECRET)

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel('gemini-pro')

def main():
    print("⚽️ Checking for news...")
    feed = feedparser.parse(RSS_URL)
    if not feed.entries: return
    latest = feed.entries[0]
    
    # AI Rewrite
    try:
        prompt = f"Rewrite this football headline into a viral tweet under 200 chars with emojis and hashtags. Do not include link: '{latest.title}'"
        tweet = model.generate_content(prompt).text
    except:
        tweet = f"🚨 {latest.title} #Football"

    final_text = f"{tweet}\n\n📰 More: {latest.link}"
    
    # Post
    try:
        client.create_tweet(text=final_text)
        print("✅ Tweeted!")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    while True:
        main()
        time.sleep(900) # Check every 15 minutes

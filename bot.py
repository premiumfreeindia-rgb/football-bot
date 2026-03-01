import time
import feedparser
import tweepy
import requests
import os
import google.generativeai as genai
from flask import Flask
from threading import Thread
import sys

# --- CONFIGURATION ---
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

# --- FAKE WEBSITE (Runs in Background) ---
app = Flask('')

@app.route('/')
def home():
    return "I am alive!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.start()

# --- BOT LOGIC ---
def check_news():
    print("⚽️ STARTING NEWS CHECK...", flush=True)
    try:
        feed = feedparser.parse(RSS_URL)
        if not feed.entries:
            print("⚠️ RSS Feed is empty or blocked.", flush=True)
            return

        latest = feed.entries[0]
        print(f"🔎 Found article: {latest.title}", flush=True)
        
        # AI Rewrite
        try:
            print("🤖 Asking AI to rewrite...", flush=True)
            prompt = f"Rewrite this football headline into a viral tweet under 200 chars with emojis and hashtags. Do not include link: '{latest.title}'"
            tweet = model.generate_content(prompt).text
        except Exception as e:
            print(f"⚠️ AI Error: {e}", flush=True)
            tweet = f"🚨 {latest.title} #Football"

        final_text = f"{tweet}\n\n📰 More: {latest.link}"
        
        # Post
        try:
            client.create_tweet(text=final_text)
            print(f"✅ TWEETED: {final_text}", flush=True)
        except Exception as e:
            if "duplicate" in str(e).lower():
                print("💤 Tweet already exists. Skipping.", flush=True)
            else:
                print(f"❌ Twitter Error: {e}", flush=True)

    except Exception as e:
        print(f"❌ General Error: {e}", flush=True)

# --- MAIN LOOP ---
if __name__ == '__main__':
    keep_alive() # Start Website in Background
    
    print("🚀 BOT IS STARTING...", flush=True)
    
    while True:
        check_news()
        print("⏳ Waiting 15 minutes...", flush=True)
        time.sleep(900)

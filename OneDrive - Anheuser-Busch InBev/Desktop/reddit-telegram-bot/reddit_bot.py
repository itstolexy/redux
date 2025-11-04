import praw
import telebot
import time
from datetime import datetime
from config import *

# Log file path
LOG_FILE = 'reddit_bot.log'

# Initialize Reddit API
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Initialize Telegram Bot
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Store processed post IDs to avoid duplicates
processed_posts = set()

def contains_keywords(text):
    """Check if text contains any of the keywords"""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in KEYWORDS)

def send_telegram_message(post):
    """Send a Telegram message with post details"""
    message = f"""
🔔 *New Reddit Post Found!*

*Subreddit:* r/{post.subreddit.display_name}
*Title:* {post.title}
*Author:* u/{post.author.name if post.author else '[deleted]'}
*Score:* {post.score}

*Link:* https://reddit.com{post.permalink}

*Preview:*
{post.selftext[:300] + '...' if len(post.selftext) > 300 else post.selftext}
    """
    
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown',
            disable_web_page_preview=False
        )
        print(f"✓ Sent notification for post: {post.title[:50]}...")
    except Exception as e:
        print(f"✗ Error sending message: {e}")

def monitor_reddit():
    """Monitor Reddit for new posts matching keywords"""
    print(f"Starting Reddit monitor...")
    print(f"Monitoring subreddits: {SUBREDDITS}")
    print(f"Looking for keywords: {KEYWORDS}")
    print(f"Check interval: {CHECK_INTERVAL} seconds\n")
    
    subreddit = reddit.subreddit(SUBREDDITS)
    
    while True:
        try:
            # Get new posts
            for post in subreddit.new(limit=25):
                # Skip if already processed
                if post.id in processed_posts:
                    continue
                
                # Check title and body for keywords
                if contains_keywords(post.title) or contains_keywords(post.selftext):
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Found matching post: {post.title[:50]}...")
                    send_telegram_message(post)
                    processed_posts.add(post.id)
                else:
                    # Add to processed to avoid checking again
                    processed_posts.add(post.id)
            
            # Clean up old post IDs (keep only last 1000)
            if len(processed_posts) > 1000:
                processed_posts.clear()
            
            time.sleep(CHECK_INTERVAL)
            
        except Exception as e:
            print(f"✗ Error in main loop: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print("=" * 60)
    print("Reddit to Telegram Notification Bot")
    print("=" * 60)
    monitor_reddit()



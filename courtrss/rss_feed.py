import math
import feedparser
import time
import tkinter as tk
from threading import Thread, Lock
import re
import webbrowser
import argparse
import yaml
import sys
import requests
import logging

logging.basicConfig(level=logging.INFO)

already_notified = set()
lock = Lock()

def extract_link_from_summary(summary):
    link_text_match = re.search(r'\[([^\]]+)\]', summary)
    link_text = link_text_match.group(1) if link_text_match else None

    url_match = re.search(r'<a\s+href=["\'](http[^\s"\'<>]+)["\']', summary, re.IGNORECASE)
    url = url_match.group(1) if url_match else None

    return link_text, url

def check_feeds(rss_urls, keywords, notify_methods, retries=3, retry_interval=60):
    retry_count = {url: 0 for url in rss_urls}

    for url in rss_urls:
        success = False
        while retry_count[url] < retries:
            feed = feedparser.parse(url)
            if feed.bozo and (400 <= feed.status < 600):
                retry_count[url] += 1
                logging.warning(f"Error {feed.status} for {url}, retrying {retry_count[url]}/{retries}...")
                time.sleep(retry_interval)
            else:
                success = True
                break

        if not success:
            notify_error(f"Failed to fetch feed from {url} after {retries} retries", notify_methods)
            continue

        for entry in feed.entries:
            title = entry.title.lower()
            summary = entry.summary.lower()
            for keyword in keywords:
                if keyword.lower() in title or keyword.lower() in summary:
                    link_text, link_url = extract_link_from_summary(entry.summary)
                    if link_url in already_notified:
                        continue
                    with lock:
                        already_notified.add(link_url)
                    notify(entry.title, link_text, link_url, notify_methods)

def notify(title, link_text, link_url, methods):
    for method in methods:
        if method['type'] == 'window_notification':
            Thread(target=show_green_screen, args=(title, link_text, link_url)).start()
        elif method['type'] == 'discord_webhook':
            send_discord_notification(title, link_text, link_url, method['webhook_url'])

def notify_error(message, methods):
    for method in methods:
        if method['type'] == 'window_notification':
            Thread(target=show_green_screen, args=(message, None, None)).start()
        elif method['type'] == 'discord_webhook':
            send_discord_notification(message, None, None, method['webhook_url'])

def show_green_screen(title_text, link_text, link_url):
    root = tk.Tk()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    root.geometry(f"{screen_width}x{screen_height}+0+0")
    root.configure(background='green')

    title_label = tk.Label(root, text=title_text, font=("Helvetica", 40, "bold"), bg="green", fg="white")
    title_label.pack(pady=20)

    if link_text and link_url:
        link_label = tk.Label(root, text=link_text, font=("Helvetica", 25, "underline"), fg="blue", bg="green", cursor="hand2")
        link_label.pack(pady=20)
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new(link_url))

    root.bind("<Escape>", lambda event: root.destroy())
    root.mainloop()

def send_discord_notification(title, link_text, link_url, webhook_url):
    content = f"**{title}**"
    if link_url:
        content += f"\n[Link]({link_url})"
    data = {"content": content}
    try:
        response = requests.post(webhook_url, json=data)
        if response.status_code != 204:
            logging.error(f"Failed to send Discord notification: {response.status_code}")
    except Exception as e:
        logging.error(f"Error sending Discord notification: {e}")

def start_monitoring(rss_urls, keywords, interval, notify_methods, retries, retry_interval):
    while True:
        check_feeds(rss_urls, keywords, notify_methods, retries, retry_interval)
        time.sleep(interval)

def parse_yaml_config(config_path):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
        return config['rss_urls'], config['keywords'], config['notifications'], config.get('interval', 60), config.get('retries', 3), config.get('retry_interval', 60)

def main():
    parser = argparse.ArgumentParser(description="Monitor RSS feeds for specific keywords.")
    parser.add_argument('--rss_urls', help="Comma-separated list of RSS feed URLs.")
    parser.add_argument('--keywords', help="Comma-separated list of keywords.")
    parser.add_argument('--config', help="Path to YAML configuration file.")
    parser.add_argument('--interval', type=int, default=60, help="Time interval between checks (in seconds).")
    parser.add_argument('--retries', type=int, default=3, help="Number of retries if RSS feed fetch fails.")
    parser.add_argument('--retry_interval', type=int, default=None, help="Time between retries (in seconds).")

    args = parser.parse_args()

    if args.config:
        try:
            rss_urls, keywords, notify_methods, interval, retries, retry_interval = parse_yaml_config(args.config)
        except Exception as e:
            logging.error(f"Error loading config file: {e}")
            sys.exit(1)
    elif args.rss_urls and args.keywords:
        rss_urls = [url.strip() for url in args.rss_urls.split(',')]
        keywords = [keyword.strip() for keyword in args.keywords.split(',')]
        notify_methods = [{'type': 'window_notification'}]
        interval = args.interval
        retries = args.retries
        retry_interval = args.retry_interval
    else:
        logging.error("Error: You must provide either --rss_urls and --keywords or --config.")
        sys.exit(1)

    if not rss_urls or len(rss_urls) == 0:
        print("Error: No RSS feed URLs provided.")
        sys.exit(1)
    if not keywords or len(keywords) == 0:
        print("Error: No keywords provided.")
        sys.exit(1)
    if not notify_methods or len(notify_methods) == 0:
        print("Error: No notification methods provided.")
        sys.exit(1)
    if interval <= 0:
        print("Error: Interval must be greater than 0.")
        sys.exit(1)
    if retries < 0:
        print("Error: Retries must be 0 or greater.")
        sys.exit(1)
    if not retry_interval:
        retry_interval = interval / math.max(retries, 1)
    elif retry_interval <= 0:
        print("Error: Retry interval must be greater than 0.")
        sys.exit(1)

    monitoring_thread = Thread(target=start_monitoring, args=(rss_urls, keywords, interval, notify_methods, retries, retry_interval))
    monitoring_thread.daemon = True
    monitoring_thread.start()

    print("Monitoring RSS feeds... Press Ctrl+C to exit.")
    while True:
        time.sleep(1)

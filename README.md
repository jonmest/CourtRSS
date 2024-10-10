# CourtRSS 📡
Most federal district courts have RSS feeds with updates on their latest docket entries. CourtRSS makes it easy to stay informed in real-time by polling these and searching for keywords that interest you. If a match is found, CourtRSS displays an alert window or sends a message through Discord webhooks.

## Features 🚀
- **Monitor multiple RSS feeds**: Add as many RSS feeds as you like and track them all.
- **Customizable keyword search**: Define keywords to trigger notifications based on the feed content.
- **Multiple notification methods**:
  - A full-screen green window with a clickable link.
  - Discord webhook notifications.
- **Retry logic** for failed feed fetches (with configurable retry attempts and intervals).
- **Easy configuration** through a YAML file or CLI arguments.

## How It Works 👇
You can install CourtRSS directly from PyPI:

```bash
pip install courtrss
```

## Usage 🎯
Once installed, you can run CourtRSS in two ways:
### 1. Using a YAML Configuration File
This is the easiest and most flexible option. Here's how you can set it up:
```yaml
rss_urls:
  - https://example.com/rss_feed_1
  - https://example.com/rss_feed_2

keywords:
  - "Neonode"
  - "Tapestry"

interval: 60  # Time interval between feed checks in seconds
retries: 3    # How many times to retry fetching a failed feed
retry_interval: 20  # How long to wait between retries in seconds

notifications:
  - type: window_notification
  - type: discord_webhook
    webhook_url: https://discord.com/api/webhooks/your_webhook_url_here
```

To run CourtRSS with this config, just call it with the `--config` argument:

```bash
courtrss --config /path/to/config.yaml
```

### 2. Using CLI Arguments
If you prefer the command line, you can directly pass RSS URLs and keywords as comma-separated arguments. Like this:

```bash
courtrss --rss_urls "https://example.com/rss1,https://example.com/rss2" --keywords "Neonode,Tapestry" --interval 60 --retries 3 --retry_interval 20
```
This will check the provided feeds every 60 seconds, retry up to 3 times on failure, and notify you about matching entries.

## Examples 🎉
### Example 1: Court RSS Monitoring with Green Window Notification

Let’s say you want to monitor a couple of court RSS feeds for the keywords "Apple" and "Cisco", and get notified via the full-screen green window:

```yaml
rss_urls:
  - https://court.example.com/rss_feed_1
  - https://court.example.com/rss_feed_2

keywords:
  - "Apple"
  - "Cisco"

interval: 60

notifications:
  - type: window_notification
```
Run it like this:

```bash
courtrss --config court_monitor.yaml
```

Every time a keyword match is found, you’ll get a big, green window notifying you about it!

### Example 2: Monitoring with Discord Webhook Notifications

You can send the notifications straight to your Discord server. Set up your config.yaml like this:

```yaml
rss_urls:
  - https://court.example.com/rss_feed_1
  - https://court.example.com/rss_feed_2

keywords:
  - "Verdict"
  - "Sentencing"

interval: 120  # Every 2 minutes

notifications:
  - type: discord_webhook
    webhook_url: https://discord.com/api/webhooks/your_webhook_url_here
```

Now, CourtRSS will send you messages in your Discord channel whenever a match occurs.

## Configuration Options 🔧

- rss_urls: List of RSS feed URLs you want to monitor.
- keywords: Keywords that will trigger notifications if found in the feed title or summary.
- interval: Time interval (in seconds) between checks. Default is 60 seconds.
- retries: Number of retries if fetching the feed fails (e.g., server issues). Default is 3 retries.
- retry_interval: Time (in seconds) between retries. Default is 60 seconds.
- notifications: List of notification methods:
    - type: Notification type, either window_notification or discord_webhook.
    - webhook_url: (Only for Discord) The URL of the Discord webhook.

## Why CourtRSS? 🤷

- Real-time notifications: Stay updated as soon as new information comes in.
- Customizable alerts: Choose between a big, eye-catching green window or a subtle Discord message.
- Reliable: Built-in retry mechanism ensures you’re not missing anything if a feed is temporarily down.

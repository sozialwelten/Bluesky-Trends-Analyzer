#!/usr/bin/env python3
"""
Bluesky Trends Analyzer
Zeigt aktuelle Trends, beliebte Posts und spezifische Hashtags an.
"""

import os
import sys
from datetime import datetime, timedelta
from collections import Counter
import re
from atproto import Client


def extract_hashtags(text):
    """Extrahiert Hashtags aus einem Text."""
    if not text:
        return []
    return re.findall(r'#\w+', text.lower())


def format_post(post, index=None):
    """Formatiert einen Post für die Ausgabe."""
    author = post.author.handle
    text = post.record.text[:200] + "..." if len(post.record.text) > 200 else post.record.text
    likes = post.like_count or 0
    reposts = post.repost_count or 0
    replies = post.reply_count or 0

    created_at = datetime.fromisoformat(post.record.created_at.replace('Z', '+00:00'))
    time_str = created_at.strftime('%d.%m.%Y %H:%M')

    prefix = f"{index}. " if index else ""

    return f"""
{prefix}@{author} ({time_str})
{text}
💙 {likes} Likes | 🔁 {reposts} Reposts | 💬 {replies} Replies
"""


def search_hashtag(client, hashtag, limit=10):
    """Sucht nach Posts mit einem bestimmten Hashtag."""
    print(f"\n{'=' * 60}")
    print(f"🔍 Suche nach {hashtag}")
    print('=' * 60)

    try:
        # Entferne # falls vorhanden
        tag = hashtag.lstrip('#')

        # Suche nach dem Hashtag
        response = client.app.bsky.feed.search_posts(
            params={'q': f'#{tag}', 'limit': limit}
        )

        if not response.posts:
            print(f"Keine Beiträge für {hashtag} gefunden.")
            return []

        print(f"Gefundene Beiträge: {len(response.posts)}\n")

        for i, post in enumerate(response.posts[:limit], 1):
            print(format_post(post, i))

        return response.posts

    except Exception as e:
        print(f"Fehler bei der Suche nach {hashtag}: {e}")
        return []


def get_trending_posts(client, hours=24, limit=20):
    """Holt die beliebtesten Posts der letzten X Stunden."""
    print(f"\n{'=' * 60}")
    print(f"🔥 Top Posts der letzten {hours} Stunden")
    print('=' * 60)

    try:
        # Nutze den Timeline-Feed und filtere nach Zeitraum
        response = client.app.bsky.feed.get_timeline(params={'limit': 100})

        cutoff_time = datetime.now(datetime.now().astimezone().tzinfo) - timedelta(hours=hours)

        # Filtere und sortiere Posts
        recent_posts = []
        for post in response.feed:
            try:
                created_at = datetime.fromisoformat(
                    post.post.record.created_at.replace('Z', '+00:00')
                )
                if created_at > cutoff_time:
                    # Berechne Engagement-Score
                    engagement = (
                            (post.post.like_count or 0) * 1 +
                            (post.post.repost_count or 0) * 3 +
                            (post.post.reply_count or 0) * 2
                    )
                    recent_posts.append((engagement, post.post))
            except:
                continue

        # Sortiere nach Engagement
        recent_posts.sort(reverse=True, key=lambda x: x[0])

        if not recent_posts:
            print(f"Keine Posts in den letzten {hours} Stunden gefunden.")
            return []

        print(f"Gefundene Posts: {len(recent_posts)}\n")

        # Zeige Top Posts
        for i, (engagement, post) in enumerate(recent_posts[:limit], 1):
            print(f"Engagement-Score: {engagement}")
            print(format_post(post, i))

        return [post for _, post in recent_posts]

    except Exception as e:
        print(f"Fehler beim Abrufen der trending Posts: {e}")
        return []


def analyze_trending_hashtags(posts):
    """Analysiert die am häufigsten verwendeten Hashtags."""
    print(f"\n{'=' * 60}")
    print("📊 Trending Hashtags")
    print('=' * 60)

    all_hashtags = []
    for post in posts:
        try:
            hashtags = extract_hashtags(post.record.text)
            all_hashtags.extend(hashtags)
        except:
            continue

    if not all_hashtags:
        print("Keine Hashtags gefunden.")
        return

    # Zähle Hashtags
    hashtag_counts = Counter(all_hashtags)

    print(f"\nTop 15 Hashtags:\n")
    for i, (hashtag, count) in enumerate(hashtag_counts.most_common(15), 1):
        bar = '█' * min(count, 50)
        print(f"{i:2d}. {hashtag:20s} {bar} ({count})")


def main():
    # Hole Credentials aus Umgebungsvariablen
    handle = os.getenv('BSKY_HANDLE')
    password = os.getenv('BSKY_APP_PASSWORD')

    if not handle or not password:
        print("❌ Fehler: BSKY_HANDLE und BSKY_APP_PASSWORD müssen gesetzt sein!")
        print("\nSetze sie in deiner .bashrc:")
        print('  export BSKY_HANDLE="dein.handle.bsky.social"')
        print('  export BSKY_APP_PASSWORD="dein-app-passwort"')
        sys.exit(1)

    print("🦋 Bluesky Trends Analyzer")
    print("=" * 60)

    # Login
    try:
        client = Client()
        print(f"🔐 Login als {handle}...")
        client.login(handle, password)
        print("✅ Erfolgreich eingeloggt!\n")
    except Exception as e:
        print(f"❌ Login fehlgeschlagen: {e}")
        sys.exit(1)

    # Sammle alle Posts für Hashtag-Analyse
    all_posts = []

    # 1. Suche nach spezifischen Hashtags
    soziologie_posts = search_hashtag(client, "#Soziologie", limit=10)
    all_posts.extend(soziologie_posts)

    cfp_posts = search_hashtag(client, "#CfP", limit=10)
    all_posts.extend(cfp_posts)

    # 2. Zeige Top Posts der letzten 24 Stunden
    trending_posts = get_trending_posts(client, hours=24, limit=15)
    all_posts.extend(trending_posts)

    # 3. Analysiere Trending Hashtags
    analyze_trending_hashtags(all_posts)

    print("\n" + "=" * 60)
    print("✨ Analyse abgeschlossen!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Abgebrochen.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")
        sys.exit(1)
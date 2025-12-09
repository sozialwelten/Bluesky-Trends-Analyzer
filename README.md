# 🦋 Bluesky Trends Analyzer

Analyse aktueller Bluesky-Trends direkt aus dem Terminal.

## Installation

```bash
# pipx installieren
sudo apt install pipx
pipx ensurepath

# Tool installieren
git clone https://github.com/sozialwelten/Bluesky-Trends-Analyzer.git
cd Bluesky-Trends-Analyzer
pipx install .
```

## Konfiguration

App-Passwort in [Bluesky-Einstellungen](https://bsky.app/settings/app-passwords) erstellen, dann in `~/.bashrc`:

```bash
export BSKY_HANDLE="dein.handle.bsky.social"
export BSKY_APP_PASSWORD="dein-app-passwort"
```

Terminal neu laden: `source ~/.bashrc`

## Verwendung

```bash
bluesky_trends
```

## Features

- 🔍 Hashtag-Suche (#Soziologie, #CfP)
- 🔥 Top Posts der letzten 24h
- 📊 Trending Hashtags

## Lizenz

GPL-3.0

## Author 

Michael Karbacher
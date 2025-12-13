# 🚀 ProjectGDB - Generic Discord Bot

**ProjectGDB** is a feature-rich Discord bot built with Python using the `discord.py` library. Designed for versatility and fun, it offers a comprehensive suite of commands ranging from economy systems to entertainment features.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Discord.py](https://img.shields.io/badge/discord.py-2.0+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🌟 Key Features

### 💰 Economy System
- **Level progression** with XP rewards
- **Currency management** (wallet & bank)
- **Work commands** with cooldowns
- **Daily rewards** system
- **Robbery mechanics** (pickpocketing & heists)
- **Skill tree** with upgradable stats
- **Gambling** (betting games)

### 🎭 Entertainment
- **AI integration** (Groq API with LLaMA 3)
- **Soundboard** with audio playback
- **Roast generator** with custom insults
- **Random generators** (coin flip, dice roll)
- **Social media integration**
- **CS:GO player stats lookup**

### ⚙️ Utility
- **Voice channel management**
- **User statistics tracking**
- **Admin tools** for server management
- **Custom logging system**

## 🛠️ Setup Instructions

### Prerequisites
- Python 3.8 or higher
- Discord bot token
- Steam API key (for CS:GO features)
- Groq API key (for AI features)

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/PidgeyOnTheCat/ProjectGDB.git
   cd ProjectGDB

2. Get the .env file:
   ```.env
   # API Keys and Tokens
   # Replace placeholders with your actual keys and tokens
   TOKEN=your_discord_bot_token
   STEAM_API_KEY=your_steam_api_key
   AI_API_KEY=your_openai_api_key
   
   # File Paths
   # Replace with your actual file paths
   BOTDATA_FILE_PATH=/data
   
   # Botdata hierarchy
   # Botdata -> Media -> Audio


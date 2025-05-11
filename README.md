# NumberCruncher Discord Bot

A Discord bot that fetches webhook‑posted orders, analyzes time‑of‑day and weekday trends (in EST), and generates charts for easy visualization.

---

## Features

- Fetches all webhook messages from a designated channel  
- Converts timestamps to US/Eastern timezone  
- Plots:
    - Orders by hour of day  
    - Orders by weekday  
    - Heatmap of weekday vs. hour  
    - Daily order volume time series  
    - 7‑day seasonal decomposition (if ≥ 14 days of data)  
- Sends chart images directly back to Discord  

---

## Prerequisites

- Python 3.8+  
- A Discord application with a bot token  
- A channel set up to receive webhook‑posted orders  

---

## Installation

1. Clone the repo
   ```bash
    git clone https://github.com/bryanygan/numbercruncher.git  
    cd numbercruncher
   ```

2. Create & activate a virtual environment
   ```bash
    python3 -m venv venv  
    source venv/bin/activate      # macOS/Linux  
    .\venv\Scripts\activate       # Windows
   ```

3. Install dependencies
   ```bash
    pip install discord.py pandas matplotlib statsmodels python-dotenv  
   ```
---

## Configuration

1. Environment variables  
   Create a `.env` file in the project root with:
   ```
       DISCORD_BOT_TOKEN=your_bot_token_here       
       APPLICATION_ID=your_application_id_here   # Your Discord application ID
       ORDER_CHANNEL_ID=your_channel_id_here     # Channel where webhook posts land
   ```

3. **Script constants**  
   At the top of `numbercruncher.py`, adjust as needed:  
    ANALYSIS_CHANNEL_ID  = ORDER_CHANNEL_ID      # Channel for sending results  

---

## Usage

1. Run the bot
   ```bash
       python numbercruncher.py  
   ```

2. In Discord  
   - Invite your bot with scopes `applications.commands` & `bot`.  
   - Use the slash command `/analyze`.  
   - The bot will fetch webhook messages from `ORDER_CHANNEL_ID`, generate charts, and post them back.  

---

## Chart Outputs

- **orders_by_hour_est.png** – Orders by hour (00–23 EST)  
- **orders_by_weekday_est.png** – Orders by weekday (Mon–Sun)  
- **orders_heatmap_est.png** – Heatmap of weekday vs. hour  
- **daily_volume_est.png** – Total orders per day  
- **decomposition_est.png** – 7‑day seasonal decomposition (requires ≥ 14 days of data)  

---

## Troubleshooting

- Environment variable errors:  
    - `DISCORD_BOT_TOKEN not set in .env`  
    - `APPLICATION_ID not set in .env`  
    - `ORDER_CHANNEL_ID not set in .env`  
  → Ensure your `.env` file contains all three entries.

- **Order channel not found**  
  → Verify `ORDER_CHANNEL_ID` matches the channel receiving webhooks.

- **No webhook messages found**  
  → Confirm the webhook is posting messages correctly.

- **Insufficient data for decomposition**  
  → Collect at least 14 days of data before running `/analyze`.

---

## License

MIT License © 2025 Bryan Gan
Feel free to fork and adapt!

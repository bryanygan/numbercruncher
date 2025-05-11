from dotenv import load_dotenv
import os
import io
import discord
import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.seasonal import seasonal_decompose
from discord.ext import commands
from discord import app_commands

load_dotenv()

DISCORD_BOT_TOKEN    = os.getenv("DISCORD_BOT_TOKEN")
APPLICATION_ID       = os.getenv("APPLICATION_ID")
ORDER_CHANNEL_ID     = os.getenv("ORDER_CHANNEL_ID")

# Validate
if not DISCORD_BOT_TOKEN:
    raise RuntimeError("DISCORD_BOT_TOKEN not set in .env")
if not APPLICATION_ID:
    raise RuntimeError("APPLICATION_ID not set in .env")
if not ORDER_CHANNEL_ID:
    raise RuntimeError("ORDER_CHANNEL_ID not set in .env")

# Convert to int
APPLICATION_ID   = int(APPLICATION_ID)
ORDER_CHANNEL_ID = int(ORDER_CHANNEL_ID)
ANALYSIS_CHANNEL_ID = ORDER_CHANNEL_ID

# Enable only the intents we need
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!", 
    intents=intents, 
    application_id=1370861466462453800
)

@bot.event
async def on_ready():
    # register (or sync) all slash commands with Discord
    await bot.tree.sync()
    print(f"Logged in as {bot.user} – slash commands synced")


@bot.tree.command(
    name="analyze", 
    description="Fetch all webhook orders and show time‑of‑day & weekday trends (in EST)"
)
async def analyze(interaction: discord.Interaction):
    # defer if you know it’ll take a moment
    await interaction.response.defer(thinking=True)

    channel = bot.get_channel(ORDER_CHANNEL_ID)
    if channel is None:
        return await interaction.followup.send("❌ Order channel not found")

    # 1) fetch all webhook messages
    msgs = [m async for m in channel.history(limit=None) if m.webhook_id]

    if not msgs:
        return await interaction.followup.send("❌ No webhook messages found.")

    # 2) build DataFrame with EST timestamps
    df = pd.DataFrame({"timestamp": [m.created_at for m in msgs]})
    df['timestamp'] = pd.to_datetime(df['timestamp']) \
                    .dt.tz_convert("US/Eastern")

    df["hour"]    = df["timestamp"].dt.hour
    df["weekday"] = df["timestamp"].dt.day_name()
    df.set_index("timestamp", inplace=True)

    # helper to send figures
    async def _send_fig(fig, fn):
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)
        await interaction.followup.send(file=discord.File(buf, fn))
        plt.close(fig)

    # 3) orders by hour
    hourly = df.groupby("hour").size().reindex(range(24), fill_value=0)
    fig, ax = plt.subplots()
    hourly.plot.bar(ax=ax)
    ax.set_title("Orders by Hour (EST)")
    ax.set_xlabel("Hour of Day (EST)")
    ax.set_ylabel("Count")
    await _send_fig(fig, "orders_by_hour_est.png")

    # 4) orders by weekday
    days = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    weekday = df.groupby("weekday").size().reindex(days, fill_value=0)
    fig, ax = plt.subplots()
    weekday.plot.bar(ax=ax)
    ax.set_title("Orders by Weekday (EST)")
    ax.set_xlabel("Day")
    ax.set_ylabel("Count")
    await _send_fig(fig, "orders_by_weekday_est.png")

    # 5) heatmap weekday vs hour
    pivot = (
        df.reset_index()
          .pivot_table(
              index="weekday",
              columns="hour",
              values="weekday",
              aggfunc="count",
          )
          .reindex(days)                    # rows in Mon–Sun order
          .reindex(columns=range(24), fill_value=0)  # columns 0–23
    )

    fig, ax = plt.subplots(figsize=(12, 5))
    heat = ax.imshow(
        pivot.values,
        aspect="auto",
        origin="lower",
    )

    ax.set_yticks(range(len(days)))
    ax.set_yticklabels(days)
    ax.set_xticks(range(24))
    ax.set_xticklabels(pivot.columns)
    ax.set_xlabel("Hour of Day (EST)")
    ax.set_ylabel("Day of Week")
    ax.set_title("Order Heatmap (EST)")
    fig.colorbar(heat, ax=ax, label="Order Count")
    await _send_fig(fig, "orders_heatmap_est.png")

    # 6) daily time series
    daily = df.resample("D").size()
    fig, ax = plt.subplots()
    daily.plot(ax=ax)
    ax.set_title("Daily Order Volume (EST)")
    ax.set_xlabel("Date (EST)")
    ax.set_ylabel("Count")
    await _send_fig(fig, "daily_volume_est.png")

    # 7) seasonal decomposition (if ≥14 days)
    if len(daily) >= 14:
        dec = seasonal_decompose(daily, model="additive", period=7)
        fig = dec.plot()
        fig.suptitle("Seasonal Decomposition (7‑day) (EST)", y=1.02)
        await _send_fig(fig, "decomposition_est.png")
    else:
        await interaction.followup.send("⚠️ Need ≥14 days for decomposition.")

    await interaction.followup.send("✅ Analysis complete! (timestamps in EST)")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)

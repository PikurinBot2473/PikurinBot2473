from keep_alive import keep_alive
import discord
import asyncio
import logging
import os
import aiohttp

TOKEN = os.environ["DISCORD_TOKEN"]
channel_id = 1277188290121961586

AUDIO_URL = "https://github.com/PikurinBot2473/PikurinBot2473/releases/download/v1/audio.mp3"
AUDIO_FILE = "audio.mp3"

intents = discord.Intents.default()
intents.voice_states = True
client = discord.Client(intents=intents)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)


async def download_audio():
    if os.path.exists(AUDIO_FILE):
        return

    log.info("音声ファイルをダウンロード中...")
    async with aiohttp.ClientSession() as session:
        async with session.get(AUDIO_URL) as resp:
            with open(AUDIO_FILE, "wb") as f:
                f.write(await resp.read())
    log.info("音声ダウンロード完了")


async def ensure_voice(channel):
    vc = channel.guild.voice_client
    if vc is None:
        return await channel.connect(self_deaf=True)

    if not vc.is_connected():
        await vc.disconnect(force=True)
        return await channel.connect(self_deaf=True)

    return vc


async def play_loop(channel):
    await download_audio()

    while True:
        try:
            vc = await ensure_voice(channel)

            if vc.is_playing():
                await asyncio.sleep(5)
                continue

            log.info("音声再生開始")
            source = discord.FFmpegPCMAudio(AUDIO_FILE)
            vc.play(source)

            while vc.is_playing():
                await asyncio.sleep(1)

        except Exception:
            log.exception("play_loop error")
            await asyncio.sleep(5)


@client.event
async def on_ready():
    log.info("ログインしました")
    await client.change_presence(
        activity=discord.Game(name="Pikurinサーバー専用BOT")
    )

    channel = client.get_channel(channel_id)
    client.loop.create_task(play_loop(channel))


keep_alive()
client.run(TOKEN)

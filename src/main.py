import asyncio
import io
import os
import re

import aiohttp
import discord


TOKEN = os.getenv('TOKEN')

CUSTOM_EMOJIS = re.compile('<:\w+:\d+>')

client = discord.Client(intents=discord.Intents.none())
tree = discord.app_commands.CommandTree(client)

# this is a bit stupid
cache = {}


@tree.context_menu()
async def yoink_emotes(interaction, message: discord.Message):
    emojis = CUSTOM_EMOJIS.findall(message.content)

    if not emojis:
        return await interaction.response.send_message("I couldn't find any emojis to yoink in that message.")

    async def callback(url):
        if url not in cache:
            response = await client.session.get(url)
            bytes = await response.read()

            cache[url] = bytes

        return cache[url]


    urls = [discord.PartialEmoji.from_str(emoji).url for emoji in emojis]
    resources = await asyncio.gather(*map(callback, urls))

    files = [discord.File(filename='file.png', fp=io.BytesIO(resource)) for resource in resources]

    return await interaction.response.send_message(files=files, ephemeral=True)


async def main():
    async with client, aiohttp.ClientSession() as session:
        client.session = session
        await client.login(TOKEN)
        await client.connect(reconnect=True)


asyncio.run(main())

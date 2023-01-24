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


async def send_emojis(interaction, urls):
    """
    Given a list of URLs to discord emojis, send a file of each.
    """

    async def callback(url):
        if url not in cache:
            response = await client.session.get(url)
            bytes = await response.read()

            cache[url] = bytes

        return cache[url]

    resources = await asyncio.gather(*map(callback, urls))

    files = [discord.File(filename='file.png', fp=io.BytesIO(resource)) for resource in resources]

    return await interaction.response.send_message(files=files, ephemeral=True)


@tree.context_menu(name='yoink emotes')
async def yoink_emotes(interaction, message: discord.Message):
    emojis = CUSTOM_EMOJIS.findall(message.content)

    if not emojis:
        return await interaction.response.send_message("There are no custom emoji in that message.")

    urls = [discord.PartialEmoji.from_str(emoji).url for emoji in emojis]

    return await send_emojis(interaction, urls)


@tree.context_menu(name='yoink reactions')
async def yoink_reactions(interaction, message: discord.Message):
    if not message.reactions:
        return await interaction.response.send_message("There are no custom reactions on this message.")

    urls = [
        reaction.url
        for reaction in message.reactions
        if isinstance(reaction.emoji, (discord.Emoji, discord.PartialEmoji))
    ]

    return await send_emojis(interaction, urls)


async def main():
    async with client, aiohttp.ClientSession() as session:
        client.session = session
        await client.login(TOKEN)
        await client.connect(reconnect=True)


asyncio.run(main())

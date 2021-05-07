import os

import asyncpraw
import discord
from discord.ext import commands, menus
from dotenv import load_dotenv

from src.help_descriptions import reddit_help

load_dotenv()
REDDIT_TOKEN = os.getenv('REDDIT_TOKEN')

categories = ['hot', 'new', 'top']


async def createEmbed(description, image, name, link, curPage, icon, logo):
    if len(description) >= 2045:
        description = description[:2045] + '...'
    if len(name) >= 120:
        name = name[:120] + '...'

    em = discord.Embed(
        description=description,
        color=0xD2691E,
    )

    em.set_author(icon_url=logo, name=name, url=link)
    em.set_footer(text=f'Page {curPage}/{25}', icon_url=icon)
    em.set_image(url=image)
    return em


async def getPosts(subreddit, category, icon):
    reddit = asyncpraw.Reddit(
        client_id="HYreCcGUQx9hIQ",
        client_secret=REDDIT_TOKEN,
        user_agent="noah",
    )
    
    if subreddit.startswith(('/r/', 'r/')):
        subreddit = subreddit.split('r/')[-1]

    try:  # Check if sub exists
        if subreddit in ['all', 'popular']:  # Special sub
            sub = await reddit.subreddit(subreddit)
        else:
            sub = await reddit.subreddit(subreddit, fetch=True)
    except:  # it doesnt exist...
        return None

    if 'community_icon' not in dir(sub):  # Special sub
        logo = 'https://www.redditinc.com/assets/images/site/reddit-logo.png'
    else:
        if sub.community_icon != "":
            logo = sub.community_icon
        elif sub.icon_img != "":
            logo = sub.icon_img
        else:  # no logo
            logo = 'https://www.redditinc.com/assets/images/site/reddit-logo.png'

    posts = None
    if category == 'hot':
        posts = sub.hot(limit=25)
    if category == 'new':
        posts = sub.new(limit=25)
    if category == 'top':
        posts = sub.top(limit=25)

    ems = []
    curPage = 0
    async for p in posts:
        postType = p.__dict__.get('post_hint', None)
        name = p.title
        link = "https://www.reddit.com" + p.permalink
        curPage += 1

        if postType == 'hosted:video':  # video, cant rlly embed
            linkThumbnail = p.preview['images'][0]['source']['url']

            # For another day
            # url = p.media['reddit_video']['fallback_url']
            # url = url.split("?")[0]
            # audio = url.split("DASH_")[0] + 'DASH_audio.mp4'
            # ems.append(await createEmbed(url + ' ' + audio, linkThumbnail, name, link, curPage, p))

            ems.append(await createEmbed('', linkThumbnail, name + ' [Video]', link, curPage, icon, logo))

        elif postType == 'rich:video':  # video, cant rlly embed
            linkThumbnail = p.preview['images'][0]['source']['url']

            ems.append(await createEmbed(p.url, linkThumbnail, name, link, curPage, icon, logo))

        elif postType == 'link':  # can embed (w/link + thumbnail)
            linkThumbnail = p.preview['images'][0]['source']['url']
            ems.append(await createEmbed(p.url, linkThumbnail, name, link, curPage, icon, logo))

        elif postType == 'image':  # can embed
            ems.append(await createEmbed('', p.url, name, link, curPage, icon, logo))

        else:  # PostType is None, could be text or a gallery (or subreddit can make them all Null on purpose,
            # and to which idk what to do about it)
            if hasattr(p, 'gallery_data'):  # gallery or images (embed w/ first pic)
                if 'caption' in p.gallery_data['items'][0]:
                    caption = p.gallery_data['items'][0]['caption']
                else:
                    caption = ''

                ems.append(
                    await createEmbed(caption, p.media_metadata[p.gallery_data['items'][0]['media_id']]['s']['u'], name,
                                      link, curPage, icon, logo))
            else:  # otherwise, just assume its text
                ems.append(await createEmbed(p.selftext, '', name, link, curPage, icon, logo))

    await reddit.close()
    return ems


class Reddit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['r'], **reddit_help)
    async def reddit(self, ctx, *args):
        icon = ctx.message.author.avatar_url

        if len(args) >= 1:
            subreddit = args[0].lower()
        else:
            subreddit = 'spelunky'

        if len(args) == 2:
            category = args[1].lower()
        else:
            category = 'hot'

        if category not in categories:
            category = 'hot'

        posts = await getPosts(subreddit, category, icon)

        if posts is None:
            await ctx.send("Not a valid subreddit! (can't be private)")

        m = RedditMenu(posts)
        await m.start(ctx)


class RedditMenu(menus.Menu):
    def __init__(self, posts):
        super().__init__()
        self.curPost = 1
        self.posts = posts

    async def send_initial_message(self, ctx, channel):
        if self.posts is None:
            return
        return await ctx.send(embed=self.posts[self.curPost - 1])

    @menus.button("◀")
    async def on_arrow_up(self, payload):
        self.curPost -= 1
        await self.message.edit(embed=self.posts[self.curPost - 1])

    @menus.button("▶")
    async def on_arrow_right(self, payload):
        self.curPost += 1
        await self.message.edit(embed=self.posts[self.curPost - 1])


def setup(bot):
    bot.add_cog(Reddit(bot))

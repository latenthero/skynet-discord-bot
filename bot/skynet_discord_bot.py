from discord.ext import commands
from discord import Embed
import requests
import config
from datetime import datetime
import logging
import traceback
import os
from siaskynet import Skynet

bot = commands.Bot(command_prefix='!')


def upload_file(path, opts=None):
    return Skynet.uri_skynet_prefix() + upload_file_request(path, opts).json()["skylink"]


def upload_file_request(path, opts=None):
    if opts is None:
        opts = Skynet.default_upload_options()

    with open(path, 'rb') as f:
        host = opts.portal_url
        path = opts.portal_upload_path
        url = f'{host}/{path}'
        filename = opts.custom_filename if opts.custom_filename else os.path.basename(f.name)
        r = requests.post(url, files={opts.portal_file_fieldname: (filename, f)})
    return r


@bot.command(pass_context=True)
async def skyup(ctx, *args):
    try:
        ts = datetime.now().strftime("-%H:%M:%S:%f")
        if ctx.message.attachments:
            url = ctx.message.attachments[0].url
            r = requests.get(url)
            file_name = url.split('/')[-1] + ts
            with open(file_name, 'wb') as new_file:
                new_file.write(r.content)
        else:
            if not args:
                return
            file_name = 'text_message.txt' + ts
            with open(file_name, 'wt') as new_file:
                new_file.write(ctx.message.content[7:])
        opts = Skynet.default_upload_options()
        opts.custom_filename = file_name[:-16]
        skylink = upload_file(file_name, opts)
        embed = Embed(title='Upload successful')
        embed.add_field(name='Sia link', value=skylink, inline=False)
        embed.add_field(name='Web link', value=skylink.replace('sia://', 'https://siasky.net/'), inline=False)
        embed.add_field(name='Requested by', value=ctx.message.author.mention, inline=False)
        await ctx.send(embed=embed)
        new_file.close()
        os.remove(file_name)
    except Exception as ex:
        traceback.print_exc()
        logging.error('Exception of type {%s}: {%s}' % (type(ex).__name__, str(ex)))

logging.basicConfig(format='[%(asctime)s] %(filename)s:%(lineno)d %(levelname)s - %(message)s',
                    level=logging.INFO, filename=config.log_name, datefmt='%d.%m.%Y %H:%M:%S')
bot.run(config.bot_token)

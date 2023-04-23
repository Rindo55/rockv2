import asyncio

import sys

from main.modules.compressor import compress_video

from main.modules.utils import episode_linker, get_duration, get_epnum, status_text, get_filesize, b64_to_str, str_to_b64, send_media_and_reply

from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from main.modules.uploader import upload_video
from main.modules.thumbnail import generate_thumbnail

import os

from main.modules.db import del_anime, save_uploads

from main.modules.downloader import downloader

from main.modules.anilist import get_anilist_data, get_anime_img, get_anime_name

from config import INDEX_USERNAME, UPLOADS_USERNAME, UPLOADS_ID, INDEX_ID, PROGRESS_ID, LINK_ID

from main import app, queue, status

from pyrogram.errors import FloodWait

from pyrogram import filters

from main.inline import button1

status: Message

async def tg_handler():

    while True:

        try:

            if len(queue) != 0:

                i = queue[0]  

                queue.remove(i)

                val, id, name, ep_num, video = await start_uploading(i)

                await del_anime(i["title"])

                await save_uploads(i["title"])

                await status.edit(await status_text(f"Adding Links To Index Channel ({INDEX_USERNAME})..."),reply_markup=button1)

                await channel_handler(val,id,name,ep_num, video)

                await status.edit(await status_text("Sleeping For 5 Minutes..."),reply_markup=button1)

                await asyncio.sleep(30)

            else:                

                if "Idle..." in status.text:

                    try:

                        await status.edit(await status_text("Idle..."),reply_markup=button1)

                    except:

                        pass

                await asyncio.sleep(30)

                

        except FloodWait as e:

            flood_time = int(e.x) + 5

            try:

                await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

            except:

                pass

            await asyncio.sleep(flood_time)

        except:

            pass

            

async def start_uploading(data):

    try:

        title = data["title"]
        title = title.replace("Dr. Stone S3", "Dr Stone New World")
        title = title.replace("Opus.COLORs", "Opus COLORs")
        link = data["link"]
        size = data["size"]
        nyaasize = data["size"]
        subtitle = data["subtitle"]
        name, ext = title.split(".")

        name += f" @animxt." + ext

        KAYO_ID = -1001948444792
        DATABASE_ID = -1001903052236
        name = name.replace(f" @animxt.","").replace(ext,"").strip()
        id, img, tit = await get_anime_img(get_anime_name(title))
        msg = await app.send_photo(KAYO_ID,photo=img,caption=title)
        img, caption = await get_anilist_data(title)

        print("Downloading --> ",name)

        await status.edit(await status_text(f"Downloading {name}"),reply_markup=button1)

        file = await downloader(msg,link,size,title)

        await msg.edit(f"Download Complete : {name}")
        print("Encoding --> ",name)

        await status.edit(await status_text(f"Encoding {name}"),reply_markup=button1)

        duration = get_duration(file)
        filed = os.path.basename(file)
        filed = filed.replace(filed[-14:], ".mkv")
        filed = filed.replace("[Erai-raws]", "")
        filed = filed.replace("[1080p][Multiple Subtitle]", "[1080p Web-DL]")
        filed = filed.replace("[1080p]", "[1080p Web-DL]")
        filed = filed.replace("2nd Season", "S2")
        filed = filed.replace("3rd Season", "S3")
        fpath = "downloads/" + filed
        ghostname = name
        ghostname = ghostname.replace("[1080p][Multiple Subtitle]", "")
        ghostname = ghostname.replace("[1080p]", "")
        ghostname = ghostname.replace("2nd Season", "S2")
        ghostname = ghostname.replace("3rd Season", "S3")
        subtitle = subtitle.replace("][", ", ")
        subtitle = subtitle.replace("[", "")
        subtitle = subtitle.replace("]", "")     
        subtitle = subtitle.replace("ENG", "English")
        subtitle = subtitle.replace("POR-BR", "Portuguese (Brazil)")
        subtitle = subtitle.replace("SPA-LA", "Spanish (Latin America)")
        subtitle = subtitle.replace("SPA", "Spanish")
        subtitle = subtitle.replace("ARA", "Arabic")
        subtitle = subtitle.replace("FRE", "French")
        subtitle = subtitle.replace("GER", "German")
        subtitle = subtitle.replace("ITA", "Italian")
        subtitle = subtitle.replace("RUS", "Russian")
        subtitle = subtitle.replace("HIN", "Hindi")
        subtitle = subtitle.replace("RUM", "Romanian")
        subtitle = subtitle.replace("FIN", "Finnish")
        subtitle = subtitle.replace("MAY", "Malaysian")
        subtitle = subtitle.replace("SWE", "Swedish")
        subtitle = subtitle.replace("GRE", "Greek")
        subtitle = subtitle.replace("HEB", "Hebrew")
        subtitle = subtitle.replace("JPN", "Japanese")
        subtitle = subtitle.replace("POL", "Polish")
        subtitle = subtitle.replace("DUT", "Dutch")
        subtitle = subtitle.replace("FIL", "Filipino")
        subtitle = subtitle.replace("CES", "Czech")
        subtitle = subtitle.replace("HRV", "Croatian")
        subtitle = subtitle.replace("HUN", "Hungarian")
        subtitle = subtitle.replace("UKR", "Ukranian")
        main = await app.send_photo(KAYO_ID,photo=img,caption=caption)
        guessname = f"**{ghostname}**" + "\n" + f"__({tit})__" + "\n" + "━━━━━━━━━━━━━━━━━━━" + "\n" + "✓  `1080p x264 Web-DL`" + "\n" + f"✓  `{subtitle} ~ Subs`" + "\n" + "#Source #WebDL"
        
        thumbnail = await generate_thumbnail(id,file)

        videox = await app.send_document(

                DATABASE_ID,

            document=file,
            
            caption=guessname,

            file_name=filed,

            force_document=True,
                        
            thumb=thumbnail

            )   
        sourcefileid = videox.message_id
        source_link = f"https://t.me/zoroloverobot?start=animxt_{str_to_b64(sourcefileid)}"
        sourcetext = "hello"
        await asyncio.sleep(5)
        untext = await app.send_message(KAYO_ID, text = sourcetext, parse_mode = "markdown")
        
        os.rename(file,"video.mkv")


        compressed = await compress_video(duration,videox,untext,name,sourcetext)
        
        dingdong = await untext.edit(sourcetext)


        if compressed == "None" or compressed == None:

            print("Encoding Failed Uploading The Original File")

            os.rename("video.mkv",fpath)

        else:

            os.rename("out.mkv",fpath)
  
        print("Uploading --> ",name)

        await status.edit(await status_text(f"Uploading {name }"),reply_markup=button1)

        message_id = int(msg.message_id) + 1
        video = await upload_video(msg,fpath,id,tit,name,size,sourcetext,untext,subtitle) 
        try:

            os.remove("video.mkv")

            os.remove("out.mkv")

            os.remove(file)

            os.remove(fpath)

        except:

            pass     

    except FloodWait as e:

        flood_time = int(e.x) + 5

        try:

            await status.edit(await status_text(f"Floodwait... Sleeping For {flood_time} Seconds"),reply_markup=button1)

        except:

            pass

        await asyncio.sleep(flood_time)

    return message_id, id, tit, name, video

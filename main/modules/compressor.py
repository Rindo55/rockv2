import asyncio
import aiofiles
import aiohttp
from pathlib import Path

from main.modules.utils import get_progress_text 

import os

import re

import math

import subprocess

async def gg():
          cmd = '''ffmpeg -hide_banner -loglevel quiet -progress "progressaa.txt" -i "video.mkv" -filter_complex "[0:v]drawtext=fontfile=font.ttf:text='t.me/animxt':fontsize=35:fontcolor=ffffff:alpha='if(lt(t,0),0,if(lt(t,5),(t-0)/5,if(lt(t,15),1,if(lt(t,20),(5-(t-15))/5,0))))':x=w-text_w-15:y=15" -c:v h264 -s 320x240 -pix_fmt yuv420p10le -preset veryfast -r 24000/1001 -crf 23.2 -map 0:v -c:a aac -b:a 128k -map 0:a -c:s copy -map 0:s? "out.mkv" -y''',
          subprocess.Popen(cmd,shell=True)

async def compress_video(total_time,untext,name,sourcetext):

  try:

    video = "video.mkv"

    out = "out.mkv" 

    prog = "progressaa.txt"

    with open(prog, 'w') as f:

      pass

    

    asyncio.create_task(gg())

   

    while True:

      with open(prog, 'r+') as file:

        text = file.read()

        frame = re.findall("frame=(\d+)", text)

        time_in_us=re.findall("out_time_ms=(\d+)", text)

        progress=re.findall("progress=(\w+)", text)

        speed=re.findall("speed=(\d+\.?\d*)", text)

        if len(frame):

          frame = int(frame[-1])

        else:

          frame = 1

        if len(speed):

          speed = speed[-1]

        else:

          speed = 1

        if len(time_in_us):

          time_in_us = time_in_us[-1]

        else:

          time_in_us = 1

        if len(progress):

          if progress[-1] == "end":

            break

        

        time_done = math.floor(int(time_in_us)/1000000)

        

        progress_str = get_progress_text(sourcetext,"Encoding",time_done,str(speed),total_time,enco=True)

        try:

          await untext.edit(progress_str)

        except:

            pass

      await asyncio.sleep(20)

    if os.path.lexists(out):

        return out

    else:

        return "None"

  except Exception as e:

    print("Encoder Error",e)

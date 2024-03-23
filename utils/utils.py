import requests
from urllib.parse import urlparse
import os.path
import time

import session



import requests
import validators
from urllib.parse import urlparse
import os
import glob
from moviepy.editor import VideoFileClip, concatenate_videoclips
from natsort import natsorted
import utils.bot_config as bot_config
import funcs as funcs
import utils.m3u8_reader as m3u8_reader


# m3u8 type
def get_m3u8_type(url : str) -> str:
    
    # download file
    r = requests.get(url, allow_redirects = True).content
    open("downloads/temp.m3u8", "wb").write(r)

    # get file name and path
    a = urlparse(url)
    session.fileName = (os.path.basename(a.path))
    session.pathName = (os.path.dirname(session.url))

    m3u8 = open("downloads/temp.m3u8", "r")

    if "#EXTM3U" in m3u8:

        if "#EXTINF" in m3u8:

            if "#EXT-X-ENDLIST" in m3u8: return "vod"
            
            else: return "live"
                 
        else: return "playlist"

    else: return "notm3u8"


def get_chunk_dir_size():

    size = 0

    for path, dirs, files in os.walk("downloads/segments"):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)

    return size



def concat(): 

    tempClips = []

    for chunk in glob.glob("downloads/segments/*" + str(session.fileExtension)):
            tempClips.append(chunk)
 
    tempClips = natsorted(tempClips)
    clips = []

    for chunk in tempClips: # create video objects
        clips.append(VideoFileClip(chunk))

    finalClip = concatenate_videoclips(clips)
    finalClip.write_videofile("downloads/segments/output" + str(session.fileExtension), codec = "libx264", logger = None)




def send_video():

    with open("downloads/segments/output" + str(session.fileExtension), "rb") as video:# send the video
        return video


def remove_all():

    for chunk in glob.glob("downloads/segments/*"):
        os.remove(chunk)

def add_log(des : str):

    cTime = time.ctime()

    with open("downloads/log.txt", "a") as log:
        log.write(cTime + " : " + des + "\n")
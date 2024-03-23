import requests
from urllib.parse import urlparse
import os
import time
import glob
from moviepy.editor import VideoFileClip, concatenate_videoclips
from natsort import natsorted

import session

# get m3u8 type
def get_m3u8_type(url : str) -> str:
    
    # download file
    r = requests.get(url, allow_redirects = True).content
    with open("downloads/temp.m3u8", "wb") as f:
        f.write(r)

    # get file name and path name
    a = urlparse(url)
    session.fileName = (os.path.basename(a.path))
    session.pathName = (os.path.dirname(url))

    m3u8 = open("downloads/temp.m3u8", "r")

    if "#EXTM3U" in m3u8:

        if "#EXTINF" in m3u8:

            if "#EXT-X-ENDLIST" in m3u8: return "vod"
            
            else: return "live"
                 
        else: return "playlist"

    else: return "notm3u8"

# get ts file folder size
def get_segment_dir_size() -> int:

    size = 0

    for path, dirs, files in os.walk("downloads/segments"):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)

    return size

# concatenate is files into a single video
def concat(): 

    tempClips = []
    
    # get all ts files
    for ts in glob.glob("downloads/segments/*" + str(session.fileExtension)):
        tempClips.append(ts)
    
    # sort in order
    tempClips = natsorted(tempClips)
    clips = []
    
    # create video objects
    for ts in tempClips: 
        clips.append(VideoFileClip(ts))
    
    # concatenate into a single video
    finalClip = concatenate_videoclips(clips)
    finalClip.write_videofile("downloads/segments/output" + str(session.fileExtension), codec = "libx264", logger = None)

# send video buffer
def send_video():

    with open("downloads/segments/output" + str(session.fileExtension), "rb") as video:# send the video
        return video

# remove downloads
def remove_all():
    
    # clear content in m3u8 file
    open("downloads/temp.m3u8", "w").close()
    
    # clear ts file folder
    for chunk in glob.glob("downloads/segments/*"):
        os.remove(chunk)

# add a log
def add_log(des : str):
    
    cTime = time.ctime()

    with open("downloads/log.txt", "a") as log:
        log.write(cTime + " : " + des + "\n")
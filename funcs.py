import requests
import validators
from urllib.parse import urlparse
import os
import glob
from moviepy.editor import VideoFileClip, concatenate_videoclips
from natsort import natsorted
import bot_config
import funcs
import chunk_reader

bot = bot_config.bot
queue = []
queue_users = []

session_status = False
# save user informations
user_id = int()
edit_message_id = int()
content = str()
# url
url = str()
path_name = str()
file_name = str()
file_extention = str()


valid_url = False
def validate_message(): # check if url is valid
    link_message = str(funcs.content).strip("\n").replace(" ","")
    valid = validators.url(link_message)
    if valid == True: # store url if valid
        funcs.valid_url = True
        funcs.url = link_message
        return 0
    else:
        funcs.valid_url = False
        return 0


m3u8_type = str()
def check_url(): # check if the url is a playlist or chunk 
    r = requests.get( funcs.url, allow_redirects=True).content # downloads file
    open("temp.m3u8", "wb").write(r)

    # get file name and pathh name
    a = urlparse(funcs.url)
    funcs.file_name = (os.path.basename(a.path))
    funcs.path_name = (os.path.dirname(funcs.url))


    if "#EXTM3U" in open("temp.m3u8").read():
        if "#EXTINF" in open("temp.m3u8").read():
            if "#EXT-X-ENDLIST" in open("temp.m3u8").read():
                funcs.m3u8_type = "vod.m3u8"
                return 0 
            else:
                funcs.m3u8_type = "live.m3u8"
                return 0   
        else:
            funcs.m3u8_type = "playlist.m3u8"
            return 0
    else:
        funcs.m3u8_type = "notm3u8"
        return 0



dir_size = 0
def check_size():
    size = 0
    for path, dirs, files in os.walk("segments"):
        for f in files:
            fp = os.path.join(path, f)
            size += os.path.getsize(fp)
    funcs.dir_size = size       
    return 0


def concat(): 

    bot.send_message(funcs.user_id,"Concatenating video.")
    temp_clips = []
    clips = []  

    try: # create a list of segments
        for i in glob.glob("segments/*"+str(funcs.file_extention)):
            temp_clips.append(i)
    except:
        pass
# ---------
    bot.send_message(funcs.user_id, len(temp_clips))
    bot.send_message(funcs.user_id, temp_clips)
    temp_clips = natsorted(temp_clips)
    bot.send_message(funcs.user_id, len(temp_clips))
    bot.send_message(funcs.user_id, temp_clips)
# ---------
    for i in temp_clips: # create video objects
        try:
            clips.append(VideoFileClip(i))
        except:
            pass

    final = concatenate_videoclips(clips)
    final.write_videofile("segments/output"+str(funcs.file_extention), codec = "libx264", logger = None)
    return 0

def send_video():
    bot.send_message(funcs.user_id,"Sending video.")
    video = open("segments/output"+str(funcs.file_extention), "rb") # send the video
    bot.send_video(funcs.user_id, video)
    video.close()
    return 0


def remove_all():
    try:
        for f in glob.glob("segments/*"):
            os.remove(f)
        return 0
    except:
        pass



def close_session():

    funcs.session_status = False
    
    funcs.queue.remove(funcs.queue[0])
    funcs.queue_users.remove(funcs.queue_users[0])
    
    funcs.edit_message_id = int()
    funcs.content = str()
    
    funcs.url = str()
    funcs.path_name = str()
    funcs.file_name = str()
    funcs.file_extention = str()

    # download   
    funcs.valid_url = False
    funcs.m3u8_type = str()
    funcs.dir_size = 0
    #chunk reader
    chunk_reader.chunk_dict = {}


    # segments   
    try: # close output video if opened
        video = open("segments/output"+str(funcs.file_extention), "rb") 
        video.close() 
        pass
    except:
        pass
    
    # remove all
    try:
        for f in glob.glob("segments/*"):
            os.remove(f) 
    except:
        pass

    # temp m3u8
    open("temp.m3u8", "w").close() 
    return 0

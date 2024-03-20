import requests
from urllib.parse import urlparse
import os

import bot_config
import session
from utils import utils

bot = bot_config.bot

def download_ts(chunkUrls : dict, streamType : str):

   tsCount = len(chunkUrls) / 2
   currentTs = 0

   while currentTs < tsCount:
      
      # check if chunk dir size exceeded
      # concatenate and send video if size exceeds
      s = utils.get_chunk_dir_size()
      
      if s >= 500000000: # 500 MB

         bot.send_message(session.userId, "Concatenating video.")
         utils.concat()

         bot.send_message(session.userId, "Sending video.")
         video = utils.send_video()
         bot.send_video(session.userId, video)
   
         utils.remove_all()

      if session.sessionStatus == False: 
         session.close_session()
         break

      # read chunk url
      chunkUrl = chunkUrls["segment" + str(currentTs)]
      
      # get chunk filename and file extension
      a = urlparse(chunkUrl)
      fileName = (os.path.basename(a.path))
      fileExtention = fileName.rstrip("\n").split(".", 1)
      session.fileExtension = ("." + str(fileExtention[1]))
      
      # download chunk
      try:

         r = requests.get(chunkUrl, allow_redirects=True).content
         with open("downloads/segments/"+str(fileName), "wb") as f:
            f.write(r)
         
         # update status bar
         session.segsDownloaded += 1
        
         if streamType == "vod":
            bot.edit_message_text(chat_id = session.userId, text = "Downloading " + str(session.segsDownloaded) 
               + " of " + str(session.segCount),  message_id = session.downloadStatus)
         else:
            bot.edit_message_text(chat_id = session.userId, text = "Recording " + str(session.segsDownloaded) 
               + " of ?",  message_id = session.downloadStatus)
      
         currentTs += 1
   
      except:
         currentTs += 1

      continue
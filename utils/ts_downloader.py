import requests
from urllib.parse import urlparse
import os

import utils.bot_config as bot_config
import session
from utils import utils

bot = bot_config.bot

# download ts file
def download_ts(tsUrls : list, streamType : str):

   tsCount = len(tsUrls)
   currentTs = 0

   while currentTs < tsCount:

      if session.sessionStatus == False: break
      
      # check if storage size exceeded
      # concatenate and send video if size exceeds
      s = utils.get_segment_dir_size()
      
      if s >= 3000000: # 500000000 500 MB
         
         # set finsihed status
         session.finished = True
         
         # concatenate and send video
         bot.send_message(session.userId, "Concatenating video...")
         utils.concat()
         
         bot.send_message(session.userId, "Sending video...")
         with open("downloads/segments/output" + str(session.fileExtension), "rb") as video:
            bot.send_video(session.userId, video)
         
         # remove downloads
         utils.remove_all()

         break

      # read ts url
      tsUrl = tsUrls[currentTs]
      
      # get ts filename and file extension
      a = urlparse(tsUrl)
      fileName = (os.path.basename(a.path))
      fileExtention = fileName.rstrip("\n").split(".", 1)
      session.fileExtension = ("." + str(fileExtention[1]))
      
      # download ts file
      try:

         r = requests.get(tsUrl, allow_redirects = True).content
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

         utils.add_log("Download failed, TS file " + str(currentTs))
         currentTs += 1

      continue
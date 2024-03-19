import threading
import validators

import bot_config
import funcs
import chunk_reader
import ts_downloader
import status_bar

from utils import admin
from utils import queue_manager
from utils import session
from utils import utils

# bot
bot = bot_config.bot

def start_download():

   try:

      while len(queue_manager.queue_users) != 0:

         funcs.remove_all()
         # start session
         message = funcs.queue[0]
         session.userId = message.from_user.id
         session.url = message.text
         session.sessionStatus = True    

         bot.reply_to(message, text = "Got it.")
         bot.send_message(session.userId, "Initializing a new process.")
         
         # process loop
         # The session status is periodically checked

         while funcs.session_status == True:

            m3u8Type = utils.get_m3u8_type(session.url)

            # vod
                       
            if m3u8Type == "vod":
               bot.send_message(session.userId, "VOD detected.")
               session.downloadStatus = bot.send_message(session.userId, "Downloading...").message_id   
               if session.sessionStatus == True:
                  chunk_reader.download_chunk()
                  if session.sessionStatus == True:
                     chunk_reader.read_chunk()
                     if session.sessionStatus == True:
                        ts_downloader.download_ts_vod()
                        bot.send_message(funcs.user_id,"Download finished.")
                  if session.sessionStatus == True:
                     funcs.concat()
                     funcs.send_video()
                     funcs.remove_all()
                     session.close_session()
               break     
            
            # live

            elif m3u8Type == "live":
               bot.send_message(session.userId,"Live detected.")
               session.downloadStatus = bot.send_message(session.userId, "Recording live.").message_id 
               status_bar.segment_number = 0
               while True:
                  if session.sessionStatus == True:
                     chunk_reader.download_chunk()
                     if session.sessionStatus == True:
                        chunk_reader.read_chunk()
                        if session.sessionStatus == True:
                           ts_downloader.download_ts_live()
                           continue
                  if session.sessionStatus == True:
                     funcs.concat()
                     funcs.send_video()
                     funcs.remove_all()
                     session.close_session()
                  break
               break
            
            # playlist

            elif m3u8Type == "playlist":
               bot.send_message(funcs.user_id,"Send only the direct chunk file link.")
               session.close_session()
               break                             
            
            # not m3u8

            elif m3u8Type == "notm3u8":
               bot.send_message(funcs.user_id,"This is not an m3u8 link or the file is corrupted.")
               session.close_session()
               break
            
            # error

            else:
               bot.send_message(funcs.user_id,"Unknown error occured.")
               session.close_session()
               break

   except Exception as e:
      bot.send_message(admin.adminId, str(e))
      session.close_session()


# start downloading loop
download_thread = threading.Thread(target = start_download)
download_thread.start()

# wait for start command
@bot.message_handler(commands = ["start"])
def start(message):

   chatId = str(message.chat.id)

   # welcome message
   bot.send_message(chatId, "Welcome.")
   bot.send_message(chatId, '''---Send the m3u8 url.\n
---To clear request, press /clear .\n
---To view queue position, press /queue .\n
*Encrypted streams are not supported yet.''')
      

# clear request
@bot.message_handler(commands = ["clear"])
def clear(message):

   chatId = str(message.chat.id)

   if chatId in queue_manager.queue_users:
      
      # terminate process and remove request
      if queue_manager.queue_users.index(chatId) == 0:
         bot.send_message(chatId, "Process terminated.")
         bot.send_message(chatId, "Request removed from queue.")
         session.close_session()
      
      # remove request
      else:
         queue_manager.queue_users.remove(chatId) 
         queue_manager.queue.pop(chatId) 
         bot.send_message(chatId, "Request removed from queue.")
            
   else:
      bot.send_message(chatId, "You don't have any requests.") 


# view queue position
@bot.message_handler(commands = ["queue"])
def queue(message):

   chatId = str(message.chat.id)
   
   if chatId in queue_manager.queue_users:
      bot.send_message(chatId, f"Request is positioned at {queue_manager.queue_users.index(chatId)} .")
   else:
      bot.send_message(chatId, "You don't have any requests.")
   
   


# wait for url message
@bot.message_handler(func = lambda message:True)
def url_message(message):

   chatId = str(message.chat.id)
   
   # check fo urls
   valid = validators.url(message.text)

   if valid == True:

      # queue request
      if chatId not in funcs.queue_users:
         queue_manager.queue[chatId] = message
         queue_manager.queue_users.append(chatId)
         bot.send_message(chatId, "Request queued.")

      # reject request
      else:
         bot.send_message(chatId, "You already have a request.")
 
   else:
      bot.send_message(chatId,"Url is not valid.")

#waits for new messages 
bot.polling() 
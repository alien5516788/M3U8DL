import threading
import validators
import os

import utils.bot_config as bot_config
import session
from utils import utils
from utils import m3u8_reader
from utils import ts_downloader

# bot
bot = bot_config.bot

# bot started message
print("--------Bot started--------")
# initialize download directory
os.mkdir("downloads")
os.mkdir("downloads/segments")
open("downloads/log.txt", "w").close()
open("downloads/temp.m3u8", "w").close()
utils.add_log("--------Bot started--------")
bot.send_message(session.adminId, "--------Bot started--------")

# download thread
def start_download():

   utils.add_log("Download thread started")
   
   # thread loop
   while True:

      try:
         
         # queue loop
         while len(session.queueUsers) != 0:
            
            # remove any garbage files
            utils.remove_all()

            # start session
            currentUser = session.queueUsers[0]
            message = session.queue[str(currentUser)]

            session.sessionStatus = True 
            session.userId = message.from_user.id

            session.url = message.text

            bot.reply_to(message, text = "Got it.")
            bot.send_message(session.userId, "Initializing a new process.")
            
            # start process
            # The session status is periodically checked

            m3u8Type = utils.get_m3u8_type(session.url)

            # vod
                        
            if m3u8Type == "vod":
               
               # vod detected
               bot.send_message(session.userId, "VOD detected.")
               session.downloadStatus = bot.send_message(session.userId, "Downloading...").message_id   
               
               if session.sessionStatus == False: break
               
               # downlaod m3u8 file
               c = m3u8_reader.download_m3u8(session.url)
               if c == False:
                  bot.send_message(session.userId, "Failed to download m3u8 file.")
                  session.close_session()

               if session.sessionStatus == False: break
               
               # read m3u8 file
               c = m3u8_reader.read_m3u8(session.pathName)
               if c == False:
                  bot.send_message(session.userId, "This is not an m3u8 file or the file is corrupted.")
                  session.close_session()

               if session.sessionStatus == False: break
               
               # download ts files
               tsCount = len(c) # type: ignore
               session.segCount = tsCount
         
               ts_downloader.download_ts(c, "vod") # type: ignore
               bot.send_message(session.userId, "Download finished.")

               if session.sessionStatus == False: break
               
               # concatenate and send video
               bot.send_message(session.userId, "Concatenating video.")
               utils.concat()
               
               bot.send_message(session.userId, "Sending video.")
               with open("downloads/segments/output" + str(session.fileExtension), "rb") as video:
                  bot.send_video(session.userId, video)
         
               break     
            
            # live

            elif m3u8Type == "live":
               
               # live detected
               bot.send_message(session.userId, "Live detected.")
               session.downloadStatus = bot.send_message(session.userId, "Recording...").message_id 
               
               # check loop
               while True:

                  if session.sessionStatus == False: break
                  if session.finished == True: break
                  
                  # downlaod m3u8 file
                  c = m3u8_reader.download_m3u8(session.url)
                  if c == False:
                     bot.send_message(session.userId, "Failed to download m3u8 file.")
                     session.close_session()

                  if session.sessionStatus == False: break
                  
                  # read m3u8 file
                  c = m3u8_reader.read_m3u8(session.pathName)
                  if c == False:
                     bot.send_message(session.userId, "This is not an m3u8 file or the file is corrupted.")
                     session.close_session()
                  
                  if session.sessionStatus == False: break
                  
                  # download ts files
                  tsCount = len(c) # type: ignore
                  session.segCount = tsCount
            
                  ts_downloader.download_ts(c, "live") # type: ignore

                  continue

               if session.sessionStatus == False: break

               bot.send_message(session.userId, "Download finished.")

               # concatenate and send video
               bot.send_message(session.userId, "Concatenating video.")
               utils.concat()
               
               bot.send_message(session.userId, "Sending video.")
               with open("downloads/segments/output" + str(session.fileExtension), "rb") as video:
                  bot.send_video(session.userId, video)
         
               break
            
            # playlist

            elif m3u8Type == "playlist":
               bot.send_message(session.userId, "Send only the direct m3u8 file link.")
               break                             
            
            # not m3u8

            elif m3u8Type == "notm3u8":
               bot.send_message(session.userId, "This is not an m3u8 link or the file is corrupted.")
               break
            
            # error

            else:
               utils.add_log("Unknown error occured.")
               bot.send_message(session.userId, "Unknown error occured.")
               break
         
         # close session and remove previous downloads
         session.close_session()
         utils.remove_all()

      except Exception as e:

         utils.add_log(str(e))
         bot.send_message(session.adminId, "M3U8DL Error: " + str(e))

         session.close_session()
         utils.remove_all()

# start downloading loop
download_thread = threading.Thread(target = start_download, daemon = True)
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
   
   # terminate process
   # remove request
   if chatId in session.queueUsers:

      if session.queueUsers.index(chatId) == 0:
         
         session.sessionStatus = False
         bot.send_message(chatId, "Process terminated.")
      
      else:
         bot.send_message(chatId, "Request removed from queue.")
      
      # doesn't use close_session,
      # because it might cause problems in downlaod thread
      session.queueUsers.remove(chatId) 
      session.queue.pop(chatId) 

   else:
      bot.send_message(chatId, "You don't have any requests.") 

# view queue position
@bot.message_handler(commands = ["queue"])
def queue(message):

   chatId = str(message.chat.id)
   
   if chatId in session.queueUsers:
      bot.send_message(chatId, f"Request is positioned at {session.queueUsers.index(chatId)} .")
   
   else:
      bot.send_message(chatId, "You don't have any requests.")
   
# start bot (admin only)
@bot.message_handler(commands = ["startbot"])
def start_bot(message):

   chatId = str(message.chat.id)

   if chatId != session.adminId:
      bot.send_message(session.adminId, "Admin only !")
      return
   
   # if download_thread.is_alive() == False:
   #    download_thread.start()

   # bot.resume() # !!!

   bot.send_message(session.adminId, "Command is not supported.")

# send log file (admin only)
@bot.message_handler(commands = ["log"])
def send_log(message):

   chatId = str(message.chat.id)

   if chatId != session.adminId:
      bot.send_message(session.adminId, "Admin only !")
      return
   
   with open("downloads/log.txt") as log:
      bot.send_message(session.adminId, log.read())

# stop bot (admin only)
@bot.message_handler(commands = ["stopbot"])
def stop_bot(message):

   chatId = str(message.chat.id)

   if chatId != session.adminId:
      bot.send_message(session.adminId, "Admin only !")
      return
   
   # bot.pause() # !!!

   bot.send_message(session.adminId, "Command is not supported.")
   
# wait for url message
@bot.message_handler(func = lambda message:True)
def url_message(message):

   chatId = str(message.chat.id)
   
   # check for urls
   valid = validators.url(message.text)

   if valid == True:

      # queue request
      if chatId not in session.queueUsers:
         session.queue[chatId] = message
         session.queueUsers.append(chatId)
         bot.send_message(chatId, "Request queued.")

      # reject request
      else:
         bot.send_message(chatId, "You already have a request.")
 
   else:
      bot.send_message(chatId, "Url is invalid.")

# wait for new messages 
bot.polling()

# bot stopped notification
# remove all files after stopping
utils.remove_all()

print("--------Bot stopped--------")
bot.send_message(session.adminId, "--------Bot stopped--------")
utils.add_log("--------Bot stopped--------")
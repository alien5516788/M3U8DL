import threading
import validators

import utils.bot_config as bot_config
import admin
import queue_manager
import session
from utils import utils
from utils import m3u8_reader
from utils import ts_downloader

# bot
bot = bot_config.bot

print("--------Bot started--------")
utils.add_log("--------Bot started--------")
bot.send_message(admin.adminId, "--------Bot started--------")

def start_download():

   utils.add_log("Download thread started")

   try:

      while len(queue_manager.queueUsers) != 0:
         
         # remove any garbage files
         utils.remove_all()

         # start session
         message = queue_manager.queue[0]

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
            utils.concat()

            bot.send_message(session.userId, "Sending video final.")
            video = utils.send_video()
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
            utils.concat()

            bot.send_message(session.userId, "Sending video final.")
            video = utils.send_video()
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
      bot.send_message(admin.adminId, "M3U8DL Error: " + str(e))

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
   if chatId in queue_manager.queueUsers:

      queue_manager.queueUsers.remove(chatId) 
      queue_manager.queue.pop(chatId)
      
      # doesn't use close_session,
      # because it might cause problems in downlaod thread
      if queue_manager.queueUsers.index(chatId) == 0:
         
         session.sessionStatus = False
         bot.send_message(chatId, "Process terminated.")
      
      else:
         bot.send_message(chatId, "Request removed from queue.")
            
   else:
      bot.send_message(chatId, "You don't have any requests.") 

# view queue position
@bot.message_handler(commands = ["queue"])
def queue(message):

   chatId = str(message.chat.id)
   
   if chatId in queue_manager.queueUsers:
      bot.send_message(chatId, f"Request is positioned at {queue_manager.queueUsers.index(chatId)} .")
   
   else:
      bot.send_message(chatId, "You don't have any requests.")
   
# wait for url message
@bot.message_handler(func = lambda message:True)
def url_message(message):

   chatId = str(message.chat.id)
   
   # check for urls
   valid = validators.url(message.text)

   if valid == True:

      # queue request
      if chatId not in queue_manager.queueUsers:
         queue_manager.queue[chatId] = message
         queue_manager.queueUsers.append(chatId)
         bot.send_message(chatId, "Request queued.")

      # reject request
      else:
         bot.send_message(chatId, "You already have a request.")
 
   else:
      bot.send_message(chatId, "Url is invalid.")

# start bot (admin only)
@bot.message_handler(commands = ["startbot"])
def start_bot(message):

   chatId = str(message.chat.id)

   if chatId != admin.adminId:
      bot.send_message(admin.adminId, "Admin only !")
      return
      
   if download_thread.is_alive() == True:
      bot.send_message(admin.adminId, "Bot is already running.")
      return
   
   bot.send_message(admin.adminId, "Thread restarted.")
   utils.add_log("Thread restarted.")
   download_thread.start()

# send log file (admin only)
@bot.message_handler(commands = ["log"])
def send_log(message):

   chatId = str(message.chat.id)

   if chatId != admin.adminId:
      bot.send_message(admin.adminId, "Admin only !")
      return
   
   bot.send_document(admin.adminId, "downloads/log.txt")

# wait for new messages 
bot.polling() 
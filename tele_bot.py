import threading
import validators

import bot_config
import admin
import queue_manager
import session
from utils import utils
from utils import chunk_reader
from utils import ts_downloader

# bot
bot = bot_config.bot

def start_download():

   try:

      while len(queue_manager.queueUsers) != 0:

         utils.remove_all()
         # start session
         message = queue_manager.queue[0]
         session.userId = message.from_user.id
         session.url = message.text
         session.sessionStatus = True    

         bot.reply_to(message, text = "Got it.")
         bot.send_message(session.userId, "Initializing a new process.")
         
         # process loop
         # The session status is periodically checked

         while session.sessionStatus == True:

            m3u8Type = utils.get_m3u8_type(session.url)

            # vod
                       
            if m3u8Type == "vod":

               bot.send_message(session.userId, "VOD detected.")
               session.downloadStatus = bot.send_message(session.userId, "Downloading...").message_id   
               
               if session.sessionStatus == False: break

               c = chunk_reader.download_chunk(session.url)
               if c == False:
                  bot.send_message(session.userId, "No files recieved.Download finished.")
                  session.close_session()

               if session.sessionStatus == False: break

               c = chunk_reader.read_chunk(session.pathName)
               if c == False:
                  bot.send_message(session.userId, "This is not an m3u8 file or the file is corrupted.")
                  session.close_session()

               if session.sessionStatus == False: break

               tsCount = len(c / 2)
               session.segCount = tsCount
               # bot.send_message(session.userId, str(tsCount) + " parts found.")

               ts_downloader.download_ts(c, "vod")
               bot.send_message(session.userId, "Download finished.")

               if session.sessionStatus == False: break
                  
               utils.concat()
               utils.send_video()
               utils.remove_all()
            
               break     
            
            # live

            elif m3u8Type == "live":

               bot.send_message(session.userId, "Live detected.")
               session.downloadStatus = bot.send_message(session.userId, "Recording. ").message_id 
               
               while True:

                  if session.sessionStatus == False: break
                  
                  c = chunk_reader.download_chunk(session.url)
                  if c == False:
                     bot.send_message(session.userId, "No files recieved.Download finished.")
                     session.close_session()

                  if session.sessionStatus == False: break
                    
                  c = chunk_reader.read_chunk(session.pathName)
                  if c == False:
                     bot.send_message(session.userId, "This is not an m3u8 file or the file is corrupted.")
                     session.close_session()
                  
                  if session.sessionStatus == False: break
                  
                  tsCount = len(c / 2)
                  session.segCount = tsCount
                  # bot.send_message(session.userId, str(tsCount) + " parts found.")

                  ts_downloader.download_ts(c, "live")
                  bot.send_message(session.userId, "Download finished.")

                  continue

               if session.sessionStatus == False: break

               utils.concat()
               utils.send_video()
               utils.remove_all()
            
               break
            
            # playlist

            elif m3u8Type == "playlist":
               bot.send_message(session.userId, "Send only the direct chunk file link.")
               break                             
            
            # not m3u8

            elif m3u8Type == "notm3u8":
               bot.send_message(session.userId, "This is not an m3u8 link or the file is corrupted.")
               break
            
            # error

            else:
               bot.send_message(session.userId, "Unknown error occured.")
               break

         session.close_session()

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

   if chatId in queue_manager.queueUsers:
      
      # terminate process and remove request
      if queue_manager.queueUsers.index(chatId) == 0:
         bot.send_message(chatId, "Process terminated.")
         bot.send_message(chatId, "Request removed from queue.")
         session.close_session()
      
      # remove request
      else:
         queue_manager.queueUsers.remove(chatId) 
         queue_manager.queue.pop(chatId) 
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
   
   # check fo urls
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
      bot.send_message(chatId,"Url is not valid.")

#waits for new messages 
bot.polling() 
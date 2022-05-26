import threading
import validators
import bot_config
import funcs
import chunk_reader
import ts_downloader


bot = bot_config.bot


def start_download():

   while True:
      while len(funcs.queue) != 0:

         funcs.remove_all()
         #save user data
         message = funcs.queue[0]
         funcs.user_id = message.from_user.id
         funcs.url = message.text
         funcs.session_status = True    

         bot.reply_to(message, text = "Got it.")
         bot.send_message(message.chat.id,"Initializing a new process.")

         while funcs.session_status == True: 
            funcs.check_url()

#-----------                   
            if funcs.m3u8_type == "vod.m3u8":
               bot.send_message(funcs.user_id,"VOD detected.")
               funcs.edit_message_id = bot.send_message(funcs.user_id,"Downloading.").message_id   
               if funcs.session_status == True:
                  chunk_reader.download_chunk()
                  if funcs.session_status == True:
                     chunk_reader.read_chunk()
                     if funcs.session_status == True:
                        ts_downloader.download_ts_vod()
                        bot.send_message(funcs.user_id,"Download finished.")
                  if funcs.session_status == True:
                     funcs.concat()
                     funcs.send_video()
                     funcs.remove_all()
                     funcs.close_session()
               break     
#----------- 
            elif funcs.m3u8_type == "live.m3u8":
               bot.send_message(funcs.user_id,"Live detected.")
               funcs.edit_message_id = bot.send_message(funcs.user_id,"Recording live.").message_id 
               while True:
                  if funcs.session_status == True:
                     chunk_reader.download_chunk()
                     if funcs.session_status == True:
                        chunk_reader.read_chunk()
                        if funcs.session_status == True:
                           ts_downloader.download_ts_live()
                           continue
                  if funcs.session_status == True:
                     funcs.concat()
                     funcs.send_video()
                     funcs.remove_all()
                     funcs.close_session()
                  break
               break
#-----------
            elif funcs.m3u8_type == "playlist.m3u8":
               bot.send_message(funcs.user_id,"Send only the direct chunk file link.")
               funcs.close_session()
               break                             
#-----------
            elif funcs.m3u8_type == "notm3u8":
               bot.send_message(funcs.user_id,"This is not an m3u8 link or the file is corrupted.")
               funcs.close_session()
               break
#-----------
            else:
               bot.send_message(funcs.user_id,"Unknown error occured.")
               funcs.close_session()
               break
      continue





# start downloading loop
download_thread = threading.Thread(target = start_download)
download_thread.start()

# waits for start command
@bot.message_handler(commands = ["start"])
def start(message):

   # sends welcome message
   bot.send_message(message.chat.id,"Welcome.")
   bot.send_message(message.chat.id,'''---Send the m3u8 url.\n
---To clear request, press /clear .\n
---To view queue position, press /queue .\n
*Encrypted streams are not supported yet.''')
      

# clear request
@bot.message_handler(commands = ["clear"])
def clear(message):

   if message.chat.id in funcs.queue_users:
      if funcs.queue_users.index(message.chat.id) == 0:
         bot.send_message(message.chat.id,"Process terminated.")
         bot.send_message(message.chat.id,"Request removed from queue.")
         funcs.close_session()
   
      else:
         bot.send_message(message.chat.id,"Request removed from queue.")
         funcs.queue.remove(funcs.queue[(funcs.queue_users).index(message.chat.id)]) # remove message from queue
         funcs.queue_users.remove(message.chat.id) # remove user from queue
   else:
      bot.send_message(message.chat.id,"You don't have any requests.") 


# view queue position
@bot.message_handler(commands = ["queue"])
def queue(message):
   
   if message.chat.id in funcs.queue_users:
      bot.send_message(message.chat.id,"Request positioned at "+str((funcs.queue_users).index(message.chat.id))+ ".")
   else:
      bot.send_message(message.chat.id,"You don't have any requests.")
   
   


# wait for url message
@bot.message_handler(func=lambda message:True)
def url_message(message):
   
   valid = validators.url(message.text)
   if valid == True:
      if message.chat.id not in funcs.queue_users:
         funcs.queue.append(message) # append message to queue
         funcs.queue_users.append(message.chat.id) # append user to queue
         bot.send_message(message.chat.id,"Request queued.")
         pass
      else:
         bot.send_message(message.chat.id,"You already have a request.")
         pass

   else:
      bot.send_message(message.chat.id,"Url is not valid.")
      pass

bot.polling() #waits for new messages 
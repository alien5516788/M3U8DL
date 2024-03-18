import requests
from urllib.parse import urlparse
import os
import funcs as funcs
import bot_config
import chunk_reader
import status_bar


bot = bot_config.bot


def download_ts_vod():
   x = 1
   while x <= (len(chunk_reader.chunk_dict)/2):
      funcs.check_size() # check if the dir size exceeds
      if funcs.dir_size >= 1500000000:
         funcs.concat()
         funcs.send_video()
         funcs.remove_all()
         pass
      else: # if not pass
         pass

      if funcs.session_status == True:
         # downloads ts files
         y = chunk_reader.chunk_dict["segment"+str(x)]
         a = urlparse(y)
         file_name = (os.path.basename(a.path)) # get file name
         file_extention = file_name.rstrip("\n").split(".", 1) # get file extention
         funcs.file_extention = ("."+str(file_extention[1]))
         try: # download the file
            r = requests.get( y, allow_redirects=True).content # request file
            open("segments/"+str(file_name), "wb").write(r)
            status_bar.segment_number = x # segment number
            status_bar.status_bar_vod() # running status bar instance
            x = x+1 # move to next url
            continue
   
         except:
            try: # try to download again if failed
               r = requests.get( y, allow_redirects=True).content
               open("segments/"+str(file_name), "wb").write(r)
               status_bar.segment_number = x # segment number
               status_bar.status_bar_vod()# running status bar instance
               x = x+1 # move to next url
               continue
            except:
               x = x+1 # move to next url
               continue
      else:
         funcs.close_session()
         break
   return 0


def download_ts_live():
   x = 1
   while x <= (len(chunk_reader.chunk_dict)/2):
      funcs.check_size() # check if the dir size exceeds
      if funcs.dir_size >= 1500000000:
         funcs.concat()
         funcs.send_video()
         funcs.remove_all()
         pass
      else: # if not pass
         pass

      if funcs.session_status == True:
         # downloads ts files
         y = chunk_reader.chunk_dict["segment"+str(x)]
         a = urlparse(y)
         file_name = (os.path.basename(a.path)) # get file name
         file_extention = file_name.rstrip("\n").split(".", 1) # get file extention
         funcs.file_extention = ("."+str(file_extention[1]))
         try:
            r = requests.get( y, allow_redirects=True).content # request file
            open("segments/"+str(file_name), "wb").write(r)
            status_bar.segment_number = status_bar.segment_number + 1 # segment number
            status_bar.status_bar_live() # running status bar instance
            x = x+1 # move to next url
            continue
   
         except:
            try:# try to download again if failed
               r = requests.get( y, allow_redirects=True).content
               open("segments/"+str(file_name), "wb").write(r)
               status_bar.segment_number = status_bar.segment_number + 1 # segment number
               status_bar.status_bar_live() # running status bar instance
               x = x+1 # move to next url
               continue
            except:
               x = x+1  # move to next url
               continue
      else:
         funcs.close_session()
         break
   return 0

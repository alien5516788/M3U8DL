import requests
import validators
import bot_config
import funcs as funcs
import utils.status_bar as status_bar



bot = bot_config.bot


def download_chunk():
   try:
      r = requests.get( funcs.url , allow_redirects=True)
      open("temp.m3u8", "wb").write(r.content)
      pass
   except:
      try:
         r = requests.get( funcs.url , allow_redirects=True)
         open("temp.m3u8", "wb").write(r.content)
         pass
      except:
            if funcs.m3u8_type == "vod.m3u8":
               bot.send_message(funcs.user_id,"No files recieved.Download finished.")
               funcs.close_session() # close session
               return 0
            elif funcs.m3u8_type == "live.m3u8":
               try:
                  funcs.concat() # concatenate segments
                  funcs.send_video # send the video
                  funcs.remove_all() # remove residuals
                  pass
               except:
                  pass
               bot.send_message(funcs.user_id,"No files recieved.Download finished.")
               funcs.close_session() # close session
               return 0






chunk_dict = {}
def read_chunk():
   

   # read chunk file
   f = open("temp.m3u8", "r").readlines()

   line_count = len(f)
   line_number = 0 # indicates which line number is chosen
   attribute_index = 1 # indicates the sttribute index
   
   # check if the file is an m3u8 file
   if "#EXTM3U" in open("temp.m3u8").read():
      pass
   else:
      download_chunk()
      if "#EXTM3U" in open("temp.m3u8").read():
         pass
      else:
         bot.send_message(funcs.user_id,"This is not an m3u8 file or the file is corrupted.")
         funcs.close_session()
         return 0

   
   while line_number <= line_count:
      # if attribute exists in the line
      if "#EXTINF:" in f[line_number]:
         g = f[line_number].rstrip("\n").split(":",1)
         s1 = g[1] # value
         s2 = f[line_number+1].rstrip("\n") # ts url
         
         valid = validators.url(s2) # validate chunk url
         if valid == True:
            pass
         else:
            s2 = (str(funcs.path_name)+"/"+str(s2))
            pass

         chunk_dict["EXTINF"+str(attribute_index)] = s1
         chunk_dict["segment"+str(attribute_index)] = s2


         if line_number == line_count-1: # break if line count out of range
            break
         else:
            line_number = line_number+1 # move to next line
            attribute_index = attribute_index+1 # increment attribute index
            continue

      else:
         if line_number == line_count-1: # break if line count out of range
            break
         else:
            line_number = line_number+1 # move to next line
            continue


   # send number of parts to be downloaded
   # bot.send_message(funcs.user_id, str(attribute_index)+" parts found.")
   status_bar.segments = attribute_index
   return 0
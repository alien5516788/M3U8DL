import requests
import validators

import utils.bot_config as bot_config
from utils.utils import add_log

bot = bot_config.bot

# download the .m3u8 file
def download_m3u8(url : str) -> bool:

   try:
      
      # download and save .m3u8 file
      r = requests.get(url , allow_redirects=True)

      with open("downloads/temp.m3u8", "wb") as f:
         f.write(r.content)

      return True
   
   except:
      add_log("Failed to download m3u8 file.")
      return False
   
# read .m3u8 file and extract ts file urls
def read_m3u8(pathName : str):
   
   # read chunk file
   m3u8File = open("downloads/temp.m3u8", "r").readlines()

   # check if the file is an m3u8 file
   if "#EXTM3U" not in m3u8File[0]:
      
      add_log("This is not an m3u8 file.")
      return False
   
   # ts file url list
   tsUrls = []

   lineCount = len(m3u8File)
   lineNumber = 0
   extinf = 0 # #EXTINF attribute number
   
   while lineNumber < lineCount:

      line = m3u8File[lineNumber]

      # if attribute exists in the line
      if "#EXTINF:" in line:
         
         # get url
         tsUrl = m3u8File[lineNumber + 1].rstrip("\n")
         
         # check if url has the full path
         if validators.url(tsUrl) != True: # type: ignore
            tsUrl = pathName + "/" + tsUrl
         
         # add info and url list
         tsUrls.append(tsUrl)
        
         # increment line number and attribute number
         lineNumber += 1
         extinf += 1

         continue

      else:

         lineNumber += 1
         continue

   return tsUrls
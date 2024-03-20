import requests
import validators
import bot_config
import funcs as funcs
import utils.status_bar as status_bar



bot = bot_config.bot


def download_chunk(url : str) -> bool:

   try:

      r = requests.get( funcs.url , allow_redirects=True)

      with open("downloads/temp.m3u8", "wb") as f:
         f.write(r.content)

      return True
   
   except:
      return False
   

def read_chunk(pathName : str):
   
   # read chunk file
   chunkFile = open("downloads/temp.m3u8", "r").readlines()

   # check if the file is an m3u8 file
   if "#EXTM3U" not in chunkFile[0]: return False
   
   # ts file url list
   chunkUrls = {}

   lineCount = len(chunkFile)
   lineNumber = 0
   attributeNumber = 0 # #EXTINF
   
   while lineNumber < lineCount:

      line = chunkFile[lineNumber]

      # if attribute exists in the line
      if "#EXTINF:" in line:
         
         # filter line
         filteredLine = line.rstrip("\n").split(":", 1)
         chunkInfo = filteredLine[1]
         tsUrl = chunkFile[lineNumber + 1].rstrip("\n")
         
         # check if url has the full path
         if validators.url(tsUrl) != True:
            tsUrl = pathName + "/" + tsUrl
         
         # add info and url to a dicitionary
         chunkUrls["EXTINF" + str(attributeNumber)] = chunkInfo
         chunkUrls["segment" + str(attributeNumber)] = tsUrl
        
         # increment line number and attribute number
         lineNumber += 1
         attributeNumber += 1

         continue

      else:

         lineNumber += 1
         continue

   return chunkUrls
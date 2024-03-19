import requests
from urllib.parse import urlparse
import os.path

import session

# m3u8 type
def get_m3u8_type(url : str) -> str:
    
    # download file
    r = requests.get(url, allow_redirects = True).content
    open("downloads/temp.m3u8", "wb").write(r)

    # get file name and path
    a = urlparse(url)
    session.fileName = (os.path.basename(a.path))
    session.pathName = (os.path.dirname(session.url))

    m3u8 = open("downloads/temp.m3u8", "r")

    if "#EXTM3U" in m3u8:

        if "#EXTINF" in m3u8:

            if "#EXT-X-ENDLIST" in m3u8: return "vod"
            
            else: return "live"
                 
        else: return "playlist"

    else: return "notm3u8"
# session
sessionStatus = False
userId : str

# url
url : str 
fileName : str
pathName : str
fileExtension : str

# bot notification message Id
downloadStatus : int
segCount = 0
segsDownloaded = 0
videoParts = 1

def close_session():
    
    # session
    sessionStatus = False
    userId = ""
    
   # funcs.queue.remove(funcs.queue[0])
   # funcs.queue_users.remove(funcs.queue_users[0])
    
    # url
    url = ""
    fileName = ""
    pathName = ""
    fileExtention = ""

    downloadStatus = 0
    segCount = 0
    segsDownloaded = 0
    videoParts = 1

    
    # # segments   
    # try: # close output video if opened
    #     video = open("segments/output"+str(funcs.file_extention), "rb") 
    #     video.close() 
    #     pass
    # except:
    #     pass
    
    # # remove all
    # try:
    #     for f in glob.glob("segments/*"):
    #         os.remove(f) 
    # except:
    #     pass

    # # temp m3u8
    # open("temp.m3u8", "w").close() 
    # return 0
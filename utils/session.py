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

def close_session():

    sessionStatus = False
    
   # funcs.queue.remove(funcs.queue[0])
   # funcs.queue_users.remove(funcs.queue_users[0])
    
    url = ""
    pathName = ""
    pathName = ""
    fileExtention = ""

    downloadStatus = 0

    
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
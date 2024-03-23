# admin id
adminId = "6334791136"

# queue urls
queue = {}
queueUsers = []

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
finished = False # Used for live

# close session and reset data
def close_session():

    # remove current user
    if len(queueUsers) > 0:
        tempId = queueUsers[0]
        queue.pop(tempId)
        queueUsers.remove(tempId)
    
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
    finished = False
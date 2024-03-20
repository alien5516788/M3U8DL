import bot_config
import funcs as funcs

bot = bot_config.bot 

segments = int() # number of segmenets
segment_number = 0 # segment number


def status_bar_vod():
    # edit message
    bot.edit_message_text(chat_id = funcs.user_id, text = "Downloading "+ str(segment_number)+" of "+str(segments),  message_id = funcs.edit_message_id )
    return 0

def status_bar_live():
    # edit message
    bot.edit_message_text(chat_id = funcs.user_id, text = "Recording live " + str(segment_number)+" of ?",  message_id = funcs.edit_message_id )
    return 0
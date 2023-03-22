#!/usr/bin/env python
# coding: utf-8

# In[ ]:


from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import pandas as pd


df = pd.read_excel(r'~/Dropbox/quantum/data/All_data_1.xlsx', sheet_name = 'List_data')
videoid_list = df['VideoID'].tolist()
title_list = df['Title'].tolist()
speaker_list = df['Speaker'].tolist()
place_list = df['Place'].tolist()
Year_list = df['Year'].tolist()
Nr_list = df['Number'].tolist()



for nr, videoId, title, speaker, place, year in zip(Nr_list, videoid_list,title_list, speaker_list, place_list, Year_list):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(videoId)
        formatter = TextFormatter()
        text_formatted = formatter.format_transcript(transcript)
        path = r'~/Dropbox/quantum/data/Try_Transcripts'
        file_name = str(videoId)
        print(file_name)
        with open(path+'/'+str(nr) + '.' + file_name+'.txt', 'w', encoding='utf-8') as txt_file:
            txt_file.write(title + '\n' + speaker + ', ' + place + ', ' + str(year) + '\n')
            txt_file.writelines(text_formatted)
    except:
        path = r'~/Dropbox/quantum/data/Try_Transcripts'
        file_name = str(videoId)
        with open(path+'/'+str(nr)+ '.' + file_name+'.txt', 'w', encoding='utf-8') as txt_file:
            txt_file.write(title + '\n' + speaker + ', ' + place + ', ' + str(year) + '\n')
            txt_file.writelines("TranscriptsDisabled")


# In[ ]:





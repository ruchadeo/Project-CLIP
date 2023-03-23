#!/usr/bin/env python
# coding: utf-8

# In[9]:


import os
import math
import cv2
import pytube as pyt
import time
from datetime import timedelta
import numpy as np
#Needs ffmpeg for audio, I think you can add that to AWS directly, if not just zip executable I think


# In[15]:


class YoutubePlaylist:
    """class with all the code, initialize with the playlist link, a name,and a folderpath,  as str"""
    def __init__(self,link,name,MainFolder):
        self.Playlist=pyt.Playlist(link)
        self.name=name
        self.streams=[]
        self.MainFolder=MainFolder
        self.mp4folder=None
        self.mp4names=[]
        self.fps=[]
        self.videonames=[]
        self.FrameFolder=None
        self.AudioFolder=None
        if not os.path.exists(self.MainFolder):
            os.mkdir(self.MainFolder)
    #run playlist_download before anything else

    def playlist_download(self,mp4folder='/mp4',start=0,stop=None):
        """Downloads all videos from the linked playlist to a folder Defined by mp4folder. name is for the file names"""
        if not os.path.exists(self.MainFolder+mp4folder):
            os.mkdir(self.MainFolder+mp4folder)
        self.mp4folder=mp4folder
        for number, video in enumerate(self.Playlist.videos[start:stop]):
            self.streams.append(video.streams.filter(file_extension='mp4').first())
            self.mp4names.append(f'{self.name}_video{number}.mp4') 
            self.streams[number].download(self.MainFolder+mp4folder,filename=f'{self.name}_video{number}.mp4') #downloads mp4 to folder 
            self.fps.append(self.streams[number].fps)
        self.videonames.append(video.title)
        

    def frame(self,videonumber,time,FrameFolder='/Frames'):
        """downloads single frame from a video. Inputs video number from the playlist, and time in the video in seconds.
        This is mainly for convenience/troubleshooting, should probably just get from whole playlist at once"""
        self.FrameFolder=FrameFolder #be consistent with FrameFolder between functions, didn't think that through
        if not os.path.exists(self.MainFolder+self.FrameFolder):
            os.mkdir(self.MainFolder+self.FrameFolder)
        cam = cv2.VideoCapture(self.MainFolder+self.mp4folder+'/'+self.mp4names[videonumber])
        maxframes=cam.get(7)
        frame_viewed=math.floor(time*self.fps[videonumber])
        if frame_viewed>maxframes:
            print ("max frames exceeded")
        cam.set(1, frame_viewed)
        ret,frame = cam.read()
        filename=f'/{self.name}_video{videonumber}_frame{frame_viewed}.jpg'
        cv2.imwrite(self.MainFolder+FrameFolder+filename,frame) #might be better format than jpg
        
    def bunch_frame(self,videonumber,times,FrameFolder='/Frames'):
        """same as frame_download_video but takes in list for times (in secodns) instead. Could easily combine them but too lazy now"""
        self.FrameFolder=FrameFolder
        for time in times:
            self.frame(videonumber,time,FrameFolder)
            
    def playlist_frame(self,timestep=5,FrameFolder='/Frames'):
        """downloads frames from each video in playlist at every time step, input timestep and FrameFolder"""
        for videonumber in range(np.size(self.streams)):
            cam = cv2.VideoCapture(self.MainFolder+self.mp4folder+'/'+self.mp4names[videonumber])
            maxtime=cam.get(7)/self.fps[videonumber]
            times=np.arange(0,maxtime,timestep)
            self.bunch_frame(videonumber,times,FrameFolder)
            
    def sound(self,videonumber,timestart,timestop,AudioFolder='/Audio'):
        """Takes videonumber, timestart and stop in seconds, AudioFolder, downloads that as wav"""
        self.AudioFolder=AudioFolder
        source=self.MainFolder+self.mp4folder+'/'+self.mp4names[videonumber]
        cam = cv2.VideoCapture(source)
        maxtime=cam.get(7)/self.fps[videonumber]
        if not os.path.exists(self.MainFolder+AudioFolder):
            os.mkdir(self.MainFolder+AudioFolder)
        start=str(timedelta(seconds=int(timestart)))
        stop= str(timedelta(seconds=int(timestop)))
        if timestop>maxtime:
            print("max time exceeded")
        else:
            audioname=self.MainFolder+AudioFolder+f'/{self.name}_video{videonumber}_Audio{timestart*self.fps[videonumber]}.wav'
            command=' ffmpeg -y -ss {} -t {} -i {} -ac 2 -f wav {}'.format(start,stop,source,audioname)
            os.system(command)
    def bunch_sound(self,videonumber,timegap=600,timelength=5,starttrim=0,endtrim=0,AudioFolder='/Audio'):
        """Downloads wav of length timelength every timegap from videonumber,can trim off start and end, use integers to be safe idk"""
        source=self.MainFolder+self.mp4folder+'/'+self.mp4names[videonumber]
        cam = cv2.VideoCapture(source)
        maxtime=cam.get(7)/self.fps[videonumber]
        for timestart in range(int(starttrim),int(maxtime-endtrim-timelength-1),int(timegap)):
            self.sound(videonumber,timestart,timestart+timelength,AudioFolder=AudioFolder)
    def playlist_sound(self,timegap=600,timelength=5,starttrim=0,endtrim=0,AudioFolder='/Audio'):
        """"Does what bunch_sound does except interated through every video"""
        parameters=(timegap,timelength,starttrim,endtrim,AudioFolder)
        for videonumber in range(np.size(self.streams)):
            self.bunch_sound(videonumber,*parameters)
        
        


# In[16]:


link='https://www.youtube.com/playlist?list=PL2A6N-SGDadzGkyg8kjFaHW1zSZbp-NiX'
Thing=YoutubePlaylist(link,'Animal','./Animal') #put playlist link, animal or whatever name, then path to put everything
Thing.playlist_download(start=2,stop=4) #Downloads everything, get rid of the start and stop when actually doing it
print('download done')
Thing.playlist_frame(timestep=600) #Downloads frame from every video from every timestep.
print('frame done')
#Puts it in a folder inside the main folder. Default is 5 seconds a a folder called /Audio
Thing.playlist_sound() #downloads the sounds from every video at a set time interval and time length. 
print('audio done')
#default is 10 minute time intervals of length 5 seconds


#!/usr/bin/env python

import threading
import time
import os
import sys
import signal

#Write First thread of creating raw file
class ThreadCreateFile (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        #set Dump environment variable
        os.environ["cameraDump"] = "1"
        #Delete all file in the sourcepng
        os.system('rm -rf ./sourcePng/*')
        print("[INFO-thread1]:Delete all file in sourcePng")

        #create directory of handlePng
        os.system('mkdir ./sourcePng/handlePng')
        print("[INFO-thread1]:Create Dir of ./sourcePng/handlePng")

        #change dir
        os.chdir("./sourcePng")
        print("[INFO-thread1]: Change Dir to ./sourcePng")
        global startHandleFlag
        startHandleFlag = 1
        print("[INFO-thread1]: Start Create File")
        os.system('gst-launch-1.0 icamerasrc device-name=imx185  scene-mode=2 ! fakesink >/dev/null')
        global endHandleFlag
        endHandleFlag = 0
        print("[INFO-thread1]: End!")
        # os.system('gst-launch-1.0 icamerasrc device-name=imx185  scene-mode=2 ! fakesink')

#Write Second thread of handle raw file to png file
class ThreadHandleRawFileToPng (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        #wait for thread one ready
        global startHandleFlag
        while not startHandleFlag:
            print("[INFO-thread2]: Wait for starting")
            time.sleep(1)
        i=0
        # wait thread1 create some file
        time.sleep(2)
        global endHandleFlag
        #Get the lastest file need handle
        while endHandleFlag:
            # print(endHandleFlag)
            global copyFlag
            copyFlag = 1
            #get filename and cp
            p = os.popen('ls *.GRBG12V32 |tail -n 2 | head -n 1')
            filename=p.read()
            filename=filename[:-1]
            command="cp ./"+filename+" ./handlePng/handlePng.raw"
            print("[INFO-thread2]: Get the New file need be handled name:", filename)
            # print(command)
            os.system(command)
            print("[INFO-thread2]: Copy file need be handled to ./handlePng")
            copyFlag = 0
            #use binary to preprocess file
            command="../raw2vec bd 1920 1088  ./handlePng/handlePng.raw ./handlePng/readyHandlePng.raw"
            print("[INFO-thread2]: Converted raw file by raw2vec")
            os.system(command)
            #use pythonfile to handle file
            print("[INFO-thread2]: Start converting raw file by python script....")
            command="python ../classification_sample_liz_png.py -i ./handlePng/readyHandlePng.raw -m ../DTTC2019/ispmodel/frozen_graph_DepthToSpace-hwc.xml>/dev/null"
            os.system(command)
            print("[INFO-thread2]: Converted raw file success by python script ")
            # i=i+1
            # command="mv ./created.png ./handlePng/created"+str(i)+".png"
            command="mv ./created.png ./handlePng/"
            # print(command)
            os.system(command)
            global thread3StartHandleFlag
            thread3StartHandleFlag = 1
            print("[INFO-thread2]: Copyed png to handlePng ")
        print("[INFO-thread2]: End! ")

#Write third thread of show png
class ThreadShowPng (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        global thread3StartHandleFlag
        while not thread3StartHandleFlag:
            print("[INFO-thread3]: Wait for starting")
            time.sleep(1)
        os.system("../a.out >>/dev/null")
        print("[INFO-thread3]: End! ")

#Write forth thread of delete raw
class ThreadDeletePng (threading.Thread):
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):
        global copyFlag
        #This thread will start when thread3 begin
        global thread3StartHandleFlag
        while not thread3StartHandleFlag:
            print("[INFO-thread4]: Wait for starting")
            time.sleep(1)
        while endHandleFlag:
            print("[INFO-thread4]: CopyFlag= ", copyFlag)
            if not copyFlag:
                p = os.popen('ls *.GRBG12V32')
                fileNameList=p.read()
                # fileNameList.replace("\n"," ")
                fileNameList = fileNameList.replace('\n',' ')
                command="rm -f " + fileNameList
                # print("[INFO-thread2]:",command)
                #Delete all file all .GRBG12V32 file
                print("[INFO-thread4]: Deleting all raw file in sourcePng")
                os.system(command)
                print("[INFO-thread4]: Deleted all raw file in sourcePng")
            time.sleep(3)
        print("[INFO-thread4]: End! ")

def quit(signum, frame):
        # global endHandleFlag
        # endHandleFlag = 0
        # print(endHandleFlag)
        print('You choose to stop me')
        sys.exit()

exitFlag = 0
startHandleFlag = 0
thread3StartHandleFlag = 0
endHandleFlag = 1
copyFlag = 0;
if __name__ == '__main__':
    #set signal to stop all thread
    signal.signal(signal.SIGINT, quit)
    signal.signal(signal.SIGTERM, quit)

    thread1 = ThreadCreateFile(1, "Thread-1", 1)
    thread2 = ThreadHandleRawFileToPng(2, "Thread-2", 2)
    thread3 = ThreadShowPng(3, "Thread-3", 3)
    thread4 = ThreadDeletePng(4, "Thread-4", 4)

    thread1.setDaemon(True)
    thread1.start()
    thread2.setDaemon(True)
    thread2.start()
    thread3.setDaemon(True)
    thread3.start()
    thread4.setDaemon(True)
    thread4.start()
    thread1.join()
    thread2.join()
    thread3.join()
    thread4.join()
    print("[mainThread] Removing all dumped file.....")
    os.system("rm *.GRBG12V32")
    print("[mainThread] exit the main thread!")

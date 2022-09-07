from inspect import isroutine
import os
import sys
from time import time, sleep, mktime
from datetime import datetime, timedelta
import logging
from tkinter import *
from tkinter import messagebox
from picamera import PiCamera, Color

HOURS = 5 # tiempo de ejecucion total
MINUTES = HOURS * 60
MINUTES = 1
PERIOD = 15 # tiempo entre cada foto en segundos
PATH = '/home/pi/Pictures'
#LOG_FORMAT = '[%(asctime)s][%(levelname)-5s] %(name) 15s: %(message)s'
LOG_FORMAT = '[%(asctime)s][%(levelname)-5s]: %(message)s'

logFileName = PATH + '/timelapse_' + datetime.now().strftime('%Y%m%d') + '.log'

logging.basicConfig(
    format = LOG_FORMAT,
    level = logging.INFO,
    filename = logFileName,
    filemode = 'a',
    #encoding = 'utf-8'
)

if logging.getLogger('').hasHandlers():
    logging.getLogger('').handlers.clear()

# Handler nivel debug con salida a fichero
fileInfoHandler = logging.FileHandler(logFileName)
fileInfoHandler.setLevel(logging.INFO)
fileInfoFormat = logging.Formatter(LOG_FORMAT)
fileInfoHandler.setFormatter(fileInfoFormat)
logging.getLogger('').addHandler(fileInfoHandler)

# Handler nivel info con salida a consola
consoleHandler = logging.StreamHandler()
consoleHandler.setLevel(logging.INFO)
#consoleHandlerFormat = logging.Formatter('%(asctime)s-%(name)s-%(levelname)s-%(message)s')
#consoleHandler.setFormatter(consoleHandlerFormat)
logging.getLogger('').addHandler(consoleHandler)

camera = PiCamera()
camera.rotation = 180
#camera.resolution = (1920, 1080) # 1080p, Full HD, FHD
camera.resolution = (2592, 1944) # MAX
camera.framerate = 15
camera.start_preview()
#camera.image_effect = 'negative'
sleep(2)
logging.info('Camara iniciada')

finalPath = PATH + '/timelapse_' + datetime.now().strftime('%Y%m%d')
if not os.path.exists(finalPath):
    logging.info("Folder created: {}".format(finalPath))
    os.makedirs(finalPath)

text = ""
timeTillDestroy = 10

isRunning = False

def startTimeLapse():
    global isRunning
    isRunning = True

    logging.info("Starting TimeLapse, until {} hours ({} minutes)".format(HOURS,MINUTES))

    currentDateTime = datetime.now()
    logging.info("Start date:\t{}".format(currentDateTime))
    currentDateTime += timedelta(seconds=10)
    currentDateTime -= timedelta(seconds=currentDateTime.second % 10,
                            microseconds=currentDateTime.microsecond)
    logging.info("Real start date:\t{}".format(currentDateTime))
    #hours_added = timedelta(hours = HORAS)
    hoursToAdd = timedelta(minutes = MINUTES)
    futureDateTime = currentDateTime + hoursToAdd
    logging.info("Fecha fin:\t{}".format(futureDateTime))

    logging.info("")
    logging.info("Number of pictures:\t{:d}".format(int(MINUTES*(60/PERIOD))))

    nextTime = mktime(currentDateTime.timetuple())
    sleepTime = nextTime - time()
    if sleepTime > 0:
        sleep(sleepTime)

    picCount = 0
    while datetime.now() <= futureDateTime:
        picCount += 1

        if not('nextTime' in locals()):
            nextTime = time()

        picName = "{}/{}.jpg".format(finalPath,datetime.now().strftime("%d%m%y_%H%M%S"))
        #print("Capturando imagen {} - {} - {}".format(picCount,datetime.now(),picName))
        logging.info("Capturing picture {} - {}".format(picCount,picName))

        # opcion 1
        #os.system("raspistill -o " + str(picName))
        #os.system("raspistill -w " + str(imgWidth) + " -h " + str(imgHeight) + " -o " + str(picName) + "  -sh 40 -awb auto -mm average -v")

        # opcion 2
        #os.system("fswebcam -i 0 -d /dev/video0 -r 640x480 -p YUYV -q --title @MartinY --no-banner " + picName)
        #os.system("fswebcam -i 0 -d /dev/video0 -r 1280x720 -p YUYV -q --title @MartinY --no-banner " + picName)

        # opcion 3
        camera.capture(picName)

        # terminar antes
        endFile = "{}/FIN".format(finalPath)
        if (os.path.exists(endFile)):
            logging.info('Finish by FIN file')
            os.remove(endFile)
            break

        #sleep(PERIODO)
        nextTime += PERIOD
        sleepTime = nextTime - time()
        if sleepTime > 0:
            sleep(sleepTime)

    logging.info("Finish TimeLapse")

    return

def stopTimeLapse():
    global isRunning
    isRunning = False
    text = 'stoptimelapse'
    print(text)
    return

def exitTimeLapse():
    global isRunning
    if isRunning:
        messagebox.showinfo("Information", "You can't get out without stopping first")
    else:
        mainWindow.quit()
        mainWindow.destroy()
        camera.stop_preview()
        camera.close()
    return

def aboutTimeLapse():
    messagebox.showinfo("About", "TimeLapseGUI v0.1")

codePath = os.path.dirname(__file__)

mainWindow = Tk()
mainWindow.title('TimeLapseGUI')
mainWindow.iconphoto(False, PhotoImage(file = f'{codePath}\camera_small.png'))
#mainWindow.geometry('400x200')
mainWindow.resizable(width = False, height = False)
mainWindow.protocol("WM_DELETE_WINDOW", exitTimeLapse)
mainWindow.bind('<Escape>', lambda e: exitTimeLapse())

menubar = Menu(mainWindow)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label = "About", command = aboutTimeLapse)
filemenu.add_command(label = "Exit", command = exitTimeLapse)
menubar.add_cascade(label = "File", menu = filemenu)
#mainWindow.config(menu = menubar)

Button(mainWindow, text = 'Start', command = startTimeLapse, width = 20).grid(row = 0, column = 0)
Button(mainWindow, text = 'Stop', command = stopTimeLapse, width = 20).grid(row = 0, column = 1)
Button(mainWindow, text = 'Exit', command = exitTimeLapse, width = 20).grid(row = 1, column = 0, columnspan = 2)

Label(mainWindow, text = 'Python version:').grid(row = 2, column = 0, sticky = W)
Label(mainWindow, text = sys.version_info, relief = 'sunken').grid(row = 2, column = 1, sticky = W)

#Label(mainWindow,text=f'Self time out GUI\nGUI will close in {timeTillDestroy} seconds').pack(side=TOP,padx=10,pady=10)
#Label(mainWindow,text='Or the GUI will time out on input').pack(side=TOP,padx=10,pady=10)

text = ''
entry = Entry(mainWindow, width = 50)
#entry.pack(side = TOP, padx = 10, pady = 10)

#mainWindow.after(timeTillDestroy*1000, lambda: mainWindow.destroy()) # Destroy the widget after (time) seconds
mainWindow.mainloop()

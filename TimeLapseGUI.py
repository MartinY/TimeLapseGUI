import os
import sys
from time import time, sleep, mktime
from datetime import datetime, timedelta
import logging
import socket
from tkinter import *
from tkinter import messagebox
from picamera import PiCamera, Color

HOURS = 5 # tiempo de ejecucion total
MINUTES = HOURS * 60
MINUTES = 1
PATH = '/home/pi/Pictures'
#LOG_FORMAT = '[%(asctime)s][%(levelname)-5s] %(name) 15s: %(message)s'
LOG_FORMAT = '[%(asctime)s][%(levelname)-5s]: %(message)s'

logFileName = PATH + '/timelapse_' + datetime.now().strftime('%Y%m%d') + '.log'

logFileExist = False
if os.path.exists(logFileName):
    logFileExist = True  

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

if logFileExist:
    logging.info('================================================================================')

logging.info("Log file: {}".format(logFileName))
logging.info("User: {} - Machine: {}".format(os.getlogin(),socket.gethostname()))

camera = PiCamera()
camera.rotation = 180
#camera.resolution = (1920, 1080) # 1080p, Full HD, FHD
camera.resolution = (2592, 1944) # MAX
camera.framerate = 15
camera.start_preview()
#camera.image_effect = 'negative'
sleep(2)
logging.info('Camera started')

isRunning = False
finalPath = ''

def startTimeLapse():
    global isRunning, finalPath

    strPeriod = period.get()
    if strPeriod is '':
        messagebox.showerror('ERROR: Period', 'Period undefined')
        return
    else:
        intPeriod = int(strPeriod)

    isRunning = True

    finalPath = PATH + '/timelapse_' + datetime.now().strftime('%Y%m%d')
    if not os.path.exists(finalPath):
        logging.info("Folder created: {}".format(finalPath))
        os.makedirs(finalPath)

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
    logging.info("End date:\t{}".format(futureDateTime))

    #logging.info("")
    logging.info("Number of pictures: {:d} - Period: {}".format(int(MINUTES*(60/intPeriod)), intPeriod))

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

        nextTime += intPeriod
        sleepTime = nextTime - time()
        if sleepTime > 0:
            sleep(sleepTime)

    logging.info("Finish TimeLapse")

    isRunning = False

    return

def stopTimeLapse():
    if isRunning:
        endFile = finalPath + '/FIN'
        if not os.path.exists(endFile):
            with open(endFile, 'a'):
                os.utime(endFile, None)
            logging.info("FIN file created: {}".format(endFile))
        else:
            messagebox.showinfo("Information", "FIN file already exists: {}".format(endFile))
    else:
        messagebox.showinfo("Information", "You can't stop it if it's not running")
    return

def exitTimeLapse():
    if isRunning:
        messagebox.showinfo("Information", "You can't get out without stopping first")
    else:
        mainWindow.quit()
        mainWindow.destroy()
        camera.stop_preview()
        camera.close()
        logging.info('Camera stoped')
    return

def aboutTimeLapse():
    messagebox.showinfo("About", "TimeLapseGUI v0.1")

def validateNumber(strNum):
    if strNum.isdigit() or strNum is '':
        return True
    else:
        return False

codePath = os.path.dirname(__file__)
iconPath = codePath + '/camera_small.png'

mainWindow = Tk()
mainWindow.title('TimeLapseGUI')
mainWindow.iconphoto(False, PhotoImage(file = iconPath))
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

Label(mainWindow, text = 'Period(s):').grid(row = 0, column = 0, sticky = W)
period = Entry(mainWindow, width = 5)
period.insert(0, '15')
period.grid(row = 0, column = 1, sticky = W)
validateNumberReg = mainWindow.register(validateNumber)
period.config(validate = 'key', validatecommand = (validateNumberReg, '%P'))

Button(mainWindow, text = 'Start', command = startTimeLapse, width = 20).grid(row = 1, column = 0)
Button(mainWindow, text = 'Stop', command = stopTimeLapse, width = 20).grid(row = 1, column = 1)
Button(mainWindow, text = 'Exit', command = exitTimeLapse, width = 20).grid(row = 2, column = 0, columnspan = 2)

Label(mainWindow, text = 'Python version:').grid(row = 3, column = 0, sticky = W)
Label(mainWindow, text = sys.version_info, relief = 'sunken').grid(row = 3, column = 1, sticky = W)

#mainWindow.after(timeTillDestroy*1000, lambda: mainWindow.destroy()) # Destroy the widget after (time) seconds
mainWindow.mainloop()

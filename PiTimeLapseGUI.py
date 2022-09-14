import os
import sys
from time import time, sleep, mktime
from datetime import datetime, timedelta
import logging
import socket
from tkinter import *
from tkinter import messagebox, ttk, filedialog
import threading
from picamera import PiCamera, Color

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
    global isRunning, finalPath, lastPath, lastPic

    strPeriod = period.get()
    if strPeriod == '':
        messagebox.showerror('ERROR: Period', 'Period undefined')
        return
    else:
        intPeriod = int(strPeriod)
    
    strDuration = duration.get()
    if strDuration == '':
        messagebox.showerror('ERROR: Duration', 'Duration undefined')
        return
    else:
        intDuration = int(strDuration)
        
    strDurationCombo = durationCombo.get()
    if strDurationCombo == 'hours':
        intDuration *= 60

    strPicsPath = picsPath.cget("text")
    if strPicsPath == '':
        messagebox.showerror('ERROR: Path', 'Path undefined')
        return

    isRunning = True

    finalPath = strPicsPath + '/timelapse_' + datetime.now().strftime('%Y%m%d')
    if not os.path.exists(finalPath):
        logging.info("Folder created: {}".format(finalPath))
        os.makedirs(finalPath)

    lastPath.config(text = (finalPath.split(strPicsPath)[1]))

    logging.info('Start TimeLapse')

    currentDateTime = datetime.now()
    logging.info("Start date:\t{}".format(currentDateTime))
    startDateTime = currentDateTime + timedelta(seconds = 5)
    startDateTime -= timedelta(seconds = startDateTime.second % 5, microseconds = startDateTime.microsecond)
    logging.info("Real start date:\t{}".format(startDateTime))
    timeToAdd = timedelta(minutes = intDuration)
    endDateTime = startDateTime + timeToAdd
    logging.info("End date:\t{}".format(endDateTime))

    #logging.info("")
    logging.info("Number of pictures: {:d} - Duration(m): {} - Period(s): {}".format(int(intDuration*(60/intPeriod)), intDuration, intPeriod))

    nextTime = mktime(startDateTime.timetuple())
    sleepTime = nextTime - time()
    if sleepTime > 0:
        sleep(sleepTime)

    picCount = 0
    while datetime.now() <= endDateTime:
        picCount += 1

        #if not('nextTime' in locals()):
        #    nextTime = time()

        picFile = "{}/{}.jpg".format(finalPath,datetime.now().strftime("%d%m%y_%H%M%S"))
        #print("Capturing picture {} - {} - {}".format(picCount,datetime.now(),picFile))
        logging.info("Capturing picture {} - {}".format(picCount, picFile))

        # opcion 1
        #os.system("raspistill -o " + str(picFile))
        #os.system("raspistill -w " + str(imgWidth) + " -h " + str(imgHeight) + " -o " + str(picFile) + "  -sh 40 -awb auto -mm average -v")

        # opcion 2
        #os.system("fswebcam -i 0 -d /dev/video0 -r 640x480 -p YUYV -q --title @MartinY --no-banner " + picFile)
        #os.system("fswebcam -i 0 -d /dev/video0 -r 1280x720 -p YUYV -q --title @MartinY --no-banner " + picFile)

        # opcion 3
        camera.capture(picFile)

        lastPicFile = picFile.split(finalPath)[1]
        lastPic.config(text = lastPicFile)

        # finish by FIN file
        endFile = "{}/FIN".format(finalPath)
        if (os.path.exists(endFile)):
            isRunning = False
            lastPath.config(text = '')
            lastPic.config(text = '')
            logging.info('Finish by FIN file')
            os.remove(endFile)
            break

        nextTime += intPeriod
        
        if mktime(endDateTime.timetuple()) <= nextTime:
            isRunning = False
            lastPath.config(text = '')
            lastPic.config(text = '')
            break
        
        sleepTime = nextTime - time()
        if sleepTime > 0:
            sleep(sleepTime)

    logging.info('Finish TimeLapse')

    isRunning = False
    lastPath.config(text = '')
    lastPic.config(text = '')

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
    messagebox.showinfo("About", f"TimeLapseGUI v0.1\nPython version: {sys.version}")

def validateNumber(strNum):
    if strNum.isdigit() or strNum == '':
        return True
    else:
        return False

def selectPicsPath():
    global picsPath

    selectedPicsPath = filedialog.askdirectory(initialdir = PATH, title = "Select folder")
    picsPath.config(text = selectedPicsPath)
    logging.info(f"Selected path: {selectedPicsPath}")

#codePath = os.path.dirname(__file__)
codePath = os.path.dirname(os.path.realpath(__file__))
iconPath = codePath + '/camera_small.png'

mainWindow = Tk()
mainWindow.title('TimeLapseGUI')
mainWindow.iconphoto(False, PhotoImage(file = iconPath))
#mainWindow.geometry('400x200')
mainWindow.resizable(width = False, height = False)
mainWindow.protocol("WM_DELETE_WINDOW", exitTimeLapse)
mainWindow.bind('<Escape>', lambda e: exitTimeLapse())

menubar = Menu(mainWindow)
filemenu = Menu(menubar, tearoff = 0)
filemenu.add_command(label = "About", command = aboutTimeLapse)
filemenu.add_command(label = "Exit", command = exitTimeLapse)
menubar.add_cascade(label = "File", menu = filemenu)
#mainWindow.config(menu = menubar)

validateNumberReg = mainWindow.register(validateNumber)

Button(mainWindow, text = 'Path:', command = selectPicsPath, width = 15, anchor = W).grid(row = 0, column = 0, sticky = W)
picsPath = Label(mainWindow, text = PATH, relief = 'sunken', width = 17, anchor = W)
picsPath.grid(row = 0, column = 1, sticky = W)

Label(mainWindow, text = 'Duration:').grid(row = 1, column = 0, sticky = W)
duration = Entry(mainWindow, width = 5)
duration.insert(0, '1')
duration.grid(row = 1, column = 1, sticky = W)
duration.config(validate = 'key', validatecommand = (validateNumberReg, '%P'))
durationCombo = ttk.Combobox(state = 'readonly', values = ['minutes', 'hours'], width = 10)
durationCombo.grid(row = 1, column = 1, sticky = E)
durationCombo.current(0)

Label(mainWindow, text = 'Period(s):').grid(row = 2, column = 0, sticky = W)
period = Entry(mainWindow, width = 5)
period.insert(0, '15')
period.grid(row = 2, column = 1, sticky = W)
period.config(validate = 'key', validatecommand = (validateNumberReg, '%P'))

Button(mainWindow, text = 'Start', command = lambda: threading.Thread(target = startTimeLapse).start(), width = 15).grid(row = 3, column = 0)
Button(mainWindow, text = 'Stop', command = lambda: threading.Thread(target = stopTimeLapse).start(), width = 15).grid(row = 3, column = 1)

Label(mainWindow, text = 'TimeLapse Path:').grid(row = 4, column = 0, sticky = W)
lastPath = Label(mainWindow, text = '', relief = 'sunken', width = 17, anchor = W)
lastPath.grid(row = 4, column = 1, sticky = W)
Label(mainWindow, text = 'Last Pic:').grid(row = 5, column = 0, sticky = W)
lastPic = Label(mainWindow, text = '', relief = 'sunken', width = 17, anchor = W)
lastPic.grid(row = 5, column = 1, sticky = W)

Button(mainWindow, text = 'Exit', command = exitTimeLapse, width = 15).grid(row = 6, column = 0, columnspan = 2)

#mainWindow.after(timeTillDestroy*1000, lambda: mainWindow.destroy()) # Destroy the widget after (time) seconds
mainWindow.mainloop()

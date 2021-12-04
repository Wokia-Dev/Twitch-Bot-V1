from ast import literal_eval
from configparser import ConfigParser
from datetime import datetime, timedelta
from os import path, system, listdir, remove
from random import randrange
from shutil import move
from subprocess import Popen
from time import sleep

from art import text2art
from colorama import Fore, Style
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from twitchAPI import Twitch
from undetected_chromedriver import Chrome

# config parser
config = ConfigParser()
config.read('config.ini')

# get value of config file

# TOKEN
CLIENT_ID = config.get('TOKEN', 'CLIENT_ID')
SECRET_CLIENT = config.get('TOKEN', 'SECRET_CLIENT')

# CLIPS
STREAMERS_LIST = literal_eval(config.get('CLIPS', 'STREAMERS_LIST'))
HASHTAG_LIST = config.get('CLIPS', 'HASHTAG_LIST')
HASHTAG_LIST = HASHTAG_LIST.replace("'", '')

# CONFIG
DEFAULT_DAYS_INTERVAL = config.getint('CONFIG', 'DEFAULT_DAYS_INTERVAL')
NUMBER_CLIPS_REQ = config.getint('CONFIG', 'NUMBER_CLIPS_REQ')
USE_STREAMLADDER = config.get('CONFIG', 'USE_STREAMLADDER')
VIDEO_PATH = config.get('CONFIG', 'VIDEO_PATH')
CHROME_USER_DATA = config.get('CONFIG', 'CHROME_USER_DATA')

# twitch api
twitch = Twitch(CLIENT_ID, SECRET_CLIENT)


# ASCII text
def TitlePrint():
    print(Fore.GREEN + text2art("TTB By Wokia", font='sub-zero'))
    print('V: 1.0')
    print(Style.RESET_ALL)


TitlePrint()

# select streamers
indexChoose = ''
finishSelect = False

while not finishSelect:
    # clear and print title
    system('cls')
    TitlePrint()
    print(Fore.CYAN + '*' * 112, '\n')
    # print all streamers
    i = 0
    for streamers in STREAMERS_LIST:
        print(i, ' | ', streamers)
        i = i + 1
    print('\n')
    # ask
    indexChoose = input(Fore.GREEN + 'Select streamers, type all for random select \n')
    # check if is None
    if indexChoose is None:
        finishSelect = False
    # check if is all
    elif str(indexChoose) == 'all':
        finishSelect = True
    # check if select is in streamers list range
    elif indexChoose.isdigit():
        for i in range(0, len(STREAMERS_LIST)):
            if int(indexChoose) == i:
                finishSelect = True

# get streamers id
streamersListId = []
print('\n')
print(Fore.CYAN + '*' * 112, '\n')
# if all select
if indexChoose == 'all':
    indexGetId = 1
    # get ids for all streamers
    for streamer in STREAMERS_LIST:
        # print advancement
        print(Fore.GREEN + str(indexGetId) + '/' + str(len(STREAMERS_LIST)) + ' get ' + streamer + ' id')
        # request api
        responseId = [twitch.get_users(logins=streamer)]
        # append id api response at streamersListId
        for item in responseId:
            data = item['data']
            for a in data:
                streamersListId.append(a['id'])

        indexGetId = indexGetId + 1
    print(Fore.GREEN + '\nFinish')

# if only one is select
else:
    # print advancement
    print(Fore.GREEN + 'get', STREAMERS_LIST[int(indexChoose)], 'id')
    # request api
    responseId = [twitch.get_users(logins=STREAMERS_LIST[int(indexChoose)])]
    # append the streamer id api response at streamersListId
    for item in responseId:
        data = item['data']
        for a in data:
            streamersListId.append(a['id'])

    print(Fore.GREEN + '\nFinish')

# select date interval
daysInterval = 0
inputInterval = None
finishSelect = False
print('\n')
print(Fore.CYAN + '*' * 112, '\n')
while not finishSelect:
    # ask days interval
    inputInterval = input(Fore.GREEN + 'Select date interval (in days) for clips selection default: ' +
                          str(DEFAULT_DAYS_INTERVAL) + ' days (just press enter for default)\n')
    if len(inputInterval) <= 0 or inputInterval.isdigit():
        finishSelect = True
    else:
        finishSelect = False

# if none select interval = default value
if len(inputInterval) <= 0:
    daysInterval = DEFAULT_DAYS_INTERVAL
# else days interval = input
else:
    daysInterval = int(inputInterval)

# request clips
clipsResponse = None
clipsUrl = []
streamerName = ''
now = datetime.now()
timeResult = now - timedelta(days=daysInterval)
# final start and end time
endDate = datetime(int(now.year), int(now.month), int(now.day))
startDate = datetime(int(timeResult.year), int(timeResult.month), int(timeResult.day))
# only one streamers
if len(streamersListId) <= 1:
    clipsResponse = [twitch.get_clips(broadcaster_id=streamersListId[0], first=NUMBER_CLIPS_REQ,
                                      started_at=startDate, ended_at=endDate)]
    nbClips = 0
    # read api response
    for clip in clipsResponse:
        data = clip['data']
        for i in data:
            nbClips = nbClips + 1
            streamerName = i['broadcaster_name']
            # add url clips in clipsUrl
            clipsUrl.append(i['url'])
    # print nb of clips and streamer name
    print(Fore.GREEN + str(nbClips) + ' clips found of ' + streamerName)
    if nbClips <= 0:
        print(Fore.RED + '\nNO CLIP FOUND')
        quit()

# random streamers
else:
    nbClips = 0
    while nbClips <= 0:
        print('random')
        clipsResponse = [twitch.get_clips(broadcaster_id=streamersListId[randrange(len(streamersListId))],
                                          first=NUMBER_CLIPS_REQ, started_at=startDate, ended_at=endDate)]

        # read api response
        for clip in clipsResponse:
            data = clip['data']
            for i in data:
                nbClips = nbClips + 1
                streamerName = i['broadcaster_name']
                # add url clips in clipsUrl
                clipsUrl.append(i['url'])
        # print nb of clips and streamer name
        print(Fore.GREEN + '\n' + str(nbClips) + ' clips found of ' + streamerName)

# download all clips
for url in clipsUrl:
    print(Fore.CYAN + '\n' + '*' * 112, '\n')
    # execute python download file
    system('python twitch-dl.pyz download -q source ' + url)

# move all file
videoFileClearName = []
videoFileName = []
fileDir = path.dirname(__file__)
sourceFiles = listdir(fileDir)
destinationPath = fileDir + r'\VideoDownload'
for file in sourceFiles:
    # get all .mp4 file and move it
    if file.endswith('.mp4'):
        # move each file
        move(path.join(fileDir, file), path.join(destinationPath, file))
        # append complete file name
        videoFileName.append(file)
        # get clean file name
        fileName = ' '.join(file.split('_')[2:]).split('.')[0]
        # append videoFileName
        videoFileClearName.append(fileName)
# print all files for choice
print(Fore.CYAN + '\n' + '*' * 112 + '\n')
print(Fore.GREEN + 'Choice one clip' + '\n')
for file in range(0, len(videoFileName)):
    print(Fore.CYAN + str(file) + ' | ' + videoFileClearName[file])

print('\n')

# open file explorer at VideoDownload folder
Popen(r'explorer /select,' + destinationPath + r'\reference')

# choose the clip
finishSelect = False
while not finishSelect:
    chosenClipsInput = input('Chose clip number in range: \n')
    # check if is a int
    if chosenClipsInput.isdigit():
        # check if is in range
        if int(chosenClipsInput) in range(0, len(videoFileName)):
            finishSelect = True
        else:
            finishSelect = False
    else:
        finishSelect = False

# delete other clips
print(Fore.CYAN + '\n' + '*' * 112 + '\n')
for file in listdir(destinationPath):
    if file.endswith('.mp4') and file != videoFileName[int(chosenClipsInput)]:
        remove(destinationPath + '/' + file)

# ask use StreamLadder
useStreamLadderAsk = ''
if str(USE_STREAMLADDER) == 'ASK':
    finishSelect = False
    while not finishSelect:
        useStreamLadderAsk = str(input(Fore.GREEN + 'use streamLadder ? y/n \n'))
        if useStreamLadderAsk == 'y' or useStreamLadderAsk == 'n':
            finishSelect = True
        else:
            finishSelect = False
    print(Fore.CYAN + '\n' + '*' * 112 + '\n')

# streamLadder headless webBrowser
if useStreamLadderAsk == 'y' or str(USE_STREAMLADDER) == 'ALL':
    # headless file dir
    service = Service(fileDir + r'\headless\geckodriver.exe')
    # options of browser
    options = webdriver.FirefoxOptions()
    options.headless = False
    options.set_preference("browser.download.folderList", 2)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.download.dir", destinationPath)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", "video/mp4")

    # driver
    driver = webdriver.Firefox(service=service, options=options)

    # install adblock extension
    driver.install_addon(fileDir + r'\headless\uBlock.xpi', temporary=True)

    # get streamLadder url
    driver.get('https://streamladder.com/')

    # find import file button and import the clip file
    clipsDir = destinationPath.split('/')

    # try to load clip in StreamLadder
    print(Fore.YELLOW + 'Try importing video clip in streamLadder')
    try:
        driver.find_element(By.ID, 'localfile').send_keys(VIDEO_PATH + videoFileName[int(chosenClipsInput)])
        print(Fore.GREEN + 'Success Importing \n')
    except:
        print(Fore.RED + 'ERROR WITH LOAD FILE IN STREAMLADDER \n')
        print(Style.RESET_ALL)

    # wait finish editing
    print(Fore.GREEN + "Select template when edit is finish press enter (don't click Finish)\n")
    input()
    driver.minimize_window()

    # try press finish button
    print(Fore.YELLOW + 'Try press finish button')
    try:
        driver.find_element(By.CSS_SELECTOR, 'button.btn.btn-lg.btn-success.w-100').click()
        print(Fore.GREEN + 'Success click on finish \n')
    except:
        print(Fore.RED + 'ERROR FINISH BUTTON NOT FOUND \n')
        print(Style.RESET_ALL)

    # try get progress rendering
    print(Fore.YELLOW + 'Try get rendering progress')
    progress = None
    try:
        sleep(2)
        progress = float(driver.find_element(By.CSS_SELECTOR, 'div.progress-bar').get_attribute('aria-valuenow'))
        print(Fore.GREEN + 'Success get rendering progress \n')
        while float(progress) < 100:
            progress = float(driver.find_element(By.CSS_SELECTOR, 'div.progress-bar').get_attribute('aria-valuenow'))
            print(Fore.GREEN + 'Rendering : ' + str(int(progress)) + ' / 100%')
            sleep(2)
    except:
        if progress <= 0:
            print(Fore.RED + 'ERROR GET RENDERING PROGRESS \n')
            print(Style.RESET_ALL)

    print(Fore.GREEN + '\nRendering finish\n')

    # try download final video
    print(Fore.YELLOW + 'Try Download final video')
    try:
        remove(destinationPath + '/' + videoFileName[int(chosenClipsInput)])
        driver.find_element(By.CSS_SELECTOR, 'a.btn.btn-primary').click()
        print(Fore.GREEN + 'Success download final video \n')
        driver.quit()
    except:
        print(Fore.RED + 'ERROR WITH DOWNLOAD \n')
        print(Style.RESET_ALL)

    print(Fore.CYAN + '\n' + '*' * 112 + '\n')

# choose title of video
defaultTitle = str(videoFileClearName[int(chosenClipsInput)])
title = None
rep = str(input(Fore.GREEN + 'Choose title and # or press enter to default title: ' + str(
    videoFileClearName[int(chosenClipsInput)]) + '\n'))
# fi press enter the title is by default else is user entry
if len(rep) > 0:
    title = rep
else:
    title = defaultTitle + HASHTAG_LIST

# upload video headless
# Chrome webdriver options
ChOptions = webdriver.ChromeOptions()
ChOptions.headless = True
ChOptions.add_argument("user-data-dir=" + CHROME_USER_DATA)
ChOptions.add_experimental_option('excludeSwitches', ['enable-logging'])

# driver
ChDriver = Chrome(options=ChOptions, executable_path=fileDir + r'\headless\chromedriver.exe')

# get tiktok upload url
ChDriver.get('https://www.tiktok.com/upload?lang=fr')

# Find upload button and load video
videoUploadName = None
for file in listdir(destinationPath):
    if file.endswith('.mp4'):
        videoUploadName = file
sleep(1)

# try to load video
print(Fore.YELLOW + '\nTry to load video on tiktok')
try:
    ChDriver.find_element(By.CSS_SELECTOR, 'input.jsx-1828163283.upload-btn-input').send_keys(
        VIDEO_PATH + videoUploadName)
    print(Fore.GREEN + 'Success load video on tiktok\n')
except:
    print(Fore.RED + 'ERROR WITH LOADING VIDEO ON TIKTOK \n')
    print(Style.RESET_ALL)
sleep(0.5)

# try to add title
print(Fore.YELLOW + 'Try to set title')
try:
    ChDriver.find_element(By.CLASS_NAME, 'public-DraftStyleDefault-block.public-DraftStyleDefault-ltr').send_keys(title)
    print(Fore.GREEN + 'Success set title\n')
except:
    print(Fore.RED + 'ERROR WITH SET TITLE \n')
    print(Style.RESET_ALL)

# try to get upload progress
print(Fore.YELLOW + 'Try to get upload progress')
try:
    progess = 0
    while progess >= 100:
        progress = int(ChDriver.find_element(By.CSS_SELECTOR, 'div.tiktok-progress').get_attribute('data-pct'))
        sleep(1.5)
except:
    print(Fore.RED + 'ERROR WITH GET UPLOAD PROGRESS\n')
    print(Style.RESET_ALL)
sleep(5)

# try to publish video
print(Fore.YELLOW + 'Try to upload video')
try:
    ChDriver.find_element(By.CSS_SELECTOR, 'button.tiktok-btn-pc.tiktok-btn-pc-large.tiktok-btn-pc-primary').click()
    sleep(3)
except:
    print(Fore.RED + 'ERROR WITH UPLOADING VIDEO\n')
    print(Style.RESET_ALL)

ChDriver.quit()

# end
sleep(2)
print('Process finish, enter anything to close')
input()
print('File deleted, FINISH')

# remove last file
for file in listdir(destinationPath):
    if file.endswith('.mp4'):
        remove(destinationPath + '/' + file)
sleep(0.3)

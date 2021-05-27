from ctypes import pythonapi
import cv2
# import imutils
import glob, os, time, pyautogui, math, enum
import numpy as np
from datetime import datetime  
from datetime import timedelta 

PLAY_AREA=(282, 214, 1388, 798)
OUTSIDE_PLAY_AREA=(178, 529)
INSIDE_PLAY_AREA=(523, 587)
HARVEST_AREA=(975, 894)
CENTER_PLAY_AREA=(694+282, 399+214)
NUMBER_OF_CAGES=4
NUMBER_OF_PLOT=6


class Template(enum.Enum):
    COIN="img/templates/coin.png"
    FARM="img/templates/land.png"
    SHOVEL="img/templates/shovel.png"
    CENTER="img/templates/center.png"
    POTATO="img/templates/potato.png"
    WHEAT="img/templates/wheat.png"

def click(p):
    x,y = p
    pyautogui.click(x, y)

def collect_coins():
    click(INSIDE_PLAY_AREA)
    for i in range(NUMBER_OF_CAGES):
        coins = detect(Template.COIN)
        if coins is not None:
            click(coins)
            time.sleep(2)
        else:
            break

def center():
    click(INSIDE_PLAY_AREA)
    center_of_home = detect(Template.CENTER)
    if center_of_home is None:
        return False
    distance = math.sqrt( ((center_of_home[0]-CENTER_PLAY_AREA[0])**2)+((center_of_home[1]-CENTER_PLAY_AREA[1])**2) )
    print(f"distance: {distance}")
    if distance > 50:
        x_diff = center_of_home[0] - CENTER_PLAY_AREA[0]
        y_diff = center_of_home[1] - CENTER_PLAY_AREA[1]
        x = INSIDE_PLAY_AREA[0] + -x_diff
        y = INSIDE_PLAY_AREA[1] + -y_diff
        pyautogui.moveTo(INSIDE_PLAY_AREA)
        # time.sleep(2)
        # print(f"x, y : {(x, y)}")
        # print(f"diff: {(x_diff, y_diff)}")
        pyautogui.dragTo(x, y, duration=0.5)
    return True

def farm():
    click(INSIDE_PLAY_AREA)
    shovel = detect(Template.SHOVEL)
    if shovel is not None:
        click((shovel[0], shovel[1] + 50))
        time.sleep(1)
        click(HARVEST_AREA)
    farm = detect(Template.FARM)
    if farm is not None:
        print(f"farm: {farm}")
        click(farm)
        crop = detect(Template.WHEAT)
        if crop is not None:
            for i in range(NUMBER_OF_PLOT):
                click((crop[0], crop[1] + 120))
                time.sleep(0.5)

    time.sleep(2)

def screenshot():
    time.sleep(2)
    filename = "img/source/screenshot.png"
    im = pyautogui.screenshot(region=PLAY_AREA)
    im2 = cv2.cvtColor(np.array(im), cv2.COLOR_BGR2GRAY)
    cv2.imwrite(filename, im2)
    return filename

def detect(template):
    template_img = template.value
    image = cv2.imread(screenshot())
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]
    for file in glob.glob(template_img):
        template_img = cv2.imread(file)
        found = None
        (tH, tW) = template_img.shape[:2]
        tEdged = cv2.Canny(template_img, 50, 200)

        for scale in np.linspace(1, 2, 20):
            resized = cv2.resize(gray, dsize = (0,0), fx = scale, fy = scale)
            r = gray.shape[1] / float(resized.shape[1])
            if resized.shape[0] < tH or resized.shape[1] < tW:
                break
            edged = cv2.Canny(resized, 50, 200)
            result = cv2.matchTemplate(edged, tEdged, cv2.TM_CCOEFF)
            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        (_, maxLoc, r) = found
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + tW) * r), int((maxLoc[1] + tH) * r))
        
        # draw rectangle
        # cv2.rectangle(image, (startX, startY), (endX, endY), (0, 0, 255), 2)
        # cv2.imshow(template.name, image)
        # cv2.imwrite('output.jpg', image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        
        center = (282+startX + tW//2, 214+startY + tH//2)
        
        if found[2] > 0.9:
            print(f"{datetime.now().strftime('%x %X')}::{template.name}::Center: {center}, Factor: {found[2]}")
            return center
        else:
            print(f"{datetime.now().strftime('%x %X')}::{template.name}::Not found, Factor: {found[2]}")
            return None

def play():
    if center():
        collect_coins()
        farm()
        click(OUTSIDE_PLAY_AREA)

while(True):
    time.sleep(5)
    play()
    # pyautogui.keyDown('alt')
    # time.sleep(.2)
    # pyautogui.press('tab')
    # time.sleep(.2)
    # pyautogui.keyUp('alt')
    # play()
    print(f"{datetime.now().strftime('%x %X')}::Resting for 5mins. Resuming in {datetime.now() + timedelta(minutes=5)}")
    time.sleep(300)
    # break


# 1,2

# 3,4
from gettext import find

import pyautogui
import time

def find_and_click(image_path, confidence=0.8, grayscale=True, duration=1,offset=(0,0),double_click=False):
    """_summary_:查找图片,移动到位置并点击

    Args:
        image_path (_type_): _description_
        confidence (float, optional): _description_. Defaults to 0.8.
        grayscale (bool, optional): _description_. Defaults to True.
        duration (int, optional): _description_. Defaults to 1.
        offset (tuple, optional): _description_. Defaults to (0,0).
    """

    try:
        position = pyautogui.locateOnScreen(
            image_path, grayscale=grayscale, confidence=confidence
        )
        print(position)
    except pyautogui.ImageNotFoundException as e:
        print(f"Image {image_path} not found on the screen.")
        return False
    
    pyautogui.moveTo(
        (position[0] + position[2] // 2 + offset[0], position[1] + position[3] // 2 + offset[1]), duration=duration
    ) 

    if double_click:
        pyautogui.doubleClick()
    else:
        pyautogui.click()
    return True

def scroll_for_image(image_path, confidence=0.8, grayscale=True, check_interval=1,max_scrolls=10):
    """滚轮查找图片

    Args:
        image_path (_type_): _description_
        confidence (float, optional): _description_. Defaults to 0.8.
        grayscale (bool, optional): _description_. Defaults to True.
        check_interval (int, optional): _description_. Defaults to 1.
        max_scrolls (int, optional): _description_. Defaults to 10.
    """

    scroll_count = 0
    while scroll_count < max_scrolls:
        try:
            position = pyautogui.locateOnScreen(
                image_path, grayscale=grayscale, confidence=confidence
            )
            print(position)
            return position
        except pyautogui.ImageNotFoundException as e:
            print(f"Image {image_path} not found, scrolling down.")
            pyautogui.scroll(-500)  # scroll down
            time.sleep(check_interval)  # wait for the page to load
            scroll_count += 1

    print(f"Image {image_path} not found after {max_scrolls} scrolls.")
    return None



def qq_open():
    # recognize the image
    find_and_click("images/qq_images/qq.png", confidence=0.8, grayscale=True, duration=1, double_click=False)
    try:
        position = pyautogui.locateOnScreen(
            "images/qq_images/qq.png", grayscale=True, confidence=0.8
        )
        print(position)
    except pyautogui.ImageNotFoundException as e:
        print("Image not found on the screen.")
        return

    # move the mouse to the image
    pyautogui.moveTo(
        (position[0] + position[2] // 2, position[1] + position[3] // 2), duration=1
    )

    time.sleep(0.5)

    # one click to open the QQ
    pyautogui.click()

    # recognize the tecent image
    try:
        position = pyautogui.locateOnScreen(
            "images/qq_images/search.png", grayscale=True, confidence=0.8
        )
        print(position)
    except pyautogui.ImageNotFoundException as e:
        print("Image not found on the screen.")
        return

    # move the mouse to the image
    pyautogui.moveTo(
        (position[0] + position[2] // 2, position[1] + position[3] // 2), duration=1
    )

    # double click to open the search
    pyautogui.click()

    # input the content
    # pyautogui.press("shift")
    pyautogui.write("shaodonglin")

    # push engter browse url
    time.sleep(0.5)
    pyautogui.press("space")
    time.sleep(0.5)
    pyautogui.press("enter")

    # start scolling
    while True:
        # check if exist education button
        try:
            position = pyautogui.locateOnScreen(
                "images/qq_images/donglin.png", grayscale=True, confidence=0.8
            )
            print(position)
            break
        except pyautogui.ImageNotFoundException as e:
            print("Donglin button not found, scrolling down.")
            # scroll down page
            pyautogui.scroll(-500)  # scroll down
            time.sleep(1)  # wait for the page to load

    if position is not None:
        print("Donglin button found at position:", position)
        pyautogui.moveTo(
            (position[0] + position[2] // 2, position[1] + position[3] // 2), duration=1
        )
        pyautogui.click()

    # double click the button of smile to type
    try:
        position = pyautogui.locateOnScreen(
            "images/qq_images/smile.png", grayscale=True, confidence=0.8
        )
        print(position)
    except pyautogui.ImageNotFoundException as e:
        print("Image not found on the screen.")
        return

    # move the mouse to the button of image
    # Y轴向下为正方向
    pyautogui.moveTo(
        (position[0] + position[2] // 2, position[1] + position[3] + 20), duration=1
    )

    # double click to open the smile
    pyautogui.click()

    # input the content
    # pyautogui.press("shift")
    pyautogui.write("hi, donglin")

    # push engter browse url
    time.sleep(0.5)
    pyautogui.press("enter")
    pyautogui.press("enter")


if __name__ == "__main__":
    qq_open()

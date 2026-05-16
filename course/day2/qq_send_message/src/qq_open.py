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
    # 点击qq图标打开qq
    find_and_click("images/qq_images/qq.png", confidence=0.8, grayscale=True, duration=1, double_click=False)
    # 点击搜索框
    find_and_click("images/qq_images/search.png", confidence=0.8, grayscale=True, duration=1, double_click=False)


    # input the content
    # pyautogui.press("shift")
    pyautogui.write("shaodonglin")

    # push engter browse url
    time.sleep(0.5)
    pyautogui.press("space")
    time.sleep(0.5)
    pyautogui.press("enter")

    # 翻滚查找头像
    scroll_for_image("images/qq_images/donglin.png", confidence=0.8, grayscale=True, check_interval=1,max_scrolls=10)
    # 点击头像
    find_and_click("images/qq_images/donglin.png", confidence=0.8, grayscale=True, duration=1, double_click=False)

    # 点击表情下方的输入框
    find_and_click("images/qq_images/smile.png", confidence=0.8, grayscale=True, duration=1, offset=(0,20), double_click=False)

    # input the content
    # pyautogui.press("shift")
    pyautogui.write("hi, donglin")

    # push engter browse url
    time.sleep(0.5)
    pyautogui.press("enter")
    pyautogui.press("enter")


if __name__ == "__main__":
    qq_open()

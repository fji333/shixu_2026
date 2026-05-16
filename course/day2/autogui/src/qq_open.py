import pyautogui
import time


def qq_open():
    # recognize the image
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

    # double click to open the edge
    pyautogui.doubleClick()

    # recognize the tecent image
    try:
        position = pyautogui.locateOnScreen(
            "image/qq_images/message.png", grayscale=True, confidence=0.8
        )
        print(position)
    except pyautogui.ImageNotFoundException as e:
        print("Image not found on the screen.")
        return

    # move the mouse to the image
    pyautogui.moveTo(
        (position[0] + position[2] // 2, position[1] + position[3] // 2), duration=1
    )

    # double click to open the message
    pyautogui.doubleClick()

    # start scolling
    while True:
        # check if exist education button
        try:
            position = pyautogui.locateOnScreen(
                "image/qq_images/donglin.png", grayscale=True, confidence=0.8
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
                (position[0] * 20), (position[1] + position[3] // 2), duration=1
            )
            pyautogui.click()
            break

    # double click the button of smile to type
    try:
        position = pyautogui.locateOnScreen(
            "image/qq_images/smile.png", grayscale=True, confidence=0.8
        )
        print(position)
    except pyautogui.ImageNotFoundException as e:
        print("Image not found on the screen.")
        return

    # move the mouse to the button of image
    pyautogui.moveTo(
        (position[0] + position[2] // 2, position[1] + position[3] // 2), duration=1
    )

    # double click to open the smile
    pyautogui.doubleClick()

    
    


if __name__ == "__main__":
    qq_open()

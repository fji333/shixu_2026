import pyautogui
import time
from src.qq_open import qq_open


# def main():
#     # recognize the image
#     try:
#         position = pyautogui.locateOnScreen(
#             "images/edge.png", grayscale=True, confidence=0.8
#         )
#         print(position)
#     except pyautogui.ImageNotFoundException as e:
#         print("Image not found on the screen.")
#         return

#     # move the mouse to the image
#     pyautogui.moveTo(
#         (position[0] + position[2] // 2, position[1] + position[3] // 2), duration=1
#     )

#     # double click to open the edge
#     pyautogui.doubleClick()
#     # wait for the edge to open
#     time.sleep(2)

#     # input the content
#     pyautogui.press("shift")
#     pyautogui.write("qq.com")

#     # push engter browse url
#     time.sleep(0.5)
#     pyautogui.press("enter")

#     # wait page open
#     time.sleep(2)

#     # recognize the tecent image
#     try:
#         position = pyautogui.locateOnScreen(
#             "image/tencent.png", grayscale=True, confidence=0.8
#         )
#         print(position)
#     except pyautogui.ImageNotFoundException as e:
#         print("Image not found on the screen.")
#         return

#     # move the mouse to the image
#     pyautogui.moveTo(
#         (position[0] + position[2] // 2, position[1] + position[3] // 2), duration=1
#     )

#     # start scolling
#     while True:
#         # check if exist education button
#         try:
#             position = pyautogui.locateOnScreen(
#                 "image/education.png", grayscale=True, confidence=0.8
#             )
#             print(position)
#             break
#         except pyautogui.ImageNotFoundException as e:
#             print("Education button not found, scrolling down.")
#             # scroll down page
#             pyautogui.scroll(-500)  # scroll down
#             time.sleep(1)  # wait for the page to load

#     if position is not None:
#         print("Education button found at position:", position)
#         pyautogui.moveTo(
#             (position[0]*20),(position[1] + position[3] // 2), duration=1
#         )
#         pyautogui.click()


if __name__ == "__main__":
    # main()
    qq_open()

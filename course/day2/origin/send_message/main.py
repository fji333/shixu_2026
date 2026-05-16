import pyautogui as ptg
import time
import pyttsx3  # 语音播报


def say(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()


def find_image(
    img,
    region=(
        0,
        0,
        2560,
    ),
    garyscale=True,
):
    try:
        position = ptg.locateOnScreen(img, grayscale=garyscale, confidence=0.8)
        print(position)
        return position
    except ptg.ImageNotFoundException as e:
        print("Image not found on the screen.")
        return None


def move_and_click(position, duration=1, double_click=False):
    ptg.moveTo(
        (position[0] + position[2] // 2, position[1] + position[3] // 2),
        duration=duration,
    )
    if double_click:
        ptg.doubleClick()
    else:
        ptg.click()


def main():
    # 首先在右下角寻找QQ图标
    position = find_image("images/qq.png", (2025, 1550, 528, 50))
    if position is None:
        say("QQ图标未找到，程序结束。")
        return
    else:
        say("QQ图标已找到，正在打开QQ。")
    move_and_click(position, duration=1, double_click=False)
    time.sleep(0.5)
    say("查找消息按钮")
    position = find_image("qq.msg2.png")
    if position is None:
        position = find_image("qq/msg1.png")
        if position is None:
            say("没有找到qq界面无法发送消息")
            return
        say("点击消息按钮")
        move_and_click(position, duration=1, double_click=False)


if __name__ == "__main__":
    main()

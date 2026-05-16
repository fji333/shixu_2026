import pyautogui as ptg
import time
import pyttsx3 # 语音播报库


def say(content):
    engine = pyttsx3.init()
    engine.say(content)
    engine.runAndWait()

def find_image(img,region=(0,0,2560,1660),grayscale=True):
    try:
        return ptg.locateOnScreen(img,region=region,grayscale=grayscale)
    except ptg.ImageNotFoundException as e:
        print("没有找到图片")
        return None

def main():
    # 首先在右下角寻找qq图标
    position = find_image("images/qq.png",(2025,1550,528,50))
    if position is None:
        say("没有找到qq图标")
    else:
        say("找到qq图标，开始操作")
        ptg.moveTo((position[0]+position[2]//2),(position[1]+position[3]/2),duration=1)
        say("打开qq")
        ptg.click()
        time.sleep(0.5)
        say("查找消息按钮")
        position = find_image("images/qq_msg2.png")
        if position is None:
            position = find_image("images/qq_msg.png")
            if position is None:
                say("没有找到qq界面无法发送消息")
                return
        say("点击消息按钮")
        ptg.moveTo((position[0]+position[2]//2),(position[1]+60),duration=1)
        ptg.click()
        # 先查找一次发送对象
        say("查找一次发送对象")
        send_group_position = find_image("images/send_group.png")
        if send_group_position is None:
            # 鼠标移动到消息列表然后滚送查找
            say("没有找到发送对象开始滚动查找")
            ptg.moveTo((position[0]+120),(position[1]+180),duration=1)
            while True:
                # 滚动页面
                pyautogui.scroll(-200)
                time.sleep(1)
                send_group_position = find_image("images/send_group.png")
                if send_group_position is not None:
                    break;
         
        # 找到了发送对象
        say("找到发送对象，点击发送对象")
        ptg.moveTo((send_group_position[0]+50),(send_group_position[1]+50),duration=1)
        ptg.click()
        say("输入消息内容")
        ptg.write("zheshiyigeceshixiaoxi")
        ptg.press("space")
        say("发送")
        ptg.hotkey("ctrl","enter")
        

if __name__ == "__main__":
    main()
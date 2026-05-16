import pyautogui
import time


def main():
    # 首先识别一下图片
    try:
        position = pyautogui.locateOnScreen("images/edge.png",grayscale=True)
        print(position)
    except pyautogui.ImageNotFoundException as e:
        print("没有找到图片")
        return 
    # 将鼠标移动到图片上去
    pyautogui.moveTo((position[0]+position[2]//2),(position[1]+position[3]/2),duration=1)
    # 双击一下 打开浏览器
    pyautogui.doubleClick() 
    #等待一下 让浏览器打开
    time.sleep(2)
    #输入内容
    pyautogui.write("qq.com")
    time.sleep(0.5)
    # 点击回车访问网页
    pyautogui.press("enter")
    #等待页面打开
    time.sleep(2)
    # 首先识别一下腾讯网的图片
    try:
        position = pyautogui.locateOnScreen("images/1.png",grayscale=True)
        print(position)
    except pyautogui.ImageNotFoundException as e:
        print("没有找到图片")
        return 
    # 鼠标移动到腾讯网上面去
    # 将鼠标移动到图片上去
    pyautogui.moveTo((position[0]+position[2]//2),(position[1]+position[3]/2),duration=1)
    # 开始滚动页面
    position = None
    while True:
        # 先检测教育按钮是否存在
        try:
            position = pyautogui.locateOnScreen("images/2.png",grayscale=True)
            print(position)
            break
        except pyautogui.ImageNotFoundException as e:
            print("没有找到图片")
            # 滚动页面
            pyautogui.scroll(-850)
            time.sleep(1)
    if position is not None:
        print("找到了")
        pyautogui.moveTo((position[0]+20),(position[1]+position[3]/2),duration=1)
        pyautogui.click() 

if __name__ == "__main__":
    main()

set ws = createObject("wscript.shell")
set spk = createObject("sapi.spvoice")
strComputer = "."
set objWMIService = GetObject("winmgmts:{impersonationLevel=impersonate}!\\" & strComputer & "\root\cimv2")
set processList = objWMIService.ExecQuery("select * from Win32_Process where Name='Apifox.exe'")
if processList.Count > 0 then 
spk.speak "检测到当前正在玩游戏，你是不是没有好好学习"
spk.speak "赶紧把游戏关掉"
res = msgbox("你确定要继续玩游戏吗？赶紧自己关掉吧",vbOkCancel,"提醒")
if res=vbOk then
spk.speak "既然这样，那就自己关闭吧"
else
spk.speak "你还不知道悔改，那我只能强行帮你关闭了，倒计时3秒"
num = 3
Do until num <= 0
spk.speak num
num = num - 1
Loop
ws.run "cmd /c ""taskkill /f /im Apifox.exe""",0,true
spk.speak "你看看你的游戏是不是已经关掉了啊"
end if
else
spk.speak "不错，你没有玩游戏，继续保持哦"
end if
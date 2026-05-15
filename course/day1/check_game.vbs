set ws = createObject("wscript.shell")
set spk = createObject("sapi.spvoice")
strComputer = "."
set objWMIService = GetObject("winmgmts:{impersonationLevel=impersonate}!\\" & strComputer & "\root\cimv2")
set processesList = objWMIService.ExecQuery("Select * from Win32_Process where Name='Apifox.exe'")
if processesList.count > 0 then
    spk.speak "Apifox is running!"
    spk.speak "Close it!"
    res = msgbox("Apifox is running! Do you want to close it?", vbOKCancel, "Apifox Check")
    if res = vbOK then
        spk.speak "Closing Apifox in 3 seconds!"
        num = 3
        do while num > 0
            spk.speak num & " seconds remaining!"
            wscript.sleep 1000
            num = num - 1
        loop
        ws.run "cmd /c taskkill /f /im Apifox.exe", 0, true
        spk.speak "Apifox has been closed!"
    end if
else
    spk.speak "Apifox is not running!"
end if
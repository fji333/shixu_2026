set ws = createObject("wscript.shell")
set spk = createobject("sapi.spvoice")
set fso = createobject("scripting.filesystemobject")

'get the path of desktop
desktop = ws.specialfolders("Desktop")

'remind user the app in running
msgbox("U disk copy is running, please wait for a moment...")

set objWMIService = GetObject("winmgmts:{impersonationLevel=impersonate}!\\" & "." & "\root\cimv2")
' 通过循环监控U盘的插入事件
DO
    '查询设备的插入事件
    set colEvents = objWMIService.ExecNotificationQuery(
        "SELECT * FROM __InstanceCreationEvent WITHIN 5 WHERE "__ &  "rgetInstance ISA 'Win32_LogicalDisk'")
    '等待插入
    set objEvent = colEvents.NextEvent
    '获取插入的设备信息
    set disk = objEvent.TargetInstance
    '检测是否为U盘（可移动磁盘）
    if disk.DriveType = 2 then
        '获取U盘的盘符
        driveLetter = disk.DeviceID
        '构建目标路径
        targetPath = desktop & "\" & fso.GetBaseName(driveLetter) & "_backup"
        '复制U盘内容到目标路径
        fso.CopyFolder driveLetter & "\*", targetPath, true
        '提示用户复制完成
        spk.speak "U disk copy completed!"
        msgbox "U disk copy completed! The backup is saved on your desktop."
    end if
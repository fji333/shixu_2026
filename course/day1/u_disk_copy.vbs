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
        '提示u盘已插入
        msgbox "检测到U盘已插入: " & usbDrive , vbInformation, "提示"
        '创建u盘中用来存放文件的文件夹
        targetFolder = usbDrive & "\back_excel"
        if not fso.folderexists(targetFolder) then
            fso.createfolder(targetFolder)
        end if
        'copy excel file
        set folder = fso.getfolder(desktopPath)
        set files = folder.files
        copyCount = 0
        '循环拷贝文件
        for each file in files
            'check if the file is an excel file
            ext = lcase(fso.getextensionname(file.name))
            if ext = "xls" or ext = "xlsx" then
                'copy file
                targetFile = targetFolder & "\" & file.name
                file.copy targetFile,true
                copyCount = copyCount + 1
            end if
        next
        'display copy info
        if copyCount > 0 then
            spk.speak "已成功复制 " & copyCount & " 个Excel文件到U盘的back_excel文件夹中！"
        else
            spk.speak "未找到Excel文件，未进行复制！"
        end if
    end if
    'ask if user want to quit the app
    res = msgbox("是否继续监控U盘插入？点击“是”继续，点击“否”退出。", vbYesNo, "继续监控")
    if res = vbNo then
        spk.speak "正在退出U盘监控程序！"
        exit do
    end if
loop
set ws = createObject("wscript.shell")
set spk = createObject("sapi.spvoice")
set fso = createObject("scripting.filesystemobject")
' 获取桌面的路径
desktopPath = ws.specialFolders("Desktop")
' 提示程序已经启动
msgbox "U盘监控已经启动，等待U盘的插入",vbInformation,"监控程序"
' 创建WMI服务连接，监控设备的插入事件
strComputer = "."
set objWMIService = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
' 通过循环监控U盘的插入事件
Do
	' 查询设备的插入事件
	set colEvents = objWMIService.ExecNotificationQuery _
		("select * from __InstanceCreationEvent within 5 where " _
		& "TargetInstance isa 'Win32_LogicalDisk'" )
		
	' 等待插入
	set objEvent = colEvents.NextEvent
	' 获取U盘的设备信息
	set disk = objEvent.TargetInstance
	' 检测是不是U盘
	if disk.DriveType = 2 then
		usbDrive = disk.DeviceID
		' 提示U盘已插入
		msgbox "检测到U盘插入：" & usbDrive , vbInformation,"提示"
		' 创建U盘中的用来存放文件的文件夹
		targetFolder = usbDrive & "\back_excel"
		if not fso.folderExists(targetFolder) then
			fso.createFolder(targetFolder)
		end if
		' 复制excel文件
		set folder = fso.getFolder(desktopPath)
		set files = folder.files
		copyCount = 0
		' 循环拷贝文件
		for each file in files
			'检测文件是不是excel
			ext = lcase(fso.getExtensionName(file.name))
			if ext = "xls" or ext = "xlsx" then
				' 拷贝文件
				targetFile = targetFolder & "\" & file.name
				file.copy targetFile ,true
				copyCount = copyCount + 1
			end if
		next
		' 显示一下拷贝的信息
		if copyCount > 0 then
			spk.speak "成功复制了" & copyCount & "个excel的文件到U盘"
		else 
			spk.speak "桌面上没有excel文件"
		end if
	end if	
	' 询问是否退出程序
	res = msgbox("是否继续监控U盘插入？",vbYesNo,"提示")
	if res = vbNo then
		spk.speak "用户不想监控了，退出程序"
		Exit Do
	end if
Loop
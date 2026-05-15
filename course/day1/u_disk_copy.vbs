set ws = createObject("wscript.shell")
set spk = createobject("sapi.spvoice")
set fso = createobject("scripting.filesystemobject")

'get the path of desktop
desktop = ws.specialfolders("Desktop")

'remind user the app in running
msgbox("U disk copy is running, please wait for a moment...")


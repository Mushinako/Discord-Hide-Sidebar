scriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)
scriptPath = scriptDir & "\vbshideside.bat"
Call CreateObject("Wscript.Shell").Run(scriptPath, 0, True)

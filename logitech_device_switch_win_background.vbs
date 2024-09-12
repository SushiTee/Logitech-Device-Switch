Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Get the directory of the current script
scriptDir = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Construct the full path to the Python script
pythonScript = scriptDir & "\logitech_device_switch.py"

' Construct the full path to the virtual environment activation script
' Adjust the path to your virtual environment's activation script
venvActivate = scriptDir & "\.venv\Scripts\activate.bat"

' Run the Python script using pythonw.exe in the background
objShell.Run "cmd /c """ & venvActivate & """ && python.exe " & pythonScript, 0, False

Set WshShell = CreateObject("WScript.Shell") 
WshShell.Run "powershell -WindowStyle Hidden -Command ""Set-Location 'D:\code_project\node-mark'; python .\app.py""", 0, False
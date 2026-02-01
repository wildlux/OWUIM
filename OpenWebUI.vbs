' ======================================================================
'  OPEN WEBUI + OLLAMA - Launcher Silenzioso
'  Doppio click per avviare tutto senza finestra nera
' ======================================================================

Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Ottieni directory dello script
scriptPath = fso.GetParentFolderName(WScript.ScriptFullName)

' Esegui il batch nascosto
WshShell.Run """" & scriptPath & "\OpenWebUI.bat""", 0, False

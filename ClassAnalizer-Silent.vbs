Option Explicit

Dim fso, shell, root, uvPath, command
Set fso = CreateObject("Scripting.FileSystemObject")
Set shell = CreateObject("WScript.Shell")

root = fso.GetParentFolderName(WScript.ScriptFullName)
uvPath = fso.BuildPath(root, "uv.exe")

If Not fso.FileExists(uvPath) Then
    shell.Run """" & fso.BuildPath(root, "ClassAnalizer.bat") & """", 1, True
End If

If Not fso.FileExists(uvPath) Then
    MsgBox "No se encontro ni se pudo descargar uv.exe en la carpeta portable.", vbCritical, "ClassAnalizer"
    WScript.Quit 1
End If

shell.CurrentDirectory = root
shell.Environment("Process")("UV_PYTHON") = "3.12"
shell.Environment("Process")("UV_PROJECT_ENVIRONMENT") = fso.BuildPath(root, ".venv")
shell.Environment("Process")("UV_CACHE_DIR") = fso.BuildPath(root, ".uv-cache")

command = """" & uvPath & """ run --directory """ & root & """ classanalizer gui"
shell.Run command, 0, False

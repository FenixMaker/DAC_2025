' ============================================================================
' Iniciar Versao Web - Sistema DAC (VBScript)
' Este script pode ser facilmente convertido em EXE usando Bat_To_Exe_Converter
' ============================================================================

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Obtém o caminho do script
strScriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)

' Caminho para o launcher Python
strLauncherPath = strScriptPath & "\scripts\inicializacao\launcher_web.py"

' Verifica se o arquivo existe
If Not objFSO.FileExists(strLauncherPath) Then
    MsgBox "Erro: launcher_web.py não encontrado em:" & vbCrLf & strLauncherPath, vbCritical, "Sistema DAC"
    WScript.Quit 1
End If

' Define o comando
strCommand = "python """ & strLauncherPath & """"

' Define o diretório de trabalho
strWorkDir = strScriptPath

' Executa o comando em uma nova janela
objShell.Run "cmd /k title Sistema DAC - Web && cd /d """ & strWorkDir & """ && " & strCommand, 1, False

' Limpa objetos
Set objShell = Nothing
Set objFSO = Nothing

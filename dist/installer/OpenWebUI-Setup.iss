; ============================================================================
; OPEN WEBUI MANAGER - Inno Setup Script
; Crea installer Windows (.exe setup)
;
; Requisiti:
;   1. Inno Setup installato: https://jrsoftware.org/isdl.php
;   2. Eseguire prima: python build.py windows (per creare l'exe)
;   3. Aprire questo file con Inno Setup e compilare
; ============================================================================

#define MyAppName "Open WebUI Manager"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Carlo"
#define MyAppURL "https://github.com/open-webui/open-webui"
#define MyAppExeName "OpenWebUI-Manager.exe"

[Setup]
; Identificatore univoco dell'applicazione
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Directory di installazione
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}

; Output
OutputDir=..\dist
OutputBaseFilename=OpenWebUI-Manager-Setup-{#MyAppVersion}

; Compressione
Compression=lzma2/max
SolidCompression=yes

; Icona
SetupIconFile=..\ICONA\ICONA.ico
UninstallDisplayIcon={app}\ICONA\ICONA.ico

; Privilegi (non richiede admin se installa per utente)
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog

; Wizard
WizardStyle=modern
WizardSizePercent=100

; Lingue
ShowLanguageDialog=auto

; Altre opzioni
DisableProgramGroupPage=yes
LicenseFile=
InfoBeforeFile=..\docs\INFO_PRIMA_INSTALLAZIONE.txt
InfoAfterFile=..\docs\INFO_DOPO_INSTALLAZIONE.txt

[Languages]
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Crea icona sul Desktop"; GroupDescription: "Icone aggiuntive:"
Name: "quicklaunchicon"; Description: "Crea icona nella barra avvio veloce"; GroupDescription: "Icone aggiuntive:"

[Files]
; Eseguibile principale
Source: "..\dist\OpenWebUI-Manager.exe"; DestDir: "{app}"; Flags: ignoreversion

; Script di avvio
Source: "..\OpenWebUI.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\OpenWebUI.vbs"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\start_all.bat"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\stop_all.bat"; DestDir: "{app}"; Flags: ignoreversion

; Configurazione Docker
Source: "..\docker-compose.yml"; DestDir: "{app}"; Flags: ignoreversion

; Icone
Source: "..\ICONA\*"; DestDir: "{app}\ICONA"; Flags: ignoreversion recursesubdirs createallsubdirs

; Tools
Source: "..\tools\*"; DestDir: "{app}\tools"; Flags: ignoreversion recursesubdirs createallsubdirs

; Scripts
Source: "..\scripts\*"; DestDir: "{app}\scripts"; Flags: ignoreversion recursesubdirs createallsubdirs

; Documentazione
Source: "..\docs\*"; DestDir: "{app}\docs"; Flags: ignoreversion recursesubdirs createallsubdirs skipifsourcedoesntexist
Source: "..\README.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist
Source: "..\CLAUDE.md"; DestDir: "{app}"; Flags: ignoreversion skipifsourcedoesntexist

[Icons]
; Menu Start
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\ICONA\ICONA.ico"
Name: "{group}\Avvia Open WebUI"; Filename: "{app}\OpenWebUI.vbs"; IconFilename: "{app}\ICONA\ICONA.ico"
Name: "{group}\Ferma Servizi"; Filename: "{app}\stop_all.bat"; IconFilename: "{app}\ICONA\ICONA.ico"
Name: "{group}\Apri Browser (localhost:3000)"; Filename: "http://localhost:3000"; IconFilename: "{app}\ICONA\ICONA.ico"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

; Desktop
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\OpenWebUI.vbs"; IconFilename: "{app}\ICONA\ICONA.ico"; Tasks: desktopicon

; Quick Launch
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon

[Run]
; Esegui dopo installazione
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
Filename: "http://localhost:3000"; Description: "Apri Open WebUI nel browser"; Flags: nowait postinstall skipifsilent shellexec unchecked

[UninstallRun]
; Ferma servizi prima di disinstallare
Filename: "{app}\stop_all.bat"; Flags: runhidden waituntilterminated skipifdoesntexist

[UninstallDelete]
; Pulisci file temporanei
Type: filesandordirs; Name: "{app}\__pycache__"
Type: filesandordirs; Name: "{app}\venv"

[Code]
// ============================================================================
// Codice Pascal per verifiche e installazione dipendenze
// ============================================================================

var
  DockerPage: TInputOptionWizardPage;
  OllamaPage: TInputOptionWizardPage;

function IsDockerInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c docker --version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function IsOllamaInstalled: Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('cmd.exe', '/c where ollama', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

procedure InitializeWizard;
begin
  // Pagina informazioni Docker
  DockerPage := CreateInputOptionPage(wpSelectTasks,
    'Verifica Requisiti',
    'Controllo dipendenze necessarie',
    'Open WebUI Manager richiede Docker Desktop e Ollama per funzionare.',
    False, False);

  if IsDockerInstalled then
    DockerPage.Add('[OK] Docker Desktop installato')
  else
    DockerPage.Add('[!] Docker Desktop NON trovato - Scarica da: docker.com/products/docker-desktop');

  if IsOllamaInstalled then
    DockerPage.Add('[OK] Ollama installato')
  else
    DockerPage.Add('[!] Ollama NON trovato - Scarica da: ollama.com/download/windows');

  DockerPage.Add('');
  DockerPage.Add('Puoi installare le dipendenze mancanti dopo il setup.');
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ResultCode: Integer;
begin
  if CurStep = ssPostInstall then
  begin
    // Converti icona PNG in ICO se necessario
    if not FileExists(ExpandConstant('{app}\ICONA\ICONA.ico')) then
    begin
      // Prova a convertire con Python se disponibile
      Exec('cmd.exe', '/c python -c "from PIL import Image; img = Image.open(r''' + ExpandConstant('{app}\ICONA\ICONA_Trasparente.png') + '''); img.save(r''' + ExpandConstant('{app}\ICONA\ICONA.ico') + ''', format=''ICO'', sizes=[(256,256), (64,64), (32,32), (16,16)])"',
        '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;

function NextButtonClick(CurPageID: Integer): Boolean;
begin
  Result := True;

  // Avvisa se mancano dipendenze
  if CurPageID = DockerPage.ID then
  begin
    if not IsDockerInstalled or not IsOllamaInstalled then
    begin
      if MsgBox('Alcune dipendenze non sono installate. Vuoi continuare comunque?' + #13#10 + #13#10 +
                'Potrai installarle in seguito prima di usare Open WebUI Manager.',
                mbConfirmation, MB_YESNO) = IDNO then
        Result := False;
    end;
  end;
end;

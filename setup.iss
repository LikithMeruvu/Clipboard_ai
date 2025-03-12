[Setup]
AppName=Clipboard AI
AppVersion=0.1.0
DefaultDirName={autopf}\Clipboard AI
DefaultGroupName=Clipboard AI
OutputBaseFilename=ClipboardAISetup
Compression=lzma
SolidCompression=yes
UninstallDisplayIcon={app}\clipboard-ai.exe
AppPublisher=Your Company
AppPublisherURL=https://github.com/yourusername/clipboard_ai
AppSupportURL=https://github.com/yourusername/clipboard_ai/issues
AppUpdatesURL=https://github.com/yourusername/clipboard_ai/releases
PrivilegesRequired=lowest
WizardStyle=modern
DisableWelcomePage=no
DisableProgramGroupPage=yes
SetupIconFile=clipboard_ai\resources\icon.ico

[Files]
Source: "dist\clipboard-ai.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "clipboard_ai\resources\icon.ico"; DestDir: "{app}\resources"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Dirs]
Name: "{app}\resources"; Flags: uninsalwaysuninstall

[Icons]
Name: "{autoprograms}\Clipboard AI"; Filename: "{app}\clipboard-ai.exe"; IconFilename: "{app}\resources\icon.ico"
Name: "{autodesktop}\Clipboard AI"; Filename: "{app}\clipboard-ai.exe"; IconFilename: "{app}\resources\icon.ico"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Run]
Filename: "{app}\clipboard-ai.exe"; Description: "Launch Clipboard AI"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
  if not FileExists(ExpandConstant('{src}\dist\clipboard-ai.exe')) then begin
    MsgBox('The application executable was not found. Please build the application first using PyInstaller.', mbError, MB_OK);
    Result := False;
  end;
end;

[UninstallDelete]
Type: files; Name: "{app}\*.*"
Type: dirifempty; Name: "{app}"
; SolarScan Inno Setup Wizard Script
; Generates standalone Windows 1-click installer (SolarScan_Setup_v1.0.0.exe)

#define MyAppName "SolarScan"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "IamOumarIbrahim"
#define MyAppURL "https://github.com/IamOumarIbrahim/SolarScan"
#define MyAppExeName "SolarScan.exe"

[Setup]
AppId={{C8E117D2-5883-49F1-8A1C-98A826B9C3F0}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\LICENSE
OutputDir=..\dist
OutputBaseFilename=SolarScan_Setup_v1.0.0
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "envpath"; Description: "Add SolarScan to system PATH (recommended to run 'solarscan' from Command Prompt / PowerShell)"; GroupDescription: "System Integration"

[Files]
Source: "..\dist\SolarScan\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName} CLI"; Filename: "cmd.exe"; Parameters: "/k ""{app}\{#MyAppExeName} --help"""
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName} CLI"; Filename: "cmd.exe"; Parameters: "/k ""{app}\{#MyAppExeName} --help"""; Tasks: desktopicon

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
var
  Path: String;
  AppDir: String;
begin
  if (CurStep = ssPostInstall) and IsTaskSelected('envpath') then
  begin
    AppDir := ExpandConstant('{app}');
    if RegQueryStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', Path) then
    begin
      if Pos(AppDir, Path) = 0 then
      begin
        Path := Path + ';' + AppDir;
        RegWriteStringValue(HKEY_LOCAL_MACHINE, 'SYSTEM\CurrentControlSet\Control\Session Manager\Environment', 'Path', Path);
      end;
    end;
  end;
end;

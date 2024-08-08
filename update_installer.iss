[Setup]
AppName=Win69Updater
AppVersion=1.0
DefaultDirName={userappdata}\Win69Updater
DefaultGroupName=Win69Updater
OutputDir=output
OutputBaseFilename=Win69UpdaterSetup
Compression=lzma
SolidCompression=yes

[Files]
Source: "dist\win69updater.exe"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Run]
Filename: "{app}\win69updater.exe"; Description: "{cm:LaunchProgram,Win69Updater}"; Flags: nowait postinstall

Unicode true
!include "MUI2.nsh"
Name "Print&View PDF ${APP_VERSION}"
OutFile "${OUTPUT}"
InstallDir "$LOCALAPPDATA\Programs\PrintViewPDF"
RequestExecutionLevel user
SetCompressor /SOLID lzma
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey /LANG=1033 "ProductName" "Print&View PDF"
VIAddVersionKey /LANG=1033 "FileDescription" "Print&View PDF installer for Windows x64"
VIAddVersionKey /LANG=1033 "FileVersion" "${APP_VERSION}"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Print&View PDF contributors"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_LANGUAGE "PortugueseBR"
!insertmacro MUI_LANGUAGE "English"
Section "Print&View PDF"
  SetShellVarContext current
  SetOutPath "$INSTDIR"
  File /r "${STAGE}/*"
  CreateDirectory "$SMPROGRAMS\Print&View PDF"
  CreateShortCut "$SMPROGRAMS\Print&View PDF\Print&View PDF.lnk" "$INSTDIR\PrintViewPDF.exe"
  CreateShortCut "$DESKTOP\Print&View PDF.lnk" "$INSTDIR\PrintViewPDF.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintViewPDF" "DisplayName" "Print&View PDF ${APP_VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintViewPDF" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintViewPDF" "UninstallString" '$\"$INSTDIR\Uninstall.exe$\"'
  WriteRegStr HKCU "Software\Classes\Applications\PrintViewPDF.exe\shell\open\command" "" '$\"$INSTDIR\PrintViewPDF.exe$\" $\"%1$\"'
  WriteRegStr HKCU "Software\Classes\Applications\PrintViewPDF.exe\SupportedTypes" ".pdf" ""
SectionEnd
Section "Uninstall"
  SetShellVarContext current
  Delete "$DESKTOP\Print&View PDF.lnk"
  RMDir /r "$SMPROGRAMS\Print&View PDF"
  DeleteRegKey HKCU "Software\Classes\Applications\PrintViewPDF.exe"
  DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\PrintViewPDF"
  RMDir /r "$INSTDIR"
SectionEnd

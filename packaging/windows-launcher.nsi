Unicode true
!include "FileFunc.nsh"
Name "Print&View PDF"
OutFile "${STAGE}/PrintViewPDF.exe"
RequestExecutionLevel user
SilentInstall silent
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey /LANG=1033 "ProductName" "Print&View PDF"
VIAddVersionKey /LANG=1033 "FileDescription" "Print&View PDF launcher"
VIAddVersionKey /LANG=1033 "FileVersion" "${APP_VERSION}"
VIAddVersionKey /LANG=1033 "LegalCopyright" "Print&View PDF contributors"
Function .onInit
  ${GetParameters} $0
  Exec '$\"$EXEDIR\python\pythonw.exe$\" $\"$EXEDIR\app\windows_bootstrap.py$\" $0'
  Quit
FunctionEnd
Section
SectionEnd

@ECHO OFF
set qvsfile=%1
set file_base_name=%2
set qv_executable=%3
set SHEBANGPREFIX=//#!
set QVSEXT=.qvs
set REPLACETEXT=
for /F "delims=" %%i in (%qvsfile%) do (  
  set shebang=%%i
  goto BREAK1
)
:BREAK1
setlocal EnableDelayedExpansion
if "%shebang:~0,4%" == "%SHEBANGPREFIX%" (goto PROCESS_SHEBANG)
set fullfilename=%file_base_name%.qvw  
if exist %fullfilename% (goto :RUNLOAD)
goto FILENOTFOUND
:PROCESS_SHEBANG
set filename=!shebang:%SHEBANGPREFIX%=%REPLACETEXT%!
set fullfilename=%filename%\%file_base_name%.qvw  
if exist %fullfilename% (goto :RUNLOAD)
set fullfilename=%filename%  
if exist %fullfilename% (goto :RUNLOAD)
goto FILENOTFOUND
:RUNLOAD
echo Starting reload with command: %qv_executable% /R /Nodata %fullfilename%
%qv_executable% /R /Nodata %fullfilename%
goto ENDSCRIPT
:FILENOTFOUND
echo File not found: %fullfilename%
:ENDSCRIPT

:: install miktex.org/download
SET PATH=C:\Docfx\;%PATH%
::SET PYTHONPATH=C:\Users\albert\Desktop\Dropbox\Python-DOC\original-EN

:top


::Doxygen
::docfx docfx.json
docfx docfx.json --serve



@echo off
set /p id="Press enter to rebuild the documentation"

goto top
cmd /k pause
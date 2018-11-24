:: install miktex.org/download
:: install Docfx: https://github.com/dotnet/docfx/releases
SET PATH=C:\Docfx\;%PATH%

:top


::Doxygen
::docfx docfx.json
docfx docfx.json --serve



@echo off
set /p id="Press enter to rebuild the documentation"

goto top
cmd /k pause
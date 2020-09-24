:: https://docs.microsoft.com/en-us/nuget/install-nuget-client-tools

nuget pack RoboDkApi.nuspec

IF %ERRORLEVEL% NEQ 0 (
pause
)
pause
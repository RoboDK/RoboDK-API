::pip install nose2
::pip install nose2-html-report
::pip install parameterized
set PATH=C:\RoboDK\Python37\;%PATH%

python -m nose2 test_RobotSim6Axes
report.html

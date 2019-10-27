Requirements: Python 3.7.4

additional modules needed:
nose2 (test runner)
nose2-html-report (html test report)

pip install nose2
pip install nose2-html-report

run pure python unittests:

> python -m unittest -v

run html runner:
> runTests.cmd

runTests.cmd:
python -m nose2
report.html


nose2 config file (nose2.cfg):
[unittest]
plugins = nose2_html_report.html_report

[html-report]
always-on = True




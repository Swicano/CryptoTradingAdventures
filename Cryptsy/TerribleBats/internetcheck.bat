:loop
ping google.com


if errorlevel 1 shutdown -r -t 30 -f
timeout 900

goto loop
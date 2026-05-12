# Wrapper Windows PowerShell para instalar skills
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/GUSTAVOHOOO/gustavohooo-agent-skills/main/scripts/install.py" -OutFile "temp_install.py"
python temp_install.py $args[0]
Remove-Item "temp_install.py"

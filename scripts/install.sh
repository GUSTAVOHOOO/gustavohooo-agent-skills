# Wrapper para instalar skills via comando de uma linha
curl -sSL https://raw.githubusercontent.com/GUSTAVOHOOO/gustavohooo-agent-skills/main/scripts/install.py -o temp_install.py
python3 temp_install.py $1
rm temp_install.py

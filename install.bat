@echo off
echo Installing Clipboard Forensics Tool...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt
echo Installation complete!
echo Run: python src/main.py --gui
pause
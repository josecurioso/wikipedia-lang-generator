import os
from pathlib import Path

os.system("python " + str(Path(__file__).parent / ('./query.py')))
os.system("python " + str(Path(__file__).parent / ('./process-query.py')))
os.system("python " + str(Path(__file__).parent / ('./build-data.py')))
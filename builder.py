# builder.py
import os
import shutil

def build_exe():
    os.system("pyinstaller --onefile main.py")

def clean():
    shutil.rmtree("build", ignore_errors=True)
    shutil.rmtree("dist", ignore_errors=True)
    shutil.rmtree("__pycache__", ignore_errors=True)

if __name__ == "__main__":
    clean()
    build_exe()

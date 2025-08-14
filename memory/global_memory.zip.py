# core/global_memory.py
import zipfile
import os

class GlobalMemory:
    def __init__(self, zip_path="memory/global_memory.zip"):
        self.zip_path = zip_path

    def extract(self, target_dir="memory/global"):
        with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
            zip_ref.extractall(target_dir)

    def list_contents(self):
        with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
            return zip_ref.namelist()

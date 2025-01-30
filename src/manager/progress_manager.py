"""
This module is used to manage the progress and the cookies.

It includes the following classes:
- ProgressManager: to manage the progress
- CookieManager: to manage the cookies
- DatabaseManager: to manage the database
"""
import logging
import os
import time


class ProgressManager:
    def __init__(self, progress_file=".progress.txt"):
        self.progress_file = progress_file

    def save(self, from_iter: int, total: int):
        with open(self.progress_file, "w", encoding="utf-8") as file:
            file.write(f"{from_iter}/{total}/{time.time()}")

    def load(self, total: int) -> int:
        if not os.path.exists(self.progress_file):
            return 0

        with open(self.progress_file, "r", encoding="utf-8") as file:
            last_, totl_, tmst_ = file.read().strip().split("/")
            last, totl = int(last_), int(totl_)

        if time.time() - float(tmst_) < 3600 and totl == total:
            action = input(f"🔍 Progress found, do you want to continue from the last progress ({last}/{totl})? [yes] | no: ").lower()
            if action in {"yes", "y", ""}:
                return last

        return 0



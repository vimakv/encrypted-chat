# =========================
# media_utils.py
# =========================

from tkinter import filedialog
import shutil
import os

UPLOAD_FOLDER = "uploads"


# CHOOSE FILE
def choose_file():

    return filedialog.askopenfilename()


# SAVE FILE
def save_file(file_path):

    if not file_path:

        return None

    filename = os.path.basename(
        file_path
    )

    destination = os.path.join(
        UPLOAD_FOLDER,
        filename
    )

    shutil.copy(
        file_path,
        destination
    )

    return destination


# GET FILE NAME
def get_filename(file_path):

    return os.path.basename(
        file_path
    )
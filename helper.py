import email
import subprocess
from redis import Redis
from rq import Queue
from pathlib import Path

from redmail import outlook
import os
ACSM_FOLDER = './acsm'
EPUB_FOLDER = './epub'
MOBI_FOLDER = './mobi'

PROCESS_LIST = Queue(connection=Redis())

outlook.username = os.environ.get('hotmail')
outlook.password = os.environ.get('hotmail_password')
target_email = os.environ.get('kindle_email')


def remove_drm(filename):
    subprocess.run(["./knock", os.path.join(ACSM_FOLDER, filename)])
    if os.path.exists(os.path.join(ACSM_FOLDER, filename.split(".")[0] + ".epub")):
        ext = ".epub"
    else:
        ext = ".pdf"
    os.rename(os.path.join(ACSM_FOLDER, filename.split(".")[0] + ext), os.path.join(
        EPUB_FOLDER, filename.split(".")[0] + ext))
    PROCESS_LIST.enqueue(convert_epub_to_mobi, filename.split(".")[0] + ext)

def convert_epub_to_mobi(filename):
    subprocess.run(["ebook-convert", os.path.join(EPUB_FOLDER, filename), os.path.join(MOBI_FOLDER, filename.split(".")[0] + ".mobi")])
    PROCESS_LIST.enqueue(email_kindle, filename.split(".")[0] + ".mobi")

def email_kindle(filename):
    outlook.send(
        receivers=[target_email],
        subject="Convert file",
        text=" ",
        attachments={filename: Path(os.path.join(MOBI_FOLDER, filename))}
    )

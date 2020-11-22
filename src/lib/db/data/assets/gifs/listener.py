import os


def png_listener(listdir: list) -> list:
    for file in listdir[:]:
        if not (file.endswith(".png")):
            listdir.remove(file)
    return listdir


def hug_gifs():
    filelist = os.listdir('./hug/')
    png_listener(filelist)
    return filelist

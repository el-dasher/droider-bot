import os


def gif_listener(listdir: list) -> list:
    for file in listdir[:]:
        if not (file.endswith(".gif")):
            listdir.remove(file)

    return listdir


def hug_gifs():
    filelist = os.listdir('./hug/')
    gif_listener(filelist)

    return filelist


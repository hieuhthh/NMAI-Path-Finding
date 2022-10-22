import os
import shutil

def try_make_dir(route):
    try:
        shutil.rmtree(route)
    except:
        pass

    try:
        os.mkdir(route)
    except:
        pass

def unique_list(l):
    list_set = set(l)
    unique_list = (list(list_set))
    return unique_list
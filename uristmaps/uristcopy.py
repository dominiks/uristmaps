import glob, os, shutil

from os.path import join as pjoin

def copy_dir_contents(src, dst):
    """ Copy the contents of the src directory into the dst directory.
    Create the path to the target directory if is does not exist already.
    """
    for item in glob.glob("{}/*".format(src)):
        if os.path.isdir(item):
            copy_dir(item, pjoin(dst, os.path.relpath(item, src)))
        else:
            copy(item, pjoin(dst, os.path.relpath(item, src)))


def copy_dir(src, dst):
    """ Copy the complete directory into the dst directory.

    shutil.copytree should work but it fails when the dst already exists and
    is unable to just overwrite that.
    """
    for root,subdirs,files in os.walk(src):
        for sub in subdirs:
            copy_dir(pjoin(src, sub), pjoin(dst, sub))
        for f in files:
            copy(pjoin(root, f), 
                 pjoin(dst, f))


def copy(src,dst):
    """ Copy a file.
    Using shutil.copyfile directly as an action for the task resulted in
    an exception so here is the copy call in its own function and it
    can also create the target directory if it does not exist.
    """
    dstdir = os.path.dirname(dst)
    if not os.path.exists(dstdir):
        os.makedirs(dstdir)
    shutil.copyfile(src, dst)

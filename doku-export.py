#!/usr/bin/env python3

import os
import sh
import shutil
import re

datadir = "/var/www/dokuwiki/data/"
repodir = "/path/to/repo/"


class Revision():
    pass


def collect_revisions():
    for i in os.walk(datadir + "pages"):
        if i[0].split("/")[-1] in ["wiki", "playground"]:
            continue
        for k in i[2]:
            if k[-4:] != ".txt":
                continue
            pagename = k[:-4]
            with open("{}meta/{}.changes".format(datadir, pagename)) as F:
                for line in F.readlines():
                    values = line.split("\t")
                    r = Revision()
                    r.name = pagename
                    r.time = values[0]
                    r.file = values[3]
                    r.author = values[4]
                    r.note = values[5]
                    yield r


def write_revision(git, r):
    print("writiing revision {} of file {}".format(r.time, r.file))
    rev_file = "{}attic/{}.{}.txt".format(datadir, r.name, r.time)
    if ":" in r.file:
        r.file = r.file.replace(":", "/")
        rev_dir = repodir + "/".join(r.file.split("/")[:-1])
        if not os.path.exists(rev_dir):
            os.makedirs(rev_dir)
    if re.search("(.*) renamed to " + r.file, r.note):
        k = re.search("(.*) renamed to " + r.file, r.note).group(1)
        git.mv(k.replace(":", "/") + ".txt", r.file + ".txt")
    else:
        shutil.copy(rev_file, repodir + r.file + ".txt")
        git.add("-A", repodir)
    if r.note == "":
        r.note = "--"
    if r.author == "":
        r.author = "unknown"
    try:
        git.commit(m="[{}] {}".format(r.file, r.note), date=r.time)
                   #author=r.author + " <email@unknown.com>")
    except Exception as e:
        print(e)


def main():
    revisions = sorted(collect_revisions(), key=lambda x: x.time)
    git = sh.git.bake(_cwd=repodir)
    git.init()
    for i in revisions:
        write_revision(git, i)


main()

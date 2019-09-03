# -*- coding:utf-8 -*-

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>
#
# ----------------------------------------------------------
# Download and setup daily blender build, uncompress
# and create stable symlink using only standard python libs
#
# Author: Stephen Leger (s-leger)
# ----------------------------------------------------------

import requests
import re
import os
import tarfile
import shutil

# relative sub directory from user home
setup_subdir = "Softs"

# link to last downloaded version,  /home/user/setup_subdir/blender-daily
symlink = "blender-daily"


# Absolute setup path under user home folder
dl_path = os.path.join(os.path.expanduser("~"), setup_subdir)

if not os.path.exists(dl_path):
    os.makedirs(dl_path)

# retrieve download link for linux builds
res = requests.get("https://builder.blender.org/download/")
match = re.search(r'''<li class="os linux"><a href=['"]/download/(.*?)\.tar\.bz2['"].*?(?:</a|/)>''', res.text, re.I)

if match:
    filename = match.group(1)
    url = "https://builder.blender.org/download/%s.tar.bz2" % filename
    dl_file = os.path.join(dl_path, "%s.tar.bz2" % filename)
    sym_folder = os.path.join(dl_path, symlink)
    bz_folder = os.path.join(dl_path, filename)
    try:
        shutil.rmtree(bz_folder, ignore_errors=False)
    except:
        pass
    try:
        os.unlink(dl_file)
    except:
        pass
    res = requests.get(url, stream=True)
    fsize = int(res.headers.get('content-length'))
    rsize = 0
    chunk = 1024 * 8
    with open(dl_file, "wb") as f:
        for data in res.iter_content(chunk):
            f.write(data)
            rsize += len(data)
            print("Read %s %%" % (100.0 * rsize / fsize))
    res.close()
    if fsize == rsize:
        tar = tarfile.open(dl_file, "r:bz2")
        tar.extractall(dl_path)
        tar.close()
        try:
            os.unlink(sym_folder)
        except:
            pass
        os.symlink(bz_folder, sym_folder)
        try:
            os.unlink(dl_file)
        except:
            pass

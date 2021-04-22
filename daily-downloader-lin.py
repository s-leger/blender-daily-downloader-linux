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

bl_info = {
    'name': 'Install daily',
    'description': 'Download and setup daily build',
    'author': 's-leger',
    'license': 'GPL',
    'deps': '',
    'version': (0, 0, 3),
    'blender': (2, 80, 0),
    'location': 'search (F3) install daily',
    'warning': '',
    'wiki_url': '',
    'tracker_url': 'https://github.com/s-leger/blender-daily-downloader-linux/issues/',
    'link': 'https://github.com/s-leger/blender-daily-downloader-linux',
    'support': 'COMMUNITY',
    'category': 'Development'
    }

import requests
import re
import os
import tarfile
import shutil
import bpy
from bpy.types import Operator, PropertyGroup
from bpy.props import StringProperty, IntProperty, CollectionProperty


def download_daily(dl_path, symlink, build):
    # Absolute setup path under user home folder

    if not os.path.exists(dl_path):
        os.makedirs(dl_path)

    filename, fileext = build.name, build.fileext

    print(filename)
    url = "https://builder.blender.org/download/%s.tar.%s" % (filename, fileext)
    dl_file = os.path.join(dl_path, "%s.tar.%s" % (filename, fileext))
    sym_folder = os.path.join(dl_path, symlink.strip())
    bz_folder = os.path.join(dl_path, filename)
    print(dl_file)
    print(sym_folder)
    print(bz_folder)

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
            print("Read %.4f %%  " % (100.0 * rsize / fsize), end="\r")
    res.close()
    if fsize == rsize:
        tar = tarfile.open(dl_file, "r:%s" % fileext)
        tar.extractall(dl_path)
        tar.close()
        try:
            os.unlink(sym_folder)
        except:
            pass
        os.symlink(bz_folder, sym_folder)
        # try:
        #    os.unlink(dl_file)
        # except:
        #    pass
        return True
    return False


class SLDAILY_builds(PropertyGroup):
    name: StringProperty(name="Filename")
    fileext: StringProperty(name="Fileext")


class SL_OT_install_daily(Operator):

    bl_idname="sl.install_daily"
    bl_label="Install daily build"
    bl_description = "Install daily build"

    setup_subdir: StringProperty(
        name="Setup directory",
        description="Absolute setup directory (must be writeable)",
        default=os.path.join(os.path.expanduser("~"), "Softs")
    )
    symlink : StringProperty(
        name="symlink",
        description="symlink to last downloaded version",
        default="blender-daily")

    idx: IntProperty(default=0)
    builds: CollectionProperty(type=SLDAILY_builds)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "setup_subdir")
        layout.prop(self, "symlink")
        layout.template_list("UI_UL_list", "SLDAILY_builds", self, "builds", self, "idx")

    def execute(self, context):
        if self.symlink.strip() != "" and self.setup_subdir.strip() != "":
            res = download_daily(self.setup_subdir, self.symlink, self.builds[self.idx])
            if res:
                self.report({"INFO"}, "Setup success")
            else:
                self.report({"WARNING"}, "Setup failed")
        return {'FINISHED'}

    def invoke(self, context, event):

        res = requests.get("https://builder.blender.org/download/")
        match = re.findall(r'''<li class="os linux"><a href=['"]/download/(.*?)\.tar\.([^"]+)['"].*?(?:</a|/)>''',
                           res.text, re.I)

        if match:
            for filename, fileext in match:
                build = self.builds.add()
                build.name = filename
                build.fileext = fileext

            return context.window_manager.invoke_props_dialog(self)
        self.report({"WARNING"}, "No build found")
        return {"CANCELLED"}

def register():
    bpy.utils.register_class(SLDAILY_builds)
    bpy.utils.register_class(SL_OT_install_daily)
    

def unregister():
    bpy.utils.unregister_class(SL_OT_install_daily)
    bpy.utils.unregister_class(SLDAILY_builds)
    

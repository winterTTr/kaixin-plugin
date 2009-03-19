# -*- encoding=utf-8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

from distutils.core import setup
import py2exe


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        # for the versioninfo resources
        self.version = "1.0"
        self.company_name = "Home - -||"
        self.copyright = "LGPL"
        self.name = u"开心网插件 by winterTTr"


target_wx = Target(
        description = u"开心网插件 by winterTTr",
        script = 'main.pyw' , 
        icon_resources = [ ( 1 , "favicon.ico")] ,
        desc_name = "kxPlugin")

setup(  windows = [ target_wx ],
        options = {
            "py2exe" : {   
                "bundle_files": 1 , 
                "compressed" : 1 ,
                "optimize": 2 } } , 
        data_files = [ ('.' , ['request.xml' , 'favicon.ico'] ) ],
        zipfile = None)

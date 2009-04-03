# -*- encoding=utf8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'


from xml.etree import ElementTree as ET
from StringIO import StringIO

class KxPacketHandler:
    def __init__(self , content):
        self.content = content
        self.result = None
        self._anylize()

    def _anylize( self ):
        pass

    def GetResult( self ):
        return self.result





class PHHavest( KxPacketHandler ):
    def _anylize( self ):
        sio = StringIO( self.content )
        sio.seek(0)
        et = ET.ElementTree( file = sio )

        self.result = {}
        self.result['ret'] = True if et.find('ret').text == 'succ' else False
        if self.result['ret'] :
            leftnum = int( et.find('leftnum').text )
            stealnum = int ( et.find('stealnum').text )
            num = int ( et.find('num').text )
            seedname = et.find('seedname').text
            self.result['status'] = u"[植物：%s] [收获%d] [剩余%d]" % ( 
                    seedname , stealnum , leftnum )
        else:
            reason = et.find('reason').text
            self.result['status'] = reason



kxPacketHandler_map = {
        'Harvest': PHHavest , 
        'None'  : None }

# -*- encoding=utf8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

import os , sys , re , operator
import urllib , urllib2 , cookielib
from xml.etree import ElementTree as ET

global_unicode_convert = re.compile( '\\\\u(?P<uchar>[\da-f]{4})')
global_friendslist_x = re.compile( r'"uid":(?P<uid>\d+),"real_name":"(?P<real_name>[\\\da-fu]+)","real_name_unsafe":"(?P<real_name_unsafe>[\\\da-fu]+)"' )

def SendRequest( request_name , **kwdict ):
    global global_local_config_info
    request_info = global_local_config_info['RequestInfo'].getRequestInfo( request_name , **kwdict )
    assert request_info , 'No info for request[%s]' % request_name

    if request_info['params'] :
        params = urllib.urlencode( request_info['params'] )
    else:
        params = None

    resp = None
    if request_info['method'] == 'POST' :
        resp = urllib2.urlopen( url = request_info['url'] , data = params )
    elif request_info['method'] == 'GET' :
        if params:
            target_url =  request_info['url'] + '?' + params
        else:
            target_url = request_info['url']

        resp = urllib2.urlopen( url = target_url )

    if resp and resp.code == 200:
        return resp

    return None

def UnicodeFromStr( s ):
    global global_unicode_convert
    return global_unicode_convert.sub( ( lambda mo : unichr( int(mo.group('uchar') ,16 ) ) ), s )

class kxFriendsList:
    __file_name__ = 'friendslist.xml'
    __xml_index__ = [ 'id' , 'real_name' , 'real_name_unsafe' ]
    def __init__( self ):
        self.flist = [ 0 , u"=自己=" , u"=自己=" ]
        if os.path.exists( self.__file_name__ ):
            self.LoadFromFile()
        else:
            self._getListByRequset()
            self.UpdateToFile()

    def _getListByRequset( self ):
        self.flist = [ 0 , u"=自己=" , u"=自己=" ]
        resp = SendRequest( 'FriendsList' )
        for x in global_friendslist_x.finditer( resp.read() ):
            self.flist.append( 
                    [ 
                        int(x.group('uid') ),  
                        UnicodeFromStr( x.group('real_name') ) , 
                        UnicodeFromStr( x.group('real_name_unsafe') ) , 
                    ])

    def UpdateToFile( self ):
        root = ET.Element('FriendsList')
        for x in self.flist:
            each = ET.SubElement( root , 'person' )
            ET.SubElement( each , self.__xml_index__[0] ).text = str( x[0] )
            ET.SubElement( each , self.__xml_index__[1] ).text = x[1]
            ET.SubElement( each , self.__xml_index__[2] ).text = x[2]

        et = ET.ElementTree( element = root)
        et.write( self.__file_name__ , encoding='utf-8')


    def LoadFromFile( self ):
        self.flist = [ 0 , u"=自己=" , u"=自己=" ]
        et = ET.ElementTree( file = self.__file_name__ )
        for x in et.findall( 'person' ):
            self.flist.append(
                    [
                        int( x.find( self.__xml_index__[0] ).text ),
                        x.find( self.__xml_index__[1] ).text ,
                        x.find( self.__xml_index__[2] ).text ,
                    ] )

    def GetList(self):
        return self.flist

    def GetUserName ( self , id ):
        for x in self.flist:
            if id == x[0] :
                return x[1]

        return u""


class RequestInfoSet:
    def __init__( self ):
        self.ET = None
        self.request_list = None
        self.attrib_list = None

    def loadFromFile( self , filename = 'request.xml' ):
        assert os.path.exists( filename ) , 'there is no config file'
        self.ET = ET.ElementTree( file = filename )
        self.request_list = self.ET.find('request_list')
        self.attrib_list = self.ET.find('attrib_list')

    def getRequestInfo( self , request_name , **kwdict ):
        req_list = self.request_list.findall( 'request' )
        for item in req_list:
            if item.find('name').text == request_name:
                break
        else:
            return {}
        return self._makeResultDict( item , **kwdict )

    def getBasicAttribList( self ):
        return self._makeAttribList( 'basic' )


    def getExtentAttribList( self ):
        return self._makeAttribList( 'extent' )

    def getAttribList( self ):
        return self._makeAttribList( 'basic' ) + self._makeAttribList( 'extent' )

    def _makeResultDict( self , element , **kwdict ):
        result_dict = {}
        for ch in element._children :
            if ch.tag in ['name' , 'url' , 'method']:
                result_dict[ch.tag] = ch.text
            elif ch.tag == 'params':
                result_dict['params'] = {}
                for x in ch._children :
                    if x.attrib.get('input') == '1':
                        if x.tag == 'verify':
                            result_dict['params'][x.tag] = global_network_operator.verify
                        else:
                            result_dict['params'][x.tag] = kwdict[x.tag]
                    else:
                        result_dict['params'][x.tag] = x.text
            else:
                assert 0 , 'Find one invalid request attrib'

        return result_dict

    def _makeAttribList( self , list_name ):
        result_list = []
        for x in self.attrib_list.find(list_name)._children:
            result_list.append( x.text )
        return result_list

class NetworkOperator :
    def __init__ ( self ):
        self.verify = ''

    def login( self , email , passwd ):
        # Process Cookie
        cookie_jar = cookielib.LWPCookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor( cookie_jar )
        cookie_opener = urllib2.build_opener( cookie_handler )
        urllib2.install_opener( cookie_opener )

        # Login
        SendRequest( 'Login' , email = email , password = passwd)

        # get verify
        resp = SendRequest( 'Verify' )
        content = resp.read()
        self.verify = re.search( 'var g_verify = "(?P<verify>.*)";' , content ).group('verify')

        # getFriends List
        self.friends_list = kxFriendsList()
        return True

    def logout( self ):
        SendRequest( 'Logout' )
        return True

class SettingsInfoSet:
    #__garden_tags__ = ['water' , 'antigrass' , 'antivermin' ,'farm' , 'havest' , 'steal']
    __garden_tags__ = [ 
            [ u"浇水" , 'water'], 
            [ u"除草" , 'antigrass'], 
            [ u"捉虫" , 'antivermin'], 
            [ u"耕地" , 'farm'],
            [ u"收获" , 'havest'],
            [ u"偷菜" , 'steal']]
    def __init__(self):
        self.gardenInfo = {}
        for x in map( operator.itemgetter(1) , self.__garden_tags__ ):
            self.gardenInfo[x] = {}
            self.gardenInfo[x]['do'] = 0
            self.gardenInfo[x]['list'] = []

    def loadFromFile( self , file = 'setting.xml' ):
        if not os.path.exists( file ):
            return

        et = ET.ElementTree( file = file )
        garden_root = et.find('garden')

        # garden section
        for tag in map( operator.itemgetter(1) , self.__garden_tags__ ):
            # init
            self.gardenInfo[tag]['do'] = 0
            self.gardenInfo[tag]['list'] = []
            # reading
            x = garden_root.find(tag)
            self.gardenInfo[tag]['do'] = int ( x.find('do').text )
            for each in x.findall('list/id'):
                self.gardenInfo[tag]['list'].append( int( each.text ) )

    def UpdateToFile( self , file = 'setting.xml' ):
        root = ET.Element('setting')

        # garden section
        garden_root = ET.SubElement( root , 'garden' )
        for x in map( operator.itemgetter(1) , self.__garden_tags__ ):
            item_root = ET.SubElement( garden_root , x )
            ET.SubElement( item_root , 'do').text = str( self.gardenInfo[x]['do'] )
            list_root = ET.SubElement( item_root , 'list' )
            for each in self.gardenInfo[x]['list']:
                ET.SubElement( list_root , 'id').text = str( each )

        et = ET.ElementTree( element = root)
        et.write( file , encoding='utf-8')

    def GetGardenUserList( self , action_type ):
        return self.gardenInfo[action_type]['list']

global_local_config_info = {
        'RequestInfo' : RequestInfoSet() ,
        'SettingsInfo'  : SettingsInfoSet() }

global_network_operator = NetworkOperator()






        


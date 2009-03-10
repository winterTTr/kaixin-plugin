# -*- encoding=utf8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

import os
import sys
import urllib
import urllib2
from xml.etree import ElementTree as ET
import re

global_unicode_convert = re.compile( '\\\\u(?P<uchar>[\da-f]{4})')
global_friendslist_x = re.compile( r'"uid":(?P<uid>\d+),"real_name":"(?P<real_name>[\\\da-fu]+)","real_name_unsafe":"(?P<real_name_unsafe>[\\\da-fu]+)"' )

def SendRequest( request_name , **kwdict ):
    global global_config_info
    request_info = global_config_info.getRequestInfo( request_name , **kwdict )
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

class ConfigureInfoLocal:
    def __init__( self ):
        self.ET = None
        self.request_list = None
        self.attrib_list = None

    def loadFromFile( self , filename ):
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
                            result_dict['params'][x.tag] = global_network_config_info.verify
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

class ConfigureInfoNetwork :
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
        resp = kxData.SendRequest( 'Verify' )
        content = resp.read()
        self.verify = re.search( 'var g_verify = "(?P<verify>.*)";' , content ).group('verify')

    def logout( self ):
        kxData.SendRequest( 'Logout' )


global_local_config_info = ConfigureInfoLocal()
global_network_config_info = ConfigureInfoNetwork()



class kxFriendsList:
    __file_name__ = 'friendslist.xml'
    __xml_index__ = [ 'id' , 'real_name' , 'real_name_unsafe' ]
    def __init__( self ):
        self.flist = []
        if os.path.exists( self.__file_name__ ):
            self._loadFromFile()
        else:
            self._getListByRequset()

    def _getListByRequset( self ):
        self.flist = []
        resp = SendRequest( 'FriendsList' )
        for x in global_friendslist_x.finditer( resp.read() ):
            self.flist.append( 
                    [ 
                        int(x.group('uid') ),  
                        UnicodeFromStr( x.group('real_name') ) , 
                        UnicodeFromStr( x.group('real_name_unsafe') )
                    ])
        root = ET.Element('FriendsList')
        for x in self.flist:
            each = ET.SubElement( root , 'person' )
            ET.SubElement( each , self.__xml_index__[0] ).text = str( x[0] )
            ET.SubElement( each , self.__xml_index__[1] ).text = x[1]
            ET.SubElement( each , self.__xml_index__[2] ).text = x[2]

        et = ET.ElementTree( element = root)
        et.write( self.__file_name__ , encoding='utf-8')



    def _loadFromFile( self ):
        self.flist = []
        et = ET.ElementTree( file = self.__file_name__ , )
        for x in et.findall( 'person' ):
            self.flist.append(
                    [
                        int( x.find( __xml_index__[0] ).text ),
                        x.find( __xml_index__[0] ).text ,
                        x.find( __xml_index__[1] ).text ,
                        x.find( __xml_index__[2] ).text 
                    ] )

    def getList(self):
        return self.flist



        


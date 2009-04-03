# -*- encoding=utf8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

import os , sys , re , operator
import urllib , urllib2 , cookielib
from xml.etree import ElementTree as ET
from kxPacketHandler import kxPacketHandler_map
import time
import sqlite3

global_unicode_convert = re.compile( '\\\\u(?P<uchar>[\da-f]{4})')
global_friendslist_x = re.compile( r'"uid":(?P<uid>\d+),"real_name":"(?P<real_name>[\\\da-fu]+)","real_name_unsafe":"(?P<real_name_unsafe>[\\\da-fu]+)"' )



def UnicodeFromStr( s ):
    global global_unicode_convert
    return global_unicode_convert.sub( ( lambda mo : unichr( int(mo.group('uchar') ,16 ) ) ), s )

class kxConfigDB:
    __file_name__ = 'kxConfig.db'
    def __init__( self , db_file = None ):
        self.db_file = db_file if db_file else self.__file_name__

        is_file_exist =  os.path.exists( self.db_file )
        self.con = sqlite3.connect( self.db_file )

        if not is_file_exist:
            self._create_tables()

    def SetAccount( self , email , password ):
        cur = self.con.cursor()
        cur.execute( 'SELECT count(*) FROM account WHERE email=?' , (email,) )
        is_exist = cur.fetchone()[0]
        if is_exist:
            cur.execute('UPDATE account SET password=?' , ( password,) )
        else:
            cur.execute('INSERT INTO account VALUES (NULL , ?,?,0,0,0,0)' , ( email , password) )

        self.con.commit()

    def GetAID( self , email ):
        cur = self.con.cursor()
        cur.execute( 'SELECT id FROM account WHERE email=?' , (email,))
        return cur.fetchone()[0]

    def GetEmail( self , aid ):
        cur = self.con.cursor()
        cur.execute( 'SELECT email FROM account WHERE id=?' , (aid,))
        return cur.fetchone()[0]

    def GetUserList( self , **kwdict ):
        try :
            aid = kwdict['aid']
        except:
            aid = self.GetAID( kwdict['email'] )

        cur = self.con.cursor()
        cur.execute( 'SELECT uid , real_name FROM config where aid=?' , ( aid , ) )
        return cur.fetchall()


    def UpdateUserInfo( self , **kwdict ):
        try :
            aid = kwdict['aid']
        except:
            aid = self.GetAID( kwdict['email'] )

        nwo = NetworkOperator( aid )
        nwo.Login()
        resp = nwo.SendRequest( 'FriendsList' )

        cur = self.con.cursor()
        # add self
        self._insert_user_info( 
                uid = 0 , 
                aid = aid , 
                real_name=u'自己' , 
                real_name_unsafe=u'自己' , 
                water = 0 ,
                antigrass = 0 ,
                antivermin = 0 ,
                harvest = 0 )

        # add friends list
        for x in global_friendslist_x.finditer( resp.read() ):
            self._insert_user_info( 
                uid = int(x.group('uid') ) , 
                aid = aid , 
                real_name= UnicodeFromStr( x.group('real_name') ) , 
                real_name_unsafe= UnicodeFromStr( x.group('real_name_unsafe') ), 
                water = 0 ,
                antigrass = 0 ,
                antivermin = 0 ,
                harvest = 0 )

        nwo.Logout()
        self.con.commit()


    def _insert_user_info( self , **kwdict ):
        cur = self.con.cursor()
        cur.execute( 
                'SELECT count(*) FROM config WHERE uid=:uid and aid=:aid' , 
                kwdict )
        is_exist = cur.fetchone()[0]

        if is_exist :
            return

        cur.execute(
                'INSERT INTO config VALUES( :uid , :aid , :real_name , :real_name_unsafe , :water , :antigrass , :antivermin , :harvest)', kwdict )
        self.con.commit()



    def GetPassowrd( self , aid ):
        cur = self.con.cursor()
        cur.execute('SELECT password FROM account WHERE id=?', (aid , ))
        return cur.fetchone()[0]


    def _create_tables( self ):
        cur = self.con.cursor()
        cur.executescript("""
                CREATE TABLE account 
                ( 
                id INTEGER NOT NULL PRIMARY KEY , 
                email TEXT UNIQUE, 
                password TEXT ,
                do_water INTEGER , 
                do_antigrass INTEGER , 
                do_antivermin INTEGER , 
                do_harvest INTEGER );

                CREATE TABLE config  
                ( 
                uid INTEGER , 
                aid INTEGER ,
                real_name TEXT , 
                real_name_unsafe TEXT ,
                water INTEGER ,
                antigrass INTEGER , 
                antivermin INTEGER , 
                harvest INTEGER 
                );
                """)
        self.con.commit()

    def __del__(self):
        self.con.commit()
        self.con.close()

#class kxFriendsList:
#    __file_name__ = 'friendslist.xml'
#    __xml_index__ = [ 'id' , 'real_name' , 'real_name_unsafe' ]
#    def __init__( self ):
#        if os.path.exists( self.__file_name__ ):
#            self.LoadFromFile()
#        else:
#            self._getListByRequset()
#            self.UpdateToFile()
#
#    def _getListByRequset( self ):
#        self.flist = [ [ 0 , u"=自己=" , u"=自己=" ] ]
#        resp = SendRequest( 'FriendsList' )
#        for x in global_friendslist_x.finditer( resp.read() ):
#            self.flist.append( 
#                    [ 
#                        int(x.group('uid') ),  
#                        UnicodeFromStr( x.group('real_name') ) , 
#                        UnicodeFromStr( x.group('real_name_unsafe') ) , 
#                    ])
#
#    def UpdateToFile( self ):
#        root = ET.Element('FriendsList')
#        for x in self.flist:
#            each = ET.SubElement( root , 'person' )
#            ET.SubElement( each , self.__xml_index__[0] ).text = str( x[0] )
#            ET.SubElement( each , self.__xml_index__[1] ).text = x[1]
#            ET.SubElement( each , self.__xml_index__[2] ).text = x[2]
#
#        et = ET.ElementTree( element = root)
#        et.write( self.__file_name__ , encoding='utf-8')
#
#
#    def LoadFromFile( self ):
#        self.flist = []
#        et = ET.ElementTree( file = self.__file_name__ )
#        for x in et.findall( 'person' ):
#            self.flist.append(
#                    [
#                        int( x.find( self.__xml_index__[0] ).text ),
#                        x.find( self.__xml_index__[1] ).text ,
#                        x.find( self.__xml_index__[2] ).text ,
#                    ] )
#
#    def GetList(self):
#        return self.flist
#
#    def GetUserName ( self , id ):
#        for x in self.flist:
#            if id == x[0] :
#                return x[1]
#
#        return u""


class RequestInfoSet:
    def __init__( self ):
        self.ET = None
        self.request_list = None
        self.attrib_list = None
        self.loadFromFile()

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
                        if kwdict.has_key(x.tag):
                            result_dict['params'][x.tag] = kwdict[x.tag]
                        else:
                            assert 0 , 'Key Error!'
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

global_request_info_set = RequestInfoSet()

class NetworkOperator :
    def __init__ ( self , aid ):
        self.verify = ''
        self.aid = aid

        # Process Cookie
        cookie_jar = cookielib.LWPCookieJar()
        cookie_handler = urllib2.HTTPCookieProcessor( cookie_jar )
        self.urlopen = urllib2.build_opener( cookie_handler ).open

    def Login( self ):
        # Get Password

        db = kxConfigDB()
        # Login
        self.SendRequest( 
                'Login' , 
                email = db.GetEmail( self.aid ) , 
                password = db.GetPassowrd( self.aid) )

        # get verify
        resp = self.SendRequest( 'Verify' )
        content = resp.read()
        self.verify = re.search( 'var g_verify = "(?P<verify>.*)";' , content ).group('verify')

        # getFriends List
        return True

    def Logout( self ):
        self.SendRequest( 'Logout' )
        return True

    def SendRequest( self , request_name , **kwdict ):
        kwdict['verify'] = self.verify
        request_info = global_request_info_set.getRequestInfo( request_name , **kwdict )
        assert request_info , 'No info for request[%s]' % request_name

        if request_info['params'] :
            params = urllib.urlencode( request_info['params'] )
        else:
            params = None

        resp = None
        sleep_time = 1
        #while True:
        #    try :
        if request_info['method'] == 'POST' :
            time.sleep(sleep_time)
            resp = self.urlopen( fullurl = request_info['url'] , data = params )

            #break
        elif request_info['method'] == 'GET' :
            if params:
                target_url =  request_info['url'] + '?' + params
            else:
                target_url = request_info['url']

            time.sleep(sleep_time)
            resp = self.urlopen( fullurl = target_url )
            #break
        #    except urllib2.HTTPError , e :
        #        open( 'error.txt', 'a' ).write( str(e) )
        #        sleep_time = 2



        if resp and resp.code == 200:
            if kxPacketHandler_map.has_key( request_name ):
                return kxPacketHandler_map[request_name]( resp.read() ).GetResult()
            return resp

        return None

class FarmSettingsInfoSet:
    __garden_tags__ = [ 
            [ u"浇水" , 'water'], 
            [ u"除草" , 'antigrass'], 
            [ u"捉虫" , 'antivermin'], 
            #[ u"耕地" , 'farm'],
            [ u"收获/偷菜" , 'harvest']]
    def __init__(self , aid ):
        self.aid = aid
        self.db = kxConfigDB()

    def GetIfAction( self , tag ):
        cur =self.db.con.cursor()
        cur.execute( 'SELECT do_%s FROM account where id=?' % tag , ( self.aid ,) )
        return cur.fetchone()[0] == 1 

    def GetActionPerUser( self , tag , uid ):
        cur =self.db.con.cursor()
        cur.execute( 'SELECT %s FROM config where uid=? and aid=? ' % tag , ( uid , self.aid ) )
        return cur.fetchone()[0]

    def SetActionPerUser( self , tag , uid , value ):
        cur =self.db.con.cursor()
        cur.execute( 'UPDATE config SET %s=? where aid=? and uid=? ' % tag , ( value , self.aid , uid ) )
        self.db.con.commit()

    def SetActionAll( self , tag , value ):
        cur =self.db.con.cursor()
        cur.execute( 'UPDATE config SET %s=? where aid=? ' % tag , ( value , self.aid ) )
        self.db.con.commit()

    def SetIfAction( self , tag , value  ):
        cur =self.db.con.cursor()
        cur.execute( 'UPDATE account SET do_%s = ? where id=?' % tag , ( value , self.aid ) )
        self.db.con.commit()

    def GetDoUser( self , tag ):
        cur =self.db.con.cursor()
        cur.execute( 'SELECT uid FROM config where aid=? and %s=1' % tag , ( self.aid ,) )
        return  map( operator.itemgetter(0) , cur.fetchall() )







        


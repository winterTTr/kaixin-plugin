# -*- encoding=utf-8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'


import wx
import sys 
from StringIO import StringIO
from xml.etree import ElementTree as ET
import kxData
import re

from wx.lib.mixins.listctrl import CheckListCtrlMixin , ListCtrlAutoWidthMixin

class PageFriendsList(wx.Panel):
    def __init__(self, parent ):
        wx.Panel.__init__(self, parent)



class CropsListFrame( wx.Frame ):
    def __init__( self , config_file_name = 'config.xml' ):
        wx.Frame.__init__( 
                self , 
                parent = None , 
                id = -1 , 
                title = u'开心菜园外挂 by winterTTr' ,
                size = ( 800 , 600 ) )

        self.panel = wx.Panel( self )
        self.notebook = wx.Notebook( self.panel )

        self.notebook.AddPage( PageFriendsList( self.notebook ) , u"好友设置")
        self.notebook.AddPage( PageFriendsList( self.notebook ) , u"自动执行")

        self.sizer = wx.BoxSizer()
        self.sizer.Add( self.notebook , 1 , wx.EXPAND )
        self.panel.SetSizer( self.sizer )

        # init configure
        #kxData.global_config_info.loadFromFile( config_file_name )
        
        ## create list
        #self.list_ctrl = wx.ListCtrl( 
        #        self , 
        #        -1 , 
        #        style = wx.LC_SINGLE_SEL | wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES )

        ## int header
        #index = 0 
        ##for x in kxData.global_config_info.getAttribList():
        ##    self.list_ctrl.InsertColumn( index , x , wx.LIST_FORMAT_LEFT , width )
        ##    index += 1
        #for x in [ [u"主人ID" , 100] , [u"主人" , 100] , [ u"成熟蔬菜id" , 100 ] , [ u"蔬菜状态" , 400] ]: 
        #    self.list_ctrl.InsertColumn( index , x[0] , wx.LIST_FORMAT_LEFT , x[1] )
        #    index += 1

        ## Bind Event
        #self.Bind(wx.EVT_CLOSE, self.on_close)

        ## Get email and passwd
        #self.email = wx.GetTextFromUser( 
        #        'Email:' , 
        #        'Acount Information[Email]' , 
        #        'winterTTr@hotmail.com' , 
        #        self)
        #self.passwd = wx.GetPasswordFromUser(
        #        'Password:',
        #        'Acount Information[Password]',
        #        'kaixin1983',
        #        self)

        #if self.email == '' or self.passwd == '':
        #    assert 0 , 'Invalid email or password'

        ## Login
        #self.Login( self.email , self.passwd )
        #self.GetVerify()
        ## getFriendlist
        #self.flist = kxData.kxFriendsList()


        ##self.UpdateListInfo()


    def UpdateListInfo( self ):
        for f_index in [ [ 0 , u"自己" , u"自己"] ] + self.flist.getList() :
        #for f_index in [ [ 4287324 , u"自己" , u"自己"] ] :
            resp = kxData.SendRequest( 'CropInfo' , fuid = f_index[0] , verify = self.verify )
            sio = StringIO( resp.read() )
            sio.seek(0)
            if sio.getvalue()[0] != '<' :
                continue
            analyzor = ET.ElementTree( file = sio )
            sio.close()

            item_list = analyzor.findall('garden/item')

            for x in item_list:
                if x.find('cropsid').text !='0' :
                    if x.find('grow').text == x.find('totalgrow').text :
                    #if True:
                        if x.find('status').text == '1' and x.find('cropsstatus').text != '3' :
                            item_index = self.list_ctrl.InsertStringItem( sys.maxint , "" )
                            self.list_ctrl.SetStringItem( item_index , 0 ,  unicode( f_index[0] ) )
                            self.list_ctrl.SetStringItem( item_index , 1 , f_index[1]  )
                            self.list_ctrl.SetStringItem( item_index , 2 , x.find('farmnum').text  )
                            try:
                                self.list_ctrl.SetStringItem( 
                                    item_index , 
                                    3 , 
                                    re.sub( r'<font.*>([^<]*)</?font>' , r'\1' ,  x.find('crops').text ) )
                            except:
                                continue


            #    for i , attrib in enumerate( kxData.global_config_info.getBasicAttribList() ):
            #        self.list_ctrl.SetStringItem( item_index , i , x.find(attrib).text )

            #    if x.find( 'cropsid' ).text != '0':
            #        for i1 , attrib in enumerate( kxData.global_config_info.getExtentAttribList() ):
            #            self.list_ctrl.SetStringItem( item_index , i + i1 + 1 , x.find(attrib).text )



    def on_close( self , event ):
        # Logout
        #resp = kxData.SendRequest('Logout' )
        self.Destroy()


if __name__ == "__main__":
    app = wx.PySimpleApp()
    mainFrame = CropsListFrame()
    mainFrame.Show()
    app.MainLoop()





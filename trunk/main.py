# -*- encoding=utf-8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'


import wx , sys , re
import kxData
from StringIO import StringIO
from xml.etree import ElementTree as ET
from wx.lib.mixins.listctrl import CheckListCtrlMixin , ListCtrlAutoWidthMixin

class CheckListCtrl(wx.ListCtrl, CheckListCtrlMixin, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style= wx.LC_SINGLE_SEL | wx.LC_REPORT | wx.SUNKEN_BORDER)
        CheckListCtrlMixin.__init__(self)
        ListCtrlAutoWidthMixin.__init__(self)
        self.list_manager = None


    def SetListManager( self , lm ):
        self.list_manager = lm

    def OnCheckItem( self , index , check ):
        id = int ( self.GetItem( index , 1 ).GetText() )
        self.list_manager.SetSteal( id , check )

    def UpdateList( self ):
        self.DeleteAllItems()
        for index , content in enumerate ( self.list_manager.GetList() ): 
            self.InsertStringItem( sys.maxint , '' )
            self.SetStringItem( index , 0 ,  content[1] )
            self.SetStringItem( index , 1 ,  unicode ( content[0] ) )
            if content[3] == 1:
                self.CheckItem( index , True )
        




class PageFriendsList(wx.Panel):
    def __init__(self, parent ):
        wx.Panel.__init__(self, parent)
        sizer = wx.BoxSizer()
        self.SetSizer ( sizer )
        
        # create list
        self.list_ctrl = CheckListCtrl( self )
        sizer.Add( self.list_ctrl , 1 , wx.EXPAND | wx.ALL , 10 )

        index = 0
        for x in [  [u"主人" , 200 ] , [u"主人ID" , 200] ]: 
            self.list_ctrl.InsertColumn( index , x[0] , wx.LIST_FORMAT_LEFT , x[1] )
            index += 1

    def UpdateList( self ):
        self.list_ctrl.UpdateList()

    def SetDataManager( self , lm ):
        self.list_ctrl.SetListManager( lm )

class PageAutoAction(wx.Panel):
    def __init__( self  ,parent ):
        wx.Panel.__init__( self , parent )

        # sizer
        main_box = wx.BoxSizer( wx.HORIZONTAL )
        left_box = wx.BoxSizer( wx.VERTICAL )

        interval_box = wx.BoxSizer( wx.HORIZONTAL )
        self.static_interval = wx.StaticText( self , wx.ID_ANY , u"间隔"  , size = ( 40 , 20 ) )
        self.edit_interval = wx.TextCtrl( self , wx.ID_ANY , size = ( 200 , 20 ) )
        interval_box.Add( self.static_interval , 0  , wx.ALIGN_LEFT | wx.ALIGN_TOP )
        interval_box.Add(  ( 50 , -1 ) )
        interval_box.Add( self.edit_interval , 1 , wx.ALIGN_LEFT | wx.ALIGN_TOP )

        button_box = wx.BoxSizer( wx.HORIZONTAL )
        self.button_start = wx.Button( self , wx.ID_ANY , u"执行" )
        self.button_stop = wx.Button( self , wx.ID_ANY , u"停止" )
        button_box.Add( (200 , -1 )  )
        button_box.Add( self.button_start , 0 , wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM  )
        button_box.Add( ( 10 , -1 )  )
        button_box.Add( self.button_stop , 0 , wx.ALIGN_RIGHT | wx.ALIGN_BOTTOM  )

        self.edit_log = wx.TextCtrl( self , wx.ID_ANY , style = wx.TE_MULTILINE )
        self.edit_log.SetBackgroundColour( '#ededed' )

        left_box.Add( interval_box , 1 , wx.TOP | wx.LEFT   , 10)
        left_box.Add( button_box , 1 , wx.BOTTOM | wx.RIGHT   , 10)

        main_box.Add( left_box , 1 , wx.ALL | wx.EXPAND , 10 )
        main_box.Add( self.edit_log , 1 , wx.ALL | wx.EXPAND, 10 )

        self.SetSizer( main_box )


class CropsListFrame( wx.Frame ):
    def __init__( self  ):
        wx.Frame.__init__( 
                self , 
                parent = None , 
                id = -1 , 
                style = wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU, 
                title = u'开心菜园外挂 by winterTTr' ,
                size = ( 800 , 600 ) )

        ### ========== Init UI
        # create item
        self.panel = wx.Panel( self )
        self.notebook = wx.Notebook( self.panel )
        self.page_friendslist = PageFriendsList( self.notebook )
        self.page_auto_action = PageAutoAction( self.notebook )

        # setup item
        self.notebook.AddPage( self.page_friendslist , u"好友设置")
        self.notebook.AddPage( self.page_auto_action , u"执行")

        # arrange item
        self.sizer = wx.BoxSizer()
        self.sizer.Add( self.notebook , 1 , wx.EXPAND )
        self.panel.SetSizer( self.sizer )


        ### ========== Init Inner Data
        # Get name and passwd
        email = wx.GetTextFromUser( 
                'Email:' , 
                'Acount Information[Email]' , 
                'winterTTr@hotmail.com' , 
                self)
        passwd = wx.GetPasswordFromUser(
                'Password:',
                'Acount Information[Password]',
                'kaixin1983',
                self)
        if email == '' or passwd == '':
            assert 0 , 'Invalid email or password'
        # init configure
        kxData.global_local_config_info.loadFromFile()
        kxData.global_network_config_info.login( 
                email = email ,
                passwd = passwd)
        
        ### ========== Bind Event
        self.Bind(wx.EVT_CLOSE, self.on_close)

        ### ========== Update UI
        self.page_friendslist.SetDataManager( kxData.global_network_config_info.friends_list )
        self.UpdateListInfo()


    def UpdateListInfo( self ):
        self.page_friendslist.UpdateList()
        #for f_index in [ [ 0 , u"自己" , u"自己"] ] + self.flist.getList() :
        ##for f_index in [ [ 4287324 , u"自己" , u"自己"] ] :
        #    resp = kxData.SendRequest( 'CropInfo' , fuid = f_index[0] , verify = self.verify )
        #    sio = StringIO( resp.read() )
        #    sio.seek(0)
        #    if sio.getvalue()[0] != '<' :
        #        continue
        #    analyzor = ET.ElementTree( file = sio )
        #    sio.close()

        #    item_list = analyzor.findall('garden/item')

        #    for x in item_list:
        #        if x.find('cropsid').text !='0' :
        #            if x.find('grow').text == x.find('totalgrow').text :
        #            #if True:
        #                if x.find('status').text == '1' and x.find('cropsstatus').text != '3' :
        #                    item_index = self.list_ctrl.InsertStringItem( sys.maxint , "" )
        #                    self.list_ctrl.SetStringItem( item_index , 0 ,  unicode( f_index[0] ) )
        #                    self.list_ctrl.SetStringItem( item_index , 1 , f_index[1]  )
        #                    self.list_ctrl.SetStringItem( item_index , 2 , x.find('farmnum').text  )
        #                    try:
        #                        self.list_ctrl.SetStringItem( 
        #                            item_index , 
        #                            3 , 
        #                            re.sub( r'<font.*>([^<]*)</?font>' , r'\1' ,  x.find('crops').text ) )
        #                    except:
        #                        continue


        #    #    for i , attrib in enumerate( kxData.global_config_info.getBasicAttribList() ):
        #    #        self.list_ctrl.SetStringItem( item_index , i , x.find(attrib).text )

        #    #    if x.find( 'cropsid' ).text != '0':
        #    #        for i1 , attrib in enumerate( kxData.global_config_info.getExtentAttribList() ):
        #    #            self.list_ctrl.SetStringItem( item_index , i + i1 + 1 , x.find(attrib).text )



    def on_close( self , event ):
        # Logout
        kxData.global_network_config_info.friends_list.UpdateToFile()
        kxData.global_network_config_info.logout()
        self.Destroy()


if __name__ == "__main__":
    app = wx.PySimpleApp()
    mainFrame = CropsListFrame()
    mainFrame.Show()
    app.MainLoop()





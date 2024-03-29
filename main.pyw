# -*- encoding=utf-8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

import wx , sys , re , os 
#import wx.aui
import kxData
from StringIO import StringIO
from xml.etree import ElementTree as ET

from kxPages import PageGarden , PageAction ,PageActionOnTime , PageAbout

class KxPluginFrame( wx.Frame ):
    def __init__( self  ):
        wx.Frame.__init__( 
                self , 
                parent = None , 
                id = -1 , 
                style = wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.MINIMIZE_BOX, 
                title = u'开心网外挂 by winterTTr' ,
                size = ( 800 , 600 ) )

        ### ========== Init Inner Data
        # Get name and passwd
        passwd_file = 'passwd.txt'
        if os.path.exists(passwd_file):
            lines = open( passwd_file ).readlines()
            if len( lines ) < 2:
                wx.MessageDialog( self, u"无效的passwd.txt文件！" , u"警告" , wx.OK |wx.ICON_EXCLAMATION ).ShowModal()
                os.exit(1)
            email , passwd = map( lambda x : x[:-1] if x[-1] == '\n' else x , lines[:2] )
        else: 
            email = wx.GetTextFromUser( 
                    'Email:' , 
                    'Acount Information[Email]' , 
                    '' , 
                    self)
            passwd = wx.GetPasswordFromUser(
                    'Password:',
                    'Acount Information[Password]',
                    '',
                    self)
        if email == '' or passwd == '':
            wx.MessageDialog( self, u"无效的用户名或者密码！" , u"警告" , wx.OK |wx.ICON_EXCLAMATION ).ShowModal()
            sys.exit(1)
        ## init configure
        kxData.global_request_info_set.loadFromFile()
        #kxData.global_local_config_info['SettingsInfo'].loadFromFile()
        db = kxData.kxConfigDB()
        db.SetAccount( email = email , password = passwd )
        db.UpdateUserInfo( email = email )

        ### ========== Init UI
        # create item
        self.tbicon = wx.TaskBarIcon()
        icon = wx.Icon("favicon.ico", wx.BITMAP_TYPE_ICO)
        self.SetIcon( icon )
        self.tbicon.SetIcon( icon , u'开心网外挂')



        self.panel = wx.Panel( self )
        self.notebook = wx.Notebook( self.panel )
        #self.notebook = wx.aui.AuiNotebook( self.panel )
        self.page_garden = PageGarden( self.notebook )
        self.page_action = PageAction( self.notebook )
        self.page_do_ontime = PageActionOnTime( self.notebook)
        self.page_about = PageAbout( self.notebook)

        # setup item
        self.notebook.AddPage( self.page_garden , u"开心花园")
        self.notebook.AddPage( self.page_action , u"运行")
        self.notebook.AddPage( self.page_do_ontime , u"定时收获")
        self.notebook.AddPage( self.page_about , u"关于")

        # arrange item
        sizer = wx.BoxSizer()
        sizer.Add( self.notebook , 1 , wx.EXPAND )
        self.panel.SetSizer( sizer )


        #### ========== Bind Event
        self.Bind(wx.EVT_CLOSE, self.on_close)
        wx.EVT_TASKBAR_LEFT_DCLICK( self.tbicon , self.OnTaskBarDoubleClick )
        self.Bind( wx.EVT_ICONIZE , self.on_icon )

        #### ========== Update UI
        #self.UpdateListInfo()


    def UpdateListInfo( self ):
        pass


    def on_close( self , event ):
        # Logout
        self.tbicon.Destroy()
        self.Destroy()

    def on_icon( self , event ):
        if self.IsIconized():
            self.Hide()



    def OnTaskBarDoubleClick( self , event ):
        if self.IsShown():
            self.Hide()
        else:
            self.Show()
            self.Restore()


if __name__ == "__main__":
    app = wx.PySimpleApp()
    mainFrame = KxPluginFrame()
    mainFrame.Show()
    app.MainLoop()





# -*- encoding=utf-8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

import wx , sys , re , os
import kxData
from StringIO import StringIO
from xml.etree import ElementTree as ET

from kxPages import PageGarden , PageAction

class KxPluginFrame( wx.Frame ):
    def __init__( self  ):
        wx.Frame.__init__( 
                self , 
                parent = None , 
                id = -1 , 
                style = wx.CAPTION | wx.CLOSE_BOX | wx.SYSTEM_MENU, 
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
            wx.MessageDialog( self, u"未输入用户名或者密码！" , u"警告" , wx.OK |wx.ICON_EXCLAMATION ).ShowModal()
            os.exit(1)
        ## init configure
        kxData.global_local_config_info['RequestInfo'].loadFromFile()
        kxData.global_local_config_info['SettingsInfo'].loadFromFile()
        kxData.global_network_operator.login( 
                email = email ,
                passwd = passwd)

        ### ========== Init UI
        # create item
        self.panel = wx.Panel( self )
        self.notebook = wx.Notebook( self.panel )
        self.page_garden = PageGarden( self.notebook )
        self.page_action = PageAction( self.notebook )

        # setup item
        self.notebook.AddPage( self.page_garden , u"开心花园")
        self.notebook.AddPage( self.page_action , u"执行")

        # arrange item
        sizer = wx.BoxSizer()
        sizer.Add( self.notebook , 1 , wx.EXPAND )
        self.panel.SetSizer( sizer )


        #### ========== Bind Event
        self.Bind(wx.EVT_CLOSE, self.on_close)

        #### ========== Update UI
        #self.UpdateListInfo()


    def UpdateListInfo( self ):
        pass
        #self.page_friendslist.UpdateList()
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
        kxData.global_local_config_info['SettingsInfo'].UpdateToFile()
        kxData.global_network_operator.friends_list.UpdateToFile()
        kxData.global_network_operator.logout()
        self.Destroy()


if __name__ == "__main__":
    app = wx.PySimpleApp()
    mainFrame = KxPluginFrame()
    mainFrame.Show()
    app.MainLoop()





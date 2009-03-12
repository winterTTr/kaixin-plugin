# -*- encoding=utf8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

import wx
import kxData
import operator
import re

class PageGarden(wx.Panel):
    __id_splitter__ = re.compile( r'\[(?P<id>.*)\]')
    __can_type__ = [ 
            u"关闭" , 
            u"开启"]
    def __init__( self  ,parent ):
        wx.Panel.__init__( self , parent )

        self.fl = kxData.global_network_operator.friends_list.GetList()
        self.si = kxData.global_local_config_info['SettingsInfo'].gardenInfo
        self.tags = kxData.global_local_config_info['SettingsInfo'].__garden_tags__

        self._create_items()
        self.chAction.SetSelection( 0 )
        self.UpdateUI( self.tags[0][1] )

        self.Bind( 
                wx.EVT_CHOICE ,
                self.OnActionTypeChange , 
                self.chAction )

        self.Bind( 
                wx.EVT_CHOICE ,
                self.OnCanTypeChange , 
                self.chCan )

        self.Bind( wx.EVT_BUTTON , self.OnAddOne , self.bnAddOne )
        self.Bind( wx.EVT_BUTTON , self.OnAddAll , self.bnAddAll )
        self.Bind( wx.EVT_BUTTON , self.OnDelOne , self.bnDelOne )
        self.Bind( wx.EVT_BUTTON , self.OnDelAll , self.bnDelAll )

    def OnAddOne( self , event ):
        sel = self.lbAllUser.GetSelection()
        if sel == wx.NOT_FOUND:
            wx.MessageDialog( self, u"请在所有用户中选择一个" , u"警告" , wx.OK |wx.ICON_EXCLAMATION ).ShowModal()
            return

        sel_string = self.lbAllUser.GetString( sel )
        id = int ( self.__id_splitter__.search( sel_string ).group('id') )
        self.si[self.tags[ self.chAction.GetSelection() ][1] ]['list'].append( id )

        self.lbAllUser.Delete( sel )
        self.lbTargetUser.Append( sel_string )
        


    def OnAddAll( self , event ):
        user_list = self.lbAllUser.GetItems()
        if len( user_list ) == 0 :
            wx.MessageDialog( self, u"全部用户已经添加" , u"警告" , wx.OK |wx.ICON_EXCLAMATION ).ShowModal()
            return

        for x in user_list:
            id = int ( self.__id_splitter__.search( x ).group('id') )
            self.si[self.tags[ self.chAction.GetSelection() ][1] ]['list'].append( id )

        self.UpdateUI( self.tags[ self.chAction.GetSelection() ][1] )


    def OnDelOne( self , event ):
        sel = self.lbTargetUser.GetSelection()
        if sel == wx.NOT_FOUND:
            wx.MessageDialog( self, u"请在目标用户中选择一个" , u"警告" , wx.OK |wx.ICON_EXCLAMATION ).ShowModal()
            return

        sel_string = self.lbTargetUser.GetString( sel )
        id = int ( self.__id_splitter__.search( sel_string ).group('id') )
        self.si[self.tags[ self.chAction.GetSelection() ][1] ]['list'].remove( id )

        self.lbTargetUser.Delete( sel )
        self.lbAllUser.Append( sel_string )


    def OnDelAll( self , event ):
        user_list = self.lbTargetUser.GetItems()
        if len( user_list ) == 0 :
            wx.MessageDialog( self, u"全部用户已经删除" , u"警告" , wx.OK |wx.ICON_EXCLAMATION ).ShowModal()
            return

        self.si[self.tags[ self.chAction.GetSelection() ][1] ]['list'] = []
        self.UpdateUI( self.tags[ self.chAction.GetSelection() ][1] )


    def OnActionTypeChange( self , event ): 
        self.UpdateUI( self.tags[ self.chAction.GetSelection() ][1] )

    def OnCanTypeChange( self , event ): 
        self.si[self.tags[ self.chAction.GetSelection() ][1]]['do'] = self.chCan.GetSelection()

    def UpdateUI( self , tag ):
        self.chCan.SetSelection ( self.si[tag]['do'] )
        self.UpdateList( * self._makeTargetList( tag ) )

    def UpdateList( self , ll , rl ):
        self.lbAllUser.SetItems( ll )
        self.lbTargetUser.SetItems( rl )

    def _makeTargetList( self , tag ):
        target_list = self.si[tag]['list']
        ret_ll = []
        ret_rl = []
        for x in self.fl:
            item = u"%s[%d]" % ( x[1] , x[0])
            if x[0] in target_list:
                ret_rl.append( item )
            else:
                ret_ll.append( item )

        return ret_ll , ret_rl

       


    def _create_items( self ):
        wx.StaticBox( self , 
                pos = ( 10 , 10 ) , 
                label = u"动作设置" ,
                size = ( 760 , 60 ) )

        wx.StaticText( self , 
                pos = ( 35, 35) , 
                label = u"动作选择:" ,
                size = ( 100 , 20 ) )

        wx.StaticText( self , 
                pos = ( 30,  110 ) , 
                label = u"有效性:" ,
                size = ( 100 , 20 ) )

        wx.StaticBox( self , 
                pos = ( 10 , 80 ) , 
                label = u"选项" ,
                size = ( 200 , 450 ) )

        wx.StaticBox( self , 
                pos = ( 220 , 80 ) , 
                label = u"目标用户" ,
                size = ( 550 , 450 ) )

        wx.StaticText( self , 
                pos = ( 240 , 120 ) , 
                label = u"所有用户:" ,
                size = ( 100 , 20 ) )

        wx.StaticText( self , 
                pos = ( 550 , 120 ) , 
                label = u"目标用户:" ,
                size = ( 100 , 20 ) )

        self.chAction = wx.Choice( self ,
                pos = ( 155 , 33 ) , 
                size = ( 200 , 20 ) ,
                choices = map( operator.itemgetter(0) , self.tags ) )

        self.chCan = wx.Choice( self ,
                pos = ( 90 , 110 ) , 
                size = ( 100 , 20 ) ,
                choices = self.__can_type__)

        self.lbAllUser = wx.ListBox( self ,
                pos = ( 240 , 150) , 
                size = ( 200 , 350 ) )

        self.lbTargetUser = wx.ListBox( self ,
                pos = ( 550 , 150) , 
                size = ( 200 , 350 ) )

        self.bnAddOne = wx.Button ( self , 
                label = u"添加 >>" ,
                pos = ( 450 , 200 ) , 
                size = ( 90 , 22  ) )

        self.bnDelOne = wx.Button ( self , 
                label = u"<< 删除" ,
                pos = ( 450 , 230 ) , 
                size = ( 90 , 22  ) )

        self.bnAddAll = wx.Button ( self , 
                label = u"添加所有 >>>" ,
                pos = ( 450 , 280 ) , 
                size = ( 90 , 22  ) )

        self.bnDelAll = wx.Button ( self , 
                label = u"<<< 删除所有" ,
                pos = ( 450 , 310 ) , 
                size = ( 90 , 22  ) )


class PageAction( wx.Panel ):
    def __init__( self , parent ):
        wx.Panel.__init__( self , parent )
        #self._create_items()

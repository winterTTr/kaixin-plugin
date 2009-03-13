# -*- encoding=utf8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

import wx
import kxData
import operator
import re
from StringIO import StringIO
from xml.etree import ElementTree as ET
import threading


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


class ThreadDoGarden( threading.Thread ):
    def __init__( self , panel , if_timer_thread = False ):
        threading.Thread.__init__( self )
        self.OutLog = panel.OutLog
        self.bnStart = panel.bnStart
        self.bnStop = panel.bnStop
        self.pool = panel.thread_do_garden
        self.evtStop = threading.Event()
        self.evtStop.clear()
        self.isTimer = if_timer_thread
        self.cbRedo = panel.cbRedo
        self.tcInterval = panel.tcInterval

    def _check_if_exit_thread( self ):
        if self.evtStop.isSet():
            self.OutLog( u'\n')
            self.OutLog( u'用户终止操作\n')
            if not self.isTimer :
                self.pool.pop()

            self.bnStart.Enable( True )
            return True
        else:
            return False

        
    def run( self ):
        self.bnStop.Enable( True )

        self.OutLog( u'\n' )
        self.OutLog( u'开始执行动作。。。\n' )

        action_list = [ 
                { 
                    'name' : u'浇水' , 
                    'req'  : 'Water' , 
                    'action_type' : 'water' , 
                    'check': lambda item_root : item_root.find('water').text != '5' } ,

                { 
                    'name' : u'除草' , 
                    'req'  : 'AntiGrass' , 
                    'action_type' : 'antigrass' , 
                    'check': lambda item_root : item_root.find('grass').text == '1' } ,
                { 
                    'name' : u'除虫' , 
                    'req'  : 'AntiVermin' , 
                    'action_type' : 'antivermin' , 
                    'check': lambda item_root : item_root.find('vermin').text == '1' } ,
                { 
                    'name' : u'收获' , 
                    'req'  : 'Havest' , 
                    'action_type'  : 'havest' ,
                    'check': ( 
                        lambda item_root : 
                            item_root.find('shared').text != '1' and 
                            item_root.find('grow').text == item_root.find('totalgrow').text and
                            item_root.find('status').text == '1' and
                            item_root.find('cropsstatus').text != '3' ) } ]

        for action in action_list:
            if self._check_if_exit_thread(): return
            do_action = kxData.global_local_config_info['SettingsInfo'].gardenInfo[action['action_type']]['do']
            user_list = kxData.global_local_config_info['SettingsInfo'].gardenInfo[action['action_type']]['list']
            self.OutLog(u'\n')
            if do_action == 0 :
                self.OutLog(u'====[%s]未开启===\n' % action['name'])
                continue
            else:
                self.OutLog(u'====开始执行[%s]===\n' % action['name'])


            self.OutLog(u'')
            for id in user_list :
                if self._check_if_exit_thread(): return
                user_name = kxData.global_network_operator.friends_list.GetUserName( id )
                self.OutLog( u'\n' )
                self.OutLog( u'取得[%s]家的菜园作物信息。。。' % user_name )
                resp = kxData.SendRequest( 'CropInfo' , fuid = id )
                sio = StringIO( resp.read() )
                sio.seek(0)
                if sio.getvalue()[0] != '<' :
                    self.OutLog( u'取得失败\n'  )
                    continue
                else:
                    self.OutLog( u'取得成功\n'  )

                analyzor = ET.ElementTree( file = sio )

                for item_root in analyzor.findall('garden/item'):
                    farmnum = item_root.find('farmnum').text
                    cropsid = item_root.find('cropsid').text
                    if cropsid == '0':
                        #self.OutLog( u'[作物%2s]尚未开发\n' % ( farmnum , ) )
                        continue
                    else:
                        if action['check']( item_root):
                            resp = kxData.SendRequest( action['req'] , fuid = id , farmnum = farmnum)
                            if isinstance( resp , type({}) ):
                                self.OutLog( u'给[作物%2s]%s...%s\n' % ( farmnum , action['name'] ,resp['status'] ) )
                            else:
                                self.OutLog( u'给[作物%2s]%s\n' % ( farmnum , action['name'] ) )
                        #else:
                        #    self.OutLog( u'[作物%2s]不需要%s' % ( farmnum , action['name'] ) )

        self.OutLog( u'\n')
        self.OutLog( u'操作结束\n')
        if not self.isTimer :
            self.bnStop.Enable( False )
            self.bnStart.Enable( True )
            self.cbRedo.Enable(True)
            self.tcInterval.Enable(True)
            self.pool.pop()

    def stop( self ):
        self.evtStop.set()


class ThreadDoGardenTimer( threading.Thread ):
    def __init__( self , panel ,timer ):
        threading.Thread.__init__( self )

        self.timer = timer
        self.evtStop = threading.Event()
        self.evtStop.clear()
        self.thread_obj = ThreadDoGarden( panel , True )
        self.panel = panel

    def run( self ):
        self.thread_obj.run()
        while True:
            self.panel.OutLog(u'\n')
            self.panel.OutLog( u"等待下次操作\n")
            self.evtStop.wait( self.timer )
            if self.evtStop.isSet():
                self.panel.OutLog(u'\n')
                self.panel.OutLog(u'用户中止操作\n')
                self.panel.bnStart.Enable(True)
                return
            else:
                self.thread_obj.run()
                if self.thread_obj.evtStop.isSet():
                    return

    def stop( self ):
        self.thread_obj.evtStop.set()
        self.evtStop.set()
        self.panel.thread_do_garden.pop()





class PageAction( wx.Panel ):
    def __init__( self , parent ):
        wx.Panel.__init__( self , parent )
        self._create_items()
        self.bnStop.Enable( False )

        self.Bind( wx.EVT_BUTTON , self.OnStart , self.bnStart )
        self.Bind( wx.EVT_BUTTON , self.OnStop , self.bnStop )

        self.thread_do_garden = []

    def OnStart( self ,event ):
        if self.thread_do_garden :
            return

        interval = self.tcInterval.GetValue()
        try:
            interval = int( interval )
            assert interval > 0 , 'interval little than 0'
        except:
            wx.MessageDialog( self, u"请输入有效的间隔值" , u"警告" , wx.OK |wx.ICON_EXCLAMATION ).ShowModal()
            return


        self.bnStart.Enable(False)
        self.cbRedo.Enable(False)
        self.tcInterval.Enable(False)
        if self.cbRedo.IsChecked():
            self.thread_do_garden.append(  ThreadDoGardenTimer( self ,  interval * 60 )) 
        else:
            self.thread_do_garden.append( ThreadDoGarden( self ) )

        self.thread_do_garden[0].start()

    def OnStop( self , event ):
        self.bnStop.Enable( False )
        self.thread_do_garden[0].stop()
        self.cbRedo.Enable(True)
        self.tcInterval.Enable(True)

    def OutLog( self , text ):
        self.tcLog.AppendText( text )

    def _create_items( self ):
        wx.StaticBox( self , 
                pos = ( 10 , 10 ) , 
                label = u"选项" ,
                size = ( 200 , 520 ) )
        wx.StaticBox( self , 
                pos = ( 220 , 10 ) , 
                label = u"输出" ,
                size = ( 550 , 520 ) )

        wx.StaticText( self, 
                label = u"循环间隔(分钟):" , 
                pos = ( 30 , 80 ) , 
                size = ( 150 , 20  ) )

        self.cbRedo = wx.CheckBox( self,
                pos = ( 30 , 30 ) , 
                label = u"循环执行",
                size = ( 150 , 20 ) )

        self.tcInterval = wx.TextCtrl( self , 
                pos = ( 30 , 100 ) , 
                value = '5' , 
                size = ( 150 , 20  ))

        self.bnStart = wx.Button( self , 
                label = u"执行" , 
                pos = ( 30 , 140 ) , 
                size = ( 50 , 20 ) )


        self.bnStop = wx.Button( self , 
                label = u"停止" , 
                pos = ( 120 , 140 ) , 
                size = ( 50 , 20 ) )

        self.tcLog = wx.TextCtrl( self , 
                pos = ( 230 , 30 ) , 
                size = ( 530 , 480 ) , 
                style = wx.TE_READONLY | wx.TE_MULTILINE )
        self.tcLog.SetBackgroundColour( "#ededed" )





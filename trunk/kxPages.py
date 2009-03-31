# -*- encoding=utf8 -*-

__version__ = '$Revision$'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

import wx
import kxData
import operator
import re
import time
import threading
from StringIO import StringIO
from xml.etree import ElementTree as ET


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
            self.OutLog( u'用户终止操作')
            if not self.isTimer :
                self.pool.pop()

            self.bnStart.Enable( True )
            return True
        else:
            return False

    def _check_havest( self , item_root ):
        _text_getter = lambda tag : item_root.find(tag).text

        if _text_getter('shared') =='1' : return False
        if _text_getter('cropsid') =='0' : return False
        if _text_getter('grow') != _text_getter('totalgrow'): return False
        if _text_getter('cropsstatus') =='3' : return False

        crops = _text_getter('crops')
        if crops.find(u'已偷光') != -1 : return False
        if crops.find(u'已枯死') != -1 : return False

        searchRet = re.search(u'剩余：(?P<farmnum>\d+)' , crops )
        if searchRet :
            return searchRet.group('farmnum') != 0
        else:
            self.OutLog( u"%s" % crops )
            return True

        return True

        
    def run( self ):
        self.bnStop.Enable( True )

        self.OutLog( u'\n' , addTime = False )
        self.OutLog( u'开始执行动作。。。' )

        action_list = [ 
                { 
                    'name' : u'浇水' , 
                    'req'  : 'Water' , 
                    'action_type' : 'water' , 
                    'check': lambda item_root : item_root.find('water').text != '5' ,
                    'if_do': kxData.global_local_config_info['SettingsInfo'].gardenInfo['water']['do'] , 
                    'u_list': kxData.global_local_config_info['SettingsInfo'].gardenInfo['water']['list'] 
                } , 
                { 
                    'name' : u'除草' , 
                    'req'  : 'AntiGrass' , 
                    'action_type' : 'antigrass' , 
                    'check': lambda item_root : item_root.find('grass').text == '1' ,
                    'if_do': kxData.global_local_config_info['SettingsInfo'].gardenInfo['antigrass']['do'] , 
                    'u_list': kxData.global_local_config_info['SettingsInfo'].gardenInfo['antigrass']['list']
                } ,
                { 
                    'name' : u'除虫' , 
                    'req'  : 'AntiVermin' , 
                    'action_type' : 'antivermin' , 
                    'check': lambda item_root : item_root.find('vermin').text == '1' ,
                    'if_do': kxData.global_local_config_info['SettingsInfo'].gardenInfo['antivermin']['do'] ,
                    'u_list': kxData.global_local_config_info['SettingsInfo'].gardenInfo['antivermin']['list']
                },
                { 
                    'name' : u'收获' , 
                    'req'  : 'Havest' , 
                    'action_type'  : 'havest' ,
                    'check': self._check_havest ,
                    'if_do' : kxData.global_local_config_info['SettingsInfo'].gardenInfo['havest']['do'] ,
                    'u_list': kxData.global_local_config_info['SettingsInfo'].gardenInfo['havest']['list'] 
                } ]


        for user in kxData.global_network_operator.friends_list.GetList():
            if self._check_if_exit_thread(): return        
            analyzor = None
            find_cailaobo = False
            for action in action_list:
                if self._check_if_exit_thread(): return        

                #self.OutLog( u'Do action [%s]\n' % action['name'] )

                if action['if_do'] == 0 :
                    #self.OutLog( u'action [%s] : close\n' % action['name'] )
                    continue

                if not ( user[0] in action['u_list'] ):
                    #self.OutLog( u'action [%s] : user no in list\n' % action['name'] )
                    continue

                if analyzor == None :
                    #self.OutLog( u'\n' , addTime = False )
                    self.OutLog( u'取得[%s]家的菜园作物信息。。。' % user[1] , addReturn = False )
                    resp = kxData.SendRequest( 'CropInfo' , fuid = user[0] )
                    sio = StringIO( resp.read() )
                    sio.seek(0)
                    #if user[0] == 10427745 :
                    #    open( '0.xml' , 'w').write( sio.getvalue() )
                    #if sio.getvalue().find( u'他还没有添加本组件'.encode('cp936') ) == -1 :
                    try:
                        analyzor = ET.ElementTree( file = sio )
                        self.OutLog( u'成功'  , addTime = False )
                        find_cailaobo =  ( analyzor.find('account/careurl').text != None )
                    except:
                        self.OutLog( u'失败' , addTime = False )
                        break

                if action['action_type'] == 'havest': 
                    if find_cailaobo:
                        self.OutLog( u'        发现菜老伯！！下次再偷 = =||')
                        continue
                    #else:
                    #    self.OutLog( u'没有菜老伯！！安全，安全 *_*\n')

                for item_root in analyzor.findall('garden/item'):
                    if self._check_if_exit_thread(): return        
                    farmnum = item_root.find('farmnum').text
                    cropsid = item_root.find('cropsid').text
                    status = item_root.find('status').text
                    #if cropsid == '0':
                    if status == '0':
                        #self.OutLog( u'[作物%2s]尚未开发\n' % ( farmnum , ) )
                        continue
                    if action['check']( item_root ):
                        resp = kxData.SendRequest( action['req'] , fuid = user[0] , farmnum = farmnum)
                        if isinstance( resp , type({}) ):
                            self.OutLog( u'        给[作物%2s]%s...%s' % ( farmnum , action['name'] ,resp['status'] ) )
                        else:
                            self.OutLog( u'        给[作物%2s]%s' % ( farmnum , action['name'] ) )
                    #else:
                    #    self.OutLog( u'[作物%2s]不需要%s\n' % ( farmnum , action['name'] ) )
    

        self.OutLog( u'操作结束')
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
            self.panel.OutLog(u'' , addTime = False )
            self.panel.OutLog( u"等待下次操作")
            self.evtStop.wait( self.timer )
            if self.evtStop.isSet():
                self.panel.OutLog(u'' , addTime = False )
                self.panel.OutLog(u'用户中止操作')
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

    def OutLog( self , text , addTime = True , addReturn = True ):
        if addTime :
            self.tcLog.AppendText( u"[%s] " % time.strftime(u'%H:%M:%S') )
            #self.tcLog.AppendText( u"[%s]" % time.strftime(u'%m/%d %H:%M:%S') )

        self.tcLog.AppendText( text )

        if addReturn:
            self.tcLog.AppendText(u'\n')

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
                value = '20' , 
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





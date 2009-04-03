# -*- encoding=utf8 -*-

__version__ = '$Revision'[11:-2]
__author__ = 'winterTTr<winterTTr@gmail.com>'
__svnid__ = '$Id$'

import threading
import kxData
from StringIO import StringIO
from xml.etree import ElementTree as ET


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

    def _check_harvest( self , item_root ):
        _text_getter = lambda tag : item_root.find(tag).text

        if _text_getter('shared') =='1' : return False
        if _text_getter('cropsid') =='0' : return False
        if _text_getter('grow') != _text_getter('totalgrow'): return False
        if _text_getter('cropsstatus') =='3' : return False

        crops = _text_getter('crops')
        if crops.find(u'已偷光') != -1 : return False
        if crops.find(u'已枯死') != -1 : return False
        if crops.find(u'即将成熟') != -1 : return False

        searchRet = re.search(u'剩余：(?P<farmnum>\d+)' , crops )
        if searchRet :
            return searchRet.group('farmnum') != 0
        else:
            self.OutLog( u"%s" % crops )
            return True

        return True

        
    def run( self ):
        setting = kxData.FarmSettingsInfoSet( aid = 1 )

        self.bnStop.Enable( True )
        self.OutLog( u'\n' , addTime = False )
        self.OutLog( u'开始执行动作。。。' )

        nwo = kxData.NetworkOperator( 1 )
        nwo.Login()
        self.OutLog( u'登陆用户[%s]...' % setting.db.GetEmail( 1 ) )

        action_list = [ 
                { 
                    'name' : u'浇水' , 
                    'req'  : 'Water' , 
                    'action_type' : 'water' , 
                    'check': lambda item_root : item_root.find('water').text != '5' ,
                    'if_do': setting.GetIfAction('water') , 
                    'u_list': setting.GetDoUser('water')
                } , 
                { 
                    'name' : u'除草' , 
                    'req'  : 'AntiGrass' , 
                    'action_type' : 'antigrass' , 
                    'check': lambda item_root : item_root.find('grass').text == '1' ,
                    'if_do': setting.GetIfAction('antigrass') , 
                    'u_list': setting.GetDoUser('antigrass')
                } ,
                { 
                    'name' : u'除虫' , 
                    'req'  : 'AntiVermin' , 
                    'action_type' : 'antivermin' , 
                    'check': lambda item_root : item_root.find('vermin').text == '1' ,
                    'if_do': setting.GetIfAction('antivermin') , 
                    'u_list': setting.GetDoUser('antivermin')
                },
                { 
                    'name' : u'收获' , 
                    'req'  : 'Harvest' , 
                    'action_type'  : 'harvest' ,
                    'check': self._check_harvest ,
                    'if_do': setting.GetIfAction('harvest') , 
                    'u_list': setting.GetDoUser('harvest')
                } ]


        for user in setting.db.GetUserList( aid = 1 ):
            if self._check_if_exit_thread(): 
                self.OutLog( u'注销登陆...')
                nwo.Logout()
                return        
            analyzor = None
            find_cailaobo = False
            for action in action_list:
                if self._check_if_exit_thread(): 
                    self.OutLog( u'注销登陆...')
                    nwo.Logout()
                    return        

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
                    resp = nwo.SendRequest( 'CropInfo' , fuid = user[0] )
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

                if action['action_type'] == 'harvest': 
                    if find_cailaobo:
                        self.OutLog( u'        发现菜老伯！！下次再偷 = =||')
                        continue
                    #else:
                    #    self.OutLog( u'没有菜老伯！！安全，安全 *_*\n')

                for item_root in analyzor.findall('garden/item'):
                    if self._check_if_exit_thread():
                        self.OutLog( u'注销登陆...')
                        nwo.Logout()
                        return
                    farmnum = item_root.find('farmnum').text
                    cropsid = item_root.find('cropsid').text
                    status = item_root.find('status').text
                    #if cropsid == '0':
                    if status == '0':
                        #self.OutLog( u'[作物%2s]尚未开发\n' % ( farmnum , ) )
                        continue
                    if action['check']( item_root ):
                        resp = nwo.SendRequest( action['req'] , fuid = user[0] , farmnum = farmnum)
                        if isinstance( resp , type({}) ):
                            self.OutLog( u'        给[作物%2s]%s...%s' % ( farmnum , action['name'] ,resp['status'] ) )
                        else:
                            self.OutLog( u'        给[作物%2s]%s' % ( farmnum , action['name'] ) )
                    #else:
                    #    self.OutLog( u'[作物%2s]不需要%s\n' % ( farmnum , action['name'] ) )
    

        self.OutLog( u'注销登陆...')
        nwo.Logout()
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
        while True:

            if self.evtStop.isSet():
                self.panel.OutLog(u'' , addTime = False )
                self.panel.OutLog(u'用户中止操作')
                self.panel.bnStart.Enable(True)
                return
            else:
                self.thread_obj.run()
                if self.thread_obj.evtStop.isSet():
                    return

            self.panel.OutLog(u'' , addTime = False )
            self.panel.OutLog( u"等待下次操作")
            self.evtStop.wait( self.timer )

    def stop( self ):
        self.thread_obj.evtStop.set()
        self.evtStop.set()
        self.panel.thread_do_garden.pop()



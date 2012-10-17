#! /usr/bin/python
# coding=utf8
"""
 attempts to be flash card program; has some lojban specific quirks
"""

# copyright (C) 2009/2012 "Stephen Joseph Pollei" <stephen.pollei@gmail.com>
# licensed gplv3 or later -- http://www.fsf.org/licensing/licenses/gpl.html

# attempts to be flash card program; has some lojban specific quirks

#import re, random, time, cPickle, os, urllib, sys



import random, time, cPickle, os

cached_now = time.time()

def update_cached_time():
  global cached_now
  tnow = time.time()
  #cached_now=max(cached_now+0.0001,tnow)
  cached_now=max(cached_now+1.0e-8,tnow)
  return cached_now
  # enforce monotonic increasing time

class QuCard:
  def __init__(self, topic, group, item, ps=None):
    self.topic = topic
    self.group = group
    self.item = item
    self.ps = ps
    if ps == None :
      self.ps = topic.gset[group][item]

def last_answer_time_from_group(iset) :
  lat=0.0
  for item in iset.keys() :
    lat=max(lat,iset[item]['lbad'],iset[item]['lgood'])
  return lat

def expired_item_time(item,lat=0.0):
  age = item['expire'] - max(item['lgood'],item['lbad'])
  #age = max(age - 18.8, 0.1)
  twin_t =min(36987.6,max(age/38.2,min(77.2,age/2.7)))
  return max(item['expire'] , (lat + twin_t) )

def is_expired_item(item,lat=0.0):
  return cached_time > expired_item_time(item,lat)

def expired_item_from_group(iset , now_t=None):
  if now_t == None:
    now_t = cached_now
  el = []
  lat = last_answer_time_from_group(iset)
  for item in iset.keys() :
    #if now_t > iset[item]['expire'] :
    if is_expired_time(item,lat) :
      el.append(item)
  if len(el) == 0 :
    return None
  elif len(el) == 1:
    return el[0]
  else:
    return random.choice(el)

class Que:
  def __init__(self):
    self.q = []
  def sz(self):
    return len(self.q)
  def is_front(self,qc) :
    return len(self.q) and qc != None and qc == self.q[0]
  def append(self,qc) :
    self.q.append(qc)
  def front(self):
    return self.q[0]
  def empty(self):
    self.q = []
  def pop(self) :
    self.q.pop(0)
  def shuffle(self) :
    random.shuffle(self.q)
  def trim(self) :
    sz = len(self.q)
    if sz > 100 :
      self.q = self.q[:50]
    elif sz >= 22 :
      self.q = self.q[:sz//2]
  def lbad(self) :
    try :
      return self.q[0]['lbad']
    except StandardError :
      return 0.0
  def fill_expired(self,pjs):
    self.q = []
    for group in pjs.keys() :
      item = expired_item_from_group(group)
      if item != None :
        self.q.append(QuCard(pjs,group,item))
    random.shuffle(self.q)

class UtilBase:
  'utility base'

  def __init__(self, name='', clh=False, stb=True):
    self.name = name
    self.can_launch = clh
    self.stub = stb
    self.cards = {}

  #def find_earliest_expired_time(self, model=None, itera=None):
  #  'this should be overriden later'
  #  return '     '

  #def find_last_expired_time(self, model=None, itera=None):
  #  'this should be overriden later'
  #  return '     '

  def format_time(self, tim):
    'format time'
    now = cached_now
    ltim = time.localtime(tim)
    if tim < now :
      return ' Now '
    # I could put something in for 365*24*60*60 .
    # however for something to be in there for so long that the year matters,
    # means some has been using this program and answering questions
    # at 100% accuracy for a very long time.
    # I'm not that optimistic to think any human will be so happy
    #   with my program for so long a time
    elif tim > now + 3628800:
      return time.strftime("%Y/%m/%d", ltim)
      # 42 days or more
    elif tim > now + 1123200:
      return time.strftime("%a %m/%d", ltim)
      # 13 days or more
    elif tim > now + 129600:
      return time.strftime("%a %m/%d %H %p", ltim)
      # 36 hours or more
    elif tim > now + 79200:
      return time.strftime("%a %H:%M %p", ltim)
      # 22 hours or more
    else:
      return time.strftime("%H:%M:%S %p", ltim)
    # when the time is getting close you might want to start checking to see if
    # the first time is isolated and so you should give a slightly later time
    # but this should be good enough to give rough indication

  def suggested_time(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return '     '
    try:
      eet = self.find_earliest_expired_time(model, itera)
    except:
      return '     '
    if self.total(model, itera) == 0:
      return '     '
    return self.format_time(eet)

  def suggested_last_time(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return '     '
    try:
      ltet = self.find_last_expired_time(model, itera)
    except:
      return '     '
    if self.total(model, itera) == 0:
      return '     '
    return self.format_time(ltet)

  def total(self, model=None, itera=None): return '     '
  def todo(self, model=None, itera=None): return '     '
  def done(self, model=None, itera=None): return '     '
  def expire_h16(self, model=None, itera=None): return '     '
  def is_stale(self): return False

# perhaps if there were other sets besides lojban sets
# then a class that deals with
# 1) persistent storage of progress
# 2) scheduling
# could factored out of LojbanBase and thus shared
# class Foo(SetBase): pass

class Pjs:
  'pickle jar storage'
  def __init__(self):
    #self.set = {}
    # set is old depracated name, if it's found it's an error FIXME
    self.gset = {}
    self.config = {}

class SetBase(UtilBase):
  'set base'
  #cards = {}
  pjs_dir_name = ''

  def mk_pjs_dir(self):
    'docstring'
    if os.name in [ 'posix', 'unix', 'linux']:
      SetBase.pjs_dir_name = os.path.expanduser('~/.jbo_fc_pjs/')
    elif os.name in [ 'windows', 'nt', 'ce']:
      SetBase.pjs_dir_name = os.path.expanduser('~\\jbo_fc_pjs\\')
    else:
      raise NotImplementedError, ('unknown operating system: ' + os.name)
    if not os.path.exists(SetBase.pjs_dir_name):
      os.mkdir(SetBase.pjs_dir_name)

  def read_cards(self):
    'should be overridden'

  def gen_item_list(self,group):
    'generate item list'
    return self.cards[group].keys()

  def gen_group_items(self,group):
    items=self.gen_item_list(group)
    #self.group_made_total=self.group_made_total+1
    self.stats['group_total'] += 1
    et = cached_now -12.0
    gt = et - 2.5
    bt = gt -999.9
    print 'making ', group
    self.pjs.gset[group]= {}
    for item in items :
      self.stats['item_total'] += 1
      rt = 15.9*random.random()
      self.stats['item_total'] += 1
      self.pjs.gset[group][item] = {
        'expire':  et, 'lgood': gt-rt, 'lbad': bt}
      #print 'making ', group, ' ', item, ' '
      

  def gen_group_list(self):
    'generate word list'
    self.read_cards()
    #self.stats['total_cnt']=len(self.cards)
    if 'grow_list' in self.pjs.config :
      print 'found grow list'
      return self.pjs.config['grow_list']
    return self.cards.keys()

  def grow_set(self,amount):
    'grow set'
    glist=self.gen_group_list()
    glist_sz =len(glist)
    if glist_sz <= 0 :
      return
    gt = self.stats['group_total']
    if amount > glist_sz - gt:
      amount = glist_sz - gt
    glist = glist[gt:gt+amount]
    for group in glist :
      self.gen_group_items(group)
    self.stats['total_cnt']=max(self.stats['item_total'],glist_sz)
    self.stats['group_max']=glist_sz
    self.stats['todo_cnt'] += amount
    self.stats['h16'] += amount

  def create_set(self):
    'create set'
    #self.group_made_total=0
    #self.item_made_total=0
    glist=self.gen_group_list()
    glist_sz =len(glist)
    if glist_sz <= 0 :
      return
    now = update_cached_time()
    sz = glist_sz
    if sz < 15 :
      sz = sz//3 +1
    else : sz =5
    if self.ordered_list :
      glist = glist[:sz]
    else :
      random.shuffle(glist)
      self.pjs.config['grow_list'] = glist
      glist = glist[:sz]
    for group in glist :
      self.gen_group_items(group)
    self.stub = False
    self.stats['total_cnt']=max(self.stats['item_total'],glist_sz)
    self.stats['group_max']=glist_sz
    self.stats['todo_cnt']=sz

  def change_cc(self):
    'change current card'
    if self.expired_q.is_front(self.cc):
      self.expired_q.pop()
    if self.wrong_q.is_front(self.cc):
      self.wrong_q.pop()
    dt = min(39.9,6.2*self.expired_q.sz()-0.5)
    recent_wrong = (self.wrong_q.sz() and 
        (self.wrong_q.front()['lbad'] < (cached_now-dt)) )
    if recent_wrong :
      self.cc = self.wrong_q.front()
    elif self.expired_q.sz():
      self.cc = self.expired_q.front()
    elif self.wrong_q.sz():
      self.cc == self.wrong_q.front()
    else:
      self.cc = None

  def scan_stats(self,force=False):
    'scan and update statistics'
    if self.stub:
      return
    now=update_cached_time()
    if self.last_scan_time + 0.7 > now and not force:
      return
    self.last_scan_time = now
    stats = { 'eet': 9.9e15, 'let': 0.0, 'todo_cnt': 0, 'h16': 0,
              'group_total':0, 'item_total':0 , 'total_cnt':0 }
    eet = 9.9e15
    let = 0.0
    gset=self.pjs.gset
    h16_t = cached_now + 57600.0
    for group in gset.keys() :
      stats['group_total'] += 1
      lat = last_answer_time_from_group(gset[group])
      g_todo=0
      g_h16=0
      for item in gset[group].keys() :
        # FIXME expire time needs to use is_expired_item FIXME
        stats['item_total'] += 1
        exp_t = expired_item_time(gset[group][item],lat)
        if stats['eet'] > exp_t:
          stats['eet'] = exp_t
        if stats['let'] < exp_t :
          stats['let'] = exp_t
        if cached_now > exp_t :
          g_todo += 1
        if h16_t < exp_t :
          g_h16 += 1
      stats['todo_cnt'] +=  (g_todo+2)//3
      stats['h16'] += (g_h16+1)//2
    stats['total_cnt']=stats['item_total']
    self.stats=stats



  def find_earliest_expired_time(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return cached_now-99.9
    self.scan_stats()
    return self.stats['eet']

  def find_last_expired_time(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return cached_now-99.9
    self.scan_stats()
    return self.stats['let']


  def find_expired_cnt(self):
    'docstring'
    if self.expired_q.sz() or self.wrong_q.sz() :
      return
    self.scan_stats()


  def find_expired(self, force=False):
    'docstring'
    now=update_cached_time()
    if now > (self.last_find_expired + 787.8) :
      force = True
    if self.expired_q.sz() or self.wrong_q.sz() :
      if force:
        self.cc = None
        self.expired_q = Que()
        self.wrong_q = Que()
      else:
        return
    if self.stub:
      return
    self.last_scan_time = now
    self.last_find_expired = now
    stats = { 'eet': 9.9e15, 'let': 0.0, 'todo_cnt': 0, 'h16': 0,
              'stale':0, 'fresh':0, 'group_total':0 , 'item_total':0,
              'total_cnt':0 }
    gset=self.pjs.gset
    h16_t = cached_now + 57600.0
    for group in gset.keys() :
      stats['group_total'] += 1
      lat = last_answer_time_from_group(gset[group])
      g_todo=0
      g_h16=0
      g_stale=0
      g_fresh=0
      gel = []
      for item in gset[group].keys() :
        stats['item_total'] += 1
        exp_t = expired_item_time(gset[group][item],lat)
        ilat = max( self.pjs.gset[group][item]['lgood'] ,
                 self.pjs.gset[group][item]['lbad'] )
        if now > exp_t :
          gel.append(item)
        if 150.0 > (self.pjs.gset[group][item]['expire'] - ilat) :
          g_fresh += 1
        if now > (self.pjs.gset[group][item]['expire'] +115200) :
          g_stale += 1
        if stats['eet'] > exp_t:
          stats['eet'] = exp_t
        if stats['let'] < exp_t :
          stats['let'] = exp_t
        if cached_now > exp_t :
          g_todo += 1
        if h16_t < exp_t :
          g_h16 += 1
      g_todo = (g_todo+2)//3
      stats['todo_cnt'] += g_todo
      stats['h16'] += (g_h16+1)//2
      stats['stale'] += min(g_stale,g_todo)
      stats['fresh'] += min(g_fresh,g_todo)
      if len(gel) :
        item = random.choice(gel)
        self.expired_q.append(QuCard(self.pjs,group,item))
    stats['total_cnt']=stats['item_total']
    self.stats=stats
    eq_sz = self.expired_q.sz()
    self.todo_cnt = eq_sz
    work_max = int(min(15, (self.end_time-now)/8.6))
    hard_cnt = stats['fresh']+stats['stale']
    grow_sz = min(3,(work_max-eq_sz-hard_cnt)//2)
    if self.expired_q.sz() >= 22:
      self.expired_q.trim()
    elif grow_sz >0 :
      self.grow_set(grow_sz)
    self.expired_q.shuffle()

  def realize(self, force=False):
    'docstring'
    if self.stub:
      self.create_set()
    now = cached_now
    if self.expired_q.sz()==0 and self.wrong_q.sz()==0:
      self.find_expired()
      self.dump_pickle()
    # 25 minutes
    elif now > (self.last_find_expired + 1500) and self.wrong_q.sz()==0:
      self.find_expired()
      self.dump_pickle()
    if not self.cc:
      self.change_cc()

  def front(self):
    'docstring'
    self.realize()
    if self.cc:
      return self.cards[self.cc.group][self.cc.item][0]
    return 'You have completed this set'

  def back(self):
    'docstring'
    #self.realize()           
    if self.cc:
      return self.cards[self.cc.group][self.cc.item][1]
    return ''

  def no(self):
    'docstring'
    self.dirty = True
    now = update_cached_time()
    self.cc.ps['lbad'] = now
    self.wrong_q.append(self.cc)
    self.change_cc()

  def yes(self):
    'docstring'
    self.dirty = True
    now = update_cached_time()
    if self.cc.ps['lbad'] > self.cc.ps['lgood']:
      dt_nb = now - self.cc.ps['lbad']
      dt_max = max(min(25.0+self.todo(), dt_nb+5.8), 1.6*self.todo() )
      self.cc.ps['expire'] = now+min(dt_max, 251.0)
    else:
      dt_eg = (self.cc.ps['expire'] -
              self.cc.ps['lgood'] )
      dt_min = max(dt_eg, 4.0+min(240.0, self.expire_h16()) )
      dt_ne = now - self.cc.ps['expire']
      dt_base = max(dt_eg, 6.5, self.todo() )
      # a little under 22 hours
      dt_max_day = min(7.4*dt_base,
                  max(4.5*dt_eg, 6.0*dt_ne, 1.9*self.todo()), 79073.0)
      dt = max(2.1*dt_eg, dt_max_day)
      # experiment with having the one day cap be bigger
      # and vary based on work load
      self.cc.ps['expire'] = now+dt
      #print self.cc.group , ' expanded from ' , dt_eg, ' to ', dt
    self.cc.ps['lgood'] = now
    self.change_cc()
    self.todo_cnt = self.todo_cnt-1
# math.sqrt(math.e) ~=~ 1.6487 # golden ratio ~=~ 1.6180
# math.pow(math.e,1.5) ~=~ 4.482 thus 4.5
# math.pow(math.e,2) ~=~ 7.389 thus 7.4
# math.pow(math.e,2.5) ~=~ 12.182 thus 12.2

  def skip(self):
    'docstring'
    # if skipping thing already on wrong que and wrong que is of short size
    # put it on the end of the expired_queue instead
    ex_sz = self.expired_q.sz()
    wr_sz = self.wrong_q.sz()
    in_wr = wr_sz and (self.wrong_q.is_front(self.cc))
    if in_wr and wr_sz < 2 and ex_sz > 2 :
      self.expired_q.append(self.cc)
    else:
      self.wrong_q.append(self.cc)
    self.change_cc()

  def total(self, model=None, itera=None):
    'docstring'
    return self.stats['total_cnt']
    return self.total_cnt

  def accu_todo(self):
    'docstring'
    self.scan_stats()
    return self.stats['todo_cnt']
    return 0
    rcnt = 0
    now = cached_now
    for itm in self.pjs.set.keys():
      if now > self.pjs.set[itm]['expire']:
        rcnt = rcnt +1
    return rcnt
    # return count of expired things

  def todo(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return self.stats['total_cnt']
    else:
      td_sz = max(self.stats['todo_cnt'],
                  self.wrong_q.sz() + self.expired_q.sz())
      if td_sz:
        return td_sz
      return self.accu_todo()
      #return len(self.wrong_queue) + len(self.expired_queue)
    #return self.todo_cnt

  def expire_h16(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return self.stats['total_cnt']
    return max(self.stats['h16'], self.todo())

  def done(self, model=None, itera=None):
    'docstring'
    return self.stats['total_cnt'] - self.wrong_q.sz() - self.expired_q.sz()
    #return self.done_cnt

  # TODO FIXME try finding and loading a pickle
  # TODO FIXME doesn't use fsync or write to new file and then rename FIXME
  # FIXME potential for corruption and data loss about crash FIXME
  # WARN this might change in non-backwards compatible way WARN
  # http://www.dwheeler.com/essays/fixing-unix-linux-filenames.html#spaces
  # also should make sure filenames don't contain spaces or other cruft
  def load_pickle(self):
    'docstring'
    pic_name = os.path.join(SetBase.pjs_dir_name, self.name+'.jp2')
    #print 'pickle file name:', pic_name
    try:
      pf = open (pic_name)
    except IOError, prob:
      #print 'caught nonexistant pickle file: ', prob
      return
    try:
      #foo=cPickle.load(pf)
      self.pjs = cPickle.load(pf)
      if 'config' not in dir(self.pjs) :
        self.pjs.config = {}
    except Exception, prob:
      print 'load pickle : ', prob
      self.pjs = Pjs()
      return # FIXME ignore errors for now and silently lose data
    self.stub = False
    #self.total_cnt = len(self.pjs.set)
    self.find_expired_cnt()

  def dump_pickle(self):
    'docstring'
    if not self.dirty:
      return
    pic_name = os.path.join(SetBase.pjs_dir_name, self.name+'.jp2')
    try:
      pf = open (pic_name, 'w')
    except IOError, prob:
      print 'pickle file dump: ', prob
      #raise prob
      return # WARN ignore errors for now and silently lose data
    try:
      cPickle.dump(self.pjs, pf)
    except Exception, prob:
      print 'dump pickle: ', prob
      return # ignore errors for now and silently lose data
    self.dirty = False

  def close(self):
    'docstring'
    self.dump_pickle()
    #self.index = None
    #self.expired_queue = []
    #self.wrong_queue = []
    self.can_launch = True

  def open(self, time_limit=55.0):
    'docstring'
    now = update_cached_time()
    self.start_time = now
    self.end_time = now+time_limit*60.0

  def reset(self):
    'docstring'
    if self.stub:
      return
    pic_name = os.path.join(SetBase.pjs_dir_name, self.name+'.jp2')
    try:
      os.remove(pic_name)
    except:
      pass
    self.cc = None
    self.expired_q = Que()
    self.wrong_q = Que()
    self.stub = True
    self.pjs = {}
    self.last_find_expired = 0.0
    self.last_scan_time = 0.0
    stats = { eet: 9.9e15, let: 0.0, todo_cnt: 0, h16: 0,
              stale:0, fresh:0 }
    #self.pjs['set'] = {}
    #self.__init__(self.name,self.can_launch)
    # FIXME TODO BUG calling __init__ doesn't reset the state properly

  def __init__(self, name, cl=False, st=True):
    UtilBase.__init__(self, name, cl, st)
    if len(SetBase.pjs_dir_name) ==0:
      self.mk_pjs_dir()
    self.read_cards()
    #self.pjs = {}
    #self.pjs['set'] = {}
    self.pjs = Pjs()
    #self.name =name
    #self.total_cnt = 0
    #self.todo_cnt = 0
    #self.done_cnt = 0
    #self.expire_h16_cnt = 0
    #self.can_launch = False
    #self.stub = True
    self.dirty = False
    self.cc = None
    self.expired_q = Que()
    self.wrong_q = Que()
    self.last_find_expired = 0.0
    self.last_scan_time = 0.0
    self.stats = { 'eet': 9.9e15, 'let': 0.0, 'todo_cnt': 0, 'h16': 0,
              'stale':0, 'fresh':0, 'group_total':0, 'item_total':0,
              'total_cnt':0  }
    now = cached_now
    self.start_time = now
    self.end_time = now+300.0
    self.load_pickle()
    self.ordered_list=False

# level 1 has 4 items of context; usually 2 before and 2 after
# level 2 has 2 items of context; usually 2 before
# level 3 has 1 item of context; always before
class OldSeqBase(SetBase):
  'sequence base'
# create_set and read_cards
  def read_cards(self):
    'docstring'
    self.cards = {}
    min_blank_sz = 20
    sz = len(self.my_seq)
    for ite in self.my_seq :
      if len(ite) < min_blank_sz: min_blank_sz =  len(ite)
    #self.cards['_'] = {}
    for ii in range(sz):
      front_txt = ''
      back_txt = ''
      jj = ii -4 + self.lvl
      kk = ii +4 - self.lvl
      if kk >= sz :
        kk = sz-1
      if self.lvl >= 4 :
        kk = ii
        jj = ii-1
      if jj < 0 :
        jj = 0
      for ll in range(jj, kk+1):
        if ll == ii :
          front_txt = front_txt + ' ' + (min_blank_sz*'?')
        else:
          front_txt = front_txt + ' ' + self.my_seq[ll]
        back_txt = back_txt + ' ' + self.my_seq[ll]
      self.cards[str(ii)] = {}
      self.cards[str(ii)]['_'] = (front_txt, back_txt)

#  def create_set(self):
#    'docstring'
#    now = update_cached_time()
#    et = now -12.0
#    min_et = min(240.0, 2*len(self.cards))
#    gt = et - min_et
#    bt = gt -999.9
#    for nn in range(len(self.cards)):
#      self.pjs.set[str(nn)] = { 'expire':  et, 'lgood': gt, 'lbad': bt}
#    self.total_cnt = len(self.cards)
#    self.todo_cnt = self.total_cnt
#    self.stub = False

  def __init__(self, name, seq, lvl, cl=True, st=True):
    suffix = [ ' 0', ' I', ' II',' III', ' IV']
    self.my_seq = seq
    self.lvl = lvl
    SetBase.__init__(self, name+suffix[lvl], cl, st)
    self.stats['todo_cnt']=len(self.cards)

class InlineBase(SetBase):
  'inline base'
  def read_cards(self):
    'read cards'
    self.cards = {}
    sz = len(self.my_pairs)
    for ii in range(sz):
      #print self.my_pairs[ii][0] +'\n'
      self.cards[ii] = {}
      self.cards[ii]['a'] = (self.my_pairs[ii][0], self.my_pairs[ii][1])
      self.cards[ii]['b'] = (self.my_pairs[ii][1], self.my_pairs[ii][0])

#  def create_set(self):
#    'create set'
#    now = update_cached_time()
#    et = now -12.0
#    min_et = min(240, 2*len(self.cards))
#    gt = et - min_et
#    bt = gt -999.9
#    # BUG FIXME this loop can be made generic
#    # and then create_set can be moved up to SetBase BUG FIXME
#    for nn in range(len(self.cards)//2):
#      self.pjs.set['a'+str(nn)] = { 'expire':  et, 'lgood': gt, 'lbad': bt}
#      self.pjs.set['b'+str(nn)] = { 'expire':  et, 'lgood': gt, 'lbad': bt}
#    self.total_cnt = len(self.cards)
#    self.todo_cnt = self.total_cnt
#    self.stub = False

  def __init__(self, name, pairs, cl=True, st=True):
    self.my_pairs = pairs
    SetBase.__init__(self, name, cl, st)
    self.stats['todo_cnt']=len(self.cards)


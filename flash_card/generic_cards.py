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



class UtilBase:
  'utility base'
  now = 0.0

  def __init__(self, name='', clh=False, stb=True):
    self.name = name
    self.can_launch = clh
    self.stub = stb
    self.cards = {}

  # hard_now and soft_now is actually stupid the settimeofday syscall
  # used to be bottleneck for some apps but most modern kernels
  # should have it optimized
  # looking at it now, I think I'm going to rip them out as
  # because they are dumb here
  def hard_now(self):
    'docstring'
    UtilBase.now = time.time()
    return UtilBase.now
  def soft_now(self):
    'docstring'
    if UtilBase.now > 99.9:
      return UtilBase.now
    else:
      return self.hard_now()

  #def find_earliest_expired_time(self, model=None, itera=None):
  #  'this should be overriden later'
  #  return '     '

  #def find_last_expired_time(self, model=None, itera=None):
  #  'this should be overriden later'
  #  return '     '

  def format_time(self, tim):
    'format time'
    now = self.soft_now()
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
    self.set = {}
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

  def create_set(self):
    'should be overridden'

  def read_cards(self):
    'should be overridden'

  def change_index(self):
    'docstring'
    ex_sz = len(self.expired_queue)
    wr_sz = len(self.wrong_queue)
    in_wr = wr_sz and (self.index == self.wrong_queue[0])
    in_ex = ex_sz and (self.index == self.expired_queue[0])
    # used variables to store boolean values because otherwise exceeding 80 char
    if self.index and len(self.index):
      if in_ex:
        self.expired_queue.pop(0)
        ex_sz = ex_sz-1
        #in_ex = ex_sz and (self.index == self.expired_queue[0])
        # the above line would keep that variable truthful,
        # but it's not used again
      elif in_wr:
        self.wrong_queue.pop(0)
        wr_sz = wr_sz-1
        in_wr = wr_sz and (self.index == self.wrong_queue[0])
    if ex_sz > 3 and self.index and len(self.index) and (
        self.index[0:-1] == self.expired_queue[0][0:-1]) :
      #print 'skipped ', self.index[0:-1]
      tmp = self.expired_queue[0]
      self.expired_queue.pop(0)
      self.expired_queue.append(tmp)
    recent_wrong = (wr_sz and
       self.pjs.set[self.wrong_queue[0]]['lbad'] <
               (self.soft_now()-25-min(25,ex_sz/10.0)) )
    if not in_wr and recent_wrong:
      self.index = self.wrong_queue[0]
    elif ex_sz:
      self.index = self.expired_queue[0]
    elif wr_sz:
      self.index = self.wrong_queue[0]
    else:
      self.index = None

  def find_earliest_expired_time(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return self.soft_now()-99.9
    kitems = self.pjs.set.keys()
    #print 'kitems ', kitems[0]
    eet = self.pjs.set[kitems[0]]['expire']
    for item in kitems:
      if eet > self.pjs.set[item]['expire']:
        eet = self.pjs.set[item]['expire']
    return eet

  def find_last_expired_time(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return self.soft_now()-99.9
    kitems = self.pjs.set.keys()
    #print 'kitems ', kitems[0]
    ltet = self.pjs.set[kitems[0]]['expire']
    for item in kitems:
      if ltet < self.pjs.set[item]['expire']:
        ltet = self.pjs.set[item]['expire']
    return ltet


  def find_expired_cnt(self):
    'docstring'
    if len(self.expired_queue) or len(self.wrong_queue) :
      return
    now = self.soft_now()
    self.expire_h16_cnt = 0
    self.todo_cnt = 0
    for item in self.pjs.set.keys():
      if now > self.pjs.set[item]['expire']:
        self.todo_cnt = self.todo_cnt + 1
      if now > (self.pjs.set[item]['expire'] - 57600):
        self.expire_h16_cnt = self.expire_h16_cnt + 1


  def find_expired(self, force=False):
    'docstring'
    if len(self.expired_queue) or len(self.wrong_queue) :
      if force:
        self.index = None
        self.expired_queue = []
        self.wrong_queue = []
      else:
        return
    now = self.soft_now()
    self.last_find_expired = now
    self.expire_h16_cnt = 0
    #print 'finding expired for ', self.name
    for item in self.pjs.set.keys():
      if now > self.pjs.set[item]['expire']:
        self.expired_queue.append(item)
      if now > (self.pjs.set[item]['expire'] - 57600):
        self.expire_h16_cnt = self.expire_h16_cnt + 1
    random.shuffle(self.expired_queue)
    self.todo_cnt = len(self.expired_queue)

  def realize(self, force=False):
    'docstring'
    if self.stub:
      self.create_set()
    now = self.soft_now()
    if len(self.expired_queue)==0 and len(self.wrong_queue)==0:
      self.find_expired()
      self.dump_pickle()
    # 25 minutes
    elif now > (self.last_find_expired + 1500) and len(self.wrong_queue)==0:
      self.find_expired()
      self.dump_pickle()
    if not self.index:
      self.change_index()

  def front(self):
    'docstring'
    self.realize()
    if self.index:
      return self.cards[self.index][0]
    return 'You have completed this set'

  def back(self):
    'docstring'
    #self.realize()           
    if self.index:
      return self.cards[self.index][1]
    return ''

  def no(self):
    'docstring'
    self.dirty = True
    now = self.hard_now()
    self.pjs.set[self.index]['lbad'] = now
    self.wrong_queue.append(self.index)
    self.change_index()

  def yes(self):
    'docstring'
    self.dirty = True
    now = self.hard_now()
    if self.pjs.set[self.index]['lbad'] > self.pjs.set[self.index]['lgood']:
      dt_nb = now - self.pjs.set[self.index]['lbad']
      dt_max = max(min(25.0+self.todo(), dt_nb+5.8), 1.6*self.todo() )
      self.pjs.set[self.index]['expire'] = now+min(dt_max, 251.0)
    else:
      dt_eg = (self.pjs.set[self.index]['expire'] -
              self.pjs.set[self.index]['lgood'] )
      #dt_min = max(dt_eg,min(250+self.total(),2500))
      #dt_min = max(dt_eg, 90+2*max(90,self.expire_h16()) )
      dt_min = max(dt_eg, 4.0+min(240.0, self.expire_h16()) )
      dt_ne = now - self.pjs.set[self.index]['expire']
      dt_base = max(dt_eg, 6.5, self.todo() )
      # a little under 22 hours
      dt_max_day = min(7.4*dt_base,
                  max(4.5*dt_eg, 6.0*dt_ne, 1.9*self.todo()), 79073.0)
      dt = max(2.1*dt_eg, dt_max_day)
      #dt = min(12.2*dt_min, max(4.5*dt_min, 9*dt_ne),
      #         dt_eg+86400+45*self.total())
      #dt = min(12.2*dt_min, max(4.5*dt_min,9*dt_ne), dt_eg+86400)
      # experiment with having the one day cap be bigger
      # and vary based on work load
      self.pjs.set[self.index]['expire'] = now+dt
      #print self.index , ' expanded from ' , dt_eg, ' to ', dt
    self.pjs.set[self.index]['lgood'] = now
    self.change_index()
    self.todo_cnt = self.todo_cnt-1
# math.sqrt(math.e) ~=~ 1.6487 # golden ratio ~=~ 1.6180
# math.pow(math.e,1.5) ~=~ 4.482 thus 4.5
# math.pow(math.e,2) ~=~ 7.389 thus 7.4
# math.pow(math.e,2.5) ~=~ 12.182 thus 12.2

  def skip(self):
    'docstring'
    # if skipping thing already on wrong que and wrong que is of short size
    # put it on the end of the expired_queue instead
    ex_sz = len(self.expired_queue)
    wr_sz = len(self.wrong_queue)
    in_wr = wr_sz and (self.index == self.wrong_queue[0])
    if in_wr and wr_sz < 2 and ex_sz > 2 :
      self.expired_queue.append(self.index)
    else:
      self.wrong_queue.append(self.index)
    self.change_index()

  def total(self, model=None, itera=None):
    'docstring'
    return self.total_cnt

  def accu_todo(self):
    'docstring'
    rcnt = 0
    now = self.soft_now()
    for itm in self.pjs.set.keys():
      if now > self.pjs.set[itm]['expire']:
        rcnt = rcnt +1
    return rcnt
    # return count of expired things

  def todo(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return self.total_cnt
    else:
      td_sz = max(self.todo_cnt,
                  len(self.wrong_queue) + len(self.expired_queue))
      if td_sz:
        return td_sz
      return self.accu_todo()
      #return len(self.wrong_queue) + len(self.expired_queue)
    #return self.todo_cnt

  def expire_h16(self, model=None, itera=None):
    'docstring'
    if self.stub:
      return self.total_cnt
    return max(self.expire_h16_cnt, self.todo())

  def done(self, model=None, itera=None):
    'docstring'
    return self.total_cnt - len(self.wrong_queue) - len(self.expired_queue)
    #return self.done_cnt

  # TODO FIXME try finding and loading a pickle
  # TODO FIXME doesn't use fsync or write to new file and then rename FIXME
  # FIXME potential for corruption and data loss about crash FIXME
  # WARN this might change in non-backwards compatible way WARN
  # http://www.dwheeler.com/essays/fixing-unix-linux-filenames.html#spaces
  # also should make sure filenames don't contain spaces or other cruft
  def load_pickle(self):
    'docstring'
    pic_name = os.path.join(SetBase.pjs_dir_name, self.name+'.jp1')
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
    self.total_cnt = len(self.pjs.set)
    self.find_expired_cnt()

  def dump_pickle(self):
    'docstring'
    if not self.dirty:
      return
    pic_name = os.path.join(SetBase.pjs_dir_name, self.name+'.jp1')
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
    now = self.hard_now()
    self.start_time = now
    self.end_time = now+time_limit*60.0

  def reset(self):
    'docstring'
    if self.stub:
      return
    pic_name = os.path.join(SetBase.pjs_dir_name, self.name+'.jp1')
    try:
      os.remove(pic_name)
    except:
      pass
    self.index = None
    self.expired_queue = []
    self.wrong_queue = []
    self.stub = True
    self.pjs = {}
    self.last_find_expired = 0.0
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
    self.total_cnt = 0
    self.todo_cnt = 0
    self.done_cnt = 0
    self.expire_h16_cnt = 0
    #self.can_launch = False
    #self.stub = True
    self.dirty = False
    self.index = None
    self.expired_queue = []
    self.wrong_queue = []
    self.last_find_expired = 0.0
    now = self.soft_now()
    self.start_time = now
    self.end_time = now+300.0
    self.load_pickle()

# level 1 has 4 items of context; usually 2 before and 2 after
# level 2 has 2 items of context; usually 2 before
# level 3 has 1 item of context; always before
class SeqBase(SetBase):
  'sequence base'
# create_set and read_cards
  def read_cards(self):
    'docstring'
    self.cards = {}
    min_blank_sz = 20
    sz = len(self.my_seq)
    for ite in self.my_seq :
      if len(ite) < min_blank_sz: min_blank_sz =  len(ite)
    for ii in range(sz):
      front_txt = ''
      back_txt = ''
      jj = ii -3 + self.lvl
      kk = ii +3 - self.lvl
      if kk >= sz :
        kk = sz-1
      if self.lvl >= 3 :
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
      self.cards[str(ii)] = (front_txt, back_txt)

  def create_set(self):
    'docstring'
    now = self.hard_now()
    et = now -12.0
    min_et = min(240.0, 2*len(self.cards))
    gt = et - min_et
    bt = gt -999.9
    for nn in range(len(self.cards)):
      self.pjs.set[str(nn)] = { 'expire':  et, 'lgood': gt, 'lbad': bt}
    self.total_cnt = len(self.cards)
    self.todo_cnt = self.total_cnt
    self.stub = False

  def __init__(self, name, seq, lvl, cl=True, st=True):
    suffix = [ ' 0', ' I', ' II',' III']
    self.my_seq = seq
    self.lvl = lvl
    SetBase.__init__(self, name+suffix[lvl], cl, st)

class InlineBase(SetBase):
  'inline base'
  def read_cards(self):
    'read cards'
    self.cards = {}
    sz = len(self.my_pairs)
    for ii in range(sz):
      #print self.my_pairs[ii][0] +'\n'
      self.cards['a'+str(ii)] = (self.my_pairs[ii][0], self.my_pairs[ii][1])
      self.cards['b'+str(ii)] = (self.my_pairs[ii][1], self.my_pairs[ii][0])

  def create_set(self):
    'create set'
    now = self.hard_now()
    et = now -12.0
    min_et = min(240, 2*len(self.cards))
    gt = et - min_et
    bt = gt -999.9
    # BUG FIXME this loop can be made generic
    # and then create_set can be moved up to SetBase BUG FIXME
    for nn in range(len(self.cards)//2):
      self.pjs.set['a'+str(nn)] = { 'expire':  et, 'lgood': gt, 'lbad': bt}
      self.pjs.set['b'+str(nn)] = { 'expire':  et, 'lgood': gt, 'lbad': bt}
    self.total_cnt = len(self.cards)
    self.todo_cnt = self.total_cnt
    self.stub = False

  def __init__(self, name, pairs, cl=True, st=True):
    self.my_pairs = pairs
    SetBase.__init__(self, name, cl, st)


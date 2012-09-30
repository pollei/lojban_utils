#! /usr/bin/python
# coding=utf8
"""
 attempts to be flash card program; has some lojban specific quirks
"""

# copyright (C) 2009/2012 "Stephen Joseph Pollei" <stephen.pollei@gmail.com>
# licensed gplv3 or later -- http://www.fsf.org/licensing/licenses/gpl.html

# attempts to be flash card program; has some lojban specific quirks


# http://espeak.sourceforge.net


# works under Linux
# untested on MS Windows and Mac osx

# links to help you get stuff installed for windows
# http://python.org/ftp/python/2.6.3/python-2.6.3.msi
# http://pygtk.org/downloads.html
# http://www.gtk.org/download-windows.html#StableRelease
# http://ftp.gnome.org/pub/GNOME/binaries/win32/gtk+/
#   How do I get PyGTK running on MS Windows?
# http://faq.pygtk.org/index.py?req=show&file=faq21.001.htp 

# http://www.lojban.org/tiki/tiki-index.php?page=Software%20assisted%20learning
# there are other alternatives as well
# I've heard great things about anki and supermemeo

# It needs to have cmavo.txt and gismu.txt in a location that it can find them
# I did add stuff so that it will attempt to download the lojban vocab it needs
# http://www.lojban.org/publications/wordlists/cmavo.txt
# http://www.lojban.org/publications/wordlists/gismu.txt
# http://www.lojban.org/publications/wordlists/lujvo.txt
# It also wants valsi_f.txt, which can be created by downloaded big_list
# and trimming it
# http://digitalkingdom.org/~rlpowell/hobbies/lojban/flashcards/big_list
# cut -f1 big_list > valsi_f.txt

# WARNING this is currently alpha level software and I plan on doing
# non-backwards compatible changes to the "progress data" persistent storage
# so don't be surprised on problems and possible data loss if you upgrade

# http://en.wikipedia.org/wiki/Spaced_repetition
# http://en.wikipedia.org/wiki/Pimsleur_language_learning_system
# pimsleur uses 5 seconds, 25 seconds, 2 minutes, 10 minutes, 1 hour, 5 hours,
#    1 day, 5 days, 25 days, 4 months, 2 years
# pimsleur uses phrases not singular words
# http://en.wikipedia.org/wiki/Sebastian_Leitner
# http://en.wikipedia.org/wiki/Flashcard
# http://en.wikipedia.org/wiki/SuperMemo
# http://headinside.blogspot.com/2009/04/more-free-flashcard-sites.html
# http://en.wikipedia.org/wiki/Spacing_effect
# https://ww5.pimsleurapproach.com/

# http://www.wired.com/medtech/health/magazine/16-05/ff_wozniak?currentPage=2
# Want to Remember Everything You'll Ever Learn? Surrender to This Algorithm

# this program uses a home-brew spaced repetition
# for times less than a day or so, it roughly increases the time between
# flashing using a exponential growth formula that takes into consideration
# how much work needs to be done soon
# if the increase between flashing would itself increase by more than a day
# we cap it

# http://how-to-learn-any-language.com/e/books/how-to-learn-any-language.html
# http://www.language-learning-advisor.com/review-barry-farber.html
# I might want to add support for the "plunge" method

# for rafsi and lujvo I desire better lists of lujvo and stage 3 fu'ivla
# http://jbovlaste.lojban.org/
# http://www.lojban.org/tiki/tiki-index.php?page=lo+valsi+po+la+nicte+cadzu&bl=y


# http://www.pygtk.org/
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

# http://docs.python.org/library/
import re, random, time, cPickle, os, urllib, sys
# os.listdir, os.name 'posix' , os.mkdir


# I could probably form this list when I read in cmavo.txt
#but it's small enough and I already formed it by other means
bai_gismu_list = [
  'bangu', 'bapli', 'basti', 'benji', 'catni', 'cinmo', 'ciste',
  'ckaji', 'ckilu', 'ckini', 'claxu', 'cmene', 'cusku', 'detri',
  'diklo', 'djuno', 'dunli', 'fasnu', 'fatne', 'finti', 'gasnu',
  'jalge', 'javni', 'jicmu', 'jimte', 'jitro', 'klama', 'klani',
  'klesi', 'korbi', 'krasi', 'krati', 'krinu', 'kulnu', 'lidne',
  'lifri', 'manri', 'marji', 'mleca', 'mukti', 'mupli', 'nibli',
  'pagbu', 'panra', 'pilno', 'pluka', 'porsi', 'pruce', 'rinka',
  'sarcu', 'sidju', 'srana', 'stidi', 'stuzi', 'tadji', 'tcika',
  'traji', 'vanbi', 'xamgu', 'zanru', 'zgana', 'zmadu', 'zukte' ]


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
    if len(LojbanBase.pjs_dir_name) ==0:
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

class LojbanBase(SetBase):
  'lojban base foundation'
  #now =0
  shared_cards = {}
  gismu_morna = re.compile("[bcdfgjklmnpqrstvxz][bcdfgjklmnpqrstvxz][aeiou]")
  da_morna = re.compile("[a-z]{0,2}[aeiou][a-z']{0,2}")
  selmaho = {}
  raf_sets = {}
  raf_map = {}
  #selmahop = {}

  def kar_path(self):
    'find the path for opening'
    if os.name in [ 'posix', 'unix', 'linux' ]:
      paths = [ '/usr/share/data/lojban', '/usr/data/lojban/',
        os.path.expanduser('~/Desktop/lojban/'),
        os.path.expanduser('~/.lojban/'), './' ]
    elif os.name in [ 'windows', 'nt', 'ce']:
      paths = [ "c:\\program_data\\lojban\\" , 'c:\\lojban\\' ,
               os.path.expanduser('~\\lojban\\') ]
      # not tested in windows and I'm not running windows
    elif os.name in [ 'mac', 'os2', 'java', 'riscos']:
      paths = [ os.path.expanduser('~/lojban/') ]
      # not tested in mac osx or other oses
    else:
      raise NotImplementedError, ('unknown operating system: ' + os.name)
    for pname in paths:
      if (os.path.isdir(pname) and
             os.path.exists(os.path.join(pname, 'gismu.txt')) ):
        return pname
    # http://www.lojban.org/publications/wordlists/cmavo.txt
    # http://www.lojban.org/publications/wordlists/gismu.txt
    # .jbo_fc maybe only make one directory cut in ~ -- down on clutter
    if os.name in [ 'posix', 'unix', 'linux' ]:
      pname = os.path.expanduser('~/.lojban/')
      os.makedirs(pname, 0o770)
      cname = os.path.join(pname, 'cmavo.txt')
      gname = os.path.join(pname, 'gismu.txt')
      urllib.urlretrieve(
        'http://www.lojban.org/publications/wordlists/cmavo.txt',cname)
      urllib.urlretrieve(
        'http://www.lojban.org/publications/wordlists/gismu.txt',gname)
      return pname
    else:
      raise RuntimeError, 'could not find lojban data directory'

  # karna means open
  def kar(self, fname, mode='r'):
    'open'
    return open(os.path.join(self.kar_path() , fname), mode)
    # may raise "IOError: [Errno 2]" if the file isn't found

  def read_cards(self):
    'read cards'
    if len(LojbanBase.shared_cards) :
      self.cards = LojbanBase.shared_cards
      return
    gf = self.kar( "gismu.txt")
    for line in gf:
      word = line[1:6].rstrip()
      if LojbanBase.gismu_morna.search(word):
        LojbanBase.shared_cards[word + "0"] = ( word, line[7:])
        LojbanBase.shared_cards[word + "1"] = (
                             line[20:61] + "gismu" , line[1:] )
        #print line[1:6], '---', line[7:19], '---',line[20:61]'---',line[62:]
      if LojbanBase.da_morna.search(word):
        if LojbanBase.da_morna.search(line[7:19]):
          #print line[1:6], '-', line[7:10] , '-',line[11:14], '-',line[15:19]
          LojbanBase.raf_sets[word] = set([x.rstrip()
              for x in [line[7:10],line[11:14],line[15:19]]
              if LojbanBase.da_morna.search(x) ] )
          for x in LojbanBase.raf_sets[word] :
            #print x, '-->',word
            LojbanBase.raf_map[x] = word
    gf.close()
    cf = self.kar( "cmavo.txt")
    cp = re.compile("[a-z']+")
    baip = re.compile("BAI")
    #selmaho_pat = re.compile("[BCDFGJKLMNPQRSTVXZ]?[AEIOU]h?[AEIOU]?\*?")
    selmaho_pat = re.compile("[BCDFGJKLMNPQRSTVXZ]?[AEIOUY]h?[AEIOUY]?")
    # right now lump compounds in the same set as singular cmavo
    bp = re.compile("[^:;\n]+")
    # FIXME TODO while I'm reading the cmavo file
    # I might as well be collecting selma'o data FIXME TODO
    for line in cf:
      cpm = cp.match(line[1:11])
      spm = selmaho_pat.match(line[11:19])
      if cpm and spm:
        word = line[1:11].strip(' ')
        bonus = ""
        bpm = bp.match(line[62:])
        if baip.match(line[11:19]):
          bonus = "modal"
        if bpm and not baip.match(line[11:19]):
          bonus = bpm.group(0)
        smw = spm.group(0)
        #if LojbanBase.selmaho.has_key(smw) :
        if smw in LojbanBase.selmaho :
          LojbanBase.selmaho[smw].append(word)
        else:
          LojbanBase.selmaho[smw] = [word]
        LojbanBase.shared_cards[word + "0"] = ( word , line[11:])
        LojbanBase.shared_cards[word + "1"] = (line[20:62] + bonus, line[1:])
        #print word, ' ++ ',line[1:11],'---',line[11:19],'---'
        #print line[20:62] + bonus, '---',line[62:]
    cf.close()
    self.cards = LojbanBase.shared_cards
    #print LojbanBase.selmaho
    return
    #lf = self.kar( "lujvo.txt")
    #lf.close()
    #FIXME todo read the lujvo list
    # so you can get a nice list of words for the rafsi section FIXME

  def espeak_phomeize_gismu(self, strg):
    'espeak normals letters to phomeme for gismu'
    ret = ''
    subs1 = { 'j':'Z', 'r':'R', 'c':'S', 'a':"'a",
        'e':"'e", 'i':"'i", 'o':"'o", 'u':"'u" }
    pstr = strg[:3]
    while len(pstr):
      if pstr[:1] in subs1:
        ret = ret + subs1[pstr[:1]]
        pstr = pstr[1:]
      else:
        ret = ret + pstr[:1]
        pstr = pstr[1:]
    ret = ret+ '_'
    pstr = strg[3:]
    subs2 = { 'j':'Z', 'r':'R', 'c':'S' }
    while len(pstr):
      if pstr[:1] in subs2:
        ret = ret + subs2[pstr[:1]]
        pstr = pstr[1:]
      else:
        ret = ret + pstr[:1]
        pstr = pstr[1:]
    return ret

  def espeak_phomeize(self, strg):
    'espeak normals letters to phomeme'
    ret = ''
    subs = { 'y':'@', 'ai':'aI', 'au':'aU', 'ei':'eI', 'ia':'ij', 'ie':'ij',
        'ii':'ij', 'io':'ij', 'iu':'ij', 'j':'Z', 'oi':'OI', 'r':'R', "'":'h',
        'ua':'wa','ue':'we','ui':'wi','uo':'wo','uu':'wu', 'c':'S'}
    while len(strg):
      if strg[0:2] in subs:
        ret = ret + subs[strg[:2]]
        strg = strg[2:]
      elif strg[:1] in subs:
        ret = ret + subs[strg[:1]]
        strg = strg[1:]
      else:
        ret = ret + strg[:1]
        strg = strg[1:]
    return ret
    # FIXME TODO must add stress and split syllable and transform a few letters
    # http://espeak.sourceforge.net/commands.html
    # ' , = % stresses
    # 'primary-stress ,secondary-stress %unstressed 

  def sound(self):
    'make a sound using espeak'
    if not self.index:
      return ''
    strg = self.index[0:-1]
    cmavo_pat = re.compile(
       "([bcdfgjklmnpqrstvxz]?[aeiouy\']+)([bcdfgjklmnpqrstvxz][aeiouy\']+)")
    cpm = cmavo_pat.match(str)
    if cpm:
      strg = cpm.group(1) + ' ' + cpm.group(2)
    gm = LojbanBase.gismu_morna.search(strg)
    if gm:
      pstr = ' [[ _: ' + self.espeak_phomeize_gismu(strg) + ' ]] '
    else:
      pstr = ' [[ _: ' + self.espeak_phomeize(strg) + ' ]] '
    #print 'sound ' , str ,'\n'
    # _:  	short pause
    ecmd = (
    "speak -v jbo -s 115 -w \".snd/" + 
      self.index[0:-1] + ".wav\" \"" +pstr + '"' )
    mcmd = ("mplayer -really-quiet -noconsolecontrols -nojoystick -nolirc ")
    print 'sound ' , ecmd , '\n', mcmd
    
    return strg
    #return None

  def gen_word_list(self):
    'generate word list -- needs to be overridden'

# create set has gotten too ugly to live
# combines creation from scratch with
# two different ways of copying from another set
  def create_set(self, o_set=None, copy_how=0):
    'create set'
    #print ' super creating ', self.name, ' begin '
    wlist = self.gen_word_list()
    now = self.hard_now()
    et = now -12.0
    #min_et = len(wlist) + 4*min(900,len(wlist))

    min_et = min(240, 2*len(wlist))
    rgt = et - 0.5
    rbt = rgt -999.9
    for word in wlist:
      try:
        e0 = o_set.set[word+'0']['expire'] - (
          max(o_set.set[word+'0']['lgood'],o_set.set[word+'0']['lbad']))
        e1 = o_set.set[word+'1']['expire'] - (
          max(o_set.set[word+'1']['lgood'],o_set.set[word+'1']['lbad']))
        if 0 == copy_how:
          # some of the sets duplicate things from other sets
          # this makes your hard work on extending earlier expire times
          # make these expire times longer as well 
          gt = et - max(min_et, 0.75*min(e0, e1))
          #if gt < rgt : print 'super creation worked for ' , word
          bt = gt - 999.9
        else:
          # the second copy_how way does a more direct copy
          # if you know the word well
          bad0 = o_set.set[word+'0']['lbad'] > o_set.set[word+'0']['lgood']
          bad1 = o_set.set[word+'1']['lbad'] > o_set.set[word+'1']['lgood']
          if bad0 or bad1 or e0 < min_et or e1 < min_et :
            gt = rgt
            bt = rbt
          else :
            #print 'super direct creation worked for ' , word
            self.pjs.set[word+'0'] = { 'expire':  o_set.set[word+'0']['expire'],
                'lgood': o_set.set[word+'0']['lgood'],
                'lbad': o_set.set[word+'0']['lbad'] }
            self.pjs.set[word+'1'] = { 'expire':  o_set.set[word+'1']['expire'],
                'lgood': o_set.set[word+'1']['lgood'],
                'lbad': o_set.set[word+'1']['lbad'] }
            continue
      except:
        gt = rgt
        bt = rbt
        # if the set didn't exist in the old original set then
        # a KeyError exception will be raised and we can use a sane default
      r0 = 7.9*random.random()
      r1 = 7.9*random.random()
      self.pjs.set[word+'0'] = { 'expire':  et, 'lgood': gt-r0, 'lbad': bt}
      self.pjs.set[word+'1'] = { 'expire':  et, 'lgood': gt-r1, 'lbad': bt}
    self.total_cnt = len(wlist)*2
    self.todo_cnt = self.total_cnt
    #print ' super creating ', self.name, ' size ', self.total_cnt
    self.stub = False

  def __init__(self, name, cl=False):
    SetBase.__init__(self, name, cl)

class LojbanByF(LojbanBase):
  'lojban by frequency'
  byf_lists = {'valsi': [], 'gismu': [] , 'cmavo':[], 'rafsi':[] }

  def __init__(self, typen, vcnt):
    self.type_name = typen
    self.valsi_cnt = vcnt
    self.wants_super_creation = True
    LojbanBase.__init__(self, typen + ' ' + str(vcnt), True)
    #self.can_launch = True
    if self.stub:
      self.todo_cnt = 2*vcnt
      self.total_cnt = 2*vcnt

  def init_valsi_byf_list(self):
    'initialize words by frequency list'
    if len(LojbanByF.byf_lists['valsi']) == 0:
      # cut -f1 big_list > valsi_f.txt
      # http://digitalkingdom.org/~rlpowell/hobbies/lojban/flashcards/big_list
      try:
        vff = self.kar( "valsi_f.txt")
      except IOError, prob:
        bl = urllib.urlopen(
       'http://digitalkingdom.org/~rlpowell/hobbies/lojban/flashcards/big_list')
        vff = self.kar( "valsi_f.txt",'w')
        for lin in bl:
          vff.write(lin.split()[0] + '\n') 
        vff.close()
        vff = self.kar( "valsi_f.txt")
      LojbanByF.byf_lists['valsi'] = [ lin.strip('.\n') for lin in vff ]
      vff.close()

  def init_byf_lists(self):
    'initialize by frequency lists'
    self.init_valsi_byf_list()
    if len(LojbanByF.byf_lists['gismu']) == 0:
      for word in LojbanByF.byf_lists['valsi']:
        if LojbanBase.gismu_morna.search(word):
          LojbanByF.byf_lists['gismu'].append(word)
        else:
          LojbanByF.byf_lists['cmavo'].append(word)

  def gen_word_list(self):
    'generate word list'
    if self.type_name == 'valsi': 
      self.init_valsi_byf_list()
    else:
      self.init_byf_lists()
    #self.word_order = LojbanByF.byf_lists[self.type_name]
    return LojbanByF.byf_lists[self.type_name][:self.valsi_cnt]

  def grow_set(self, amount):
    'grow a set'
    #self.total_cnt= self.total_cnt+2*amount
    start_ind = self.total_cnt//2
    wl_sz = len( LojbanByF.byf_lists[self.type_name])
    if start_ind >= wl_sz :
      return

    # FIXME AUDIT a lot of this only triggers near the end,
    # so is under tested FIXME AIDIT
    left_sz = wl_sz-start_ind
    if amount > left_sz : amount = left_sz
    if left_sz < 50 :
      if left_sz > 24 :
        if amount > left_sz//2 +1 and left_sz-amount < 12 and amount < left_sz :
          amount = left_sz//2 +1

    end_ind = start_ind + amount
    add_list = LojbanByF.byf_lists[self.type_name][start_ind:end_ind]
    now = self.soft_now()
    et = now -12.0
    min_et = min(240, 2*end_ind)
    gt = et - 0.5
    bt = gt -999.9
    for word in add_list :
      print 'growing ', word
      r0 = 7.9*random.random()
      r1 = 7.9*random.random()
      self.pjs.set[word+'0'] = { 'expire':  et, 'lgood': gt-r0, 'lbad': bt}
      self.pjs.set[word+'1'] = { 'expire':  et, 'lgood': gt-r1, 'lbad': bt}
      if self.pjs.set[word+'0']['lgood'] < self.pjs.set[word+'1']['lgood'] :
        self.expired_queue.append(word+'0')
      else :
        self.expired_queue.append(word+'1')
    self.total_cnt = self.total_cnt+2*amount
    self.todo_cnt = self.todo_cnt+2*amount
    self.expire_h16_cnt = self.expire_h16_cnt+2*amount

  # limit the number of expired things found to first 400
  #  grow the list if it's too short
  def find_expired(self, force=False):
    #print 'finding expired for ', self.name
    now = self.soft_now()
    if now > (self.last_find_expired + 787.0) :
      force = True
    if len(self.expired_queue) or len(self.wrong_queue) :
      if force:
        self.index = None
        self.expired_queue = []
        self.wrong_queue = []
      else:
        return
    self.last_find_expired = now
    self.expire_h16_cnt = 0
    #print 'finding expired for ', self.name
    for item in self.pjs.set.keys():
      if now > (self.pjs.set[item]['expire'] - 57600):
        self.expire_h16_cnt = self.expire_h16_cnt + 1
    dt_fresh = max(350, 100+self.expire_h16_cnt)
    #print 'dt_fresh: ',dt_fresh, ' total_cnt:', self.total_cnt
    fresh_cnt = 0
    stale_cnt = 0
    #self.word_order = LojbanByF.byf_lists[self.type_name]
    #print 'type name:', self.type_name
    #print 'word size list',len(LojbanByF.byf_lists[self.type_name])
    if len(LojbanByF.byf_lists[self.type_name]) == 0 :
      self.gen_word_list()
    #for word in LojbanByF.byf_lists[self.type_name][:self.total_cnt/2]:
    for word in LojbanByF.byf_lists[self.type_name][:self.total_cnt//2]:
      #print 'evaluating:', word
      if (now >  self.pjs.set[word+'0']['expire'] +115200) :
        stale_cnt = stale_cnt +1
        #print 'stale ', word, ' ', self.pjs.set[word+'0']['expire']-115200 
        if stale_cnt > 110 :
          break
      if (now >  self.pjs.set[word+'1']['expire'] +115200):
        stale_cnt = stale_cnt +1
        if stale_cnt > 110 :
          break

      # only put one of the pairs in at a time
      # and not too soon after another was answered
      la0 = max( self.pjs.set[word+'0']['lgood'] ,
                 self.pjs.set[word+'0']['lbad'] )
      la1 = max( self.pjs.set[word+'1']['lgood'] ,
                 self.pjs.set[word+'1']['lbad'] )
      twin_t = min(36987.6,
         (self.pjs.set[word+'0']['expire']- la0 ) ,
         (self.pjs.set[word+'1']['expire']- la1 ) )/5.0
      ex0 = now > self.pjs.set[word+'0']['expire'] and now > la1+twin_t
      ex1 = now > self.pjs.set[word+'1']['expire'] and now > la0+twin_t

      if ex0 and ex1 :
        if self.pjs.set[word+'0']['expire'] < self.pjs.set[word+'1']['expire'] :
          self.expired_queue.append(word+'0')
        else :
          self.expired_queue.append(word+'1')
      elif ex0 :
        self.expired_queue.append(word+'0')
      elif ex1 :
        self.expired_queue.append(word+'1')

      if dt_fresh > (self.pjs.set[word+'0']['expire']-
                     self.pjs.set[word+'0']['lgood']) :
        fresh_cnt = fresh_cnt +1
      if dt_fresh > (self.pjs.set[word+'1']['expire']-
                     self.pjs.set[word+'1']['lgood']) :
        fresh_cnt = fresh_cnt +1
    eq_sz = len(self.expired_queue)
    self.todo_cnt = eq_sz
    work_max = int(min(15, (self.end_time-now)/8.6))
    hard_cnt = min(fresh_cnt+stale_cnt, eq_sz//3)
    grow_sz = min(5,(110-hard_cnt)//2,(work_max-eq_sz-hard_cnt)//2)
    print 'eq_sz:', eq_sz, ' grow_sz: ', grow_sz, ' stale_cnt:', stale_cnt
    print ' fresh_cnt: ', fresh_cnt, ' work_max: ', work_max
    print 'time left:', self.end_time-now , 'now:', now
    if eq_sz > 100 :
      self.expired_queue = self.expired_queue[:50]
    elif eq_sz > 22 :
      self.expired_queue = self.expired_queue[:eq_sz//2]
    elif grow_sz > 0 :
      self.grow_set(grow_sz)
    random.shuffle(self.expired_queue)

class LojbanRafByF(LojbanByF):
  'lojban rafsi by frequency'
  def __init__(self):
    LojbanByF.__init__(self, 'rafsi', 20)
    self.init_byf_lists()
    self.type_name = 'rafsi'

  def init_raf_list(self):
    'initialize raf list'
    self.init_valsi_byf_list()
    if len(LojbanByF.byf_lists['rafsi']) == 0:
      for word in LojbanByF.byf_lists['valsi']:
        if word in LojbanBase.raf_sets:
          LojbanByF.byf_lists['rafsi'].append(word)
          #print word


  def gen_word_list(self):
    'generate word list'
    self.init_raf_list()
    #self.word_order = LojbanByF.byf_lists[self.type_name]
    return LojbanByF.byf_lists[self.type_name][:self.valsi_cnt]

  # TODO FIXME these need to be overridden
  def create_set(self):
    'create set'
    #print ' super creating ', self.name, ' begin '
    wlist = self.gen_word_list()
    self.pjs.so_far = len(wlist)
    now = self.hard_now()
    et = now -12.0
    #min_et = len(wlist) + 4*min(900,len(wlist))

    min_et = min(240, 2*len(wlist))
    gt = et - min_et
    bt = gt -999.9
    for word in wlist:
      self.pjs.set['V:'+word] = { 'expire':  et, 'lgood': gt, 'lbad': bt}
      for raf in LojbanBase.raf_sets[word]:
        self.pjs.set['R:'+raf] = { 'expire':  et, 'lgood': gt, 'lbad': bt}
    self.total_cnt = len(self.pjs.set)
    self.todo_cnt = self.total_cnt
    #print ' super creating ', self.name, ' size ', self.total_cnt
    self.stub = False

  def grow_set(self): pass
  # TODO FIXME these need to be overridden

  def find_expired(self):
    SetBase.find_expired(self)

  def find_bogus_rafsi(self):
    word = self.index[2:]
    ccvcv = re.compile('[b-z][b-z][aeiou][b-z][aeiou]')
    cvccv = re.compile('[b-z][aeiou][b-z][b-z][aeiou]')
    if ccvcv.match(word) :
      return [ word[0]+word[2]+word[3],
               word[1]+word[2]+word[3],
               word[0]+word[2]+'\''+word[4],
               word[0]+word[2]+word[4],
               word[1]+word[2]+'\''+word[4],
               word[1]+word[2]+word[4],
               word[0]+word[1]+word[2], ]
    if cvccv.match(word) :
      return [ word[0]+word[1]+word[2],
               word[0]+word[1]+word[3],
               word[0]+word[1]+'\''+word[4],
               word[0]+word[1]+word[4],
               word[2]+word[3]+word[4],
               word[0]+word[2]+word[1], ]
    ret = [ word, word[0]+'v'+word[1], word[0]+'z'+word[1], 
            word[0]+word[1]+'\'i', word[0]+word[1]+'\'o' ]
    for l in 'bcfijlmnprstuvz':
      ret.append(word[0]+word[1]+l)
    return ret

  def find_bogus_valsi(self):
    raf = self.index[2:]
    ret = []
    cvhv = re.compile('[b-z][aeiou]\'[aeiou]')
    cvv = re.compile('[b-z][aeiou][aeiou]')
    cvc = re.compile('[b-z][aeiou][bcdfgjklmnprstvxz]')
    ccv = re.compile('[b-z][bcdfgjklmnprstvxz][aeiou]')
    if cvhv.match(raf) :
      ret = [raf, raf[0]+raf[1] ]
      for w in LojbanByF.byf_lists['gismu'] :
        if raf[0] == w[0] and raf[1] == w[1] and raf[3] == w[4] :
          ret.append(w)
        if raf[0] == w[0] and raf[1] == w[2] and raf[3] == w[4] :
          ret.append(w)
        if raf[0] == w[1] and raf[1] == w[2] and raf[3] == w[4] :
          ret.append(w)
      return ret
    if cvv.match(raf) :
      ret = [raf, raf[0]+raf[1] ]
      for w in LojbanByF.byf_lists['gismu'] :
        if raf[0] == w[0] and raf[1] == w[1] and raf[2] == w[4] :
          ret.append(w)
        if raf[0] == w[0] and raf[1] == w[2] and raf[2] == w[4] :
          ret.append(w)
        if raf[0] == w[1] and raf[1] == w[2] and raf[2] == w[4] :
          ret.append(w)
      return ret
    if cvc.match(raf) :
      ret = [raf[0]+raf[1], raf[0]+raf[1]+'i', raf[0]+raf[1]+'u' ]
      for l in 'aeiou':
        ret.append(raf[0]+raf[1]+'\''+l)
      for w in LojbanByF.byf_lists['gismu'] :
        if raf[0] == w[0] and raf[1] == w[1] and raf[2] == w[2] :
          ret.append(w)
        if raf[0] == w[0] and raf[1] == w[1] and raf[2] == w[3] :
          ret.append(w)
        if raf[0] == w[0] and raf[1] == w[2] and raf[2] == w[3] :
          ret.append(w)
        if raf[0] == w[1] and raf[1] == w[2] and raf[2] == w[3] :
          ret.append(w)
      return ret
    if ccv.match(raf) :
      ret = [raf[0]+raf[2], raf[0]+raf[2]+'i', raf[0]+raf[2]+'u' ]
      for l in 'aeiou':
        ret.append(raf[0]+raf[2]+'\''+l)
      for w in LojbanByF.byf_lists['gismu'] :
        if raf[0] == w[2] and raf[1] == w[3] and raf[2] == w[4] :
          ret.append(w)
        if raf[0] == w[0] and raf[1] == w[2] and raf[2] == w[1] :
          ret.append(w)
        if raf[0] == w[0] and raf[1] == w[1] and raf[2] == w[2] :
          ret.append(w)
      return ret
    return ['gismu', 'da', 'blarg', 'buff', 'TODO', 'FIXME']

  def answers(self):
    'return the right answers and some bogus but deceive worthy ones'
    ret = { 'right':[], 'bogus':[] }
    if self.index:
      if self.index[0] == 'R' :
        ret['right'] = [ LojbanBase.raf_map[self.index[2:] ] ]
        ret['bogus'] = self.find_bogus_valsi()
      else:
        ret['right'] = [ x for x in LojbanBase.raf_sets[self.index[2:]] ]
        ret['bogus'] = self.find_bogus_rafsi()
      #ret['bogus'] = ['blarg','buff','TODO','FIXME']
    return ret
  # back is no longer good use answers instead

  def front(self):
    'docstring'
    self.realize()
    if self.index:
      ans = self.answers()
      #bogus=random.shuffle(ans['bogus'])
      random.shuffle(ans['bogus'])
      bogus = ans['bogus']
      #ret = self.index + ' -- ' + string.join(bogus)
      ret = self.index + ' -- ' + ' '.join(bogus)
      return ret
    return 'You have completed this set'

  def back(self):
    'docstring'
    ret = ''
    if self.index:
      ans = self.answers()
      #ret = string.join(ans['right']) + ' -- ' + string.join(ans['bogus'])
      #ret = string.join(ans['right'])
      ret = ' '.join(ans['right'])
      return ret
    return 'TODO back is deprecated for rafsi use FIXME'


class LojbanByStatic(LojbanBase):
  'lojban by cmavo group'
  def __init__(self, name, alist):
    LojbanBase.__init__(self, name, True)
    self.all_list = alist
    #self.can_launch = True
    self.valsi_cnt = len(alist)
    #self.can_launch = True
    if self.stub:
      self.todo_cnt = 2*self.valsi_cnt
      self.total_cnt = 2*self.valsi_cnt

  def gen_word_list(self):
    'generate word list'
    return self.all_list

# Maybe the by Cmavo Group should inherit from LojbanByStatic
class LojbanByCG(LojbanBase):
  'lojban by cmavo group'
  def __init__(self, name, glist):
    LojbanBase.__init__(self, name, True)
    self.group_list = glist
    #self.can_launch = True
    if self.stub:
      self.create_set()

  def gen_word_list(self):
    'generate word list'
    ret = []
    for item in self.group_list:
      ret = ret+LojbanBase.selmaho[item]
    return ret

class RowTotal(UtilBase):
  'row total'
  def __init__(self, name, path=None):
    UtilBase.__init__(self, name, False, False)
    #self.name=name
    #self.path=path
    # path is probably not needed as an iter is passed in
    #self.can_launch = False
    self.last_scan = 0
    self.total_cnt = 0
    self.todo_cnt = 0
    self.done_cnt = 0
    self.eh16 = 0
    self.eet = 0
    self.last_et = 0

  def scan(self, model, itera):
    'scan'
    now = self.hard_now()
    if now > self.last_scan + 3:
      self.last_scan = now
      self.total_cnt = 0
      self.todo_cnt = 0
      self.done_cnt = 0
      self.eh16 = 0
      self.eet = now + 9.9e9
      self.last_et = - 9.9e9

      # loop over each child and add to total sum
      # except for eet find the earliest
      itera = model.iter_children(itera)
      while itera:
        obj = model.get_value(itera, 0)
        if not obj.stub and not obj.is_stale():
        #if not obj.stub and obj.can_launch and not obj.is_stale():
          self.total_cnt = self.total_cnt + obj.total(model, itera)
          self.todo_cnt = self.todo_cnt + obj.todo(model, itera)
          self.done_cnt = self.done_cnt + obj.done(model, itera)
          self.eh16 = self.eh16 + obj.expire_h16(model, itera)
          ceet = obj.find_earliest_expired_time(model, itera)
          if ceet < self.eet:
            self.eet = ceet
          cltet = obj.find_last_expired_time(model, itera)
          if cltet > self.last_et:
            self.last_et = cltet
        itera = model.iter_next(itera)
      

  def total(self, model=None, itera=None):
    'total'
    #return '     '
    self.scan(model, itera)
    return self.total_cnt
    # FIXME TODO this should actualy sum up the children

  def todo(self, model=None, itera=None):
    'todo'
    self.scan(model, itera)
    #return '     '
    return self.todo_cnt

  def done(self, model=None, itera=None):
    'done'
    self.scan(model, itera)
    #return '     '
    return self.done_cnt

  def expire_h16(self, model=None, itera=None):
    '16 hours'
    self.scan(model, itera)
    #return '     '
    return self.eh16

  #def suggested_time(self,iter):
  #  return '  '
  def find_earliest_expired_time(self, model=None, itera=None):
    'eet'
    self.scan(model, itera)
    #return 1249868564
    return self.eet

  def find_last_expired_time(self, model=None, itera=None):
    'last_et'
    self.scan(model, itera)
    #return 1249868564
    return self.last_et

class FlashCardWind:
  'flash-card window'
  def reset(self):
    'reset'
    self.front.get_buffer().set_text(self.ds.front())
    self.back.get_buffer().set_text("???")
    self.ans.set_text("")
    self.ans.grab_focus()
    
  def sens_state(self, anp=False):
    'sensitive state'
    self.yes_butt.set_sensitive(not anp)
    self.no_butt.set_sensitive(not anp)
    tcnt = self.ds.todo()
    self.done_butt.set_sensitive(anp and (tcnt != 0))
    self.skip_butt.set_sensitive(anp and (tcnt != 0))

  def cb_delete_event(self, widget, event, data=None):
    'callback'
    if self.ds:
      self.ds.close()
    return False

  def done_cb(self, widget, data=0):
    'callback'
    #reveal the backside
    #make yes/no buttons sensitive, desensitize done/skip
    self.back.get_buffer().set_text(self.ds.back())
    self.sens_state(False)

  def skip_cb(self, widget, data=0):
    'callback'
    self.ds.skip()
    self.reset()
    #self.ans.set_text("")
    #self.sens_state()
    return False

  def hear_cb(self, widget, data=0):
    'callback'
    # FIXME TODO use text2speech
    strg = self.ds.sound()
    return False

  def yes_cb(self, widget, data=0):
    'callback'
    self.sens_state(True)
    self.ds.yes()
    self.reset()
    #self.ans.set_text("")
    self.tmodel.row_changed(self.tmodel.get_path(self.titer), self.titer)
    # emit "row-changed" so the gui view gets updated
    return False

  def no_cb(self, widget, data=0):
    'callback'
    self.sens_state(True)
    self.ds.no()
    self.reset()
    #self.ans.set_text("")
    return False

  def __init__(self, data_set=None, tmodel=None, titer=None, time_limit=55.0):
    self.window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    self.window.set_title("flash cards")
    self.window.set_border_width(10)
    self.window.connect("delete_event", self.cb_delete_event)
    # TODO FIXME have it save the data set instead of quiting
    self.ds = data_set
    self.ds.open(time_limit)
    self.tmodel = tmodel
    self.titer = titer

    self.vb = Gtk.VBox()
    self.window.add(self.vb)

    frame = Gtk.Frame(label="Front")
    self.front = Gtk.TextView()
    self.front.set_editable(False)
    self.front.set_wrap_mode(Gtk.WrapMode.WORD)
    self.front.get_buffer().set_text(data_set.front())
    frame.add(self.front)
    self.vb.pack_start(frame, True, False, 0)
    self.front.set_size_request(460, 88)
    # magic numbers that should be based on font size instead
    self.front.show()
    frame.show()

    self.abar = Gtk.HBox()
    self.vb.pack_start(self.abar, True, False, 0)

    self.ans = Gtk.Entry()
    self.ans.set_width_chars(48)
    self.abar.pack_start(self.ans, True, False, 0)
    self.ans.connect("activate", self.done_cb, 0)
    self.ans.show()

    self.done_butt = Gtk.Button("Done")
    self.abar.pack_start(self.done_butt, True, False, 0)
    self.done_butt.connect("clicked", self.done_cb, 0)
    self.done_butt.show()

    self.skip_butt = Gtk.Button("Skip")
    self.abar.pack_start(self.skip_butt, True, False, 0)
    self.skip_butt.connect("clicked", self.skip_cb, 0)
    self.skip_butt.show()

    self.hear_butt = Gtk.Button("Hear TODO")
    self.abar.pack_start(self.hear_butt, True, False, 0)
    self.hear_butt.connect("clicked", self.hear_cb, 0)
    self.hear_butt.show()
    #self.hear_butt.set_sensitive(False)

    self.cbar = Gtk.HBox()
    self.vb.pack_start(self.cbar, True, False, 0)

    self.yes_butt = Gtk.Button("I remember")
    self.cbar.pack_start(self.yes_butt, True, False, 0)
    self.yes_butt.connect("clicked", self.yes_cb, 0)
    self.yes_butt.show()

    self.no_butt = Gtk.Button("I forgot or never knew")
    self.cbar.pack_start(self.no_butt, True, False, 0)
    self.no_butt.connect("clicked", self.no_cb, 0)
    self.no_butt.show()

    self.sens_state(True)
    self.abar.show()

    self.cbar.show()

    frame = Gtk.Frame(label="Back")
    self.back = Gtk.TextView()
    self.back.set_editable(False)
    self.back.set_wrap_mode(Gtk.WrapMode.WORD)
    self.back.get_buffer().set_text("???")
    frame.add(self.back)
    self.vb.pack_start(frame, True, False, 0)
    #self.back.set_size_request(460,156)
    #self.back.set_size_request(460,190)
    self.back.set_size_request(460, 224)
    #jdima
    # the back card is taller than the front because it sometimes displays
    # much more information
    # magic numbers that should be based on font size instead
    self.back.show()
    frame.show()
    self.vb.show()
    self.window.show()

class SetChooser:
  'set chooser'
  def fill_byf_subtree(self, piter, tstr, nums):
    'fill by frequency'
    for child in nums:
      self.tstore.append(piter, ('%s %i' % (tstr, child,) , "", 0, child)) 

  def find_prev_set(self, model, itera):
    'find previous set'
    path = list(model.get_path(itera))
    #print "got path ", path , "tuple ", tuple(path)
    while True:
      path[-1] = path[-1] -1
      if path[-1] < 0 :
        return None
      #print "got path ", path , "tuple ", tuple(path)
      obj = model.get_value(model.get_iter(tuple(path)), 0) 
      if not obj.stub:
        return obj

  def reset_cb(self, widget, data=0):
    'callback'
    tmodel, titer = self.treeview.get_selection().get_selected()
    obj = tmodel.get_value(titer, 0)
    if not obj.stub and obj.can_launch:
      obj.reset()
      tmodel.row_changed(tmodel.get_path(titer), titer)
      # emit "row-changed" so the gui view gets updated
      self.ch_butt.set_active(False)
      # toggle radio off
      # WARN untested AUDIT
    return False

  def activate_helper(self):
    'helper'
    tmodel, titer = self.treeview.get_selection().get_selected()
    if titer == None :
      return
    obj = tmodel.get_value(titer, 0)
    #print obj.name
    #self.wants_super_creation = True
    tlv = self.time_limit.get_value()
    if obj.can_launch:
      try:
        if obj.stub and obj.wants_super_creation:
          pre_obj = self.find_prev_set(tmodel, titer)
          if pre_obj :
            obj.create_set(pre_obj, 1)
            #print 'prev set ', pre_obj.name
          # find earlier set
          # obj.create_set(earlier_set)
      except:
        pass
      obj.can_launch = False
      FlashCardWind(obj, tmodel, titer, tlv)
    #else:
    #  FlashCardWind(flash_set_test0())
      
  def act_cb(self, widget, data=0):
    'act callback'
    print 'act callback'
    self.activate_helper()
    return False

  # kludge to handle that the different subsets are getting too big
  # to have more than one open and still fit on the screen
  def expand_cb(self, treeview, itera, path=None, data=0):
    'expand callback'
    print 'expand callback'
    #print "got path ", path , " " , self.last_expanded 
    # BUG FIXME when I put in nested hierarchy it broke bad
    if self.last_expanded and path != self.last_expanded:
      pass
      #print "got old path ", self.last_expanded  
      #treeview.collapse_row(self.last_expanded)
    self.last_expanded = path
    print 'expand callback exited'
    return False

  def row_active_cb(self, tvw, path, vcolumn):
    'row active callback'
    print 'row active callback'
    self.activate_helper()
    #print 'activated'
    return False

  def safety_cb(self, widget, data=None):
    'callback'
    self.dbutt.set_sensitive(widget.get_active())
    #FIXME TODO don't do anything yet removes file but is buggy
    return False

  def curs_chan_cb(self, data=None):
    'cursor change callback'
    print 'cursor change callback'
    self.ch_butt.set_active(False)

  def cdf_name(self, treeviewcolumn, cell_renderer, model, itera, data):
    'name'
    cell_renderer.set_property('text',
       model.get_value(itera, 0).name)
  def cdf_total(self, treeviewcolumn, cell_renderer, model, itera, data):
    'total'
    cell_renderer.set_property('text',
       str(model.get_value(itera, 0).total(model, itera)))
  def cdf_todo(self, treeviewcolumn, cell_renderer, model, itera, data):
    'todo'
    cell_renderer.set_property('text',
       str(model.get_value(itera, 0).todo(model, itera)))
  def cdf_done(self, treeviewcolumn, cell_renderer, model, itera, data):
    'done'
    cell_renderer.set_property('text',
      str(model.get_value(itera, 0).done(model, itera)))
  def cdf_expire_h16(self, treeviewcolumn, cell_renderer, model, itera, data):
    'expire 16 hour'
    cell_renderer.set_property('text',
      str(model.get_value(itera, 0).expire_h16(model, itera)))
  def cdf_when(self, treeviewcolumn, cell_renderer, model, itera, data):
    'when'
    cell_renderer.set_property('text',
      str(model.get_value(itera, 0).suggested_time(model, itera)))
  def cdf_last_time(self, treeviewcolumn, cell_renderer, model, itera, data):
    'last time'
    cell_renderer.set_property('text',
      str(model.get_value(itera, 0).suggested_last_time(model, itera)))

  def __init__(self):
    window = Gtk.Window(type=Gtk.WindowType.TOPLEVEL)
    window.set_title("flash card -- set chooser")
    window.set_border_width(10)
    window.connect("destroy", lambda wid: Gtk.main_quit())
    window.connect("delete_event", lambda a1, a2:Gtk.main_quit())

    #vbx = Gtk.VBox(False, 0)
    vbx = Gtk.VBox()
    window.add(vbx)

    self.tstore = Gtk.TreeStore(object)
    topi = self.tstore.append(None, (RowTotal("lojban"),))

    try:
      piter = self.tstore.append(topi, (RowTotal("Cmavo by Frequency"),))
      #for vcnt in [ 35,70,140,280,420,490,560,615,667 ]:
      #for vcnt in [ 420,455,490,525,560,615,667 ]:
      #for vcnt in [ 35, 70, 140]:
      for vcnt in [ 3 ]:
        self.tstore.append(piter, (LojbanByF('cmavo', vcnt),))
      # FIXME TODO I've come to realize that fixed sized sets
      # wasn't the best way .
      # they should have been able to grow in size more smoothly FIXME
      piter = self.tstore.append(topi, (RowTotal("Gismu by Frequency"),))
      #for vcnt in [ 45, 85, 170, 340, 510, 671, 805, 939, 1073, 1207, 1342 ]:
      for vcnt in [ 4 ]:
        self.tstore.append(piter, (LojbanByF('gismu', vcnt),))
      piter = self.tstore.append(topi, (RowTotal("Valsi by Frequency"),))
      #for vcnt in [ 45,90,180,375,750,912,1075,1230,1386,1542,1697,1853,2009]:
      #for vcnt in [ 1075,1110,1145,1180,1215,1250]:
      #for vcnt in [ 1250,1285,1320,1355,1390,1425]:
      #for vcnt in [ 45, 90, 180]:
      for vcnt in [ 4 ]:
        self.tstore.append(piter, (LojbanByF('valsi', vcnt),))
    except IOError , prob:
      print 'io error: ' , prob
      # FIXME TODO should make an error window
      # or otherwise show the error in the gui FIXME TODO
    except NotImplementedError , prob:
      print 'not implemeted error: ' , prob
    except RuntimeError, prob:
      print 'run time error: ' , prob

    # I use two try blocks because the below might still work
    # if you have gismu.txt and cmavo.txt but not valsi_f.txt

    try:
      self.tstore.append(topi,
         (LojbanByStatic("ro me zo bai gismu",bai_gismu_list),))
      # gismu ki'i lo cmavo be zo bai
      piter = self.tstore.append(topi,(RowTotal("Cmavo by selma'o groups"),))
      terminators = [
        'BEhO', 'BOI', 'CU', 'DOhU', 'FEhU', 'FOI', 'FUhO', 'GEhU', 'KEhE',
        'KEI', 'KU', 'KUhE', 'KUhO', 'LEhU', 'LIhU', 'LOhO', 'LUhU', 'MEhU',
        'NUhU', 'TEhU', 'SEhU', 'TOI', 'TUhU', 'VAU', 'VEhO', 'ZOhU']
      self.tstore.append(piter, (LojbanByCG('Terminators', terminators),))
      self.tstore.append(piter,
               (LojbanByCG('Attitudinals Evidentals Discursives', [
         'UI','DAhO','FAhO','LAU','NIhO','RAhO','SA','SI','SU',
         'SOI','NAI','CAI','BAhE','SEI','SEhU','MAI','Y']),))
      self.tstore.append(piter, (LojbanByCG('bai Modal', [
         'BAI','NAI','JAI','GEhU','KU','FEhU']),))
      self.tstore.append(piter, (LojbanByCG('lerfu Numbers Letters Symbols', [
         'PA','BY','BOI','BU','XI']),))
      self.tstore.append(piter, (LojbanByCG('Vocatives', [
         'COI','DOI','DOhU','NAI','CAI']),))
      self.tstore.append(piter, (LojbanByCG('Proassign', [
         'GOhA','KOhA']),))
      self.tstore.append(piter, (LojbanByCG('Connectives', terminators + [
         'A','BIhI','GA','GAhO','GI','GIhA','GUhA', 'I','JOI','VUhO',
         'ZEI','ZIhE', 'CEhE','PEhE','CEI','GOI','NOI','BO','CO','BE','BEI']),))
      self.tstore.append(piter, (LojbanByCG('Group', terminators + [
         'FUhE','KE','NUhI','TEI','SEI','TO','TUhE','VEI','LAU','LOhU','LU',
         'ZO','ZOI', 'LA','LAhE','LE','LI','NU','NA','NAhE','FA','FAhO',
         'JAI','SE']),))
      self.tstore.append(piter, (LojbanByCG('Converters', [
         'FIhO','MAhO','ME','MOhE','MOI','NAhU','NIhE','NUhA','ROI',
         'BOI','FEhU','MEhU','TEhU']),))
      self.tstore.append(piter, (LojbanByCG('Math', [
         'BIhE','FUhA','JOhI','PEhO','VUhU','PA','BOI','XI','KUhE',
         'LOhO','LI']),))
      self.tstore.append(piter, (LojbanByCG('Time and Space', [
         'CAhA','CUhE','FAhA','FEhE','KI','MOhI','PU','TAhE','VA',
         'VEhA','VIhA','ZAhO','ZEhA','ZI','JA','MOI','ROI']),))
      self.tstore.append(piter, (LojbanByStatic('selmaho sampler', [
          i.lower().replace("h","'") for i in LojbanBase.selmaho.keys()
         ]),))
      piter = self.tstore.append(topi, (RowTotal("cmevla"),))
      self.tstore.append(piter, (UtilBase('FIXME TODO'),))
      piter = self.tstore.append(topi, (RowTotal("rafsi"),))
      self.tstore.append(piter, (LojbanRafByF(),))
      self.tstore.append(piter, (UtilBase('FIXME TODO'),))
      piter = self.tstore.append(topi, (RowTotal("lujvo"),))
      self.tstore.append(piter, (UtilBase('FIXME TODO'),))
      piter = self.tstore.append(topi,(RowTotal("fu'ivla"),))
      self.tstore.append(piter, (UtilBase('FIXME TODO'),))
    except IOError , prob:
      print 'io error: ' , prob
      # FIXME TODO should make an error window
      # or otherwise show the error in the gui
    except NotImplementedError , prob:
      print 'not implemeted error: ' , prob
    except RuntimeError, prob:
      print 'run time error: ' , prob
    # gismu ki'i lo cmavo be zo bai

    topi = self.tstore.append(None, (RowTotal("Army"),))
    topi = self.tstore.append(None, (RowTotal("Radio"),))



    self.treeview = Gtk.TreeView(model=self.tstore)
    self.treeview.connect("row-activated", self.row_active_cb)
    self.last_expanded = None
    #self.treeview.connect("test-expand-row", self.expand_cb)
    self.treeview.connect("cursor-changed", self.curs_chan_cb)

    col_name = Gtk.TreeViewColumn(
            '     Name                                              ')
    # has lots of white-space to reserve space
    # and avoid certain display glitches
    self.treeview.append_column(col_name)
    cell = Gtk.CellRendererText()
    col_name.pack_start(cell, True)
    #self.col_name.add_attribute(self.cell, 'text', 0)
    col_name.set_cell_data_func(cell, self.cdf_name)

    coln = Gtk.TreeViewColumn('  Todo  ')
    self.treeview.append_column(coln)
    cell = Gtk.CellRendererText()
    coln.pack_start(cell, True)
    coln.set_cell_data_func(cell, self.cdf_todo)

    coln = Gtk.TreeViewColumn('  Total  ')
    self.treeview.append_column(coln)
    cell = Gtk.CellRendererText()
    coln.pack_start(cell, True)
    coln.set_cell_data_func(cell, self.cdf_total)

    coln = Gtk.TreeViewColumn('  When               ')
    self.treeview.append_column(coln)
    cell = Gtk.CellRendererText()
    coln.pack_start(cell, True)
    coln.set_cell_data_func(cell, self.cdf_when)

    coln = Gtk.TreeViewColumn('  Last Time          ')
    self.treeview.append_column(coln)
    cell = Gtk.CellRendererText()
    coln.pack_start(cell, True)
    coln.set_cell_data_func(cell, self.cdf_last_time)

    self.treeview.set_search_column(0)
    self.treeview.show_all()
    vbx.pack_start(self.treeview, True, False, 0)

    #self.time_limit=Gtk.ScaleButton(-1,0,90,1)
    self.time_limit = Gtk.Adjustment(55.0, 0.0, 100.0)
    tls = Gtk.HScale(adjustment=self.time_limit)
    tls.show()
    vbx.pack_start(tls, True, False, 0)

    butt =  Gtk.Button("Activate Set")
    butt.connect("clicked", self.act_cb, 0)
    butt.show()
    vbx.pack_start(butt, True, False, 0)

    reset_bar = Gtk.HBox()
    self.ch_butt = Gtk.CheckButton()
    self.ch_butt.connect("toggled", self.safety_cb, 0)
    reset_bar.pack_start(self.ch_butt, True, False, 0)
    self.dbutt =  Gtk.Button("Destroy Set")
    self.dbutt.connect("clicked", self.reset_cb, 0)
    self.ch_butt.show()
    self.dbutt.show()
    self.dbutt.set_sensitive(False)
    reset_bar.show()
    # FIXME don't show yet because of BUG
    #sepp=Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
    sepp = Gtk.HSeparator()
    sepp.set_size_request(10, 10)
    sepp.show()
    vbx.pack_start(sepp, True, False, 0)
    #frame = Gtk.Frame(label="remove old sets; protected by extra button",
    #           shadow_type=Gtk.ShadowType.IN)
    frame = Gtk.Frame(label="remove old sets; protected by extra button")
    reset_bar.pack_start(self.dbutt, True, False, 0)
    frame.add(reset_bar)
    frame.show()
    frame.show_all()
    vbx.pack_start(frame, True, False, 0)

    vbx.show()
    window.show()

if __name__ == "__main__":
  SetChooser()
  Gtk.main()

#! /usr/bin/python
# coding=utf8
"""
 attempts to be flash card program; has some lojban specific quirks
"""

# copyright (C) 2009/2012 "Stephen Joseph Pollei" <stephen.pollei@gmail.com>
# licensed gplv3 or later -- http://www.fsf.org/licensing/licenses/gpl.html

# attempts to be flash card program; has some lojban specific quirks

#import random, time, cPickle, os
import re, random, time, cPickle, os, urllib, sys

import generic_cards

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

class LojbanBase(generic_cards.SetBase):
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
    generic_cards.SetBase.__init__(self, name, cl)

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


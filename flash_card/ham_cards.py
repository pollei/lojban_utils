#! /usr/bin/python
# coding=utf8
"""
 attempts to be flash card program; has some lojban specific quirks
"""

# copyright (C) 2009/2012 "Stephen Joseph Pollei" <stephen.pollei@gmail.com>
# licensed gplv3 or later -- http://www.fsf.org/licensing/licenses/gpl.html

# attempts to be flash card program; has some lojban specific quirks

#import re, random, time, cPickle, os, urllib, sys
import re, os, sys
import generic_cards

# http://www.ncvec.org/ is where I found text version of the questions

# '[TGE][0-9][A-J][0-2][0-9] ([A-D]'

# '[fF]igure [TGE][0-9]'
# some of the questions have pictures that go with it


class HamBase(generic_cards.SetBase):
  'ham radio base foundation'

  def kar_path(self):
    'find the path for opening'
    if os.name in [ 'posix', 'unix', 'linux' ]:
      paths = [ '/usr/share/data/ham_radio', '/usr/data/ham_radio/',
        os.path.expanduser('~/Desktop/ham_radio/'),
        os.path.expanduser('~/.ham_radio/'), './' ]
    elif os.name in [ 'windows', 'nt', 'ce']:
      paths = [ "c:\\program_data\\ham_radio\\" , 'c:\\ham_radio\\' ,
               os.path.expanduser('~\\ham_radio\\') ]
      # not tested in windows and I'm not running windows
    elif os.name in [ 'mac', 'os2', 'java', 'riscos']:
      paths = [ os.path.expanduser('~/ham_radio/') ]
      # not tested in mac osx or other oses
    else:
      raise NotImplementedError, ('unknown operating system: ' + os.name)
    for pname in paths:
      if (os.path.isdir(pname) and
             os.path.exists(os.path.join(pname, 'ham_general.txt')) ):
        return pname
    raise RuntimeError, 'could not find ham_radio data directory'

  # karna means open
  def kar(self, fname, mode='r'):
    'open'
    return open(os.path.join(self.kar_path() , fname), mode)
    # may raise "IOError: [Errno 2]" if the file isn't found

  def read_cards(self):
    'read cards'
    if len(self.cards) :
      return
    #print 'reading ham fcc cards'
    group='x'
    item='00'
    ans='A'
    quest=''
    cf = self.kar(self.fname)
    idpat=re.compile('([TGE][0-9][A-J])([0-2][0-9]) \(([A-D])')
    endpat=re.compile('~~')
    for line in cf:
      midpat=idpat.match(line)
      if midpat :
        group=midpat.group(1)
        item=midpat.group(2)
        ans=midpat.group(3)
        quest=''
      elif endpat.match(line) :
        #print 'got -', group, '-', item, '-', len(self.cards)
        if group not in self.cards :
          self.cards[group] = {}
        self.cards[group][item] = (quest, ans)
      else :
        quest += line
    cf.close()
    #print 'done reading ham fcc cards'



  def __init__(self, name, fname, cl=True):
    self.fname=fname
    generic_cards.SetBase.__init__(self, name, cl)
    if self.stub:
      self.stats['todo_cnt'] = 600
      self.stats['total_cnt'] = 600


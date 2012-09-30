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
#import re, random, time, cPickle, os, urllib, sys
# os.listdir, os.name 'posix' , os.mkdir

import generic_cards, jbo_cards

# this Pjs is for legacy files only
class Pjs:
  'pickle jar storage'
  def __init__(self):
    self.set = {}
    self.gset = {}
    self.config = {}

class RowTotal(generic_cards.UtilBase):
  'row total'
  def __init__(self, name, path=None):
    generic_cards.UtilBase.__init__(self, name, False, False)
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
        self.tstore.append(piter, (jbo_cards.LojbanByF('cmavo', vcnt),))
      # FIXME TODO I've come to realize that fixed sized sets
      # wasn't the best way .
      # they should have been able to grow in size more smoothly FIXME
      piter = self.tstore.append(topi, (RowTotal("Gismu by Frequency"),))
      #for vcnt in [ 45, 85, 170, 340, 510, 671, 805, 939, 1073, 1207, 1342 ]:
      for vcnt in [ 4 ]:
        self.tstore.append(piter, (jbo_cards.LojbanByF('gismu', vcnt),))
      piter = self.tstore.append(topi, (RowTotal("Valsi by Frequency"),))
      #for vcnt in [ 45,90,180,375,750,912,1075,1230,1386,1542,1697,1853,2009]:
      #for vcnt in [ 1075,1110,1145,1180,1215,1250]:
      #for vcnt in [ 1250,1285,1320,1355,1390,1425]:
      #for vcnt in [ 45, 90, 180]:
      for vcnt in [ 4 ]:
        self.tstore.append(piter, (jbo_cards.LojbanByF('valsi', vcnt),))
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
         (jbo_cards.LojbanByStatic("ro me zo bai gismu",
                jbo_cards.bai_gismu_list),))
      # gismu ki'i lo cmavo be zo bai
      piter = self.tstore.append(topi,(RowTotal("Cmavo by selma'o groups"),))
      terminators = [
        'BEhO', 'BOI', 'CU', 'DOhU', 'FEhU', 'FOI', 'FUhO', 'GEhU', 'KEhE',
        'KEI', 'KU', 'KUhE', 'KUhO', 'LEhU', 'LIhU', 'LOhO', 'LUhU', 'MEhU',
        'NUhU', 'TEhU', 'SEhU', 'TOI', 'TUhU', 'VAU', 'VEhO', 'ZOhU']
      self.tstore.append(piter,
               (jbo_cards.LojbanByCG('Terminators', terminators),))
      self.tstore.append(piter,
               (jbo_cards.LojbanByCG('Attitudinals Evidentals Discursives', [
         'UI','DAhO','FAhO','LAU','NIhO','RAhO','SA','SI','SU',
         'SOI','NAI','CAI','BAhE','SEI','SEhU','MAI','Y']),))
      self.tstore.append(piter, (jbo_cards.LojbanByCG('bai Modal', [
         'BAI','NAI','JAI','GEhU','KU','FEhU']),))
      self.tstore.append(piter,
         (jbo_cards.LojbanByCG('lerfu Numbers Letters Symbols', [
         'PA','BY','BOI','BU','XI']),))
      self.tstore.append(piter, (jbo_cards.LojbanByCG('Vocatives', [
         'COI','DOI','DOhU','NAI','CAI']),))
      self.tstore.append(piter, (jbo_cards.LojbanByCG('Proassign', [
         'GOhA','KOhA']),))
      self.tstore.append(piter, (jbo_cards.LojbanByCG('Connectives',
          terminators + [
         'A','BIhI','GA','GAhO','GI','GIhA','GUhA', 'I','JOI','VUhO',
         'ZEI','ZIhE', 'CEhE','PEhE','CEI','GOI','NOI','BO','CO','BE','BEI']),))
      self.tstore.append(piter, (jbo_cards.LojbanByCG('Group', terminators + [
         'FUhE','KE','NUhI','TEI','SEI','TO','TUhE','VEI','LAU','LOhU','LU',
         'ZO','ZOI', 'LA','LAhE','LE','LI','NU','NA','NAhE','FA','FAhO',
         'JAI','SE']),))
      self.tstore.append(piter, (jbo_cards.LojbanByCG('Converters', [
         'FIhO','MAhO','ME','MOhE','MOI','NAhU','NIhE','NUhA','ROI',
         'BOI','FEhU','MEhU','TEhU']),))
      self.tstore.append(piter, (jbo_cards.LojbanByCG('Math', [
         'BIhE','FUhA','JOhI','PEhO','VUhU','PA','BOI','XI','KUhE',
         'LOhO','LI']),))
      self.tstore.append(piter, (jbo_cards.LojbanByCG('Time and Space', [
         'CAhA','CUhE','FAhA','FEhE','KI','MOhI','PU','TAhE','VA',
         'VEhA','VIhA','ZAhO','ZEhA','ZI','JA','MOI','ROI']),))
      self.tstore.append(piter,
                 (jbo_cards.LojbanByStatic('selmaho sampler', [
          i.lower().replace("h","'") for i in jbo_cards.LojbanBase.selmaho.keys()
         ]),))
      piter = self.tstore.append(topi, (RowTotal("cmevla"),))
      self.tstore.append(piter, (generic_cards.UtilBase('FIXME TODO'),))
      piter = self.tstore.append(topi, (RowTotal("rafsi"),))
      self.tstore.append(piter, (jbo_cards.LojbanRafByF(),))
      self.tstore.append(piter, (generic_cards.UtilBase('FIXME TODO'),))
      piter = self.tstore.append(topi, (RowTotal("lujvo"),))
      self.tstore.append(piter, (generic_cards.UtilBase('FIXME TODO'),))
      piter = self.tstore.append(topi,(RowTotal("fu'ivla"),))
      self.tstore.append(piter, (generic_cards.UtilBase('FIXME TODO'),))
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

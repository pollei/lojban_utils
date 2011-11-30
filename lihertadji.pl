#! /usr/bin/perl
use 5.010;
use strict;
use utf8;
use warnings;
our $VERSION = 0.000_003;

use Lojban::Valsi ':ALL';

# By Stephen Pollei
# Copyright (C) 2011, "Stephen Pollei"<stephen.pollei@gmail.com>
# GPLv3 or later http://www.gnu.org/licenses/gpl.html

#use Parse::Earley;
# http://search.cpan.org/~lpalmer/Parse-Earley-0.15/Earley.pm
# I think instead of writing my own tokenizer smart enough to handle zoi bu
# and other makfa selma'o that I need to bring out a real parser

# a lojban preprocessor
# separate words based on lojban morphology and add some pauses
# TODO add commas and stress capitization FIXME
# TODO correct a few common typos FIXME
# TODO know a little bit of grammar aka zoi and la'o and la'oi and lo'u/le'u
# 
# This can be useful on it's own to show how a piece of text would be processed
# It also can do some of the work that would be needed for a text-to-speech system
# it also can do some tokenization that a parser might find helpful
#
# of course in order to know a bit about the grammar I might just add a parser
# directly to this

# http://www.lojban.org/publications/reference_grammar/chapter3.html
# The Hills Are Alive With The Sounds Of Lojban

# http://www.lojban.org/publications/reference_grammar/chapter4.html
# The Shape Of Words To Come: Lojban Morphology

# http://www.lojban.org/tiki/Magic+Words+Alternatives
# http://www.lojban.org/tiki/Magic+Words
# SI SA SU ZO ZOI LOhU LEhU ZEI BU and FAhO

#FIXME neither break_level nor pause_level do anything FIXME
# --break
# level 0 only separate cmavo clusters
# level 1 split leading cmavo off of some brivla
# level 2 split leading cmavo off of all brivla
# level 3 split stressed brivla apart

our $BREAK_LEVEL=3;
#FIXME neither break_level nor pause_level do anything FIXME

# --pause
# level 0 preserve pauses only, don't add new "."s
# level 1 preserve pauses and make sure cmene is properly paused
# level 2 pause quotes and errors and some other spots
# level 3 slow down for new beginers pause everywhere
our $PAUSE_LEVEL=2;
#FIXME neither break_level nor pause_level do anything FIXME

Lojban::Valsi::test_regex_foundation0(); 

#xu lujvo
sub xu_lujvo {
  my ($word) =@_;
  #tosmabru
  if ($word =~ /^ [.]* $C $V ($L{4,}) [.]* $ /x ) {
    if (xu_brivla($1)) { return 0;}
  }
  return $word =~ $LUJVO ;
}

#FIXME AUDIT lot's of hairy regex in here: is it all correct and sufficient? FIXME
#xu fu'ivla
sub xu_fuhivla {
  my ($word) =@_;
  #return 0 unless $word =~ $CC5;
  if ($word =~ /[yY]/x) { return 0; }
  return 0 unless $word =~ $FUH4;
  # not combo of cmavo and gismu and/or lujvu
  if ($word =~ / ^ [.]* (?: $C?$V$H?$V?){1,6} (?: $GISMU_ | $LUJVO_) [.]* $ /ix)
        {return 0;}
  # slinku'i paslinku'i
  if (('pa' . $word) =~ $LUJVO )
     { return 0; }
  #FIXME TODO if leading dot is there it will mess things up FIXME TODO
  # pa.slinku'i
  # stage 3 detection not really being used
  #if ($word =~ / ^ [.]* $RAFC $L_HYPH $C /ix) {return 3;}
  if ($word =~ $FUH3 ) {return 3;}
  return 1;
}

# xu bridi valsi
sub xu_brivla {
  my ($word) =@_;
  return 0 unless $word =~ $BRIVLA;
  return 0 unless ($word =~ /^ $WS* (?: $NO_STRESS | $PSTRESS ) $WS* $ /x);
  if ($word =~ $GISMU) { return 1; }
  if (xu_lujvo($word)) { return 2; }
  if (xu_fuhivla($word)) { return 3; }
  return 0;
}

sub xu_cmavo {
  my ($word) =@_;
  return $word =~ $CM_SIMPLE;
}

sub classify_word {
  my ($word) =@_;
  my $classed=q{};
  my $btype=0;
  if ($word eq q{}) {return 'x';}
  if ($word =~ $WEAK_BAD || $word !~ $WEAK_GOOD) { return 'XXX'; }
  if ($word =~ $CMENE ) { return 'N'; }
  if ($word =~ $STRONG_BAD || $word !~ $GOOD) { return 'XXX'; }
  if ($btype=xu_brivla($word)) {
    return 'B' . qw(x G L F)[$btype]; }
  if (xu_cmavo($word) ) {return 'c';}
  return 'U';
}

our @DONE =();
our @TBD =();
our $ZOI_XU=0;
our $LAHO_VALSI;
our $LEHU_XU=0;

# TODO FIXME have the splitter work on two queue's @DONE and @TBD
# have some state to handle zoi and la'o and le'u/lo'u
# maybe toss it into an object
#
# TODO FIXME have comments that can effect processing and split files apart
# q{#%%}
#%% pre-dotside=force-split pre-dotside=split pre-dotside=fix
#%%# controls how things should work in a pre dot-side world
#%%# default is split
#%% dotside no-dotside dotside=no
#%%# says we use dotside rules for cmene; turn off all pre-dotside
#%%# default is yes
#%% magic=no magic=yes no-magic
#%%# whether we handle zoi and la'o
#%% pause
#%% break-apart
#%%#


#cmavo splitter
sub cmavo_sepli {
  my ($word) =@_;
  my @parts;
  my $cmavo;
  my $leftover;
    if ($word =~ /^(y+)(bu)?$/x) {
       # TODO FIXME do this differently FIXME TODO
       my $y=$1 ; my $bu=$2;
       $bu //= q{};
       $y =~ s/y(?! )/. y /g;
       return $y . $bu . ' .'; }
    if ($word =~ /^((?:$C$Y)+)(boi)? $ /ix) {
       # TODO FIXME this looks potentialy b0rken FIXME AUDIT
       my $l = $1; my $boi=$2; my $n= length($l); my $i=0;
       $boi //= q{};
       #print "x" . $l ."x $n" . $boi ."x\n";
       for ($i=0;$i < $n; $i+=2) {push (@parts,substr($l,$i,2)); }
       return ". " . join(q{ },@parts) . q{ } . $boi . " .";
      }
      if ($word =~ /^y'y$/ix) {return q{. y'y .};}
    if ($word =~ /^[aeiouy]/ix) {push(@parts, '. ');}
    while ($word =~
      /^($CM_0)($C$V .*)$ /ix) {
         $cmavo=$1;$leftover=$2;
         if ($cmavo eq q{lo'u} || $cmavo eq q{le'u}) {
                $cmavo = '. ' . $cmavo . ' .';}
         push(@parts,$cmavo);$word=$leftover;
       }
    if ($word eq q{lo'u} || $word eq q{le'u}) { $word = '. ' . $word . ' .';}
    push(@parts,$word);
    return join(q{ },@parts);
}

#unknow splitter
sub unknown_sepli {
  my ($oword) =@_;
  my @parts;
  my $type;
  my $cmavo;
  my $leftover;
  my $word=$oword;
  #$type=classify_word($word);
  $type=classify_valsi($word);
  if ($type eq 'c') {
    return cmavo_sepli($word); }
  if ($word =~ /^[aeiouy]/ix) {push(@parts, '. ');}
  while ( $type eq 'U' && $word =~
      /^($CM_0)($C .* ) $ /ix) {
     $cmavo=$1;$leftover=$2;
     if ($cmavo eq q{lo'u} || $cmavo eq q{le'u}) { $cmavo = '. ' . $cmavo . ' .';}
     push(@parts,$cmavo);$word=$leftover;
     #$type=classify_word($word);
     $type=classify_valsi($word);
  }
  #return undef unless ($type =~ /^B[GLF]$/);
  return unless ($type =~ /^B[GLF]$/x);
  push(@parts,$word);
  #print ' (' . $type . ') ';
  return join(q{ },@parts);
}

#splitter
sub sepli {
  my ($oword,$otype) =@_;
  #if ($otype ne 'c' ) {return $oword;}
  my $type=$otype;
  my $word=$oword;
  my @parts;
  my $cmavo;
  my $front;
  my $seped;
  my $leftover;
 if ($otype eq 'c') {
    return cmavo_sepli($oword);
  }
 if ($otype eq 'XXX') {
   # FIXME TODO add something that "fixes" things
   # or at least makes problems painfully obvious TODO FIXME
   return ' .. ..' . $oword . '.. .. ';
 }
 if ($otype eq 'N') {
   return '. ' . $oword . ' .';
 }
 if ($otype eq 'U') {
   #fixme split the brivla and then rip cmavo from the front of each
   # stress and relax are very case sensitive
  while ($word =~ /^($STRESS $RELAX)($C .*)$ /x) {
    $front =$1; $word=$2;
    $seped=unknown_sepli($front);
    if (defined ($seped)) { push (@parts,$seped); }
    else { return '.. ' . $oword . ' ..'; }
  }
  $seped=unknown_sepli($word);
  if (defined ($seped)) { push (@parts,$seped); }
  else { return '.. ' . $oword . ' ..'; }
  return join(q{ },@parts);
 }

  return $word;
  #return $word . ' ' . $otype . ' ';
}

my $line;
#my $raw_word;

while ($line = <>) {
  binmode(STDOUT, ":encoding(UTF-8)");
  chomp $line;
  for my $raw_word (split(/ [.\t\n ]+ /x,$line)) {
    #my $type=classify_word($raw_word);
    my $type=classify_valsi($raw_word);
    #print $raw_word, ' -- ',cmavo_sepli($raw_word,$type),q{ },$type,"\n";
    #if ($raw_word =~ / ( $BAD ) /ix ) { print 'BAD ( ', $1 , " )\n"; }
    print sepli($raw_word,$type),q{ };
  }
  print "\n";
}

1;

__END__

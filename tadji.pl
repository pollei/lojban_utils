#! /usr/bin/perl
use 5.010;
use strict;
use utf8;
use warnings;
our $VERSION = 0.000_001;

#use Lojban::Valsi ':ALL';
use Lojban::Saprvalsep ':ALL';

# By Stephen Pollei
# Copyright (C) 2011, "Stephen Pollei"<stephen.pollei@gmail.com>
# GPLv3 or later http://www.gnu.org/licenses/gpl.html

#use Parse::Earley;
# http://search.cpan.org/~lpalmer/Parse-Earley-0.15/Earley.pm
# I think instead of writing my own tokenizer smart enough to handle zoi bu
# and other makfa selma'o that I need to bring out a real parser

# a lojban processor
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

Lojban::Valsi::test_regex_foundation0(); 

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

my $line;
my $in_str=q{};
my $ret;
#my $raw_word;

binmode(STDOUT, ":encoding(UTF-8)");

while ($line = <>) {
  if ($line =~ m/ \# \% \% /x) {
    next if ($line =~ m/ \# \% \% \# /x ); 
    #say 'cheese';
    $ret=saprvalsep($in_str);
    say join(q{|},@{$ret});
    $in_str=q{};
  }
  else {
    $in_str .= $line;
    #say '$$$<<', $in_str, '>>$$$';
  }
}
$ret=saprvalsep($in_str);
say join(q{|},@{$ret});

1;

__END__

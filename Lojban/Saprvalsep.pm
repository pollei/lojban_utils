#! /usr/bin/perl
package Lojban::Saprvalsep;
use 5.010;
use strict;
use utf8;
use warnings;

use Exporter 'import';
our @EXPORT_OK = qw(saprvalsep vlalaha);
our %EXPORT_TAGS = ( ALL => [@EXPORT_OK] );

our $VERSION = 0.000_004;

use Lojban::Valsi ':ALL';

# By Stephen Pollei
# Copyright (C) 2011, "Stephen Pollei"<stephen.pollei@gmail.com>
# GPLv3 or later http://www.gnu.org/licenses/gpl.html

# a "simple" word splitter sampu valsi sepli
#handles the gaps between words both splits and rejoins

#FIXME TODO add smarter join later
sub vlalaha {
  #my @parts = @_ ;
  #my (@parts,$flag) = (@_) ;
  my @parts =@{ $_[0] };
  my %flag;
  if ($#_ >0 ) { %flag = %{ $_[1]} ; }
     else { %flag =(); }
  #say 'vlalaha flag', $flag{liquid};
  if ($#parts<0) {return q{.}; }
  #say 'vlalaha<', $parts[0],'>';
  if ($parts[0] !~ / [\s.] /x) { unshift @parts, q{.}; }
  if ($parts[-1] !~ / [\s\.] /x) { push @parts, q{ .}; }
  return join(q{.},@parts);
}

my $makfa_cmavo=Lojban::Valsi::make_cmavo_pat( qw(lo'u le'u zoi zo'oi la'o la'oi));

q{lo'u} =~ $makfa_cmavo or die;
q{le'u} =~ $makfa_cmavo or die;
q{zoi} =~ $makfa_cmavo or die;
q{la} =~ $makfa_cmavo and die;


# FIXME TODO maybe I'd like to split things further
sub cmavo_split {
  my ($words) =@_;
  my @ret;
  while (length($words)) {
    if ( $words =~
       / ^ (  (?: (?! $makfa_cmavo) $CMAVO)* ) ( $makfa_cmavo ) ( $X* ) $ /x) {
      #say 'cheese wiz <',$words,'><',$1,'><',$2,'><',$3,'>',$4;
      if ($1 ne q{}) { push @ret,$1; }
      push @ret, $2;
      if ($3 eq q{}) {return \@ret};
      $words=$3;
    }
    else {
      push @ret,$words;
      return \@ret;
    }
  }
  push @ret,$words;
  return \@ret;
}

sub split_words {
  my @ret;
  my ($words) =@_;
  while (length($words) ) {
    #say 'split_words<',$words,'>';
    #start ripping apart words that have bad combo of letters
    if ($words =~ / ^ ($X* (?= $BAD_CC) $C) ($C .* )  $ /x) {
      #say 'split_words bad cc<',$words,'>',$1,'-',$2;
      $words=$2;
      push @ret, @{ split_words($1) }; next;
    }
    if ($words =~ / ^ ($X* (?= $BAD_CCC) $C $C ) ($C .* ) $ /x) {
      #say 'split_words bad ccc<',$words,'>',$1,'-',$2;
      $words=$2;
      push @ret, @{ split_words($1) }; next;
    }
    if ($words =~ / ^ ($X* $C) ($H .* ) $ /x) {
      $words=$2;
      push @ret, @{ split_words($1) }; next;
    }
    if ($words =~ / ^ ($X* $H $C) ($X .* ) $ /x) {
      $words=$2;
      push @ret, @{ split_words($1) }; next;
    }
    #ok any words that survive this far don't have bad combo of letters
    #they might not be proper syllables and might still have other issues

    if ($words =~ / [wq] | $H $H | ^ $H | $H $C /ix ) {
      $words=fix_word($words);
    }
    if ($words !~ / ^ $SYLL+ $ /sx) {
      #say 'split_word fix_word<',$words,'>',fix_word($words);
      $words=fix_word($words);
    }

    #if it's a name we do not need to split it further
    if ($words =~ /^ $CMENE $ /x) {
      #say 'found cmene<',$words,'>',fix_word($words);
      push @ret,fix_word($words); return \@ret;
    }

    #split cmavo off the front try breaking off at consonant first
    if ($words =~ / ^ ($CMAVO+) ( (?= $BRIVLAS) $C $X+ ) $ /x) {
      $words=$2;
      push @ret, @{ split_words($1) }; next;
    }
    if ($words =~ / ^ ($CMAVO+) ( (?= $BRIVLAS) $X+) $ /x) {
      $words=$2;
      push @ret, @{ split_words($1) }; next;
    }
    #if ($words =~ / ^ ($CMAVO+) ( (?! $CMAVO) $X+) $ /x) {
    #  push @ret, @{ split_words($1) }; next;
    #}

    if ($words =~ / ^ $CMAVO+ $ /x) {
      push @ret, @{ cmavo_split($words) }; return \@ret;
    }

    # break words apart based on stress
    # try to be gentler at first
    if ($words =~ / ^ ($STRESS $RELAX)
                        ( $C+ $X+ | $V $H $X+ | $Y $X+ ) $ /x) {
      $words=$2;
      push @ret, @{ split_words($1) }; next;
    }
    #if that did not work, try ripping harder
    if ($words =~ / ^ ($X* $STRESS $RELAX)
                        ( $X* (?: $YC | $V $H) $X+ ) $ /x) {
      $words=$2;
      push @ret, @{ split_words($1) }; next;
    }

    if ($words =~ / ^ $BRIVLAS $ /x) {
      push @ret,  fix_word($words) ; return \@ret;
    }

    #say 'FIXME unhandled split word: ' , $words;
    push @ret,q{.} . fix_word($words) . q{.} ; return \@ret;
  }
  return \@ret;
}

my $ws =qr/(?! $RAW_NUM) [\s.[:punct:]] \s* /x;
#match whitespace and punctuation but be careful to not eat raw numbers
my $cluster_jam =qr/ (?: (?! $SYLL) $C)+ /ix;

sub saprvalsep {
  my ($str) = @_;
  my @ret;
  while (length($str)) {
    #say 'sapr<',$str,'>';
    if ($str =~ / ^ ($ws+)([^\s]+.*|) $ /sx) {
      $str=$2;
      push @ret, fix_white($1); next;
    }
    if ($str =~ / ^ ($RAW_NUM+)( (?!  $RAW_NUM) .*|) $ /sx) {
      $str=$2;
      push @ret, fix_num($1); next;
    }
    # words should be made out of pronounceable syllabies
    if ($str =~ / ^ ($SYLL+)( (?! $SYLL) .* |) $ /sx) {
      $str=$2;
      push @ret, @{ split_words($1) }; next;
    }
    # if no syllable is available likely there is a consonant cluster jam
    #if ($str =~ / ^ ($cluster_jam)( $SYLL .* | $WS .* | ) $ /sx) {
    if ($str =~ / ^ ($cluster_jam)( (?! $cluster_jam) .* | ) $ /sx) {
      $str=$2;
      push @ret, fix_word($1) ; next;
    }
    if ($str =~ / ^ ($CCC $CCC)( $C .* |) $ /sx) {
      $str=$2;
      push @ret, fix_word($1) ; next;
    }
    if ($str =~ / ^ ($C+)( $WS .* |) $ /sx) {
      $str=$2;
      push @ret, @{ split_words($1) }; next;
    }
    # handle words that include illegal letters like q and-or w
    if ($str =~ / ^ ($GOB+)( (?! $GOB) .* |) $ /sx) {
      $str=$2;
      push @ret, @{ split_words($1) } ; next;
    }
    # last ditch effort to do something
    if ($str =~ / ^ ([^\s.]+)(.*) $ /sx) {
      $str=$2;
      push @ret, @{ split_words($1) } ; }
    else {
      push @ret,$str; return \@ret; }
      # the else clause should never trigger; dead code hopefully
  }
  return \@ret;
}

1;

__END__

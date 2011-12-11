#! /usr/bin/perl
package Lojban::Saprvalsep;
use 5.010;
use strict;
use utf8;
use warnings;

use Exporter 'import';
our @EXPORT_OK = qw(saprvalsep vlalaha);
our %EXPORT_TAGS = ( ALL => [@EXPORT_OK] );

our $VERSION = 0.000_003;

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
  if ($words =~ /^ $CMENE $ /x) {
    push @ret,$words; return \@ret;
  }
  while (length($words) ) {
    #say 'split_words<',$words,'>';
    if ($words =~ / ^ ($CMAVO+) ( $X+ |) $ /x) {
      push @ret, @{ cmavo_split($1) }; $words=$2;
      return \@ret if ($words eq q{});
    }
    if ($words =~ / ^ ($STRESS $RELAX) ( $X+ |) $ /x) {
      push @ret, $1; $words=$2; next;
    }
    push @ret,$words; return \@ret;
  }
  return \@ret;
}

sub saprvalsep {
  my ($str) = @_;
  my @ret;
  while (length($str)) {
    #say 'sapr<',$str,'>';
    if ($str =~ / ^ ([\s.[:punct:]]+)([^\s]+.*|) $ /sx) {
      push @ret, $1; $str=$2;
      return \@ret if ($str eq q{});
    }
    if ($str =~ / ^ ($RAW_NUM+)( (?!  $RAW_NUM) .*|) $ /sx) {
      push @ret, $1; $str=$2; next;
    }
    if ($str =~ / ^ ($WEAK_SYLL+)( (?! $WEAK_SYLL) .* |) $ /sx) {
      push @ret, @{ split_words($1) }; $str=$2; next;
    }
    #TODO FIXME maybe I should make the fixup optional or move it elsewhere
    if ($str =~ / ^ ($GOB+)( (?! $GOB) .* |) $ /sx) {
      push @ret, fix_word($1); $str=$2; next;
    }
    if ($str =~ / ^ ([^\s.]+)(.*) $ /sx) {
        push @ret, fix_word($1); $str=$2;}
    else {
        push @ret,$str; return \@ret; }
  }
  return \@ret;
}

1;

__END__

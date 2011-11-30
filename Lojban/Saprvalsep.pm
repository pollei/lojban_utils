#! /usr/bin/perl
package Lojban::Saprvalsep;
use 5.010;
use strict;
use utf8;
use warnings;

use Exporter 'import';
our @EXPORT_OK = qw(saprvalsep);
our %EXPORT_TAGS = ( ALL => [@EXPORT_OK] );

our $VERSION = 0.000_001;

use Lojban::Valsi ':ALL';

# By Stephen Pollei
# Copyright (C) 2011, "Stephen Pollei"<stephen.pollei@gmail.com>
# GPLv3 or later http://www.gnu.org/licenses/gpl.html

# a "simple" word splitter sampu valsi sepli

my $makfa_cmavo=Lojban::Valsi::make_cmavo_pat( qw(lo'u le'u zoi zo'oi la'o la'oi));

q{lo'u} =~ $makfa_cmavo or die;
q{le'u} =~ $makfa_cmavo or die;
q{zoi} =~ $makfa_cmavo or die;
q{la} =~ $makfa_cmavo and die;


# FIXME TODO maybe I'd like to split things further
sub cmavo_split {
  my ($words) =@_;
  my @ret;
  my $max=length($words);
  while (length($words) and $max>0) {
    if ( $words =~
       / ^ (  (?: (?! $makfa_cmavo) $CMAVO)* ) ( $makfa_cmavo ) ( $X* ) $ /x) {
      #say 'cheese wiz <',$words,'><',$1,'><',$2,'><',$3,'>',$4;
      if ($1 ne q{}) { push @ret,$1; }
      push @ret, $2;
      if ($3 eq q{}) {return \@ret};
      $words=$3;
    }
    $max--;
  }
  push @ret,$words;
  return \@ret;
}

sub split_words {
  my @ret;
  my ($words) =@_;
  if ($words =~ /^ $CMENE $ /x) {
    return $words;
  }
  while (length($words) ) {
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
    if ($str =~ / ^ ([\s.]+)([^\s]+.*|) $ /sx) {
      push @ret, $1; $str=$2;
    }
    if ($str =~ / ^ ($WEAK_SYLL+)( (?! $WEAK_SYLL) .* |) $ /sx) {
      push @ret, @{ split_words($1) }; $str=$2; next;
    }
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

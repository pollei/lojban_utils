#! /usr/bin/perl
package Lojban::Gerna;
use 5.010;
use strict;
use utf8;
use warnings;

use Exporter 'import';
our @EXPORT_OK = qw(new_token_base new_mini_mu);
our %EXPORT_TAGS = ( ALL => [@EXPORT_OK] );

our $VERSION = 0.000_001;

use Lojban::Valsi ':ALL';
use Parse::Earley;

# By Stephen Pollei
# Copyright (C) 2011, "Stephen Pollei"<stephen.pollei@gmail.com>
# GPLv3 or later http://www.gnu.org/licenses/gpl.html

# gerna aka grammar -- stuff that has to deal with parsing

# WARN this breaks encapsulation of the Earley object by directly
# monkeying with it's internals WARN
sub new_token_base {
  my $gram = new Parse::Earley;
  my %tok = ( lineno => q{_}, type => 'regex' );
  for my $sm (keys(%SM) ) {
    $gram->{rules}{$sm . q(_tt)}[0] = [ { %tok, match => $SM{$sm} } ] ;
  }
  $gram->{rules}{WS}[0] = [ { %tok, match => $WS } ];
  $gram->{rules}{CY_tt}[0] = [ { %tok, match => $Lojban::Valsi::CM_CY } ];

  return $gram;
}

# a very simple pseudo subset of lojban for testing purposes
sub new_mini_mu {
  my $gram_txt =<<'EO_MM_G' ;
jbovla: BRIVLA_tt | CMENE_tt | CMAVO_tt
cy0: CY_tt | CMAVO_tt BU_tt
cy: cy0 | cy cy0
cysumti: cy | cy BOI_tt
selbridi0: GOhA_tt | BRIVLA_tt
selbridi0c: selbridi0 | selbridi0c selbridi0
selbridi1: selbridi0c | KE_tt selbridi0c | KE_tt selbridi0c KEhE_tt
selbridi1c: selbridi1 | selbridi1c selbridi1
cmevlac: CMENE_tt | cmevlac CMENE_tt
sumti0: cysumti | LE_tt selbridi1c | LE_tt selbridi1c KU_tt | LA_tt cmevlac
sumti1: sumti0 | LE_tt sumti2 selbridi1c | LE_tt sumti2 selbridi1c KU_tt
sumti1c: sumti1 | sumti1c sumti1
bridi0: selbridi1 | sumti1c selbridi1c | sumti1c CU_tt selbridi1c | sumti1c CU_tt selbridi1c sumti1c | sumti1c selbridi1c sumti1c | selbridi1c sumti1c
bridi2: bridi0 | bridi0 GIhA_tt bridi0 | bridi0 GIhA_tt bridi0 VAU_tt | bridi0 GIhA_tt bridi0 VAU_tt sumti1c
bridi3: bridi2 | bridi2 VAU_tt
sumti2: sumti1 | LE_tt NU_tt bridi3 | LE_tt NU_tt bridi3 KEI_tt
sumti2c: sumti2 | sumti2c sumti2
bridi4: selbridi1 | sumti2c selbridi1c | sumti2c CU_tt selbridi1c | sumti2c CU_tt selbridi1c sumti2c | sumti2c selbridi1c sumti2c | selbridi1c sumti2c
bridi5: bridi4 | bridi4 GIhA_tt bridi4 | bridi4 GIhA_tt bridi4 VAU_tt | bridi4 GIhA_tt bridi4 VAU_tt sumti1c
done: bridi5 | bridi5 VAU_tt | I_tt bridi5 | I_tt bridi5 VAU_tt |  sumti2 | I_tt sumti2
EO_MM_G
  my $gram=new_token_base();
  #$Parse::Earley::DEBUG = 1;
  $gram->grammar($gram_txt);
  $gram->start('done');
  $gram->{skip} = qr/ $WS* /ix;;

  return $gram;
}

sub test_mini_mu_match {
  my ($parser,$input,$verbose) = (@_);
  $parser->start('done');
  $parser->{skip} = qr/ $WS* /ix;
  $Parse::Earley::DEBUG = $verbose;
  $parser->advance($input);
  #say 'mmm enter loop';
  while (not $parser->fails($input,'done')
         and not $parser->matches($input, 'done')) {
    $parser->advance($input);
    #print '#';
    }
  #say 'mmm left loop';
  my $ret=$parser->matches($input, 'done');
  if (not $verbose or not $ret) { return $ret; }
  my @m;
  my $graph;
  @m = $parser->matches($input, 'done');
  $graph = $m[0];
  say 'match#', scalar @m;
  #say 'graph: ',$graph,' tok ' ,$graph->{tok};
  say 'graph: ',$graph;
  say ' lhs ',$graph->{lhs}, ' pos ', $graph->{pos};
  say ' down ', $graph->{down}, ' down[0]', $graph->{down}[0];
  say ' left ', $graph->{left},' left[0]', $graph->{left}[0];
  return $ret;
}

sub test_mini_mu {
  #$Parse::Earley::DEBUG = 1;
  my $gram = new_mini_mu();
  #test_mini_mu_match($gram, q{ gismu },0) or die;
  test_mini_mu_match($gram, q{gismu},0) or die;
  test_mini_mu_match($gram, q{ gismu },0) or die;
  #$Parse::Earley::DEBUG = 1;
  q{le gismu} =~ m/^ $SM{LE} /ix or die;
  test_mini_mu_match($gram, q{legismu },0) or die;
  test_mini_mu_match($gram, q{le gismu },0) or die;
  test_mini_mu_match($gram, q{le gismu ku},0) or die;
  return;
}

1;

__END__

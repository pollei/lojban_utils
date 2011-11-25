#! /usr/bin/perl
use strict;
use utf8;
use warnings;

# separate words based on lojban morphology and add some pauses

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

# misnamed also trigers if it's foreign word
# xu cmene ja fange valsi

our $C =qr/[bcdfghjklmnpqrstvwxz]/i;
our $BAD_W = qr/h|q|w|aa|ae|ao|ea|ee|eo|eu|oa|oe|ou|cx|kx|xc|xk|mz|iy|uy|ndj|ndz|ntc|nts/ix;
sub xu_cmene {
  my ($word) =@_;
}

sub xu_cmena_olde {
  my ($word) =@_;
  if ($word =~ /[bcdfghjklmnpqrstvwxz]\.*$/ix) { return 1; }
  if ($word =~ /(h|q|w|aa|ae|ao|ea|ee|eo|eu|oa|oe|ou|cx|kx|xc|xk|mz|iy|uy|ndj|ndz|ntc|nts)/i)
           { return 1;  }
  if ($word =~ /([bcdfghjklmnpqrstvwxz])\1/i) { return 1; }
  if ($word =~ /[ptkfcsx][bdgvjz]/i) { return 1; }
  if ($word =~ /[bdgvjz][ptkfcsx]/i) { return 1; }
  if ($word =~ /[cjsz][cjsz]/i ) { return 1; }
  if ($word =~ /[bcdfghjklmnpqrstvwxz](bd|bg|bj|bm|bn|bv|bz|db|dg|dl|dm|dn|dv|fc|fk|fm|fn|fp|fs|ft|fx|gb|gd|gj|gm|gn|gv|gz|jl|jn|jr|kc|kf|km|kn|kp|ks|kt|lb|lc|ld|lf|lg|lj|lk|lm|ln|lp|lr|ls|lt|lv|lx|lz|mb|mc|md|mf|mg|mj|mk|mn|mp|ms|mt|mv|mx|nb|nc|nd|nf|ng|nj|nk|nl|nm|np|nr|ns|nt|nv|nx|nz|pc|pf|pk|pm|pn|ps|pt|px|rb|rc|rd|rf|rg|rj|rk|rl|rm|rn|rp|rs|rt|rv|rx|rz|sx|tf|tk|tl|tm|tn|tp|tx|vb|vd|vg|vj|vm|vn|vz|xf|xm|xn|xp|xs|xt|zl|zn|zr)/i ) { return 1;}
  return 0;
}

# is the first consonant cluster consist only of valid initial pairs?
sub xu_CC {
  my ($word) =@_;
  # FIXME regex needs to capture less FIXME
  $word =~ /^\.?((?:[bcdfgjklmnprstvxzaeiouy',][,']?){0,3}[bcdfgjklmnprstvxz,]+y?[bcdfgjklmnprstvxz,]+)[aeiouy]/i;
  my $start=$1;
  if ($start =~ /bd|bg|bj|bm|bn|bv|bz|db|dg|dl|dm|dn|dv|fc|fk|fm|fn|fp|fs|ft|fx|gb|gd|gj|gm|gn|gv|gz|jl|jn|jr|kc|kf|km|kn|kp|ks|kt|lb|lc|ld|lf|lg|lj|lk|lm|ln|lp|lr|ls|lt|lv|lx|lz|mb|mc|md|mf|mg|mj|mk|mn|mp|ms|mt|mv|mx|nb|nc|nd|nf|ng|nj|nk|nl|nm|np|nr|ns|nt|nv|nx|nz|pc|pf|pk|pm|pn|ps|pt|px|rb|rc|rd|rf|rg|rj|rk|rl|rm|rn|rp|rs|rt|rv|rx|rz|sx|tf|tk|tl|tm|tn|tp|tx|vb|vd|vg|vj|vm|vn|vz|xf|xm|xn|xp|xs|xt|zl|zn|zr/i ) { return 0;}
  if ($start =~ /bl|br|cf|ck|cl|cm|cn|cp|cr|ct|dj|dr|dz|fl|fr|gl|gr|jb|jd|jg|jm|jv|kl|kr|ml|mr|pl|pr|sf|sk|sl|sm|sn|sp|sr|st|tc|tr|ts|vl|vr|xl|xr|zb|zd|zg|zm|zv/i ) {return 1; }
  return 0;
}

#xu gismu
sub xu_gismu {
  my ($word) =@_;
  #if (xu_cmene($word)) return 0;
  if ($word =~
     /^\.?[bcdfgjklmnprstvxz][aeiou][bcdfgjklmnprstvxz]{2,2}[aeiou]\.?$/i )
        { return 1; }
  if ( $word =~
     /^\.?[bcdfgjklmnprstvxz]{2,2}[aeiou][bcdfgjklmnprstvxz][aeiou]\.?$/i)
        { return 1; }
  return 0;
}

#xu lujvo
sub xu_lujvo {
  my ($word) =@_;
  #if (xu_cmene($word)) return 0;
  #tosmabru
  if ($word =~ /^[bcdfgjklmnprstvxz][aeiou](.*)$/ ) {
    if (xu_brivla($1)) { return 0;}
  }
#FIXME AUDIT is this regex really correct and sufcient? FIXME
  if ($word =~
   /^(([bcdfgjklmnprstvxz][aeiou][bcdfgjklmnprstvxz]{2,2}[aeiouy]|[bcdfgjklmnprstvxz]{2,2}[aeiou][bcdfgjklmnprstvxz][aeiouy]|[bcdfgjklmnprstvxz][aeiou][bcdfgjklmnprstvxz]|[bcdfgjklmnprstvxz]{2,2}[aeiou]|[bcdfgjklmnprstvxz][aeiou]'?[aeiou][rn]?)y?){2,27}$/i )
     { return 1; }
  return 0;
}

#FIXME AUDIT lot's of hairy regex in here: is it all correct and sufient? FIXME
#xu fu'ivla
sub xu_fuhivla {
  my ($word) =@_;
  #if (xu_cmene($word)) return 0;
  return 0 unless xu_CC($word);
  if ($word =~ /[yY]/) { return 0; }
  # not combo of cmavo and gismu and/or lujvu
  if ($word =~ /^(\.?[bcdfgjklmnprstvxz]?[aeiou]\'?[aeiou]?){1,6}[bcdfgjklmnprstvxz][aeiou][bcdfgjklmnprstvxz]{2,2}[aeiou]\.?$/i) { return 0; }
  if ($word =~ /^(\.?[bcdfgjklmnprstvxz]?[aeiou]\'?[aeiou]?){1,6}[bcdfgjklmnprstvxz]{2,2}[aeiou][bcdfgjklmnprstvxz][aeiou]\.?$/i) { return 0; }
  if ($word =~ /^(\.?[bcdfgjklmnprstvxz]?[aeiou]\'?[aeiou]?){1,6}(([bcdfgjklmnprstvxz][aeiou][bcdfgjklmnprstvxz]{2,2}[aeiouy]|[bcdfgjklmnprstvxz]{2,2}[aeiou][bcdfgjklmnprstvxz][aeiouy]|[bcdfgjklmnprstvxz][aeiou][bcdfgjklmnprstvxz]|[bcdfgjklmnprstvxz]{2,2}[aeiou]|[bcdfgjklmnprstvxz][aeiou]'?[aeiou][rn]?)y?){2,27}\.?$/i) { return 0; }
  # slinku'i paslinku'i
  if (('pa' . $word) =~
   /^(([bcdfgjklmnprstvxz][aeiou][bcdfgjklmnprstvxz]{2,2}[aeiou]?|[bcdfgjklmnprstvxz]{2,2}[aeiou][bcdfgjklmnprstvxz][aeiou]?|[bcdfgjklmnprstvxz][aeiou][bcdfgjklmnprstvxz]|[bcdfgjklmnprstvxz]{2,2}[aeiou]|[bcdfgjklmnprstvxz][aeiou]'?[aeiou][rn]?)y?){2,27}$/i )
     { return 0; }
  # stage 3 detection not really being used
  if ($word =~ /^([bcdfgjklmnprstvxz][aeiouy][bcdfgjklmnprstvxz]{2,2}[aeiouy]?|[bcdfgjklmnprstvxz]{2,2}[aeiouy][bcdfgjklmnprstvxz][aeiouy]?|[bcdfgjklmnprstvxz][aeiouy][bcdfgjklmnprstvxz]|[bcdfgjklmnprstvxz]{2,2}[aeiouy]|[bcdfgjklmnprstvxz][aeiouy]'?[aeiouy])[rnl][bcdfgjklmnprstvxz]/i ) { return 3; }
  return 1;
}

# xu bridi valsi
sub xu_brivla {
  my ($word) =@_;
  #if (xu_cmene($word)) return 0;
  #if (! $word =~ /^\.?[bcdfgjklmnprstvxzaeiouy',]{0,3}[bcdfgjklmnprstvxz]y?[bcdfgjklmnprstvxz][bcdfgjklmnprstvxzaeiouy',]*[aeiouy]\.?$/i) { return 0; }
  return 0 unless ($word =~ /^\.?(?:[bcdfgjklmnprstvxzaeiouy',][,']?){0,3}[bcdfgjklmnprstvxz]y?[bcdfgjklmnprstvxz][bcdfgjklmnprstvxzaeiouy',]*[aeiouy]\.?$/i);
  return 0 unless ($word =~ /^[^AEIOU]+[aeiouAEIOU][,yYbcdfgjklmnprstvxzBCDFGJKLMNPRSTVXZ]+[aeiou']+$/) ;
  if ($word =~ /^([bcdfgjklmnprstvxz]{2,})/ ) {
     return 0 unless xu_CC($1); }
  if (xu_gismu($word)) { return 1; }
  if (xu_lujvo($word)) { return 2; }
  if (xu_fuhivla($word)) { return 3; }
  return 0;
}

sub xu_cmavo {
  my ($word) =@_;
  if (xu_cmene($word)) { return 0; }
  if ($word =~ /^(\.?[bcdfgjklmnprstvxz]?[aeiou]\'?[aeiou]?)+\.?$/i) { return 1; }
  if ($word =~ /^y+(bu)?$/) { return 1; }
  if ($word =~ /^([bcdfgjklmnprstvxz]y)+(boi)?$/i) { return 1; }
  if ($word =~ /^y'y$/i) {return 1;}
  return 0;
}

sub classify_word {
  my ($word) =@_;
  my $classed="";
  my $btype=0;
  if ($word eq "") {return 'x';}
  if (xu_cmene($word) ) { return "N"; }
  elsif ($btype=xu_brivla($word)) {
    return 'B' . ( 'x', 'G','L', 'F')[$btype];
    # FIXME DEADCODE
#    $classed .="B";
# #   if (xu_gismu($word)) { $classed .= 'G';}
# #   elsif (xu_lujvo($word)) { $classed .= 'L';}
# #   elsif (xu_fuhivla($word)) { $classed .='F';}
#  #  return $classed;
   }
  elsif (xu_cmavo($word) ) {return 'c';}
  return "U";
}

#cmavo splitter
sub cmavo_sepli {
  my ($word) =@_;
  my @parts;
  my $cmavo;
  my $leftover;
    if ($word =~ /^(y+)(bu)?$/) {
       my $y=$1 ; my $bu=$2; $y =~ s/y(?! )/. y /g; return $y . $bu . " ."; }
    if ($word =~ /^([bcdfgjklmnprstvxzy]+)(boi)?$/i) {
       my $l = $1; my $boi=$2; my $n= length($l); my $i=0;
       #print "x" . $l ."x $n" . $boi ."x\n";
       for ($i=0;$i < $n; $i+=2) {push (@parts,substr($l,$i,2)); }
       return ". " . join(" ",@parts) . " " . $boi . " .";
      }
      if ($word =~ /^y'y$/i) {return ". y'y .";}
    if ($word =~ /^[aeiouy]/i) {push(@parts, '. ');}
    while ($word =~
      /^([bcdfgjklmnprstvxz]?[aeiou']{1,4})([bcdfgjklmnprstvxzy][aeiou].*)$/) {
         $cmavo=$1;$leftover=$2;
         if ($cmavo eq "lo'u" || $cmavo eq "le'u") {
                $cmavo = '. ' . $cmavo . ' .';}
         push(@parts,$cmavo);$word=$leftover;
       }
    if ($word eq "lo'u" || $word eq "le'u") { $word = '. ' . $word . ' .';}
    push(@parts,$word);
    return join(' ',@parts);
}

#unknow splitter
sub unknown_sepli {
  my ($oword) =@_;
  my @parts;
  my $type;
  my $cmavo;
  my $leftover;
  my $word=$oword;
  $type=classify_word($word);
  if ($type eq 'c') {
    return cmavo_sepli($word); }
  if ($word =~ /^[aeiouy]/i) {push(@parts, '. ');}
  while ( $type eq 'U' && $word =~
      /^([bcdfgjklmnprstvxz]?[aeiou']{1,4})([bcdfgjklmnprstvxzBCDFGJKLMNPRSTVXZ].*)$/) {
     $cmavo=$1;$leftover=$2;
     if ($cmavo eq "lo'u" || $cmavo eq "le'u") { $cmavo = '. ' . $cmavo . ' .';}
     push(@parts,$cmavo);$word=$leftover; $type=classify_word($word);
  }
  #return undef unless ($type =~ /^B[GLF]$/);
  return unless ($type =~ /^B[GLF]$/);
  push(@parts,$word);
  #print ' (' . $type . ') ';
  return join(' ',@parts);
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
    #FIXME all this is duplicate delete
#    if ($word =~ /^(y+)(bu)?$/) {
#       my $y=$1 ; my $bu=$2; $y =~ s/y(?! )/. y /g; return $y . $bu . " ."; }
#    if ($word =~ /^([bcdfgjklmnprstvxzy]+)(boi)?$/i) {
#       my $l = $1; my $boi=$2; my $n= length($l); my $i=0;
#       #print "x" . $l ."x $n" . $boi ."x\n";
#       for ($i=0;$i < $n; $i+=2) {push (@parts,substr($l,$i,2)); }
#       return ". " . join(" ",@parts) . " " . $boi . " .";
#      }
#      if ($word =~ /^y'y$/i) {return ". y'y .";}
#    if ($word =~ /^[aeiouy]/i) {push(@parts, '. ');}
#    while ($word =~
#      /^([bcdfgjklmnprstvxz]?[aeiou']{1,4})([bcdfgjklmnprstvxzy][aeiou].*)$/) {
#         $cmavo=$1;$leftover=$2;
#         if ($cmavo eq "lo'u" || $cmavo eq "le'u") {
#                $cmavo = '. ' . $cmavo . ' .';}
#         push(@parts,$cmavo);$word=$leftover;
#       }
#    if ($word eq "lo'u" || $word eq "le'u") { $word = '. ' . $word . ' .';}
#    push(@parts,$word);
#    return join(' ',@parts);
    #FIXME all this is duplicate delete
  }
 if ($otype eq 'N') {
   return '. ' . $oword . ' .';
 }
 if ($otype eq 'U') {
   #fixme split the brivla and then rip cmavo from the front of each
  while ($word =~ /^([^AEIOU]+[AEIOU][,yYbcdfgjklmnprstvxzBCDFGJKLMNPRSTVXZ]{1,4}[aeiou']{1,4})([bcdfgjklmnprstvxzBCDFGJKLMNPRSTVXZ].*)$/) {
    $front =$1; $word=$2;
    $seped=unknown_sepli($front);
    if (defined ($seped)) { push (@parts,$seped); }
    else { return '.. ' . $oword . ' ..'; }
  }
  $seped=unknown_sepli($word);
  if (defined ($seped)) { push (@parts,$seped); }
  else { return '.. ' . $oword . ' ..'; }
  return join(' ',@parts);
 }

  return $word;
  #return $word . ' ' . $otype . ' ';
}

my $line;
#my $raw_word;

while ($line = <>) {
  binmode(STDOUT, ":encoding(UTF-8)");
  chomp $line;
  for my $raw_word (split(/[\.\t\n ]+/,$line)) {
    my $type=classify_word($raw_word);
    #print $raw_word, ' -- ',cmavo_sepli($raw_word,$type)," ",$type,"\n";
    print sepli($raw_word,$type),' ';
  }
  print "\n";
}



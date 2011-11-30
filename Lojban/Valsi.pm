#! /usr/bin/perl
package Lojban::Valsi;
use 5.010;
use strict;
use utf8;
use warnings;

use Exporter 'import';
our @EXPORT_OK = qw(
    $STRESS $NO_STRESS $RELAX $PSTRESS $GOOD $WEAK_GOOD $WEAK_BAD $STRONG_BAD
    $GOB %SM %SM_LIST $WEAK_SYLL $CMENE $BRIVLA $BRIVLA_ $BRIVLAS $GISMU $CMAVO
    $CM_SIMPLE $LUJVO $FUH3 $FUH4 $CM_0 $GISMU_ $LUJVO_
    $C $V $L $H $Y $X $WS classify_valsi fix_word);
our %EXPORT_TAGS = ( ALL => [@EXPORT_OK] );

our $VERSION = 0.000_004;

# By Stephen Pollei
# Copyright (C) 2011, "Stephen Pollei"<stephen.pollei@gmail.com>
# GPLv3 or later http://www.gnu.org/licenses/gpl.html


# http://www.lojban.org/publications/reference_grammar/chapter3.html
# The Hills Are Alive With The Sounds Of Lojban

# http://www.lojban.org/publications/reference_grammar/chapter4.html
# The Shape Of Words To Come: Lojban Morphology

sub comma_add {
  my ($word) =@_;
  return join(q{},map( $_ . '\,?' , split(m//m,$word )));
}

#TODO AUDIT maybe rework this func
sub make_list_pat {
  my @li = map(comma_add($_) , @_) ;
  my $pat=join(q{|},@li);
  #for my $item (@_) { }
  #print $pat, "\n\n";
  return qr/$pat/ix;
}

sub cmavo_escape {
  my ($word) =@_;
  my $rword=q{};
  for my $let (split m//m,$word) {
    if ($let =~ /[hH']/x) { $rword .= q{[h'],?}; }
    else { $rword .= $let . q{,?}; }
  }
  return $rword ;
}


our $WS =qr/[.\s]/ix;
our $NOT_WS =qr/ [^\s.]+ /;
our $C =qr/[bcdfgjklmnprstvxz],?/ix;
our $V =qr/[aeiou],?/ix;
our $VY =qr/[aeiouy],?/ix;
our $VH =qr/[aeiouh'],?/ix;
our $VHY =qr/[aeiouyh'],?/ix;
our $H =qr/[h'],?/ix;
our $VHH =qr/$VH $H?/ix;
our $Y =qr/y,?/ix;
our $L =qr/$C|$VHY/ix;
our $YC =qr/$C|$Y/ix;
our $BAD_W = make_list_pat( qw(h q w));
our $X =qr/$L|$BAD_W/ix;
our $M =qr/ [lmnr] \,? /ix;
our $YM =qr/ [lmnry] \,? /ix;
our $BAD_CX = make_list_pat( qw(cx kx xc xk mz));
our $BAD_CCC = make_list_pat( qw(ndj ndz ntc nts));
our $BAD_VV = make_list_pat( qw(aa ae ao ea ee eo eu oa oe ou iy uy));
our $BAD_DD = make_list_pat (
         qw(bb cc dd ff gg hh jj kk ll mm nn pp qq rr ss tt vv ww xx zz));
our $BAD_XZ = qr/[ptkfcsx]\,?[bdgvjz]|[bdgvjz]\,?[ptkfcsx]|[cjsz]\,?[cjsz]/ix;
our $BAD_CC = qr/$BAD_DD | $BAD_XZ | $BAD_CX /ix;
our $BAD_HH = qr/[h']{2,}/ix;

our $BAD_TRI_TAIL =make_list_pat( qw(
   bd bg bj bm bn bv bz db dg dl dm dn dv fc fk fm fn fp fs 
   ft fx gb gd gj gm gn gv gz jl jn jr kc kf km kn kp ks kt lb lc ld lf lg lj 
   lk lm ln lp lr ls lt lv lx lz mb mc md mf mg mj mk mn mp ms mt mv mx nb nc nd 
   nf ng nj nk nl nm np nr ns nt nv nx nz pc pf pk pm pn ps pt px rb rc rd rf 
   rg rj rk rl rm rn rp rs rt rv rx rz sx tf tk tl tm tn tp tx vb vd vg vj 
   vm vn vz xf xm xn xp xs xt zl zn zr));

our $BAD_TRI= qr/$C $BAD_TRI_TAIL | $BAD_CCC/ix;
#our $BAD = qr/$BAD_W|$BAD_VV|$BAD_CC|$BAD_HH|$BAD_TRI/ix;
# bad_tri catches too much like the {g,r,b} in {bang,r,blgaria}
our $STRONG_BAD = qr/$BAD_W|$BAD_VV|$BAD_CC|$BAD_HH|$BAD_CCC/ix;
our $WEAK_BAD = qr/$BAD_W|$BAD_CC|$BAD_HH/ix;
# http://hrwiki.org/wiki/Strong_Bad


#our $CMENE = qr/$C [.]* $ /ix;
our $CMENE_ = qr/ $X* $C (?! $X) /ix;
our $CMENE = qr/ ^ $WS* $CMENE_ $WS* $ /ix;
our $L3_LAX =qr/(?: $L \'?){0,3}/ix;
our $L3=qr/(?: $V $H? | $C (?= $V) ){0,3}/ix;
our $V3=qr/(?: $V $H? ){0,3}/ix;
our $C3=qr/$VHH $C $VHH | $C $VHH $V? /ix;
our $CYC = qr/$C $Y? $C/ix;
our $PCC = qr/$C $C/ix;
our $ICC = make_list_pat ( qw ( bl br cf ck cl cm cn cp cr ct dj dr dz
             fl fr gl gr jb jd jg jm jv kl kr ml mr pl pr sf sk sl sm
             sn sp sr st tc tr ts vl vr xl xr zb zd zg zm zv));
# "tc" | "ts" | "dj" | "dz" | /[cjzs][pkfxbgvmtdnlr]/ | /[pkfxbgvmtdn][lr]/
# for icc this also matches some illegal combos
# should icc be looser to ignore some errors ??
#our $CYC5 = qr/^ [.]* $L3 $CYC ${C}* $VY /ix;
#our $CC5 = qr/^ [.]* $L3 $PCC ${C}* $V /ix;
our $CC5 =  qr/^ [.]* (?: $C3 $PCC| $V3 $ICC) ${C}* $V   /ix;
our $CYC5 = qr/^ [.]* (?: $C3 $CYC| $V3 $ICC) ${C}* $VY  /ix;
our $GISMU_ = qr/ $C$V$C$C$V | $ICC$V$C$V /ix;
our $GISMU = qr/ ^ [.]* $GISMU_ [.]* $ /ix;
#our $GISMU_ = qr/ $C$V$ICC$V | $ICC$V$C$V /ix;
#FIXME AUDIT should gismu pattern be tighter ?? AUDIT

our $R_HYPH =qr/ [rn] \,? (?= $C ) /ix;
our $L_HYPH =qr/ [rnl] \,? (?= $C ) /ix;
our $Y_HYPH =qr/ y  \,? (?= $C ) /ix;
our $M_HYPH =qr/ [lmnr] \,? (?= $C ) /ix;

our $B_C3 = qr/ $C3 $CYC $L* $V (?! $VHY) /ix;
our $B_V3 = qr/ $VHH{1,3} $ICC $L* $V (?! $VHY) | $ICC $C* $VH+ $YC+ $L* $V (?! $VHY) /ix;
our $BRIVLA_ = qr/$B_C3 | $B_V3 /ix;

our $R_CVV =qr/$C$V$H$V|$C a,?i,?| $C e,?i.?| $C o,?i,? | $C a,?u,? /ix;
our $R_CVVR =qr/ $R_CVV $R_HYPH /ix;
our $RAFC =qr/$C$V$C$C|$ICC$V$C|$C$V$C /ix;
our $RAF = qr/$RAFC$Y_HYPH?|$ICC$V|$R_CVV/ix;
# tosmabru FIXME AUDIT tosmabru regex might be wrong
# #tosmabru if ($word =~ /^ [.]* $C $V ($L{4,}) [.]* $ /x ) { if (xu_brivla($1)) { return 0;} }
our $TOSMABRU = qr/ $C $V $BRIVLA_ /ix;
our $LUJVO_ =qr/(?!$TOSMABRU)(?: $RAF | $R_CVVR) $RAF* (?: $RAF | $GISMU_) /ix;
our $LUJVO = qr/ ^ [.]* $LUJVO_ [.]* $ /ix;
#FIXME AUDIT is this lujvo regex really correct and sufficient? FIXME

our $CCC =qr/ $C | $C$C | $C$ICC /ix;
our $SYLL =qr/ $M_HYPH? $CCC? $VHY+ $CCC? $M_HYPH? /ix;
our $WEAK_SYLL =qr/ $M_HYPH? $C* $VHY+ $C* $M_HYPH? | $YM /ix;
our $SYLL_NOY =qr/ $M_HYPH? $CCC? $VH* $V $CCC? $M_HYPH? /ix;
our $SYLL_BTAIL =qr/ $M_HYPH? $CCC $VH* $V (?! $VHY) /ix;
our $GOB =qr/ $M_HYPH? $C* (?: $VHY | $BAD_W)+ $C* $M_HYPH? | $YM /ix;

our $GOOD =qr/ ^ $WS* $SYLL+ $WS* $ /ix;
our $WEAK_GOOD =qr/ ^ $WS* $WEAK_SYLL+ $WS* $ /ix;

#FIXME 
# slinku'i
  # not combo of cmavo and gismu and/or lujvu
  #if ($word =~ / ^ [.]* (?: $C?$V$H?$V?){1,6} (?: $GISMU_ | $LUJVO_) [.]* $ /ix)
  # slinku'i paslinku'i
  #if (('pa' . $word) =~ $LUJVO ) { return 0; }
our $FUH3_NOCOMBO = qr/(?: $C?$V$H?$V?){1,6} (?: $GISMU_ | $LUJVO_)/ix;
our $SLI_RAF = qr/ [iu]\? $R_HYPH? | $C $C? $Y? /ix;
our $SLINKUHI = qr/ $SLI_RAF $RAF* (?: $RAF | $GISMU_) /ix;
our $BAD_FUH =qr/ $SLINKUHI | $FUH3_NOCOMBO /ix;
our $FUH3_ =qr/ (?! $BAD_FUH) $RAFC $L_HYPH $C (?: $C | $VH)* $V (?! $VHY ) /ix;
our $FUH3  =qr/ ^ $WS* $FUH3_ $WS* $ /ix;
#our $FUH4_ =qr/ (?: $C | $VH){3,} $VH (?! $VHY ) /ix;
our $FUH4_ =qr/ $SYLL_NOY+ $SYLL_BTAIL /ix;
our $FUH4  =qr/ ^ $WS* $FUH4_ $WS* $ /ix;

our $BRIVLA = qr/ ^ [.]* $BRIVLA_ [.]* $ /ix;
#TODO AUDIT this brivla pattern is a bit tricky AUDIT
our $BRIVLAS =qr/ (?= $BRIVLA_) (?: $GISMU_ | $LUJVO_ | $FUH4_) /ix;

# stress is very case sensitive
our $NO_STRESS = qr/ [^AEIOU]+ /x;
our $STRESS = qr/ [^AEIOU]+ (?: [AEIOU][Hh,']? )+ $VH* (?! $VHY) /x;
our $RELAX = qr/ $YC+ (?: [aeiou][Hh,']? )+ (?! $VHY) /x;
our $PSTRESS = qr/ $STRESS $RELAX /x;

#our $CM_OK = qr/  $WS* (?! $BRIVLAS | $CMENE_ ) /ix;
our $CM_BAD = qr/  $WS* (?= $BRIVLAS | $CMENE_ ) /ix;
our $CM_0 = qr/ (?! $CM_BAD) $C? $VH* $V (?! $VHY ) /ix;
our $CM_Y =qr/ (?! $CM_BAD)$Y+ (?! $VHY) /ix;
# TODO FIXME bu and other concrete cmavo need to go through make_cmavo_pat
our $CM_YBU =qr/ $CM_Y (?:(?! $CM_BAD)bu)? (?! $VHY) /ix;
#our $CM_CY =qr/ (?=$CM_OK) (?:(?: $C$Y)+) (?! $VHY) /ix;
our $CM_CY =qr/ (?! $CM_BAD ) (?: $C$Y) (?! $VHY) /ix;
our $CM_CYBOI =qr/ $CM_CY+ (?:(?!$CM_BAD)boi)? (?! $VHY) /ix;
our $CM_YHY = qr/ (?! $CM_BAD) y'y (?! $VHY) /ix;
our $CM_YHYBU =qr/ $CM_YHY (?:(?! $CM_BAD)bu)? (?! $VHY) /ix;
our $CM_SIMPLE =qr/  $WS* (?: $CM_0+ | $CM_YBU | $CM_CYBOI | $CM_YHYBU ) $WS*  /ix;
our $CMAVO =qr/  $WS* (?: $CM_0 | $CM_Y | $CM_CY | $CM_YHY ) $WS*  /ix;

sub make_cmavo_pat {
  my @li = map (cmavo_escape($_)   , @_ ) ;
  my $pat= join(q{|},@li) ;
  my $ret= qr/(?! $CM_BAD) (?: $pat ) (?! $VHY) /ix;
  #print $ret, "\n\n";
  # in trying to debug this thing I noticed that printing out
  # the pattern this thing creates is just plain huge and ugly
  # over 10_000 chars long
  return $ret;
}


# pattern match on selma'o 
our %SM;
our %SM_LIST= ( 
   A =>  [qw( a e ji o u )] ,
   BAhE =>  [qw( ba'e za'e )] ,
   BAI =>  [qw( ba'i bai bau be'i ca'i cau ci'e ci'o ci'u cu'u de'i di'o
      do'e du'i du'o fa'e fau fi'e ga'a gau ja'e ja'i ji'e ji'o ji'u ka'a
      ka'i kai ki'i ki'u koi ku'u la'u le'a li'e ma'e ma'i mau me'a me'e
      mu'i mu'u ni'i pa'a pa'u pi'o po'i pu'a pu'e ra'a ra'i rai ri'a
      ri'i sau si'u ta'i tai ti'i ti'u tu'i va'o va'u zau zu'e )] ,
   BE =>  [qw( be )] ,
   BEhO =>  [qw( be'o )] ,
   BEI =>  [qw( bei )] ,
   BIhE =>  [qw( bi'e )] ,
   BIhI =>  [qw( bi'i bi'o mi'i )] ,
   BO =>  [qw( bo )] ,
   BOI =>  [qw( boi )] ,
   BU =>  [qw( bu )] ,
   BY =>  [qw( by cy dy fy ga'e ge'o gy je'o jo'o jy ky lo'a ly
      my na'a ny py ru'o ry se'e sy to'a ty vy xy y'y zy )] ,
   CAhA =>  [qw( ca'a ka'e nu'o pu'i )] ,
   CAI =>  [qw( cai cu'i pei ru'e sai )] ,
   CEhE =>  [qw( ce'e )] ,
   CEI =>  [qw( cei )] ,
   CO =>  [qw( co )] ,
   COI =>  [qw( be'e co'o coi fe'o fi'i je'e ju'i
      ke'o ki'e mi'e mu'o nu'e pe'u re'i ta'a vi'o ki'ai sa'ei)] ,
   CU =>  [qw( cu )] ,
   CUhE =>  [qw( cu'e nau )] ,
   DAhO =>  [qw( da'o )] ,
   DOhU =>  [qw( do'u )] ,
   DOI =>  [qw( doi da'oi)] ,
   FA =>  [qw( fa fai fe fi fi'a fo fu )] ,
   FAhA =>  [qw( be'a bu'u ca'u du'a fa'a ga'u ne'a ne'i ne'u ni'a
      pa'o re'o ri'u ru'u te'e ti'a to'o vu'a ze'o zo'a zo'i zu'a )] ,
   FAhO =>  [qw( fa'o )] ,
   FEhE =>  [qw( fe'e )] ,
   FEhU =>  [qw( fe'u )] ,
   FIhO =>  [qw( fi'o )] ,
   FOI =>  [qw( foi )] ,
   FUhA =>  [qw( fu'a )] ,
   FUhE =>  [qw( fu'e )] ,
   FUhO =>  [qw( fu'o )] ,
   GA =>  [qw( ga ge ge'i go gu )] ,
   GAhO =>  [qw( ga'o ke'i )] ,
   GEhU =>  [qw( ge'u )] ,
   GI =>  [qw( gi )] ,
   GIhA =>  [qw( gi'a gi'e gi'i gi'o gi'u )] ,
   GOhA =>  [qw( bu'a bu'e bu'i co'e du go'a go'e go'i go'o go'u mo nei no'a )] ,
   GOI =>  [qw( goi ne no'u pe po po'e po'u )] ,
   GUhA =>  [qw( gu'a gu'e gu'i gu'o gu'u )] ,
   I =>  [qw( i )] ,
   JA =>  [qw( ja je je'i jo ju )] ,
   JAI =>  [qw( jai )] ,
   JOhI =>  [qw( jo'i )] ,
   JOI =>  [qw( ce ce'o fa'u jo'e jo'u joi ju'e ku'a pi'u )] ,
   KE =>  [qw( ke )] ,
   KEhE =>  [qw( ke'e )] ,
   KEI =>  [qw( kei )] ,
   KI =>  [qw( ki )] ,
   KOhA =>  [qw( ce'u da da'e da'u de de'e de'u dei di di'e di'u do
      do'i do'o fo'a fo'e fo'i fo'o fo'u ke'a ko ko'a ko'e ko'i ko'o
      ko'u ma ma'a mi mi'a mi'o ra ri ru ta ti tu vo'a
      vo'e vo'i vo'o vo'u zi'o zo'e zu'i xai)] ,
   KU =>  [qw( ku )] ,
   KUhE =>  [qw( ku'e )] ,
   KUhO =>  [qw( ku'o )] ,
   LA =>  [qw( la la'i lai )] ,
   LAhE =>  [qw( la'e lu'a lu'e lu'i lu'o tu'a vu'i )] ,
   LAU =>  [qw( ce'a lau tau zai )] ,
   LE =>  [qw( le le'e le'i lei lo lo'e lo'i loi xo'e)] ,
   LEhU =>  [qw( le'u )] ,
   LI =>  [qw( li me'o )] ,
   LIhU =>  [qw( li'u )] ,
   LOhO =>  [qw( lo'o )] ,
   LOhU =>  [qw( lo'u )] ,
   LU =>  [qw( lu )] ,
   LUhU =>  [qw( lu'u )] ,
   MAhO =>  [qw( ma'o )] ,
   MAI =>  [qw( mai mo'o )] ,
   ME =>  [qw( me )] ,
   MEhU =>  [qw( me'u )] ,
   MOhE =>  [qw( mo'e )] ,
   MOhI =>  [qw( mo'i )] ,
   MOI =>  [qw( cu'o mei moi si'e va'e )] ,
   NA =>  [qw( ja'a na )] ,
   NAhE =>  [qw( je'a na'e no'e to'e )] ,
   NAhU =>  [qw( na'u )] ,
   NAI =>  [qw( nai ja'ai)] ,
   NIhE =>  [qw( ni'e )] ,
   NIhO =>  [qw( ni'o no'i )] ,
   NOI =>  [qw( noi poi voi )] ,
   NU =>  [qw( du'u jei ka li'i mu'e ni nu pu'u si'o su'u za'i zu'o )] ,
   NUhA =>  [qw( nu'a )] ,
   NUhI =>  [qw( nu'i )] ,
   NUhU =>  [qw( nu'u )] ,
   PA =>  [qw( bi ce'i ci ci'i da'a dau du'e fei fi'u gai jau ji'i
       ka'o ki'o ma'u me'i mo'a mu ni'u no no'o pa pai pi pi'e ra'e
       rau re rei ro so so'a so'e so'i so'o so'u su'e su'o
       te'o tu'o vai vo xa xo za'u ze xei)] ,
   PEhE =>  [qw( pe'e )] ,
   PEhO =>  [qw( pe'o )] ,
   PU =>  [qw( ba ca pu )] ,
   RAhO =>  [qw( ra'o )] ,
   ROI =>  [qw( re'u roi ba'oi mu'ei)] ,
   SA =>  [qw( sa )] ,
   SE =>  [qw( se te ve xe )] ,
   SEhU =>  [qw( se'u )] ,
   SEI =>  [qw( sei ti'o )] ,
   SI =>  [qw( si )] ,
   SOI =>  [qw( soi )] ,
   SU =>  [qw( su )] ,
   TAhE =>  [qw( di'i na'o ru'i ta'e )] ,
   TEhU =>  [qw( te'u )] ,
   TEI =>  [qw( tei )] ,
   TO =>  [qw( to to'i )] ,
   TOI =>  [qw( toi )] ,
   TUhE =>  [qw( tu'e )] ,
   TUhU =>  [qw( tu'u )] ,
   UI =>  [qw( a'a a'e a'i a'o a'u ai au ba'a ba'u be'u bi'u bu'o ca'e
      da'i dai do'a e'a e'e e'i e'o e'u ei fu'i ga'i ge'e i'a i'e i'i
      i'o i'u ia ie ii io iu ja'o je'u ji'a jo'a ju'a ju'o ka'u kau
      ke'u ki'a ku'i la'a le'o li'a li'o mi'u mu'a na'i o'a o'e o'i
      o'o o'u oi pa'e pau pe'a pe'i po'o ra'u re'e ri'e ro'a ro'e ro'i
      ro'o ro'u ru'a sa'a sa'e sa'u se'a se'i se'o si'a su'a ta'o ta'u
      ti'e to'u u'a u'e u'i u'o u'u ua ue ui uo
      uu va'i vu'e xu za'a zo'o zu'u )] ,
   VA =>  [qw( va vi vu )] ,
   VAU =>  [qw( vau )] ,
   VEhA =>  [qw( ve'a ve'e ve'i ve'u )] ,
   VEhO =>  [qw( ve'o )] ,
   VEI =>  [qw( vei )] ,
   VIhA =>  [qw( vi'a vi'e vi'i vi'u )] ,
   VUhO =>  [qw( vu'o )] ,
   VUhU =>  [qw( cu'a de'o fa'i fe'a fe'i fu'u ge'a gei ju'u ne'o pa'i
      pi'a pi'i re'a ri'o sa'i sa'o si'i su'i te'a va'a vu'u )] ,
   XI =>  [qw( xi )] ,
   Y =>  [qw( y )] ,
   ZAhO =>  [qw( ba'o ca'o co'a co'i co'u de'a di'a mo'u pu'o za'o )] ,
   ZEhA =>  [qw( ze'a ze'e ze'i ze'u )] ,
   ZEI =>  [qw( zei )] ,
   ZI =>  [qw( za zi zu )] ,
   ZIhE =>  [qw( zi'e )] ,
   ZO =>  [qw( zo )] ,
   ZOhU =>  [qw( zo'u )] ,
   ZOI =>  [qw( la'o zoi )] ,
   ZOhOI => [qw(la'oi zo'oi)],
   MEhOI => [q(me'oi)], FUhEI => [q(fu'ei)], FUhOI => [q(fu'oi)],
   LOhAI => [q(lo'ai)], SAhAI => [q(sa'ai)], LEhAI => [q(le'ai)],
   ZEhEI => [q(ze'ei)]
 ) ;

for my $skey (keys %SM_LIST) {
  $SM{$skey} = make_cmavo_pat($SM_LIST{$skey}); }


$SM{BRIVLA}=$BRIVLA;
$SM{CMENE}=$CMENE;
$SM{CMAVO}=$CMAVO;
$SM{ANYTHING}=$NOT_WS;

#TODO these tests should be more comprehensive and be moved elsewhere
#TODO so that they aren't run all the time and take up space here
#TODO but they do seem to run quickly
#TODO also could use Carp qw(confess);
sub test_regex_foundation0 () {
  'stinv' =~ $CMENE or die;
  'gis,mu' =~ $CYC or die;
  'gis,mu' =~ $CYC5 or die;
  'gis,mu' =~ $CC5 or die;
  'broda' =~ $CC5 or die;
  q{vi'etri'o} =~ $CC5 or die;
  q{mamypatfu} =~ $CYC5 or die;
  'gis,mu' =~ $GISMU or die;
  'broda' =~ $GISMU or die;
  q{bralo'i} =~ $LUJVO or die;
  q{soirsai} =~ $LUJVO or die;
  q{mamtypatfu} =~ $LUJVO or die;
  q{patyta'a} =~ $LUJVO or die;
  q{ro'inre'o} =~ $LUJVO or die;
  q{bang,r,blgaria} =~ $CMENE and die;
  q{bang,r,blgaria} =~ $BRIVLA or die;
  q{bang,r,blgaria} =~ $FUH3 or die;
  q{bang,r,blgaria} =~ $WEAK_GOOD or die;
  q{bang,r,blgaria} =~ $WEAK_BAD and die;
  q{bang,r,blgaria} =~ $GOOD and die;
  q{bang,r,blgaria} =~ $STRONG_BAD and die;
  q{bang,r,blgaria} =~ $FUH4 and die; # blg is illegal consonant cluster
  q{blg} =~ $BAD_TRI or die;
  q{cidj,r,spageti} =~ $FUH3 or die;
  q{cidj,r,spageti} =~ $FUH4 or die;
  q{sypyboi} =~ $CM_SIMPLE or die;
  q{sypyboi} =~ $CM_CYBOI or die;
  q{sypyboi} =~ /^ $CM_CYBOI $ /ix or die;
  q{ybu} =~ $CM_YBU or die;
  q{ybu} =~ $CM_SIMPLE or die;
  q{y'ybu} =~ $CM_SIMPLE or die;
  q{y'ybu} =~ $CM_YHYBU or die;
  q{eparele} =~ $CM_SIMPLE or die;
  q{eparele} =~ $CM_0 or die;
  #q{la'o} =~ $SM_ZOI or die;
  #q{la'} =~ $SM_ZOI and die;
  q{la'orbangu} =~ $CM_BAD or die;
  q{la'orbangu} =~ $LUJVO or die;
  #q{la'orbangu} =~ $SM_ZOI and die;
  #q{la'orbangu} =~ $SM{ZOI} and die;
  #q{la'oi} =~ $SM_ZOI and die;
  q{ge'uzdani} =~ $LUJVO and die;
  q{ge'urzdani} =~ $LUJVO or die;
  q{slinku'i} =~ $FUH3 and die;
  #my $test_zoi1 = qq{$SM_ZOI};
  #say ref($SM_ZOI), q{ --  }, ref($test_zoi1), q{ -- };
  return;
}

sub classify_valsi {
  my ($word) =@_;
  my $classed=q{};
  my $btype=0;
  if ($word eq q{}) {return 'x';}
  if ($word =~ $WEAK_BAD || $word !~ $WEAK_GOOD) { return 'XXX'; }
  if ($word =~ $CMENE ) { return 'N'; }
  if ($word =~ $STRONG_BAD || $word !~ $GOOD) { return 'XXX'; }
  if ($word =~ $BRIVLA) {
    if ($word =~ $GISMU) { return 'BG'; }
    if ($word =~ $LUJVO) { return 'BL'; }
    if ($word =~ $FUH4) { return 'BF'; }
  }
  if ($word  =~ $CM_SIMPLE) {return 'c';}
  return 'U';
}

#FIXME TODO STUB
sub fix_word {
  my ($word) =@_;
  return q{.. ..} . $word . q{.. ..};
}
#FIXME TODO STUB


1;

__END__

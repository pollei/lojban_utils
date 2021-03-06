#! /usr/bin/perl
package Lojban::Valsi;
use 5.010;
use strict;
use utf8;
use warnings;

use Exporter 'import';
our @EXPORT_OK = qw(
    $STRESS $NO_STRESS $RELAX $PSTRESS $GOOD $WEAK_GOOD $WEAK_BAD $STRONG_BAD
    $GOB %SM %SM_LIST $SYLL $WEAK_SYLL $CMENE $BRIVLA $BRIVLA_ $BRIVLAS
    $GISMU $CMAVO
    $CM_SIMPLE $LUJVO $FUH3 $FUH4 $CM_0 $GISMU_ $LUJVO_ $BAD_CC $BAD_CCC $CCC
    $C $V $L $H $Y $X $YC $WS $WSS $RAW_NUM classify_valsi vlalei
    fix_word fix_white fix_num );
our %EXPORT_TAGS = ( ALL => [@EXPORT_OK] );

our $VERSION = 0.000_007;

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


our $WS =qr/ [\.\s[:punct:]] /ix;
our $WSS =qr/ [\s[:punct:]]* [\.\s]+ [\s[:punct:]]* /ix;
our $NOT_WS =qr/ [^\s.]+ /;
our $C =qr/[bcdfgjklmnprstvxz],?/ix;
our $V =qr/[aeiou],?/ix;

#relaxed and stressed vowels; case sensitive is important !!
our $VR =qr/[aeiou],?/x;
our $VS =qr/[AEIOU],?/x;

our $VY =qr/[aeiouy],?/ix;
our $VH =qr/[aeiouh'],?/ix;
our $NOVH =qr/(?! ,* [aeiouh']) /ix;
our $VHY =qr/[aeiouyh'],?/ix;
our $NOVHY =qr/(?! ,* [aeiouyh']) /ix;
our $H =qr/[h'],?/ix;
our $VHH =qr/$VH $H?/ix;
our $VV = qr/ $V $H $V | a,?i,? | a,?u,? | e,?i,? | o,?i,? /ix;
our $Y =qr/y,?/ix;
our $L =qr/$C|$VHY/ix;
our $YC =qr/$C|$Y/ix;
our $BAD_W = make_list_pat( qw(h q w));
our $X =qr/$L|$BAD_W/ix;
our $NOX =qr/(?! ,* [[:alpha:]\'] )/ix;
our $M =qr/ [lmnr] \,? /ix;
our $YM =qr/ [lmnry] \,? /ix;
our $BAD_CX = make_list_pat( qw(cx kx xc xk mz));
our $BAD_CCC = make_list_pat( qw(ndj ndz ntc nts));
our $BAD_VV = make_list_pat( qw(aa ae ao ea ee eo eu oa oe ou iy uy));
our $BAD_DD = make_list_pat (
         qw(bb cc dd ff gg jj kk ll mm nn pp qq rr ss tt vv ww xx zz));
our $VOICED = qr/[bdgjvz] ,? /ix;
our $UNVOICED = qr/[cfkpstx] ,? /ix;
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
# http://hrwiki.org/wiki/Strong_Bad ;-)


#our $CMENE = qr/$C [.]* $ /ix;
our $CMENE_ = qr/ $X* $C (?! $X) /ix;
our $CMENE = qr/ ^ $WSS* $CMENE_ $WSS* $ /ix;
our $L3_LAX =qr/(?: $L \'?){0,3}/ix;
our $L3=qr/(?: $V $H? | $C (?= $V) ){0,3}/ix;
our $V3=qr/(?: $V $H? ){0,3}/ix;
#our $VY3=qr/(?: $VY $H? ){0,3}/ix;
our $C3=qr/$VHH $C $VHH | $C $VHH $V? /ix;
our $CYC = qr/$C $Y? $C/ix;
our $PCC = qr/$C $C/ix;
our $ICC = make_list_pat ( qw ( bl br cf ck cl cm cn cp cr ct dj dr dz
             fl fr gl gr jb jd jg jm jv kl kr ml mr pl pr sf sk sl sm
             sn sp sr st tc tr ts vl vr xl xr zb zd zg zm zv));
# "tc" | "ts" | "dj" | "dz" | /[cjzs][pkfxbgvmtdnlr]/ | /[pkfxbgvmtdn][lr]/
# /[pbcsmfvkgx][lr]|[td]r|[cs][pftkmn]|[jz][bvdgm]|t[cs]|d[jz]/
# for icc this also matches some illegal combos
# should icc be looser to ignore some errors ??
our $CYC5 = qr/^ [.]* $L3 $CYC ${C}* $VY /ix;
our $CC5 = qr/^ [.]* $L3 $PCC ${C}* $V /ix;
#our $CC5 =  qr/^ [.]* (?: $C3 $PCC| $V3 $ICC) ${C}* $V   /ix;
#our $CYC5 = qr/^ [.]* (?: $C3 $CYC| $V3 $ICC) ${C}* $VY  /ix;
our $GISM_ = qr/ $C$V$C$C | $ICC$V$C /ix;
our $GISMU_ = qr/ $C$V$C$C$V | $ICC$V$C$V /ix;
our $GISMU = qr/ ^ [.]* $GISMU_ [.]* $ /ix;
#our $GISMU_ = qr/ $C$V$ICC$V | $ICC$V$C$V /ix;
#FIXME AUDIT should gismu pattern be tighter ?? AUDIT

our $R_HYPH =qr/ [rn] \,? (?= $C ) /ix;
our $L_HYPH =qr/ [rnl] \,? (?= $C ) /ix;
our $Y_HYPH =qr/ y  \,? (?= $C ) /ix;
our $M_HYPH =qr/ [lmnr] \,? (?= $C ) /ix;

our $B_C3 = qr/ $C3 $CYC $L* $V (?! $VHY) /ix;
our $B_V3 = qr/ $VHH{1,3} $PCC $L* $V (?! $VHY) | $ICC $C* $VH+ $YC+ $L* $V (?! $VHY) /ix;
our $B_F = qr/ $C* $ICC $C* $VH{3,} (?! $VHY) /x;
#our $B_V3 = qr/ $VHH{1,3} $PCC $L* $V (?! $VHY) | $ICC $C* $VH+ $YC+ $L* $V (?! $VHY) /ix;
#our $B_F = qr/ $C* $PCC $C* $VH{3,} (?! $VHY) /x;
our $BRIVLA_ = qr/ $B_C3 | $B_V3 | $B_F /ix;

#our $R_CVV =qr/$C$V$H$V|$C a,?i,?| $C e,?i.?| $C o,?i,? | $C a,?u,? /ix;
our $R_CVV =qr/ $C $VV /ix;
our $R_CVVR =qr/ $R_CVV $R_HYPH /ix;
our $R_CVC = qr/ $C$V$C /ix;
our $RAFC =qr/$C$V$C$C|$ICC$V$C|$C$V$C /ix;
our $RAFV =qr/$ICC$V|$R_CVV/ix;
our $RAFCY =qr/$C$V$C$C$Y_HYPH|$ICC$V$C$Y_HYPH|$C$V$C /ix;
our $RAF = qr/$RAFCY$Y_HYPH?|$ICC$V|$R_CVV/ix;
# tosmabru FIXME AUDIT tosmabru regex *IS* wrong
# #tosmabru if ($word =~ /^ [.]* $C $V ($L{4,}) [.]* $ /x ) { if (xu_brivla($1)) { return 0;} }
# http://www.lojban.org/tiki/tosmabru+test
# http://www.lojban.org/publications/reference_grammar/chapter4.html#s11
our $TOSMABRU = qr/ (?= $R_CVC+ $GISMU_ ) $C $V $BRIVLA_ /ix;
#our $TOSMABRU = qr/ $C $V $BRIVLA_ /ix;
# tosmabru FIXME AUDIT tosmabru regex *IS* wrong
our $LUJVO_ =qr/(?!$TOSMABRU)(?: $RAF | $R_CVVR) $RAF* (?: $RAF | $GISMU_) /ix;
our $LUJVO = qr/ ^ [.]* $LUJVO_ [.]* $ /ix;
#FIXME AUDIT is this lujvo regex really correct and sufficient? FIXME

our $CCC =qr/ $C | $C$C | $C? $ICC+ /ix;
our $CCCYM =qr/ $YM* $CCC $YM*  | $YM+ /ix;
#our $SYLL =qr/ $M_HYPH? $CCC? $VHY+ $CCC? $M_HYPH? /ix;
our $SYLL =qr/ $CCCYM? (?: $VHY+ | $YM+) $CCCYM? /ix;
#our $WEAK_SYLL =qr/ $M_HYPH? $C* $VHY+ $C* $M_HYPH? | $YM /ix;
our $WEAK_SYLL =qr/ $YC* (?: $VHY+ | $YM+)  $YC* /ix;
#our $SYLL_NOY =qr/ $M_HYPH? $CCC? $VH* $V $CCC? $M_HYPH? | $VHH+ $V /ix;
our $SYLL_NOY =qr/ $M_HYPH? $CCC? $VH* $V $CCC? $M_HYPH? /ix;
our $SYLL_BTAIL =qr/ $M_HYPH? (?: $CCC | $VH+) $VH* $V (?! $VHY) /ix;
#our $GOB =qr/ $M_HYPH? $C* (?: $VHY | $BAD_W)+ $C* $M_HYPH? | $YM /ix;
our $GOB =qr/ $YC* (?: $VHY+ | $YM+ | $BAD_W+)  $YC* /ix;

our $GOOD =qr/ ^ $WSS* $SYLL+ $WSS* $ /ix;
our $WEAK_GOOD =qr/ ^ $WSS* $WEAK_SYLL+ $WSS* $ /ix;

#FIXME 
# slinku'i
  # not combo of cmavo and gismu and/or lujvu
  #if ($word =~ / ^ [.]* (?: $C?$V$H?$V?){1,6} (?: $GISMU_ | $LUJVO_) [.]* $ /ix)
  # slinku'i paslinku'i
  #if (('pa' . $word) =~ $LUJVO ) { return 0; }
our $FUH_NOCOMBO = qr/(?: $C?$V$H?$V?){1,6} (?: $GISMU_ | $LUJVO_) $NOX /ix;
#our $FUH_NOCOMBO = qr/$C (?: $V$H?$V?){1,6} (?: $GISMU_ | $LUJVO_)/ix;
#our $SLI_RAF = qr/ [iu] \,? $R_HYPH? | $R_HYPH | $C (?:$C$Y) /ix;
our $SLI_RAF = qr/ $C (?:$C$Y) /ix;
our $SLINKUHI = qr/ $SLI_RAF $RAF* (?: $RAFV | $GISMU_) $NOX /ix;
our $BAD_FUH =qr/ $SLINKUHI | $FUH_NOCOMBO /ix;
our $FUH3_ =qr/ (?! $BAD_FUH) $RAFC $L_HYPH $C (?: $C | $VH)* $V (?! $VHY ) /ix;
our $FUH3  =qr/ ^ $WSS* $FUH3_ $WSS* $ /ix;
#our $FUH4_ =qr/ (?: $C | $VH){3,} $VH (?! $VHY ) /ix;
our $FUH4_ =qr/ (?! $BAD_FUH) $SYLL_NOY+ $SYLL_BTAIL /ix;
#our $FUH4_ =qr/ $SYLL_NOY+ $SYLL_BTAIL /ix;
our $FUH4  =qr/ ^ $WSS* $FUH4_ $WSS* $ /ix;

our $BRIVLA = qr/ ^ [.]* $BRIVLA_ [.]* $ /ix;
#TODO AUDIT this brivla pattern is a bit tricky AUDIT
our $BRIVLAS =qr/ (?= $BRIVLA_) (?: $GISMU_ | $LUJVO_ | $FUH4_) /ix;

# stress is very case sensitive
our $NO_STRESS = qr/ [^AEIOU]+ /x;
#TODO FIXME stress shouldn't extend over h' or ,
our $STRESS = qr/ [^AEIOU]+ [AEIOU]+ $V{0,2} /x;
our $RELAX = qr/ [hH',]? $YC* [aeiou]{1,2} [,]? (?! $H ) /x;
our $PSTRESS = qr/ $STRESS $RELAX /x;
#TODO FIXME stress shouldn't extend over h'

#our $CM_OK = qr/  $WSS* (?! $BRIVLAS | $CMENE_ ) /ix;
our $CM_BAD = qr/  $WSS* (?= $BRIVLAS | $CMENE_ ) /ix;
our $CM_V = qr/ $V | a,?i,? | a,?u,? | e,?i,? | o,?i,? /ix;
our $CM_0 = qr/ (?! $CM_BAD) $C? $VH* $V (?! $VH ) /ix;
our $CM_1 =qr/ (?! $CM_BAD) (?: [iu],? $V | $C? $CM_V (?: $H $CM_V){0,2} ) /ix;
our $CM_2 =qr/ (?! $CM_BAD)  $C? $V $H? $V? (?! $VH) /ix;
our $CM_Y =qr/ (?! $CM_BAD)$Y+ (?! $VHY) /ix;
# TODO FIXME bu and other concrete cmavo need to go through make_cmavo_pat
#our $CM_YBU =qr/ $CM_Y (?:(?! $CM_BAD)bu)? (?! $VHY) /ix;
our $CM_YBU =qr/ (?: $CM_2? $CM_Y | $CM_Y $CM_2? ) (?! $VHY) /ix;
#our $CM_CY =qr/ (?=$CM_OK) (?:(?: $C$Y)+) (?! $VHY) /ix;
our $CM_CY =qr/ (?! $CM_BAD ) (?: $C$Y) (?! $VHY) /ix;
our $CM_CYBOI =qr/ $CM_CY+ (?:(?!$CM_BAD)boi)? (?! $VHY) /ix;
our $CM_YHY = qr/ (?! $CM_BAD) y'y (?! $VHY) /ix;
our $CM_YHYBU =qr/ $CM_YHY (?:(?! $CM_BAD)bu)? (?! $VHY) /ix;
our $CM_SIMPLE =qr/  $WSS* (?: $CM_1+ (?! $VHY) | $CM_YBU | $CM_CYBOI | $CM_YHYBU ) $WSS*  /ix;
our $CMAVO =qr/  $WSS* (?: $CM_0 | $CM_Y | $CM_CY | $CM_YHY ) $WSS*  /ix;
our $CMAVO_1 =qr/  $WSS* (?: $CM_1 | $CM_Y | $CM_CY | $CM_YHY ) $WSS*  /ix;

our $RAW_DIGITS = qr/ [\d_,]* \d [\d_,]* /x;
our $RAW_NUM = qr/  [+-]? $RAW_DIGITS (?: [.] $RAW_DIGITS)? /x;

sub make_cmavo_pat {
  my @li = map (cmavo_escape($_)   , @_ ) ;
  my $pat= join(q{|},@li) ;
  #say $pat;
  my $ret= qr/ (?! $CM_BAD) (?: $pat ) (?! $VH) /ix;
  #print $ret, "\n\n";
  # in trying to debug this thing I noticed that printing out
  # the pattern this thing creates is just plain huge and ugly
  # over 10_000 chars long
  return $ret;
}


# http://www.lojban.org/publications/wordlists/cmavo.txt
# http://jbovlaste.lojban.org/dict/listing.html?type=experimental%20cmavo
# http://www.lojban.org/tiki/Experimental+cmavo
# pattern match on selma'o 
# should have all of the normal cmavo and most of the experimental
our   @UI0 =  qw( a'a a'e a'i a'o a'u ai au ba'a ba'u be'u bi'u bu'o ca'e
      da'i dai do'a e'a e'e e'i e'o e'u ei fu'i ga'i ge'e i'a i'e i'i
      i'o i'u ja'o je'u ji'a jo'a ju'a ju'o ka'u kau
      ke'u ki'a ku'i la'a le'o li'a li'o mi'u mu'a na'i o'a o'e o'i
      o'o o'u oi pa'e pau pe'a pe'i po'o ra'u re'e ri'e ro'a ro'e ro'i
      ro'o ro'u ru'a sa'a sa'e sa'u se'a se'i se'o si'a su'a ta'o ta'u
      ti'e to'u u'a u'e u'i u'o u'u va'i vu'e xu za'a
      zo'o zu'u a'a'a a'o'e bu'a'a fu'au li'oi sei'u xo'o ) ;
our @UI1 = qw(ia ie ii io iu ua ue ui uo uu );
# these ui are separated out for special treatment
our %SM;
our %SM_LIST= ( 
   A =>  [qw( a e ji o u )] ,
   BAhE =>  [qw( ba'e za'e ba'ei )] ,
   BAI =>  [qw( ba'i bai bau be'i ca'i cau ci'e ci'o ci'u cu'u de'i di'o
      do'e du'i du'o fa'e fau fi'e ga'a gau ja'e ja'i ji'e ji'o ji'u ka'a
      ka'i kai ki'i ki'u koi ku'u la'u le'a li'e ma'e ma'i mau me'a me'e
      mu'i mu'u ni'i pa'a pa'u pi'o po'i pu'a pu'e ra'a ra'i rai ri'a
      ri'i sau si'u ta'i tai ti'i ti'u tu'i va'o va'u zau zu'e va'ai )] ,
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
   CAhA =>  [qw( ca'a ka'e nu'o pu'i bi'ai ca'ai ka'ei nau'a nu'oi)] ,
   CAI =>  [qw( cai cu'i pei ru'e sai dau'i mau'i me'ai )] ,
   CEhE =>  [qw( ce'e )] ,
   CEI =>  [qw( cei )] ,
   CO =>  [qw( co )] ,
   COI =>  [qw( be'e co'o coi fe'o fi'i je'e ju'i
      ke'o ki'e mi'e mu'o nu'e pe'u re'i ta'a vi'o ki'ai sa'ei di'ai )] ,
   CU =>  [qw( cu )] ,
   CUhE =>  [qw( cu'e nau )] ,
   DAhO =>  [qw( da'o )] ,
   DOhU =>  [qw( do'u )] ,
   DOI =>  [qw( doi da'oi)] ,
   FA =>  [qw( fa fai fe fi fi'a fo fu foi'a foi'e foi'e foi'o foi'u )] ,
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
   GOhA =>  [qw( bu'a bu'e bu'i co'e du go'a go'e go'i
                 go'o go'u mo nei no'a nei'i no'au )] ,
   GOI =>  [qw( goi ne no'u pe po po'e po'u goi'a xe'e )] ,
   GUhA =>  [qw( gu'a gu'e gu'i gu'o gu'u )] ,
   I =>  [qw( i oi'a )] ,
   JA =>  [qw( ja je je'i jo ju )] ,
   JAI =>  [qw( jai )] ,
   JOhI =>  [qw( jo'i )] ,
   JOI =>  [qw( ce ce'o fa'u jo'e jo'u joi ju'e ku'a pi'u )] ,
   KE =>  [qw( ke )] ,
   KEhE =>  [qw( ke'e )] ,
   KEI =>  [qw( kei boi'a boi'e boi'i boi'o boi'u )] ,
   KI =>  [qw( ki )] ,
   KOhA =>  [qw( ce'u da da'e da'u de de'e de'u dei di di'e di'u do
      do'i do'o fo'a fo'e fo'i fo'o fo'u ke'a ko ko'a ko'e ko'i ko'o
      ko'u ma ma'a mi mi'a mi'o ra ri ru ta ti tu vo'a
      vo'e vo'i vo'o vo'u zi'o zo'e zu'i xai zi'oi ru'ai
      foi'a foi'e foi'i foi'o foi'u koi'a koi'e koi'i koi'o koi'u )] ,
   KU =>  [qw( ku kei'a kei'e kei'i kei'o kei'u
               fei'a fei'e fei'i fei'o fei'u)] ,
   KUhE =>  [qw( ku'e )] ,
   KUhO =>  [qw( ku'o )] ,
   LA =>  [qw( la la'i lai da'ai ko'ai la'ei )] ,
   LAhE =>  [qw( la'e lu'a lu'e lu'i lu'o tu'a vu'i xa'e zo'ei )] ,
   LAU =>  [qw( ce'a lau tau zai )] ,
   LE =>  [qw( le le'e le'i lei lo lo'e lo'i loi
               xo'e lau'a lau'e lau'i lau'o le'ei lei'e lo'ei loi'e )] ,
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
   NA =>  [qw( ja'a na da'au jai'a nai'a )] ,
   NAhE =>  [qw( je'a na'e no'e to'e )] ,
   NAhU =>  [qw( na'u )] ,
   NAI =>  [qw( nai ja'ai)] ,
   NIhE =>  [qw( ni'e )] ,
   NIhO =>  [qw( ni'o no'i )] ,
   NOI =>  [qw( noi poi voi noi'a poi'a voi'a )] ,
   NU =>  [qw( du'u jei ka li'i mu'e ni nu
               pu'u si'o su'u za'i zu'o dau'au du'au kai'a poi'i)] ,
   NUhA =>  [qw( nu'a )] ,
   NUhI =>  [qw( nu'i )] ,
   NUhU =>  [qw( nu'u )] ,
   PA =>  [qw( bi ce'i ci ci'i da'a dau du'e fei fi'u gai jau ji'i
       ka'o ki'o ma'u me'i mo'a mu ni'u no no'o pa pai pi pi'e ra'e
       rau re rei ro so so'a so'e so'i so'o so'u su'e su'o
       te'o tu'o vai vo xa xo za'u ze xei zei'a )] ,
   PEhE =>  [qw( pe'e )] ,
   PEhO =>  [qw( pe'o )] ,
   PU =>  [qw( ba ca pu xoi'a xoi'e )] ,
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
   UI =>  [ @UI0, @UI1] ,
   VA =>  [qw( va vi vu )] ,
   VAU =>  [qw( vau vau'a vau'e vau'i vau'o vau'u)] ,
   VEhA =>  [qw( ve'a ve'e ve'i ve'u )] ,
   VEhO =>  [qw( ve'o )] ,
   VEI =>  [qw( vei )] ,
   VIhA =>  [qw( vi'a vi'e vi'i vi'u )] ,
   VUhO =>  [qw( vu'o )] ,
   VUhU =>  [qw( cu'a de'o fa'i fe'a fe'i fu'u ge'a gei ju'u ne'o pa'i
      pi'a pi'i re'a ri'o sa'i sa'o si'i su'i te'a va'a vu'u )] ,
   XI =>  [qw( xi )] ,
   Y =>  [qw( y )] ,
   ZAhO =>  [qw( ba'o ca'o co'a co'i co'u de'a di'a mo'u pu'o za'o xa'o )] ,
   ZEhA =>  [qw( ze'a ze'e ze'i ze'u ze'ai)] ,
   ZEI =>  [qw( zei )] ,
   ZI =>  [qw( za zi zu za'ai )] ,
   ZIhE =>  [qw( zi'e )] ,
   ZO =>  [qw( zo ma'oi )] ,
   ZOhU =>  [qw( zo'u kau'a kau'e kau'i kau'o kau'u
                 fau'a fau'e fau'i fau'o fau'u)] ,
   ZOI =>  [qw( la'o zoi )] ,
   ZOhOI => [qw(la'oi zo'oi ra'oi )],
   MEhOI => [q(me'oi)], FUhEI => [q(fu'ei)], FUhOI => [q(fu'oi)],
   LOhAI => [q(lo'ai)], SAhAI => [q(sa'ai)], LEhAI => [q(le'ai)]
 ) ;
# me'ei me'au  -- maybe add these as well

for my $skey (keys %SM_LIST) {
  $SM{$skey} = make_cmavo_pat( @{ $SM_LIST{$skey} });
}


$SM{BRIVLA}=$BRIVLA_;
$SM{CMENE}=$CMENE_;
$SM{CMAVO}=$CMAVO;
$SM{ANYTHING}=$NOT_WS;

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

sub vlalei {
  my ($word) =@_;
  my $classed=q{};
  my $btype=0;
  if ($word eq q{}) {return 'Empty';}
  if ($word =~ $WEAK_BAD || $word !~ $WEAK_GOOD) { return 'Ugly'; }
  if ($word =~ $CMENE ) { return 'cmene'; }
  if ($word =~ $STRONG_BAD || $word !~ $GOOD) { return 'Bad'; }
  if ($word =~ $BRIVLA) {
    if ($word =~ $GISMU) { return 'gismu'; }
    if ($word =~ $LUJVO) { return 'lujvo'; }
    if ($word =~ $FUH4) { return 'fuhivla'; }
  }
  if ($word  =~ / ^ $CMAVO $ /) {return 'cmavo';}
  if ($word  =~ /^ $CM_SIMPLE $ / ) {return 'Cmavo Compound';}
  return 'Unknown';
}

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
  q{soirsai} =~ $BRIVLA or die;
  q{soirsai} =~ $LUJVO or die;
  q{mamtypatfu} =~ $LUJVO or die;
  q{patyta'a} =~ $LUJVO or die;
  q{ro'inre'o} =~ $LUJVO or die;
  q{bang,r,blgaria} =~ $CMENE and die;
  q{bang,r,blgaria} =~ $BRIVLA or die;
  q{bang,r,blgaria} =~ $FUH3 or die;
  q{bang,r,blgaria} =~ $WEAK_GOOD or die;
  q{bang,r,blgaria} =~ $WEAK_BAD and die;
  #q{bang,r,blgaria} =~ $GOOD and die;
  q{bang,r,blgaria} =~ $STRONG_BAD and die;
  #q{bang,r,blgaria} =~ $FUH4 and die; # blg is illegal consonant cluster
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
  q{la'o} =~ $CM_BAD and die;
  q{la'o} =~ $SM{ZOI} or die;
  q{la'} =~ $SM{ZOI} and die;
  q{la'orbangu} =~ $CM_BAD or die;
  q{la'orbangu} =~ $LUJVO or die;
  q{la'orbangu} =~ $SM{ZOI} and die;
  q{la'oi} =~ $SM{ZOI} and die;
  #q{ge'uzdani} =~ $LUJVO and die;
  q{ge'urzdani} =~ $LUJVO or die;
  q{slinku'i} =~ $FUH3 and die;
  q{ui} =~ $SM{UI} or die;
  #my $test_zoi1 = qq{$SM_ZOI};
  #say ref($SM_ZOI), q{ --  }, ref($test_zoi1), q{ -- };

  # http://www.lojban.org/tiki/Exhaustive+list+of+short+fu%27ivla+forms
  # saiaspa was in a list of fu'ivla but I don't count it as such
  my @flist = qw(iglu spa'i spraile
    praia  spra'i  ostoi  astro  uiski 
    ma'agni  saprka  brai'oi  tce'exo  stroia
    astroi asrkoi astrgo iastro  uaisto 
    saispai saispra  sarpaia  sarpasa  sasprai  sarprai sabrpai
    satspra spaiaia spaiapa  spaipsa  spapaia spapapa  spaprka  spraiai
    spraika jglandi
    aspapsa  asrkaia eskrima  asrstai  asrkrai
    asprkai asprkra aitsmla  aisrpai  uaispra uaispai
    cidjrspageti djarspageti tricrxaceru ricrxaceru
    saktrxaceru cirlrbri sincrkobra saskrkuarka
    djinrnintegrale tarmrnintegrale
    tci'ile
    alga iksoia odbenu aksroi iandau
    apsaiai  apsapai  apsaipa apsaspa
     arpraia  apsrkai ainstai airpasa  airpaia tsmla'i  
   tsmlaia  tsmlatu stsmla'u
    );
  for my $fw (@flist) {
    if ($fw !~ $FUH4) {say 'bad fuh ', $fw ,' ', vlalei($fw); die; }
    if ( $fw =~ / ^ ($SLI_RAF) ($RAF*) ($RAFV | $GISMU_) /ix ) {
      say 'bad slinkuhi fuh<',$1,'><',$2,'><',$3,'>'; }
    if ($fw =~ / ^ ($C?$V$H?$V?){1,6} ($GISMU_ | $LUJVO_) /ix) {
      say 'bad combo fuh<',$1,'><',$2,'>'; }
    #if ($fw =~ $SLINKUHI) {say 'bad slinkuhi fuh ', $fw ,' ', vlalei($fw); }
  #our $SLINKUHI = qr/ $SLI_RAF $RAF* (?: $RAF | $GISMU_) $NOX /ix;
  #our $FUH_NOCOMBO = qr/(?: $C?$V$H?$V?){1,6} (?: $GISMU_ | $LUJVO_) $NOX /ix;
    #if ($fw =~ $FUH_NOCOMBO) {say 'bad combo fuh ', $fw ,' ', vlalei($fw); }
    #$fw =~ $FUH4 or die;
    #$fw =~ /^ $BRIVLAS /ix or die;
    #$fw =~ /^ $BRIVLAS $ /ix or die;
    #if ($fw !~ $FUH4) {say 'bad fuh ', $fw ,' ', vlalei($fw); }
    }

  for my $sm_key (keys %SM_LIST) {
    for my $cm ( @{ $SM_LIST{$sm_key} } ) {
      $cm =~ /^ $CMAVO $ /ix or die;
      $cm =~ /^ $CMAVO_1 $ /ix or die;
    }
  }

  return;
}

my %fix_numy = (
    '0' => 'no',
    '1' => 'pa', '2' => 're', '3' => 'ci', '4' => 'vo', '5' => 'mu',
    '6' => 'xa', '7' => 'ze', '8' => 'bi', '9' => 'so',
    q{,} => q{ki'o}, q{_} => q{ki'o}, q{.} => q{pi},
    q{+} => q{ma'u}, q{-} => q{ni'u}
);

sub fix_num {
  my ($word) =@_;
  my $rword=q{ .};
  for my $let (split m//m,$word) {
    $rword .= $fix_numy{$let};
  }
  return $rword . q{. } ;
}

sub fix_white {
  my ($word) =@_;
  $word =~ s/[,']+/./g;
  return $word;
}

sub fix_word {
  my ($word) =@_;
  if ($word =~ / ^ $RAW_NUM $ /x ) {
    return fix_num($word);
  }
  $word =~ s/$H{2,}/'/g;
  $word =~ s/[hH]+/'/g;
  $word =~ s/^[\s,.]+//g;
  $word =~ s/[\s,.]+$//g;
  $word =~ s/[,]{2,}/,/g;
  if ($word =~ / [qw] | ^ $H | $H $C /ix or
      $word !~ / ^ $SYLL+ $ /sx ) {
    $word =~ s/[^[:alpha:],']//g;
    # force it to be a cmene
    if ($word !~ / $C $ /x) {
      $word .= q{r}; }
    $word =~ s/w/uu/ig;
    $word =~ s/q/yky/ig;
    if ($word =~ / ^ $H /x) {
      $word = q{y} . $word;}
    while ($word =~ / ^ ($X $H) ($C .*) $ /x ) {
      $word = $1 . q{y} . $2; }
    while ($word =~ / ^ ($X* (?= $BAD_CC) $C) ($C .* )  $ |
                      ^ ($X* (?= $BAD_CCC) $C $C ) ($C .* ) $ /ix) {
      $word = $1 . q{y} . $2; }
    if ($word !~ / $SYLL $ / ) {
      if ($word =~ / ( $X* $C) ( (?= $CCC) $C $C $C) /ix) {
        $word = $1 . q{y} . $2; }
      elsif ($word =~ / ( $X* $C) ( $C $C ) /ix) {
        $word = $1 . q{y} . $2; }
      elsif ($word =~ / ( $X* $C) ( $C ) /ix) {
        $word = $1 . q{y} . $2; }
    }
    while ($word =~ / ($X*? (?! $SYLL) $C )
                      ( (?= $SYLL) $CCC $X* ) $/x ) {
      $word = $1 . q{y} . $2; }
    #if ( $word =~ / ^ ( (?! $SYLL) $CCC) ( (?= $SYLL) $CCC .* | $CCC ) $ /x) {
    #  $word = $1 . q{y} . $2; }
    if ( $word =~ / ^ (?! $SYLL) $C $ /x) {
      $word = q{y} . $word; }
    return q{.} . $word . q{.};
  }
  return $word ;
}

# join an array of rafsi into a lujvo
sub rafyjongau {
}

#split a lujvo into an array of rafsi
sub jvokatna {
}

1;

__END__

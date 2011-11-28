#! /usr/bin/perl
use 5.010;
use strict;
use utf8;
use warnings;
our $VERSION = 0.000_002;

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
our $CM_YHY = qr / (?! $CM_BAD) y'y (?! $VHY) /ix;
our $CM_YHYBU =qr/ $CM_YHY (?:(?! $CM_BAD)bu)? (?! $VHY) /ix;
our $CM_SIMPLE =qr/ ^ $WS* (?: $CM_0+ | $CM_YBU | $CM_CYBOI | $CM_YHYBU ) $WS* $ /ix;

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

# SI SA SU ZO ZOI LOhU LEhU ZEI BU and FAhO

# in order to deal with a few magic words that have powerful effects
# I added a few things that can pattern match on selma'o 
# maybe this should be more data driven and maybe should be stored in %SM
# $SM{A} vs $SM_A

our $SM_A = make_cmavo_pat( qw( a e ji o u ) );
our $SM_BAhE = make_cmavo_pat( qw( ba'e za'e ) );
our $SM_BAI = make_cmavo_pat( qw( ba'i bai bau be'i ca'i cau ci'e ci'o
  ci'u cu'u de'i di'o do'e du'i du'o fa'e fau fi'e ga'a gau ja'e ja'i
  ji'e ji'o ji'u ka'a ka'i kai ki'i ki'u koi ku'u la'u le'a li'e ma'e
  ma'i mau me'a me'e mu'i mu'u ni'i pa'a pa'u pi'o po'i pu'a pu'e ra'a
  ra'i rai ri'a ri'i sau si'u ta'i tai ti'i ti'u tu'i va'o va'u zau zu'e ) );
our $SM_BE = make_cmavo_pat( qw( be ) );
our $SM_BEhO = make_cmavo_pat( qw( be'o ) );
our $SM_BEI = make_cmavo_pat( qw( bei ) );
our $SM_BIhE = make_cmavo_pat( qw( bi'e ) );
our $SM_BIhI = make_cmavo_pat( qw( bi'i bi'o mi'i ) );
our $SM_BO = make_cmavo_pat( qw( bo ) );
our $SM_BOI = make_cmavo_pat( qw( boi ) );
our $SM_BU = make_cmavo_pat( qw( bu ) );
our $SM_BY = make_cmavo_pat( qw( by cy dy fy ga'e ge'o gy je'o jo'o jy
   ky lo'a ly my na'a ny py ru'o ry se'e sy to'a ty vy xy y'y zy ) );
our $SM_CAhA = make_cmavo_pat( qw( ca'a ka'e nu'o pu'i ) );
our $SM_CAI = make_cmavo_pat( qw( cai cu'i pei ru'e sai ) );
our $SM_CEhE = make_cmavo_pat( qw( ce'e ) );
our $SM_CEI = make_cmavo_pat( qw( cei ) );
our $SM_CO = make_cmavo_pat( qw( co ) );
our $SM_COI = make_cmavo_pat( qw( be'e co'o coi fe'o fi'i je'e
  ju'i ke'o ki'e mi'e mu'o nu'e pe'u re'i ta'a vi'o ) );
our $SM_CU = make_cmavo_pat( qw( cu ) );
our $SM_CUhE = make_cmavo_pat( qw( cu'e nau ) );
our $SM_DAhO = make_cmavo_pat( qw( da'o ) );
our $SM_DOhU = make_cmavo_pat( qw( do'u ) );
our $SM_DOI = make_cmavo_pat( qw( doi ) );
our $SM_FA = make_cmavo_pat( qw( fa fai fe fi fi'a fo fu ) );
our $SM_FAhA = make_cmavo_pat( qw( be'a bu'u ca'u du'a fa'a ga'u ne'a ne'i
  ne'u ni'a pa'o re'o ri'u ru'u te'e ti'a to'o vu'a ze'o zo'a zo'i zu'a ) );
our $SM_FAhO = make_cmavo_pat( qw( fa'o ) );
our $SM_FEhE = make_cmavo_pat( qw( fe'e ) );
our $SM_FEhU = make_cmavo_pat( qw( fe'u ) );
our $SM_FIhO = make_cmavo_pat( qw( fi'o ) );
our $SM_FOI = make_cmavo_pat( qw( foi ) );
our $SM_FUhA = make_cmavo_pat( qw( fu'a ) );
our $SM_FUhE = make_cmavo_pat( qw( fu'e ) );
our $SM_FUhO = make_cmavo_pat( qw( fu'o ) );
our $SM_GA = make_cmavo_pat( qw( ga ge ge'i go gu ) );
our $SM_GAhO = make_cmavo_pat( qw( ga'o ke'i ) );
our $SM_GEhU = make_cmavo_pat( qw( ge'u ) );
our $SM_GI = make_cmavo_pat( qw( gi ) );
our $SM_GIhA = make_cmavo_pat( qw( gi'a gi'e gi'i gi'o gi'u ) );
our $SM_GOhA = make_cmavo_pat( qw( bu'a bu'e bu'i co'e
    du go'a go'e go'i go'o go'u mo nei no'a ) );
our $SM_GOI = make_cmavo_pat( qw( goi ne no'u pe po po'e po'u ) );
our $SM_GUhA = make_cmavo_pat( qw( gu'a gu'e gu'i gu'o gu'u ) );
our $SM_I = make_cmavo_pat( qw( i ) );
our $SM_JA = make_cmavo_pat( qw( ja je je'i jo ju ) );
our $SM_JAI = make_cmavo_pat( qw( jai ) );
our $SM_JOhI = make_cmavo_pat( qw( jo'i ) );
our $SM_JOI = make_cmavo_pat( qw( ce ce'o fa'u jo'e jo'u joi ju'e ku'a pi'u ) );
our $SM_KE = make_cmavo_pat( qw( ke ) );
our $SM_KEhE = make_cmavo_pat( qw( ke'e ) );
our $SM_KEI = make_cmavo_pat( qw( kei ) );
our $SM_KI = make_cmavo_pat( qw( ki ) );
our $SM_KOhA = make_cmavo_pat( qw( ce'u da da'e da'u de de'e
  de'u dei di di'e di'u do do'i do'o fo'a fo'e fo'i fo'o fo'u
  ke'a ko ko'a ko'e ko'i ko'o ko'u ma ma'a mi mi'a mi'o ra ri
  ru ta ti tu vo'a vo'e vo'i vo'o vo'u zi'o zo'e zu'i ) );
our $SM_KU = make_cmavo_pat( qw( ku ) );
our $SM_KUhE = make_cmavo_pat( qw( ku'e ) );
our $SM_KUhO = make_cmavo_pat( qw( ku'o ) );
our $SM_LA = make_cmavo_pat( qw( la la'i lai ) );
our $SM_LAhE = make_cmavo_pat( qw( la'e lu'a lu'e lu'i lu'o tu'a vu'i ) );
our $SM_LAU = make_cmavo_pat( qw( ce'a lau tau zai ) );
our $SM_LE = make_cmavo_pat( qw( le le'e le'i lei lo lo'e lo'i loi ) );
our $SM_LEhU = make_cmavo_pat( qw( le'u ) );
our $SM_LI = make_cmavo_pat( qw( li me'o ) );
our $SM_LIhU = make_cmavo_pat( qw( li'u ) );
our $SM_LOhO = make_cmavo_pat( qw( lo'o ) );
our $SM_LOhU = make_cmavo_pat( qw( lo'u ) );
our $SM_LU = make_cmavo_pat( qw( lu ) );
our $SM_LUhU = make_cmavo_pat( qw( lu'u ) );
our $SM_MAhO = make_cmavo_pat( qw( ma'o ) );
our $SM_MAI = make_cmavo_pat( qw( mai mo'o ) );
our $SM_ME = make_cmavo_pat( qw( me ) );
our $SM_MEhU = make_cmavo_pat( qw( me'u ) );
our $SM_MOhE = make_cmavo_pat( qw( mo'e ) );
our $SM_MOhI = make_cmavo_pat( qw( mo'i ) );
our $SM_MOI = make_cmavo_pat( qw( cu'o mei moi si'e va'e ) );
our $SM_NA = make_cmavo_pat( qw( ja'a na ) );
our $SM_NAhE = make_cmavo_pat( qw( je'a na'e no'e to'e ) );
our $SM_NAhU = make_cmavo_pat( qw( na'u ) );
our $SM_NAI = make_cmavo_pat( qw( nai ) );
our $SM_NIhE = make_cmavo_pat( qw( ni'e ) );
our $SM_NIhO = make_cmavo_pat( qw( ni'o no'i ) );
our $SM_NOI = make_cmavo_pat( qw( noi poi voi ) );
our $SM_NU = make_cmavo_pat( qw( du'u jei ka li'i
         mu'e ni nu pu'u si'o su'u za'i zu'o ) );
our $SM_NUhA = make_cmavo_pat( qw( nu'a ) );
our $SM_NUhI = make_cmavo_pat( qw( nu'i ) );
our $SM_NUhU = make_cmavo_pat( qw( nu'u ) );
our $SM_PA = make_cmavo_pat( qw( bi ce'i ci ci'i da'a dau du'e
  fei fi'u gai jau ji'i ka'o ki'o ma'u me'i mo'a mu ni'u no no'o
  pa pai pi pi'e ra'e rau re rei ro so so'a so'e so'i so'o so'u
  su'e su'o te'o tu'o vai vo xa xo za'u ze ) );
our $SM_PEhE = make_cmavo_pat( qw( pe'e ) );
our $SM_PEhO = make_cmavo_pat( qw( pe'o ) );
our $SM_PU = make_cmavo_pat( qw( ba ca pu ) );
our $SM_RAhO = make_cmavo_pat( qw( ra'o ) );
our $SM_ROI = make_cmavo_pat( qw( re'u roi ) );
our $SM_SA = make_cmavo_pat( qw( sa ) );
our $SM_SE = make_cmavo_pat( qw( se te ve xe ) );
our $SM_SEhU = make_cmavo_pat( qw( se'u ) );
our $SM_SEI = make_cmavo_pat( qw( sei ti'o ) );
our $SM_SI = make_cmavo_pat( qw( si ) );
our $SM_SOI = make_cmavo_pat( qw( soi ) );
our $SM_SU = make_cmavo_pat( qw( su ) );
our $SM_TAhE = make_cmavo_pat( qw( di'i na'o ru'i ta'e ) );
our $SM_TEhU = make_cmavo_pat( qw( te'u ) );
our $SM_TEI = make_cmavo_pat( qw( tei ) );
our $SM_TO = make_cmavo_pat( qw( to to'i ) );
our $SM_TOI = make_cmavo_pat( qw( toi ) );
our $SM_TUhE = make_cmavo_pat( qw( tu'e ) );
our $SM_TUhU = make_cmavo_pat( qw( tu'u ) );
our $SM_UI = make_cmavo_pat( qw( a'a a'e a'i a'o a'u ai au ba'a ba'u
  be'u bi'u bu'o ca'e da'i dai do'a e'a e'e e'i e'o e'u ei fu'i ga'i
  ge'e i'a i'e i'i i'o i'u ia ie ii io iu ja'o je'u ji'a jo'a ju'a
  ju'o ka'u kau ke'u ki'a ku'i la'a le'o li'a li'o mi'u mu'a na'i o'a
  o'e o'i o'o o'u oi pa'e pau pe'a pe'i po'o ra'u re'e ri'e ro'a ro'e
  ro'i ro'o ro'u ru'a sa'a sa'e sa'u se'a se'i se'o si'a su'a ta'o ta'u
  ti'e to'u u'a u'e u'i u'o u'u ua ue ui uo uu va'i vu'e xu za'a zo'o zu'u ) );
our $SM_VA = make_cmavo_pat( qw( va vi vu ) );
our $SM_VAU = make_cmavo_pat( qw( vau ) );
our $SM_VEhA = make_cmavo_pat( qw( ve'a ve'e ve'i ve'u ) );
our $SM_VEhO = make_cmavo_pat( qw( ve'o ) );
our $SM_VEI = make_cmavo_pat( qw( vei ) );
our $SM_VIhA = make_cmavo_pat( qw( vi'a vi'e vi'i vi'u ) );
our $SM_VUhO = make_cmavo_pat( qw( vu'o ) );
our $SM_VUhU = make_cmavo_pat( qw( cu'a de'o fa'i
  fe'a fe'i fu'u ge'a gei ju'u ne'o pa'i pi'a pi'i
  re'a ri'o sa'i sa'o si'i su'i te'a va'a vu'u ) );
our $SM_XI = make_cmavo_pat( qw( xi ) );
our $SM_Y = make_cmavo_pat( qw( y ) );
our $SM_ZAhO = make_cmavo_pat( qw( ba'o ca'o co'a
  co'i co'u de'a di'a mo'u pu'o za'o ) );
our $SM_ZEhA = make_cmavo_pat( qw( ze'a ze'e ze'i ze'u ) );
our $SM_ZEI = make_cmavo_pat( qw( zei ) );
our $SM_ZI = make_cmavo_pat( qw( za zi zu ) );
our $SM_ZIhE = make_cmavo_pat( qw( zi'e ) );
our $SM_ZO = make_cmavo_pat( qw( zo ) );
our $SM_ZOhU = make_cmavo_pat( qw( zo'u ) );
our $SM_ZOI = make_cmavo_pat( qw( la'o zoi ) );

# TODO FIXME add these words types for completeness
our $SM_BRIVLA;
our $SM_CMENE;
our $SM_CMAVO_FORM;
# TODO FIXME add these words types for completeness

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
  q{la'o} =~ $SM_ZOI or die;
  q{la'} =~ $SM_ZOI and die;
  q{la'orbangu} =~ $CM_BAD or die;
  q{la'orbangu} =~ $LUJVO or die;
  q{la'orbangu} =~ $SM_ZOI and die;
  q{la'oi} =~ $SM_ZOI and die;
  q{ge'uzdani} =~ $LUJVO and die;
  q{ge'urzdani} =~ $LUJVO or die;
  q{slinku'i} =~ $FUH3 and die;
}
test_regex_foundation0(); 

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
  $type=classify_word($word);
  if ($type eq 'c') {
    return cmavo_sepli($word); }
  if ($word =~ /^[aeiouy]/ix) {push(@parts, '. ');}
  while ( $type eq 'U' && $word =~
      /^($CM_0)($C .* ) $ /ix) {
     $cmavo=$1;$leftover=$2;
     if ($cmavo eq q{lo'u} || $cmavo eq q{le'u}) { $cmavo = '. ' . $cmavo . ' .';}
     push(@parts,$cmavo);$word=$leftover; $type=classify_word($word);
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
    my $type=classify_word($raw_word);
    #print $raw_word, ' -- ',cmavo_sepli($raw_word,$type),q{ },$type,"\n";
    #if ($raw_word =~ / ( $BAD ) /ix ) { print 'BAD ( ', $1 , " )\n"; }
    print sepli($raw_word,$type),q{ };
  }
  print "\n";
}

1;

__END__

#!/usr/bin/env python
#
# __future__ imports for Python 3 compliance in Python 2
# 
from __future__ import absolute_import, division, print_function
from __future__ import unicode_literals
#
# end of __future__ imports
#


import sys
import re

#
# codes and translations
#
#   codeDict for optical type
#   programCodeSites for station codes
#   catCodes for astcAT translation
# 
codeDict = {  # converts code to mode for optical type
 # 'A': 'PHA', # sets subFrm to 'B1950.0' maps to 'PHO'

  ' ': 'PHo', # blank means photographic -- see Xx
  'P': 'PHO',
  'e': 'ENC',
  'C': 'CCD',
  'T': 'MER',
  'M': 'MIC',
  'c': 'ccd',
  'E': 'OCC',
  'O': 'OFF',
  'H': 'PMT', # hipparcos
  'N': 'NOR',
  'n': 'VID',

 #  'X': 'Pho',  # maps to CCD
 #  'x': 'pho',  # maps to CCD

 # 'V': 'CCD', # by type
 # 'S': 'CCD', # by type
}
reverseCodeDict = { codeDict[i] : i for i in codeDict }  # no duplicates

validCodes = "A PeCTMcEOHNnRrSsVvXx"+"0"  # 0 is special for header lines
validNotes = ' AaBbcDdEFfGgGgHhIiJKkMmNOoPpRrSsTtUuVWwYyCQX2345vzjeL16789'
validProgramCodes = ' AaBbcDdEFfGgGgHhIiJKkMmNOoPpRrSsTtUuVWwYyCQX2345016789=#$%"&\+-![]`!|(){}.?@,^;:_/~*<>eLvzjZ'"'"
programCodeSites = \
set([ "010",
      "012",
      "084",
      "089",
      "094",
      "095",
      "121",
      "260",
      "261",
      "262",
      "266",
      "267",
      "268",
      "269",
      "290",
      "309",
      "413",
      "561",
      "568",
      "658",
      "673",
      "675",
      "688",
      "689",
      "695",
      "696",
      "705",
      "807",
      "809",
      "950",
      "A84",
      "B35",
      "D90",
      "E03",
      "E10",
      "E26",
      "F65",
      "G40",
      "G73",
      "G83",
      "H06",
      "I03",
      "I05",
      "I11",
      "I89",
      "J13",
      "N50",
      "Q62",
      "U69",
      "V07",
      "W84",
      "W88",
      "Z18",
      "Z19",
      "Z20",
      "249",
      "C49",
      "C50 ", ])

catCodes = { ' ': 'UNK',
             'a': 'USNOA1',
             'b': 'USNOSA1',
             'c': 'USNOA2',
             'd': 'USNOSA2',
             'e': 'UCAC1',
             'f': 'Tyc1',
             'g': 'Tyc2',
             'h': 'GSC1.0',
             'i': 'GSC1.1',
             'j': 'GSC1.2',
             'k': 'GSC2.2',
             'l': 'ACT',
             'm': 'GSCACT',
             'n': 'SSDS8',
             'o': 'USNOB1',
             'p': 'PPM',
             'q': 'UCAC4',
             'r': 'UCAC2',
             's': 'USNOB2',  # USNOB2 missing on ADES web page
             't': 'PPMXL',
             'u': 'UCAC3',
             'v': 'NOMAD',
             'w': 'CMC14',
             'x': 'Hip2',
             'y': 'Hip1',
             'z': 'GSC',
             'A': 'AC',
             'B': 'SAO1984',
             'C': 'SAO',
             'D': 'AGK3',
             'E': 'FK4',
             'F': 'ACRS',
             'G': 'LickGas',
             'H': 'Ida93',
             'I': 'Perth70',
             'J': 'COSMOS',
             'K': 'Yale',
             'L': '2MASS',
             'M': 'GSC2.3',
             'N': 'SDSS7',
             'O': 'SSTRC1',
             'P': 'MPOSC3',
             'Q': 'CMC15',
             'R': 'SSTRC4',
             'S': 'URAT1',
             'T': 'URAT2',  # URAT2 missing on ADES web page
             'U': 'Gaia1',
             'V': 'Gaia2',
             'W': 'UCAC5',  # UCAC5 mission on ADES web page
           }

rCatCodes = { catCodes[i]:i for i in catCodes }



def packProgID(c): # for program code id -- must be alpha
   return  hex(ord(c))[-2:]  # code in hex

def unpackProgID(s): # for program code id -- must be alpha
   return  chr(int(s, 16))  # decode into alpha


# PermID and ProvID pack/unpack
#
# PermID for a minor planet is a postive integer
# PermID for a comet is a positive integer followed by P or D
#   Comets may have fragments
# PermID for a natural satellite is "Jupiter VIII" or J8 ?
#
# ProvID for a minor planet is 
# ProvID for a comet is 
#   Comets may have fragments
# ProvID for a natual satellite is 
#
# a Packed PermID for a minor planet may use A-Z or a-z to encode
# the first digit of the integer for numbers > 10000
#
# a Packed ProvID for a minor planet
#     J95X00A -> 1995 XA
#     J95X01A -> 1995 XA1
#     J95Xa1A -> 1995 XA361
#  unless it is a survey
#     2050 P-L -> PLS2040
#     3138 T-1 -> T1S2040
#        There may be minor planets which become comets.
# a Packed ProvID for a comet
#   Comets may have fragments
# a Packed ProvID for a natural satellite

minorplanetProvIDRegex = re.compile('^(\d{2})(\d{2}) ([A-HJ-Y])([A-HJ-Z])(\d+)?$')
minorplanetSurveyProvIDRegex = re.compile('^(\d{4}) (P-L|T-1|T-2|T-3)$')
cometProvIDRegex = re.compile('^([ACDPX])/(\d{4}) ([A-Z])([A-Z])?(\d*)$')
cometfragmentProvIDRegex = re.compile('^([CDPX])/(\d{4}) ([A-Z])(\d*)-([A-Z])$')
satelliteProvIDRegex = re.compile('^S/(\d{4}) ([JSUN]) (\d+)$')

minorplanetPermIDRegex = re.compile('^(\d+)$')
cometPermIDRegex = re.compile('^(\d+)([PD])$')
cometfragmentPermIDRegex = re.compile('^(\d+)([PD])-([A-Z]{1,2})$')
satellitePermIDRegex = re.compile('^(Jupiter|Saturn|Uranus|Neptune) (\d+)$')
asteroidsatellitePermIDRegex = re.compile('^\((\d+|\d{4} [A-Z]{2}\d+)\) (\d+)$')

#
# trkSub matches any 7 characters starting with a letter except anything
# matching a minorplanetPackedProvIDRegex or a minorplanetSurveyRegex
#
# note minor planet centuries are restricted to [I-K] (1800 - 2099; maybe allow 2199?)
# Also we must exclude PLS and T[1-3]S for the surveys
#
# Use the extra outside parentheses to add comments to the continuation
#
# This is a mess because it's hard to exclude things in regex
#
trksubRegexHelp = ( '([A-Za-z][A-Za-z0-9]{0,5}' +         # anything six characters
                    '|[A-HL-OQ-SU-Z][A-Za-z0-9]{0,6}' +   # anything seven not starting with I-K,P or T
                    '|[I-K][A-Za-z0-9]{5}[a-z1-9]' +      # anything starting with I-K not ending in A-Z or 0
                    '|[I-K][A-Za-z][A-Za-z0-9]{4}[0A-Z]' + # anything starting with I-K ending in [A-Z] with not digit as second character
                    '|[I-K][0-9][A-Za-z][A-Za-z0-9]{3}[0A-Z]' + # anything starting with [I-K]<digit> ending in [A-Z] with not digit as third character
                    '|[I-K][0-9][0-9][Ia-z0-9][A-Za-z0-9]{2}[0A-Z]' + # anything starting with [I-K]<digit> ending in [A-Z] with not [A-Z] as fourth character
                    '|[I-K][0-9][0-9][A-HJ-Z][A-Za-z0-9][A-Za-z][0A-Z]' + # anything with [I-K]\d\d[A-HJ-Z][A-Za-z0-9]<not digit> [A-Z]
                    '|P[A-KM-Za-z0-9][A-Za-z0-9]{5}' +   # anything seven starting with P<not L>
                    '|T[A-Za-z04-9][A-Za-z0-9]{5}' +   # anything seven starting with T<not 1-3>
                     '|(?:PL|T1|T2|T3)[A-RT-Za-z0-9][A-Za-z0-9]{4}' + # anything starting PL|T1|T2|T3 not followed by S 
                     '|(?:PL|T1|T2|T3)S[A-Za-z][A-Za-z0-9]{3}' + # anything starting PL|T1|T2|T3 followed by S with not digit in 4
                     '|(?:PL|T1|T2|T3)S[A-Za-z0-9][A-Za-z][A-Za-z0-9]{2}' + # anything starting PL|T1|T2|T3 followed by S with not digit in 5
                     '|(?:PL|T1|T2|T3)S[A-Za-z0-9]{2}[A-Za-z][A-Za-z0-9]' + # anything starting PL|T1|T2|T3 followed by S with not digit in 6
                     '|(?:PL|T1|T2|T3)S[A-Za-z0-9]{3}[A-Za-z]' + # anything starting PL|T1|T2|T3 followed by S with not digit in 7
                    ')' )
trksubRegex = re.compile('^' + trksubRegexHelp + '$')


#
# Minor Planet groups: 
#   PermID:  None if not present
#      1: <letnum>
#      2: 4 digits
#   Normal ProvID: None if not present
#      3: <letnum> 
#      4: <yy> 
#      5: <halfmonth> 
#      6: <letnum> 
#      7: digit 
#      8: order -- is None if matches 0 for comet id
#   Survey ProvID: None if not present
#      9: PL | T1 | t3 | T3  
#      10: 4 digits
#   trkSub:  None if not present
#      11: six characters starting with a letter
#
minorplanetPackedIDRegex = re.compile('^(?: {5}|([0-9A-Za-z])(\d{4}))'+ 
                                      '(?:' + '([I-K])(\d{2})([A-HJ-Y])([a-zA-Z0-9])(\d)(?:([A-HJ-Z])|0)' + '|'
                                            + '(PL|T1|T2|T3)S(\d{4})' + '|'
                                            + trksubRegexHelp + ' *|'
                                            + ' *'
                                       + ')$')

#
# Comet groups:
#
#  PermID:  
#    1: 4 digits  -- None if no PermID
#    2: PCDX  -- used by provID too.  Only PD for PermID.  Is A allowed????
#  ProvID:  None if not present
#    3: <letnum>
#    4: <yy>
#    5: <halfmonth>
#    6: <letnum>
#    7: <digit>
#    8: A-Z; comet coded as asteroid
#    9: a-z; comet fragment 
# fragment marker for permID only (blanks in cols 6-10)
#   10: a-z; comet fragment first letter or blank
#   11: a-z; comet fragment 
#
cometPackedIDRegex = re.compile('^(?: {4}|(\d{4}))([APCDX])'  
                                  + '(?:' + '([0-9A-Za-z])(\d{2})([A-HJ-Y])([a-zA-Z0-9])(\d)(?:0|([A-Z])|([a-z]))' + '|'
                                          + '     ([a-z ])([a-z])'  + '|'
                                          + ' *$'
                                  + ')$')

#
# Satellite groups:
#
#  PermID:  None if not present
#    1: [JSUN]
#    2: 3 digits
#  ProvID:  None if not present
#    3: <letnum>
#    4: <yy>
#    5: JSUN
#    6: <letnum>
#    7: <digit>
#
satellitePackedIDRegex = re.compile('^(?: {4}|([JSUN])(\d{3}))S'  
                                       + '(?:' + '([0-9A-Za-z])(\d{2})([JSUN])([a-zA-Z0-9])(\d)0$' + '|'
                                               + ' *$'
                                       + ')$')

#
# A dictionary for unpacking planet names
#
planetNameDict = {
     'J': 'Jupiter',
     'S': 'Saturn',
     'U': 'Uranus',
     'N': 'Neptune',
}

#
# A dictionary for unpacking letters as numbers
#
packLetters = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
unpackLetters = {}

def _initpackLetters():
   global packLetters, unpackLetters
   for i in range(len(packLetters)):
     unpackLetters[packLetters[i]] = i

_initpackLetters()



        

def unpackPackedID(packedID):
   """
   unpackePackedID unpacks an MPC 80-column ID

   Input:
      packedID: The 12-character packed ID
   Output:
      (permID, provID, trkSub)
   """
   permID = None
   provID = None
   trkSub = None
   #
   # groups:  0: <letnum> or None  1: 4 digits or None -- 2: <letnum> 3: yy 4: <halfmonth> : 5: <letnum> 6: digig 7: order
   #
   m = minorplanetPackedIDRegex.match(packedID)
   if m: 
      if m.group(1):  # check for permID presence
         n = int(m.group(2)) + 10000*unpackLetters[m.group(1)]
         if (n == 0):
            raise RuntimeError("Can't unpack because minor planet number for " 
                                + packedID + " is zero")
         permID = str(n)
      
      if m.group(3): # check for normal provID presence
         y = unpackLetters[m.group(3)] * 100 + int(m.group(4))
         y = "{0:0d}".format(y)
         n = unpackLetters[m.group(6)] * 10 + int(m.group(7))
         if n==0:
            ns = ''
         else:
            ns = str(n)
         if m.group(8):  # normal asteroid provid
             provID =  y + ' ' + m.group(5) + m.group(8) + ns
         else:           # comet ID -- use A/
             provID =  'A/' + y + ' ' + m.group(5) + ns

      if m.group(9): # check for survey provID presence
         provID =  m.group(10) + ' ' + m.group(9)[0] + '-' + m.group(9)[1]

      if not permID and m.group(11): # check for trkSub -- can't be provID may not have permID
         trkSub = m.group(11).strip()

   #
   # Comet groups:
   #
   #  PermID:  
   #    1: 4 digits  -- None if no PermID
   #    2: PCDX  -- used by provID too.  Only PD for PermID.  Is A allowed????
   #  ProvID:  None if not present
   #    3: <letnum>
   #    4: <yy>
   #    5: <halfmonth>
   #    6: <letnum>
   #    7: <digit>
   #    8: A-Z; comet coded as asteroid
   #    9: a-z; comet fragment 
   # fragment marker for permID only (blanks in cols 6-10)
   #   10: a-z; comet fragment first letter or blank
   #   11: a-z; comet fragment 
   #
   m = cometPackedIDRegex.match(packedID)
   if m:
     cometType = m.group(2)
     if m.group(1):
        n = int(m.group(1))
        if (n == 0):
           raise RuntimeError("Can't unpack because comet number for " 
                               + packedID + " is zero")
        if (cometType != 'P' and cometType != 'D'):
           raise RuntimeError("Can't unpack because comet type for " 
                               + packedID + " must be P or D")
        permID = str(n) + cometType
        #
        # now check for fragments
        #
        if m.group(9):
          permID = permID + '-' + m.group(9).upper()
        if m.group(11):
          frag = (m.group(10) + m.group(11)).strip().upper()
          permID = permID + '-' + frag

     if m.group(3):
        y = unpackLetters[m.group(3)] * 100 + int(m.group(4))
        y = "{0:0d}".format(y)
        n = unpackLetters[m.group(6)] * 10 + int(m.group(7))
        if n==0:
           ns = ''
        else:
           ns = str(n)
        extra = ''
        if m.group(8): # m.group(8) changes nothing 
           extra = m.group(8) # adds order

        frag = ''
        if m.group(9): # fragment letter
           frag = '-' + m.group(9).upper()

        provID =  m.group(2) + '/' + y + ' ' + m.group(5) + extra + ns + frag

   #
   # Satellite groups:
   #
   #  PermID:  None if not present
   #    1: [JSUN]
   #    2: 3 digits
   #  ProvID:  None if not present
   #    3: <letnum>
   #    4: <yy>
   #    5: JSUN
   #    6: <letnum>
   #    7: <digit>
   #
   m = satellitePackedIDRegex.match(packedID)
   if m:
     if m.group(1):
        n = int(m.group(2))
        if (n == 0):
           raise RuntimeError("Can't unpack because satellite number for " 
                               + packedID + " is zero")
        permID =  planetNameDict[m.group(1)] + " " +  str(n)
     if m.group(3):
        y = unpackLetters[m.group(3)] * 100 + int(m.group(4))
        y = "{0:0d}".format(y)
        n = unpackLetters[m.group(6)] * 10 + int(m.group(7))
        if n==0:
           ns = ''
        else:
           ns = str(n)
        provID =  'S/' + y + ' ' + m.group(5) + ' ' + ns

   if not permID and not provID and not trkSub: # oops -- nothing here
      raise RuntimeError("Can't unpack " + repr(packedID) + " because this does not match a valid packed ID")

   return (permID, provID, trkSub)


def packTupleID(triplet):
   """
   packTupleID packs an (permID, provID, trkSub) into
   MPC 80-column format or raises an exception about why not

   Input:
      (permID, provID, trkSub)  or  [permID, provID, trkSub]
   Output:
      packedID: The 12-character packed ID
   """

   try:
      permID = triplet[0]
      provID = triplet[1]
      trkSub = triplet[2]
   except:
      raise RuntimeError("Can't pack " + repr(triplet) + " because it isn't (permID, provID, trkSub)")
   if len(triplet) != 3:
      raise RuntimeError("Can't pack " + repr(triplet) + "because it is not of length 3")

   #
   # figure out permID type and value using regex
   #
   packedPermID = None # may be None if permID is None
   if permID is not None: # otherwise try to decode it
      #
      # may be a minor planet
      #
      m = minorplanetPermIDRegex.match(permID)
      if m:
         mp = int(m.group(1))
         if (mp > 0) and (mp < 620000): # 1 through 619999 allowed
             firstDigit = mp//10000   
             lastDigits = mp - firstDigit * 10000
             packedPermID =  packLetters[firstDigit] + "{0:0d}".format(lastDigits + 10000)[1:]
             permIDType = 'A'
         else:
             raise RuntimeError("Can't pack permID " + permID + " because it is not in range 1-619000")

      #
      # may be a comet
      #
      m = cometPermIDRegex.match(permID)
      if m:
         n = int(m.group(1))
         if n > 9999:
            raise RuntimeError("Can't pack because comet number for " 
                                + permID + " is too large")
         if n == 0:
            raise RuntimeError("Can't pack because comet number for " 
                                + permID + " is zero")
         packedPermID =  "{0:0d}".format(n + 10000)[1:] + m.group(2)
         permIDType = 'C'

      #
      # may be a comet fragmnet
      #
      m = cometfragmentPermIDRegex.match(permID)
      if m:
         n = int(m.group(1))
         if n > 9999:
            raise RuntimeError("Can't pack because comet number for " 
                                + permID + " is too large")
         if n == 0:
            raise RuntimeError("Can't pack because comet number for " 
                                + permID + " is zero")
         packedPermID =  "{0:0d}".format(n + 10000)[1:] + m.group(2)
         permIDType = 'F'
         permIDFragment = m.group(3)
   
   
      #
      # may be a satellite
      #
      m = satellitePermIDRegex.match(permID)
      if m:
         n = int(m.group(2))
         if n > 999:
            raise RuntimeError("Can't pack because satellite number for " 
                                + permID + " is too large")
         if n == 0:
            raise RuntimeError("Can't pack because satellite number for " 
                                + permID + " is zero")
         permIDType = 'S'
         packedPermID = m.group(1)[0]  + "{0:0d}".format(1000 + int(m.group(2)))[1:] + 'S'

      #
      # may not be a satellite of an asteroid
      #
      m = asteroidsatellitePermIDRegex.match(permID)
      if m:
         raise RuntimeError("Can't pack satellites of asteroids: " +  permID)

      if not packedPermID:  # none falls through
          raise RuntimeError("invalid permID " + permID)

   #
   # figure out provID type and value using regex
   #
   packedProvID = None # may be None if provID is None
   if provID is not None:  # otherswise try to decode it
   #
   # minor planets in normal format
   #
      m = minorplanetProvIDRegex.match(provID)
      if m:
         y = int(m.group(1))  # two-digit head of year
         if (y<18) or (y>61):
            raise RuntimeError("Can't pack because minor planet year for " 
                                + provID + " is invalid")
         n = m.group(5)
         if not n: # None is 0
           n = 0  
         else:
           n = int(n)
         if n>619: # can't encode if it's too big
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is too big")
         n1 = int(n/10)
         nn = packLetters[n1]
         n2 = "{0:0d}".format(n - 10*n1  + 10)[1:]
         
         packedProvID =  ' ' + packLetters[y] + m.group(2) + \
                m.group(3) + nn + n2 + m.group(4)
         provIDType = 'A'
   
      #
      # minor planets from survey
      #
      m = minorplanetSurveyProvIDRegex.match(provID)
      if m:
         n = int(m.group(1))
         s1 = m.group(2)[0]
         s2 = m.group(2)[2]
         packedProvID =  ' ' + s1 + s2 + 'S' + "{0:0d}".format(10000 + n)[1:]
         provIDType = 'A'
   
      #
      # comets
      #
      m = cometProvIDRegex.match(provID)
      if m:
         extra = '0' 
         if m.group(4):  # handle two-letter comets -- these were originally asteroids and can't have fragments
           extra = m.group(4)
         n = int('0' + m.group(5)) # may be ''
         n1 = n//10
         n2 = n - n1*10
         if n1 > 61:
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is too big")
         
         y1 = packLetters[int(m.group(2)[0:2])]
         y2 = m.group(2)[2:4]
         packedProvID =  m.group(1) + y1 + y2 + m.group(3) + packLetters[n1] + packLetters[n2] + extra
         if m.group(1) == 'A': # asteroid in disguise
            provIDType = 'A'
         else:
            provIDType = 'C'
   
      #
      # comet fragments
      #
      m = cometfragmentProvIDRegex.match(provID)
      if m:
         n = int(m.group(4))
         n1 = n//10
         n2 = n - n1*10
         if n1 > 61:
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is too big")
         
         y1 = packLetters[int(m.group(2)[0:2])]
         y2 = m.group(2)[2:4]
         packedProvID =  m.group(1) + y1 + y2 + m.group(3) + packLetters[n1] + packLetters[n2] + m.group(5).lower()
         provIDType = 'F'
         provIDFragment = m.group(5) # single character only
         
      #
      # satellites
      #
      m = satelliteProvIDRegex.match(provID)
      if m:
         n = int(m.group(3))
         n1 = n//10
         n2 = n - n1*10
         if n1 > 61:
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is too big")
         if n == 0:
            raise RuntimeError("Can't pack because number for " 
                                + provID + " is zero")
         
         
         y1 = packLetters[int(m.group(1)[0:2])]
         y2 = m.group(1)[2:4]
         packedProvID =  'S' + y1 + y2 + m.group(2) + packLetters[n1] + packLetters[n2]  + '0'
         provIDType = 'S'

      if not packedProvID:  # none falls through
          raise RuntimeError("invalid provID " + provID)


   packedTrkSub = None # may be None if trksub is None
   #
   # figure out permID type and value using regex
   #
   packedTrkSub = None # may be None if permID is None
   if trkSub is not None: # otherwise try to decode it
      #
      # check trksub regex
      #
      m = trksubRegex.match(trkSub)
      if m:
         tmp = m.group(1)
         #print ("m.groups is ", m.groups())
         if len(tmp) > 7:
            raise RuntimeError("Can't pack " + trkSub + " because it it is too long")
         packedTrkSub = m.group(1)

      if not packedTrkSub:  # none falls through
          raise RuntimeError("invalid trkSub " + trkSub)

   #
   # Now pack it in the final format
   #
   packed = None
   #print ( packedPermID, packedProvID, packedTrkSub )
   if packedPermID:  
      if packedProvID: # must match
        if permIDType != provIDType:
           raise RuntimeError("Can't pack " + repr(triplet) + " because provID and permID types don't match")
        if permIDType == 'F':
           if permIDFragment != provIDFragment:
              raise RuntimeError("Can't pack " + repr(triplet) + " because provID and permID fragments don't match")
        packed = packedPermID + packedProvID[1:]  # works for all cases that match

      else: # no packed provID
        if packedTrkSub:  # is this legal?
           pass
        else:
           packed = packedPermID + '       '
           if permIDType == 'F':  # fragments are special
             if len(permIDFragment) == 1:
                permIDFragment = ' ' + permIDFragment
             packed = packed[:10] + permIDFragment.lower()

   else:  # no packedPermID
      if packedProvID:
        if packedTrkSub: # this is illegal
          raise RuntimeError("Can't pack " + repr(triplet) + " because it has both provID and trksub")
        packed = '    ' + packedProvID # captures column 5

      else:
        if packedTrkSub: 
           packed = '     ' + packedTrkSub  # need to pad to column 12
           packed = '{0:12s}'.format(packed)

   if packed:
      return packed

   raise RuntimeError("Can't pack " + repr(triplet) )

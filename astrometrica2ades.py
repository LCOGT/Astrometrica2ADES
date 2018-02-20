#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import re

import sexVals
import packUtil


def parse_header(header_lines):

    version_string = "# version=2017"
    observatory = observers = measurers = telescope = ''

    if type(header_lines) != list:
        header_lines = [header_lines,]
    for line in header_lines:
        if line[0:3] == 'COD':
            observatory = parse_obscode(line[4:])
        elif line[0:3] == 'OBS':
            observers = parse_observers(line[4:])
        elif line[0:3] == 'MEA':
            measurers = parse_measurers(line[4:])
        elif line[0:3] == 'TEL':
            telescope = parse_telescope(line[4:])
    header = version_string + '\n'
    if observatory != '':
        header += observatory
    if observers != '':
        header += observers
    if measurers != '':
        header += measurers
    if telescope != '':
        header += telescope
    return header

def parse_obscode(code_line):
    config = configparser.ConfigParser()
    config.read('config.ini')

    site_code = code_line.strip()
    try:
        site_name = config.get('OBSERVATORY', site_code + '_SITE_NAME')
    except configparser.NoOptionError:
        site_name = None
    observatory = ( "# observatory" + "\n"
                    "! mpcCode " + site_code + "\n")
    if site_name:
        observatory += "! name " + site_name +"\n"

    return observatory

def parse_observers(code_line):

    observers = ''

    obs = code_line.split(',')
    if len(obs) >= 1:
        observers = '# observers\n'
        for observer in obs:
            observers += "! name " + observer.strip() + "\n"
    return observers

def parse_measurers(code_line):

    measurers = ''

    meas = code_line.split(',')
    if len(meas) >= 1:
        measurers = '# measurers\n'
        for measurer in meas:
            measurers += "! name " + measurer.strip() + "\n"
    return measurers

def parse_telescope(code_line):

    telescope = ''
    tel_string, detector = code_line.split('+')
    tel_chunks = tel_string.strip().split(' ')
    aperture = tel_chunks[0][:-2]
    if len(tel_chunks) == 2:
        design = tel_chunks[1]
        f_ratio = ''
    elif len(tel_chunks) == 3:
        f_ratio = tel_chunks[1]
        design = tel_chunks[2]

    telescope = ("# telescope" + "\n"
                 "! aperture " + aperture + "\n"
                 "! design " + design + "\n"
                 "! detector " + detector.strip() + "\n"
                )

    if f_ratio != '':
        telescope += "! fRatio " + f_ratio + "\n"

    return telescope

def error80(msg, l):
   badLineMsg = 'Invalid MPC80COL line ('
   raise RuntimeError(badLineMsg + msg + ') in line:\n' + l)

def parse_dataline(line):

    #
    # matches optical line; also V and S and X
    #
    # groups: first seven are for all types
    #   1: id group
    #   2: discovery
    #   3: notes -- notes can be anything; valid Notes is wrong
    #   4: codes  and RvSsVvXx
    #   5: yyyy  from obsDate
    #   6: blank or a-e for asteroid satellites (embedded in obsDat)
    #   7: rest of obsDate

    commonRegexHelp1 = ( '([A-za-z0-9 ]{12})'    # id group 1-12
                         + '([ *+])'                # discovery group 13 may be ' ', '*' or '+'
                         #+ '( AaBbcDdEFfGgGgHhIiJKkMmNOoPpRrSsTtUuVWwYyCQX2345vzjeL16789])' # notes group 14
                         + '(.)'                 # notes can be anything
                         )
    commonRegexHelp2 = ( '(\d{4})'            # yyyy from obsDate 16-19
                         + '([ a-e])'            # asteroid satellite embedded in date 20
                         + '([0-9 .]{12})'       # rest of obsDate loosely checked 21-32
                         )


    # ----------- remainder depends on type.  This is for optical and SV
    #   8: Ra
    #   9: Dec
    #  10: doc says blank but stuff is here
    #  11: mag
    #  12: band
    #  13: packedref and astCode as first character
    #  14: 3-character obs stn code
    #
    normalLineRegex = re.compile( ( '^'
                                       + commonRegexHelp1
                                       + '([A PeCTMcEOHNnSVXx])' # codes group -- include SVXx but not Rrsv 15
                                       + commonRegexHelp2
                                       + '([0-9 .]{12})'       # Ra loosely checked 33-44
                                       + '([-+ ][0-9 .]{11})'  # Dec loosely checked 45-56
                                       + '(.{9})'              # mpc doc says blank but not 57-65
                                       + '(.{5})'              # mag 66-70
                                       + '(.{1})'              # band 71
                                       + '(.{6})'              # packedref 72-77.  72 by itself is astCode
                                       + '(.{3})'              # obs stn 78-80
                                       + '$' )  )

    ret  = {}
    if not line:
        return ret
    if len(line) > 80:
        error80 ( repr(len(line)) + ' columns', line)

    ret['subFmt'] = 'M92'  # since were are MPC 80-col format
    m = normalLineRegex.match(line)  # optical, SVXx
    if m:
        #  print (m.groups())
        ret['totalid'] = m.group(1)
        ret['disc'] = m.group(2)
        ret['notes'] = m.group(3)
        ret['code'] = m.group(4)
        ret['date'] = m.group(5) + m.group(6) + m.group(7)

        ret['raSexagesimal']   =   m.group(8)
        ret['decSexagesimal'] =   m.group(9)
        ret['bl1']  =   m.group(10)
        ret['mag']  =   m.group(11)
        ret['band'] =   m.group(12)
        ret['packedref'] = m.group(13)
        ret['stn']  =   m.group(14)

        sexVals.checkDate(ret) # check date first
        sexVals.checkRa(ret)
        sexVals.checkDec(ret)
    else:
        error80 ("no match for line", line)

    #
    # more value sanity checks
    #
    sexVals.checkDate(ret) # check date always
    if ( ret['code'] not in packUtil.validCodes):
        error80 ("invalid column 14 " + ret['code']+ " in line " +  repr(lineNumber), line)

    if ( ret['notes'] not in packUtil.validNotes):
       error80 ("invalid note "+ ret['notes'] +" in line "+ repr(lineNumber), line)

    ret['astCat']   = ret['packedref'][0] # catalog code; 72 - first in packed reference. Blank for submissions

    #
    # compute unpacked ID fields.  This may be only a trkSub
    #

    (permID, provID, trkSub) = packUtil.unpackPackedID(ret['totalid'])
    ret['permID'] = permID
    ret['provID'] = provID
    ret['trkSub'] = trkSub
    #print(permID, provID, trkSub)

    try:
        packtest =  packUtil.packTupleID( (permID, provID, trkSub) )
        if packtest != ret['totalid']:
            print ("ID does not round-trip; " + packtest + " vs. " + ret['totalid'])
    except:
        print ("fails pack: ", permID, provID, trkSub)

    return ret

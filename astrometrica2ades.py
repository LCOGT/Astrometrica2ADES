#!/usr/bin/env python

from __future__ import print_function
from __future__ import unicode_literals
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import re
import os
import sys

import sexVals
import packUtil


def parse_header(header_lines):

    version_string = "# version=2017"
    site_code = ''
    observatory = observers = measurers = telescope = ''

    if type(header_lines) != list:
        header_lines = [header_lines,]
    for line in header_lines:
        if line[0:3] == 'COD':
            observatory, site_code = parse_obscode(line[4:])
        elif line[0:3] == 'OBS':
            observers = parse_observers(line[4:])
        elif line[0:3] == 'MEA':
            measurers = parse_measurers(line[4:])
        elif line[0:3] == 'TEL':
            telescope = parse_telescope(line[4:])
    header = version_string + '\n'
    if observatory != '':
        header += observatory
    submitter = determine_submitter(measurers, site_code)
    if submitter != '':
        header += submitter
    else:
        print("Error: Submitter is required")
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
    observatory = ("# observatory" + "\n"
                   "! mpcCode " + site_code + "\n")
    if site_name:
        observatory += "! name " + site_name +"\n"

    return observatory, site_code

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
        try:
            f_ratio = tel_chunks[1].replace('f/', '')
            f_ratio = "%.1f" % float(f_ratio)
        except ValueError:
            f_ratio = ''
        design = tel_chunks[2]

    telescope = ("# telescope" + "\n"
                 "! aperture " + aperture + "\n"
                 "! design " + design + "\n"
                 "! detector " + detector.strip() + "\n"
                )

    if f_ratio != '':
        telescope += "! fRatio " + f_ratio + "\n"

    return telescope

def determine_submitter(measurers, site_code):
    submitter_lines = ''

    measurer_lines = measurers.split('\n')
    if len(measurer_lines) >= 2:
        submitter = measurer_lines[1].replace('! name ','')
    else:
        config = configparser.ConfigParser()
        config.read('config.ini')

        try:
            submitter = config.get('OBSERVATORY', site_code + '_SUBMITTER')
        except configparser.NoOptionError:
            submitter = ''
            print("Could not determine submitter from measurers")
            print('Either fix MEA line or define "<site_code>_SUBMITTER" in config.ini')

    if submitter != '':
        submitter_lines = "# submitter\n" + "! name " + submitter + "\n"

    return submitter_lines

def error80(msg, line):
    badLineMsg = 'Invalid MPC80COL line ('
    raise RuntimeError(badLineMsg + msg + ') in line:\n' + line)

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

    commonRegexHelp1 = ('([A-za-z0-9 ]{12})'    # id group 1-12
                        + '([ *+])'                # discovery group 13 may be ' ', '*' or '+'
                        #+ '( AaBbcDdEFfGgGgHhIiJKkMmNOoPpRrSsTtUuVWwYyCQX2345vzjeL16789])' # notes group 14
                        + '(.)'                 # notes can be anything
                       )
    commonRegexHelp2 = ('(\d{4})'            # yyyy from obsDate 16-19
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
    normalLineRegex = re.compile(('^'
                                  + commonRegexHelp1
                                  + '([A PeCTMcEOHNnSVXx])' # codes group -- include SVXx but not Rrsv 15
                                  + commonRegexHelp2
                                  + '([0-9 .]{12})'       # Ra loosely checked 33-44
                                  + '([-+ ][0-9 .]{11})'  # Dec loosely checked 45-56
                                  + '(.{9})'              # mpc doc says blank but not 57-65
                                  + '(.{5})'              # mag 66-70
                                  + '(.{1})'              # band 71
                                  + '(.{6})'              # packedref 72-77. 72 by itself is astCode
                                  + '(.{3})'              # obs stn 78-80
                                  + '$')
                                )

    ret = {}
    if not line:
        return ret
    if len(line) > 80:
        error80(repr(len(line)) + ' columns', line)

    ret['subFmt'] = 'M92'  # since were are MPC 80-col format
    m = normalLineRegex.match(line)  # optical, SVXx
    if m:
        #  print (m.groups())
        ret['totalid'] = m.group(1)
        ret['disc'] = m.group(2)
        ret['notes'] = m.group(3)
        ret['code'] = m.group(4)
        ret['date'] = m.group(5) + m.group(6) + m.group(7)

        ret['raSexagesimal'] = m.group(8)
        ret['decSexagesimal'] = m.group(9)
        ret['bl1'] = m.group(10)
        ret['mag'] = m.group(11)
        ret['band'] = m.group(12)
        ret['packedref'] = m.group(13)
        ret['stn'] = m.group(14)

        sexVals.checkDate(ret) # check date first
        sexVals.checkRa(ret)
        sexVals.checkDec(ret)
    else:
        error80("no match for line", line)

    #
    # more value sanity checks
    #
    sexVals.checkDate(ret) # check date always
    if ret['code'] not in packUtil.validCodes:
        error80("invalid column 14 " + ret['code']+ " in line ", line)
    else:
        ret['mode'] = packUtil.codeDict[ret['code']]

    # No mapping of program codes yet
    ret['prog'] = '  '
    if ret['notes'] not in packUtil.validNotes:
        error80("invalid note "+ ret['notes'] +" in line ", line)

    # Determine catalog code; 72 - first in packed reference. Blank for submissions
    ret['astCat'] = ret['packedref'][0]

    #
    # compute unpacked ID fields.  This may be only a trkSub
    #

    (permID, provID, trkSub) = packUtil.unpackPackedID(ret['totalid'])
    ret['permID'] = permID
    ret['provID'] = provID
    ret['trkSub'] = trkSub
    #print(permID, provID, trkSub)

    try:
        packtest = packUtil.packTupleID((permID, provID, trkSub))
        if packtest != ret['totalid']:
            print ("ID does not round-trip; " + packtest + " vs. " + ret['totalid'])
    except RuntimeError:
        print ("fails pack: ", permID, provID, trkSub)

    return ret

def read_mpcreport_file(mpcreport_file):
    '''Open the MPC 1992 format file specified by <mpcreport_file>, returning the
    header lines in <header> and the observations in <body>'''

    header = []
    body = []

    try:
        mpc_fh = open(mpcreport_file, 'r')
        for line in mpc_fh:
            if line[0:3] in ['COD', 'CON', 'OBS', 'MEA', 'TEL', 'ACK', 'AC2', 'COM', 'NET']:
                header.append(line.rstrip())
            elif '----- end -----' not in line:
                body.append(line.rstrip())
    finally:
        mpc_fh.close()

    return header, body

def map_NET_to_catalog(header):
    '''Handle mapping of a possible NET line in the passed set of <header> lines
    to a astrometric catalog'''

    catalog = ''
    # Mapping of Astromerica names to MPC approved names from
    # https://www.minorplanetcenter.net/iau/info/ADESFieldValues.html
    catalog_mapping = {'USNO-SA 2.0' : 'USNOSA2',
                       'USNO-A 2.0'  : 'USNOA2',
                       'USNO-B 1.0'  : 'USNOB1',
                       'UCAC-3'      : 'UCAC3',
                       'UCAC-4'      : 'UCAC4',
                       'URAT-1'      : 'URAT1',
                       'NOMAD'       : 'NOMAD',
                       'CMC-14'      : 'CMC14',
                       'CMC-15'      : 'CMC15',
                       'PPMXL'       : 'PPMXL',
                       'Gaia DR1'    : 'Gaia1',
                       'Gaia DR2'    : 'Gaia2',
                      }
    for line in header:
        if 'NET ' in line:
            catalog_name = line.rstrip()[4:]
            catalog = catalog_mapping.get(catalog_name, ' ')

    return catalog

if __name__ == '__main__':

    rms_available = False

    if len(sys.argv) == 2:
        mpcreport = sys.argv[1]
        outFileName = os.path.basename(mpcreport)
        if '.txt' in outFileName:
            outFileName = outFileName.replace('.txt', '.psv')
        else:
            outFileName += '.psv'
        outFile = os.path.join(os.path.dirname(mpcreport), outFileName)
    elif len(sys.argv) == 3:
        mpcreport = sys.argv[1]
        outFile = sys.argv[2]
    else:
        print("Usage: %s <MPCReport file> [output PSV file]" % (os.path.basename(sys.argv[0])))
        exit()

    print("Reading from: %s, writing to: %s" % (mpcreport, outFile))
    header, body = read_mpcreport_file(mpcreport)
    if len(header) == 0 or len(body) == 0:
        print("No valid data in file")
        exit()
    print("Read %d header lines,%d observation lines from %s" % (len(header), len(body), mpcreport))

    out_fh = open(outFile, 'w')

    # Write obsContext out
    psv_header = parse_header(header)
    print(psv_header.rstrip(), file=out_fh)

    # Define and write obsData header
    tbl_fmt = '%7s|%-11s|%8s|%4s|%-4s|%4s|%-23s|%11s|%11s|%8s|%5s|%6s|%8s|%-5s|%-s'
    tbl_hdr = tbl_fmt % ('permID', 'provID', 'trkSub', 'mode', 'stn', 'prog', 'obsTime', \
        'ra', 'dec', 'astCat', 'mag', 'band', 'photCat', 'notes', 'remarks')
    rms_tbl_fmt = '%7s|%-11s|%8s|%4s|%-4s|%4s|%-23s|%11s|%11s|%5s|%6s|%7s|%8s|%5s|%6s|%4s|%8s|%6s|%6s|%6s|%4s|%-5s|%-s'
    rms_tbl_hdr = rms_tbl_fmt % ('permID', 'provID', 'trkSub', 'mode', 'stn', 'prog', 'obsTime', \
        'ra', 'dec', 'rmsRA', 'rmsDec', 'rmsCorr', 'astCat', 'mag', 'rmsMag', 'band', 'photCat', \
        'photAp', 'logSNR', 'seeing', 'exp', 'notes', 'remarks')
#    rms_tbl_data = '%7s|%-11s|%8s|%4s|%-4s|%4s|%-23s|%11s|%11s|%5.3f|%6.4f|%7.4f|%8s|%5s|%6.4f|%4s|%8s|%6.3f|%6.4f|%6s|%-5s|%-s'

    if rms_available:
        print(rms_tbl_hdr, file=out_fh)
    else:
        print(tbl_hdr, file=out_fh)

    # Parse and write out obsData records
    for line in body:
        data = parse_dataline(line)
        # For Astrometrica, photCat = astCat
        if data['astCat'] == ' ':
            data['astCat'] = map_NET_to_catalog(header)
        data['photCat'] = data['astCat']
        data['remarks'] = ''
        permID = data['permID']
        if permID is None:
            permID = ''
        provID = data['provID']
        if provID is None:
            provID = ''
        trkSub = data['trkSub']
        if trkSub is None:
            trkSub = ''
        if data != {} and data.get('trkSub', None) is None:
            if rms_available:
                pass
            else:
                tbl_data = tbl_fmt % (permID, provID, trkSub, data['mode'], data['stn'], \
                    data['prog'], data['obsTime'], data['ra'], data['dec'], data['astCat'],\
                    data['mag'], data['band'], data['photCat'], data['notes'], data['remarks'])
            print(tbl_data, file=out_fh)
    out_fh.close()

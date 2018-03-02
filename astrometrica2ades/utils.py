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
from math import log10
import pkg_resources

from astrometrica2ades import sexVals
from astrometrica2ades import packUtil

global _converter_version
_converter_version = "astrometrica2ades V0.0.3"

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
    config_file = pkg_resources.resource_filename(__package__, os.path.join('data', 'config.ini'))
    config.read(config_file)

    site_code = code_line.strip()
    try:
        site_name = config.get('OBSERVATORY', site_code + '_SITE_NAME')
    except configparser.NoSectionError:
        print("Could not find an OBSERVATORY section in ", config_file)
        site_name = None
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
        config_file = pkg_resources.resource_filename(__package__, os.path.join('data', 'config.ini'))
        config.read(config_file)

        try:
            submitter = config.get('OBSERVATORY', site_code + '_SUBMITTER')
        except (configparser.NoOptionError, configparser.NoSectionError):
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

def read_astrometrica_logfile(log, dbg=False):
    """
    Read an Astrometrica log file, extracting the version number, the images
    measured (with details about the no. of stars used and the RA, Dec & magnitude
    rms values)

    Parameters
    ----------
    log : str
        Path/filename of the Astrometrica.log file
    dbg: bool, optional
        Turn on debugging print statements

    returns
    -------
    version : str
        The version string of Astrometrica that was used
    images : list
        A list of tuples containing the image filename and a dictionary of the
        RA, Dec, magnitude and no. of stars used in the astrometric fit.
    asteroids: list
        A list of dicts containing the id, observation time, RA, Dec, Mag rms,
        SNR and FWHM of asteroid measured by Astrometrica.
    """

    log_fh = open(log, 'r')

    images_regex = re.compile('^\d{2}:\d{2}:\d{2} - Astrometry of Image \d* \(' + '(.*)\):')
    photom_regex = re.compile('^\d{2}:\d{2}:\d{2} - Photometry of Image \d* \(' + '(.*)\):')
    version_regex = re.compile('^\s*(Astrometrica .*[^\r\n]+)')
    astrom_rms_regex = re.compile('(\d+)[^=]+=\s*([.0-9]+)\"[^=]+=\s*([.0-9]+)\"')
    photom_rms_regex = re.compile('(\d+)[^=]+=\s*([.0-9]+)[^=]+')
    pos_regex = re.compile('^\d{2}:\d{2}:\d{2} - Position\ added|Moving\ Object')
    pos_rms_regex = re.compile('([.0-9]+)')
    apradius_regex = re.compile('^\s*Aperture Radius\s*=\s*(\d)')

    images = []
    asteroids = []
    avg_pix_size = None
    ap_radius_pix = None
    version = ''
    while True:
        line = log_fh.readline()
        i = images_regex.match(line)
        v = version_regex.match(line)
        p = photom_regex.match(line)
        pos = pos_regex.match(line)
        ap = apradius_regex.search(line)
        if v:
            # Match to version string
            version = v.group(1)
        elif ap:
            ap_radius_pix = float(ap.group(1))
        elif i:
            # Match to Astrometry image line
            line2 = log_fh.readline()
            if not line2: break
            m = astrom_rms_regex.search(line2)
            image = i.group(1)
            if m:
                rms = {}
                rms['nstars'] = m.group(1)
                rms['dRA'] = m.group(2)
                rms['dDec'] = m.group(3)
                image_list = [i[0] for i in images]
                try:
                    # Image is already in list, update values
                    image_index = image_list.index(image)
                    images[image_index]= (image, rms)
                except ValueError:
                    # Image is not in list, add details
                    images.append((image , rms))
            line_count = 0
            while line_count < 6:
                line2 = log_fh.readline()
                if not line2: break
                line_count += 1
            pix_size_regex = re.compile('([.0-9]+)\"')
            pix_size = pix_size_regex.findall(line2)
            if dbg: print(pix_size)
            if len(pix_size) == 2:
                avg_pix_size = (float(pix_size[0]) + float(pix_size[1]))/2.0
        elif p:
            # Match to photometry line
            line2 = log_fh.readline()
            if not line2: break
            m = photom_rms_regex.search(line2)
            image = p.group(1)
            if m:
                image_list = [i[0] for i in images]
                try:
                    image_index = image_list.index(image)
                    images[image_index][1]['dMag'] = m.group(2)
                except ValueError:
                    print("Image not found in list to update")
        elif pos:
            # Match to position added/Moving object detected lines
            line2 = log_fh.readline()
            if not line2: break
            chunks = line2.rstrip().split()
            if dbg: print("Pos match. line2 #chunks=", len(chunks))
            asteroid = {}
            if len(chunks) == 13:
                # Object not known to Astrometrica (not in MPCORB.DAT etc)
                ##   0  1   2               3   4   5               6                7        8         9    10    11     12
                # RAhh mm ss.sss           sdd mm ss.ss           Mag                X        Y       Flux   FWHM  SNR   Fit RMS
                #  10 05 04.994           +03 48 16.27           20.87           2018.73  2063.05    1951   0.8   12.6  0.151
                asteroid['fwhm'] = chunks[10]
                asteroid['snr'] = chunks[11]
            elif len(chunks) == 16:
                # Object known to Astrometrica (in MPCORB.DAT etc)
                ##   0  1   2        3      4   5   6       7       8       9        10      11        12    13    14     15
                # RAhh mm ss.sss  deltaRA? sdd mm ss.ss deltaDec?  Mag   deltaMag    X        Y       Flux   FWHM  SNR   Fit RMS
                #   10 05 13.676   +3.44   +03 56 04.33   +0.58   19.77   -0.21   1650.78   898.43    5327   0.0   18.4  -.---
                asteroid['fwhm'] = chunks[13]
                asteroid['snr'] = chunks[14]
            else:
                print("Unexpected number of fields in line:\n", line2)
            # Read uncertainties line
            line3 = log_fh.readline()
            if not line3: break
            chunks = pos_rms_regex.findall(line3)
            if dbg: print("Pos match. line3 #chunks=", len(chunks))
            if len(chunks) == 3:
                asteroid['rmsRA'] = chunks[0]
                asteroid['rmsDec'] = chunks[1]
                asteroid['rmsMag'] = chunks[2]
            # Read MPC format line, parse and add bits we need later to dict
            line4 = log_fh.readline()
            if not line4: break
            data = parse_dataline(line4.rstrip())
            asteroid['totalid'] = data['totalid']
            asteroid['obsTime'] = data['obsTime']
            if asteroid not in asteroids:
                asteroids.append(asteroid)
            if dbg: print(asteroid)
        if not line: break
    log_fh.close()

    # If we have an aperture radius (in pixels) and a pixel scale (in arcsec), go
    # ahead and compute an aperture radius (in arcsec) and add this into the dict
    # for each asteroid
    if ap_radius_pix and avg_pix_size:
        ap_radius_arcsec = ap_radius_pix * avg_pix_size
        for ast in asteroids:
            ast['photAp'] = ap_radius_arcsec

    return version, images, asteroids

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

def find_astrometrica_log(mpcreport):
    """
    Based on the passed path to the MPCReport.txt file, determine if there is an
    Astrometrica.log in the same directory. If there is, return the path to that
    file.

    Parameters
    ----------
    mpcreport : str
        Path/filename of the MPCReport.txt file

    Returns
    -------
    outFile : str
        Path/filename of the Astrometrica.log file
   """

    log = None
    if mpcreport is None:
        return log

    path = os.path.dirname(mpcreport)
    log = os.path.join(path, 'Astrometrica.log')
    try:
        with open(log) as fh:
            line = fh.readline()
    except IOError:
        print("Could not matching Astrometrica.log to %s in %s" % (os.path.basename(mpcreport), path))
        log = None

    return log

def map_NET_to_catalog(header):
    '''Handle mapping of a possible NET line in the passed set of <header> lines
    to a astrometric catalog'''

    catalog = ''
    # Mapping of Astromerica names to MPC approved names from
    # https://www.minorplanetcenter.net/iau/info/ADESFieldValues.html
    catalog_mapping = {'USNO-SA2.0'  : 'USNOSA2',  # Can't test, don't have CDs
                       'USNO-A2.0'   : 'USNOA2',   # Can't test, don't have CDs
                       'USNO-B1.0'   : 'USNOB1',
                       'UCAC-3'      : 'UCAC3',
                       'UCAC-4'      : 'UCAC4',
                       'URAT-1'      : 'URAT1',    # Failed in Astrometrica, couldn't test
                       'NOMAD'       : 'NOMAD',
                       'CMC-14'      : 'CMC14',    # Failed in Astrometrica, couldn't test
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

def convert_mpcreport_to_psv(mpcreport, outFile, rms_available=False, astrometrica_log=None):
    """
    Convert an Astrometrica-produced MPCReport.txt file in MPC1992 80 column
    format to ADES PSV format.

    Parameters
    ----------
    mpcreport : str
        Path/filename of the MPCReport.txt file
    outFile : str
        Path/filename of the output ADES PSV file
    rms_available : bool, optional
        Whether RMS values for RA, Dec etc are available

    returns
    -------
    num_objects : int
        The number of objects written out (or -1 if nothing could be read from the input)

    References
    ----------
    * https://minorplanetcenter.net/iau/info/ADES.html
    """

    header, body = read_mpcreport_file(mpcreport)
    if len(header) == 0 or len(body) == 0:
        print("No valid data in file")
        return -1
    print("Read %d header lines,%d observation lines from %s" % (len(header), len(body), mpcreport))

    if rms_available and astrometrica_log is not None:
        version, images, asteroids = read_astrometrica_logfile(astrometrica_log)
        fwhm_vals = [float(ast['fwhm']) for ast in asteroids if ast['fwhm'] != '0.0']
        seeing = None
        if len(fwhm_vals) > 0:
            seeing = sum(fwhm_vals)/float(len(fwhm_vals))

    out_fh = open(outFile, 'w')

    # Write obsContext out
    psv_header = parse_header(header)
    if rms_available:
        if version != '':
            psv_header += ("# software" + "\n"
                           "! astrometry " + version + "\n"
                           "! photometry " + version + "\n"
                           "! objectDetection " + version + "\n"
                          )
    psv_header += ("# comment" + "\n"
                   "! line Converted to PSV with " + _converter_version + "\n"
                  )
    print(psv_header.rstrip(), file=out_fh)

    # Define and write obsData header
    tbl_fmt = '%7s|%-11s|%8s|%4s|%-4s|%4s|%-23s|%11s|%11s|%8s|%5s|%6s|%8s|%-5s|%-s'
    tbl_hdr = tbl_fmt % ('permID', 'provID', 'trkSub', 'mode', 'stn', 'prog', 'obsTime', \
        'ra', 'dec', 'astCat', 'mag', 'band', 'photCat', 'notes', 'remarks')
    rms_tbl_fmt = '%7s|%-11s|%8s|%4s|%-4s|%4s|%-23s|%11s|%11s|%5s|%6s|%8s|%5s|%6s|%4s|%8s|%6s|%6s|%6s|%-5s|%-s'
    rms_tbl_hdr = rms_tbl_fmt % ('permID', 'provID', 'trkSub', 'mode', 'stn', 'prog', 'obsTime', \
        'ra', 'dec', 'rmsRA', 'rmsDec', 'astCat', 'mag', 'rmsMag', 'band', 'photCat', \
        'photAp', 'logSNR', 'seeing', 'notes', 'remarks')

    if rms_available:
        print(rms_tbl_hdr, file=out_fh)
    else:
        print(tbl_hdr, file=out_fh)

    # Parse and write out obsData records
    num_objects = 0
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
                # Find asteroid uncertainties in the data read from the Astrometrica.log by
                # matching on the totalid and obsTime
                asteroid = [ast for ast in asteroids if ast['totalid'] == data['totalid'] and ast['obsTime'] == data['obsTime']]
                asteroid = asteroid[0]
                for field in ['rmsRA', 'rmsDec', 'rmsMag', 'photAp']:
                    data[field] = asteroid[field]
                try:
                    logSNR = log10(float(asteroid['snr']))
                    data['logSNR'] = "%6.4f" % logSNR
                except ValueError:
                    data['logSNR'] = '    '
                if asteroid['fwhm'] != '0.0':
                    data['seeing'] = "%6.4f" % (float(asteroid['fwhm']))
                else:
                    # Substitute average seeing
                    data['seeing'] = "%6.4f" % (float(seeing))

                tbl_data = rms_tbl_fmt % (permID, provID, trkSub, data['mode'], data['stn'], \
                    data['prog'], data['obsTime'], data['ra'], data['dec'], data['rmsRA'], data['rmsDec'],\
                    data['astCat'], data['mag'], data['rmsMag'], data['band'], \
                    data['photCat'], data['photAp'], data['logSNR'], data['seeing'], \
                    data['notes'], data['remarks'])
            else:
                tbl_data = tbl_fmt % (permID, provID, trkSub, data['mode'], data['stn'], \
                    data['prog'], data['obsTime'], data['ra'], data['dec'], data['astCat'],\
                    data['mag'], data['band'], data['photCat'], data['notes'], data['remarks'])
            print(tbl_data, file=out_fh)
            num_objects += 1
    out_fh.close()

    return num_objects

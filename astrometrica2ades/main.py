from __future__ import absolute_import
import os
import sys
import argparse

from astrometrica2ades import utils

def parse_args(args):

    parser = argparse.ArgumentParser(description='Convert Astrometrica output to ADES PSV format',
                                     usage='%(prog)s [--sitecode] <MPCReport file> [output PSV file]')
    parser.add_argument('mpcreport', help='Path to MPCReport.txt file')
    parser.add_argument('outFile', nargs='?', help='Output file')
    parser.add_argument('--sitecode', help='Sitecode to process if different from that in MPCReport.txt')

    options = parser.parse_args(args)

    mpcreport = ''
    outFile = ''

    if options.outFile is None:
        mpcreport = options.mpcreport
        outFileName = os.path.basename(mpcreport)
        if '.txt' in outFileName:
            outFileName = outFileName.replace('.txt', '.psv')
        else:
            outFileName += '.psv'
        outFile = os.path.join(os.path.dirname(mpcreport), outFileName)
    else:
        mpcreport = options.mpcreport
        outFile = options.outFile

    return mpcreport, outFile

def convert():

    rms_available = False

    mpcreport, outFile = parse_args(sys.argv[1:])

    log_string = ''
    astrometrica_log = utils.find_astrometrica_log(mpcreport)
    if astrometrica_log:
        rms_available = True
        log_string = ' and ' + astrometrica_log
    print("Reading from: %s%s, writing to: %s" % (mpcreport, log_string, outFile))
    num_objects = utils.convert_mpcreport_to_psv(mpcreport, outFile, rms_available, astrometrica_log)
    if num_objects > 0:
        print("Wrote %d objects to %s" % (num_objects, outFile))
    else:
        print("Error processing file")

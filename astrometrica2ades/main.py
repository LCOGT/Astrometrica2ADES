from __future__ import absolute_import
import os
import sys
from astrometrica2ades import utils

def convert():

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

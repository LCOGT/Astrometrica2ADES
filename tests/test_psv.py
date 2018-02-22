import os

import pytest

from astrometrica2ades import *

class Test_ParseHeader(object):

    def setup_method(self):
        test_mpcreport = os.path.join('tests', 'data', 'MPCReport.txt')
        test_fh = open(test_mpcreport, 'r')
        self.header = []
        self.body = []
        for line in test_fh:
            if line[0:3] in ['COD','CON','OBS','MEA','TEL','ACK','AC2','COM','NET']:
                self.header.append(line.rstrip())
            else:
                self.body.append(line.rstrip())
        test_fh.close()

    def test_COD_header(self):

        expected_header = ("# version=2017" + "\n"
                           "# observatory" + "\n"
                           "! mpcCode G96" + "\n"
                           "! name Catalina Sky Survey" + "\n"
                           )

        header_line = "COD G96"

        header = parse_header(header_line)

        assert expected_header == header

    def test_COD_header_no_name(self):

        expected_header = ("# version=2017" + "\n"
                           "# observatory" + "\n"
                           "! mpcCode G99" + "\n"
                           )

        header_line = "COD G99"

        header = parse_header(header_line)

        assert expected_header == header

    def test_OBS_header(self):

        expected_header = ("# version=2017" + "\n"
                           "# observers" + "\n"
                           "! name R. L. Seaman" + "\n"
                           )

        header_line = "OBS R. L. Seaman"

        header = parse_header(header_line)

        assert expected_header == header

    def test_OBS_header_multi_observers(self):

        expected_header = ("# version=2017" + "\n"
                           "# observers" + "\n"
                           "! name R. L. Seaman" + "\n"
                           "! name E. J. Christensen" + "\n"
                           "! name D. C. Fuls" + "\n"
                           "! name A. R. Gibbs" + "\n"

                           )

        header_line = "OBS R. L. Seaman, E. J. Christensen, D. C. Fuls, A. R. Gibbs"

        header = parse_header(header_line)

        assert expected_header == header

    def test_MEA_header(self):

        expected_header = ("# version=2017" + "\n"
                           "# submitter" + "\n"
                           "! name R. L. Seaman" + "\n"
                           "# measurers" + "\n"
                           "! name R. L. Seaman" + "\n"
                           )

        header_line = "MEA R. L. Seaman"

        header = parse_header(header_line)

        assert expected_header == header

    def test_MEA_header_multi_observers(self):

        expected_header = ("# version=2017" + "\n"
                           "# submitter" + "\n"
                           "! name R. L. Seaman" + "\n"
                           "# measurers" + "\n"
                           "! name R. L. Seaman" + "\n"
                           "! name E. J. Christensen" + "\n"
                           "! name D. C. Fuls" + "\n"
                           "! name A. R. Gibbs" + "\n"

                           )

        header_line = "MEA R. L. Seaman, E. J. Christensen, D. C. Fuls, A. R. Gibbs"

        header = parse_header(header_line)

        assert expected_header == header

    def test_TEL_header(self):
        expected_header = ("# version=2017" + "\n"
                           "# telescope" + "\n"
                           "! aperture 1.5" + "\n"
                           "! design reflector" + "\n"
                           "! detector CCD" + "\n"
                           )

        header_line = "TEL 1.5-m reflector + CCD"

        header = parse_header(header_line)

        assert expected_header == header

    def test_TEL_header_fRatio(self):
        expected_header = ("# version=2017" + "\n"
                           "# telescope" + "\n"
                           "! aperture 1.5" + "\n"
                           "! design reflector" + "\n"
                           "! detector CCD" + "\n"
                           "! fRatio 3.3" + "\n"
                           )

        header_line = "TEL 1.5-m f/3.3 reflector + CCD"

        header = parse_header(header_line)

        assert expected_header == header

    def test_full_header(self):
        expected_header = ( "# version=2017" + "\n"
                            "# observatory" + "\n"
                            "! mpcCode W85" + "\n"
                            "# submitter" + "\n"
                            "! name T. Lister" + "\n"
                            "# observers" + "\n"
                            "! name T. Lister" + "\n"
                            "# measurers" + "\n"
                            "! name T. Lister" + "\n"
                            "# telescope" + "\n"
                            "! aperture 1.0" + "\n"
                            "! design Ritchey-Chretien" + "\n"
                            "! detector CCD" + "\n"
                            "! fRatio 8.0" + "\n"
                           )

        header = parse_header(self.header)

        assert expected_header == header

    def test_submitter_from_config(self):
        expected_header = ( "# version=2017" + "\n"
                            "# observatory" + "\n"
                            "! mpcCode Z99" + "\n"
                            "# submitter" + "\n"
                            "! name J. R. Random" + "\n"
                           )

        header_no_MEA = ("COD Z99" + "\n"
                         )

        header = parse_header(header_no_MEA)

        assert expected_header == header

class Test_ParseBody(object):

    def setup_method(self):
        test_mpcreport = os.path.join('tests', 'data', 'MPCReport.txt')
        test_fh = open(test_mpcreport, 'r')
        self.header = []
        self.body = []
        for line in test_fh:
            if line[0:3] in ['COD','CON','OBS','MEA','TEL','ACK','AC2','COM','NET']:
                self.header.append(line.rstrip())
            else:
                self.body.append(line.rstrip())
        test_fh.close()

    def test_line_too_long(self):

        data_line = self.body[0] + 'foo'
        expected_message = 'Invalid MPC80COL line (83 columns) in line:\n' + data_line

        with pytest.raises(RuntimeError) as e_info:
            data = parse_dataline(data_line)
        assert expected_message == e_info.value.message

    def test_unnumbered(self):
        expected_data = {u'astCat': ' ',
                         u'band': 'G',
                         u'bl1': '         ',
                         u'code': 'C',
                         u'date': '2018 02 16.198172',
                         u'dec': u'-4.41242',
                         u'decSexagesimal': '-04 24 44.7 ',
                         u'disc': ' ',
                         u'mag': '20.2 ',
                         u'mode' : u'CCD',
                         u'notes': 'K',
                         u'obsTime': u'2018-02-16T04:45:22.06Z',
                         u'packedref': '      ',
                         u'permID': None,
                         u'precDec': 0.1,
                         u'precRA': 0.01,
                         u'precTime': 1,
                         u'prog': u'  ',
                         u'provID': u'2017 BT121',
                         u'ra': u'171.72571',
                         u'raSexagesimal': '11 26 54.17 ',
                         u'stn': 'W85',
                         u'subFmt': u'M92',
                         u'totalid': '     K17BC1T',
                         u'trkSub': None}


        data_line = self.body[0]

        data = parse_dataline(data_line)

        assert expected_data == data

class Test_Convert_mpcreport_to_psv:

    def read_file_lines(self, filename):
        test_fh = open(filename, 'r')
        test_lines = test_fh.readlines()
        test_fh.close()
        return test_lines

    @pytest.fixture(autouse=True)
    def setup_method(self, tmpdir):
        self.tmpdir = tmpdir.strpath

        self.test_mpcreport = os.path.join('tests', 'data', 'MPCReport.txt')
        test_psv = os.path.join('tests', 'data', 'MPCReport.psv')
        self.test_psv_lines = self.read_file_lines(test_psv)

    def test_convert(self):
        outfile = os.path.join(self.tmpdir, 'out.psv')
        num_objects = convert_mpcreport_to_psv(self.test_mpcreport, outfile)

        outfile_lines = self.read_file_lines(outfile)
        assert outfile_lines == self.test_psv_lines

class Test_ReadAstrometricaLog(object):

    def setup_method(self):
        self.test_log = os.path.join('tests', 'data', 'Astrometrica.log')

    def test_read(self):
        expected_version = 'Astrometrica 4.10.0.431'
        expected_images = [('lsc1m005-fl15-20180215-0129-e11.fits',
                             {u'dRA': '0.12', u'dDec': '0.10', u'dMag' : '0.10', u'nstars': '439'}),
                           ('lsc1m005-fl15-20180215-0130-e11.fits',
                             {u'dRA': '0.15', u'dDec': '0.09', u'dMag' : '0.09', u'nstars': '383'})
                          ]

        version, images = read_astrometrica_logfile(self.test_log)

        assert expected_version == version
        assert expected_images == images

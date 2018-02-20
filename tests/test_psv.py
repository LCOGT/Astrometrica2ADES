import os

import pytest

from astrometrica2ades import parse_header, parse_dataline

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
                           "# measurers" + "\n"
                           "! name R. L. Seaman" + "\n"
                           )

        header_line = "MEA R. L. Seaman"

        header = parse_header(header_line)

        assert expected_header == header

    def test_MEA_header_multi_observers(self):

        expected_header = ("# version=2017" + "\n"
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
                           "! fRatio f/6" + "\n"
                           )

        header_line = "TEL 1.5-m f/6 reflector + CCD"

        header = parse_header(header_line)

        assert expected_header == header

    def test_full_header(self):
        expected_header = ( "# version=2017" + "\n"
                            "# observatory" + "\n"
                            "! mpcCode W85" + "\n"
                            "# observers" + "\n"
                            "! name T. Lister" + "\n"
                            "# measurers" + "\n"
                            "! name T. Lister" + "\n"
                            "# telescope" + "\n"
                            "! aperture 1.0" + "\n"
                            "! design Ritchey-Chretien" + "\n"
                            "! detector CCD" + "\n"
                            "! fRatio f/8" + "\n"
                           )

        header = parse_header(self.header)

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
                         u'notes': 'K',
                         u'obsTime': u'2018-02-16T04:45:22.06Z',
                         u'packedref': '      ',
                         u'permID': None,
                         u'precDec': 0.1,
                         u'precRA': 0.01,
                         u'precTime': 1,
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

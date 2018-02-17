import os

from astrometrica2ades import parse_header

class Test_ParseHeader(object):

    def setup_method(self):
        test_mpcreport = os.path.join('tests', 'data', 'MPCReport.txt')
        test_fh = open(test_mpcreport, 'r')
        self.header = []
        self.body = []
        for line in test_fh:
            if line[0:3] in ['COD','CON','OBS','MEA','TEL','ACK','AC2','COM','NET']:
                self.header.append(line)
            else:
                self.body.append(line)
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

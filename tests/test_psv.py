from astrometrica2ades import parse_header

class Test_ParseHeader():

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

from astrometrica2ades import parse_header

def test_header():

    expected_header = ("# version=2017" + "\n"
                       "# observatory" + "\n"
                       "! mpcCode G96" + "\n"
                       "! name Catalina Sky Survey" + "\n"
                       )
                    
    header_line = "COD G96"

    header = parse_header(header_line)

    assert expected_header == header

import pytest

from sexVals import checkSexagesimal

class Test_checkSexagesimal(object):

    def setup_method(self):
        self.expected_message = 'Invalid Sexagesimal string (sexagesimal date must be "HH MM SS.ss" not ) in string \n'

    def test_no_minutes1(self):

        line = "12"
        with pytest.raises(RuntimeError) as e_info:
            data = checkSexagesimal(line)
        assert self.expected_message + line == e_info.value.message

    def test_no_minutes2(self):

        line = "12 "
        with pytest.raises(RuntimeError) as e_info:
            data = checkSexagesimal(line)
        assert self.expected_message + line == e_info.value.message

    def test_no_minutes3(self):

        line = "12.1"
        with pytest.raises(RuntimeError) as e_info:
            data = checkSexagesimal(line)
        assert self.expected_message + line == e_info.value.message

    def test_no_minutes4(self):

        line = "12.1 "
        with pytest.raises(RuntimeError) as e_info:
            data = checkSexagesimal(line)
        assert self.expected_message + line == e_info.value.message

    def test_minutes1(self):

        expected_data = (12, 13.1, 0, 6)

        line = "12 13.1 "

        data = checkSexagesimal(line)
        assert expected_data == data

    def test_minutes2(self):

        expected_data = (12, 13, 0, 60)

        line = "12 13   "

        data = checkSexagesimal(line)
        assert expected_data == data

    def test_bad_minutes1(self):

        line = "12 13. "
        with pytest.raises(RuntimeError) as e_info:
            data = checkSexagesimal(line)
        assert self.expected_message + line == e_info.value.message

    def test_seconds1(self):

        expected_data = (12, 13, 14, 1)

        line = "12 13 14"

        data = checkSexagesimal(line)
        assert expected_data == data

    def test_seconds2(self):

        expected_data = (12, 13, 14.5, 0.1)

        line = "12 13 14.5"

        data = checkSexagesimal(line)
        assert expected_data == data

    def test_seconds3(self):

        expected_data = (12, 13, 14.56, 0.01)

        line = "12 13 14.56"

        data = checkSexagesimal(line)
        assert expected_data == data

    def test_seconds4(self):

        expected_data = (12, 13, 14.56, 0.01)

        line = "12 13 14.56  "

        data = checkSexagesimal(line)
        assert expected_data == data

    def test_seconds5(self):

        expected_data = (12, 13, 14.567, 0.001)

        line = "12 13 14.567"

        data = checkSexagesimal(line)
        assert expected_data == data

    def test_bad_seconds1(self):

        line = "12 13 14x5"
        with pytest.raises(RuntimeError) as e_info:
            data = checkSexagesimal(line)
        assert self.expected_message + line == e_info.value.message

    def test_bad_seconds2(self):

        line = "12 13 14.56 x"
        with pytest.raises(RuntimeError) as e_info:
            data = checkSexagesimal(line)
        assert self.expected_message + line == e_info.value.message

    def test_bad_seconds3(self):

        line = " 13 13 14.56  "
        with pytest.raises(RuntimeError) as e_info:
            data = checkSexagesimal(line)
        assert self.expected_message + line == e_info.value.message

#checkSexagesimal("12 13.12 ") #bad - only tenths digid

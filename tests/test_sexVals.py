import pytest

from sexVals import checkSexagesimal, checkDate

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

class Test_checkDate(object):

    def setup_method(self):
        self.expected_message =  'Invalid Sexagesimal string (date  must be "YYYY MM DD.d..." not ) in string \n'
        self.expected_message2 = 'Invalid Sexagesimal string ( Date invalid reverse: %s) in string \n%-17s'
        self.expected_message3 = 'Invalid Sexagesimal string (invalid date for February, should not be ) in string \n'

    def test_bad_month1(self):

        rdict = { 'date' : "1800 00 01.333  " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message + rdict['date'] == e_info.value.message

    def test_bad_day1(self):

        rdict = { 'date' : "1800 01 00.333  " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message + rdict['date'] == e_info.value.message

    def test_bad_day2(self):

        rdict = { 'date' : "1800 01 01    " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message + rdict['date'] == e_info.value.message

    def test_bad_day3(self):

        rdict = { 'date' : "1800 01 01.   " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message + rdict['date'] == e_info.value.message

    def test_bad_day4(self):

        rdict = { 'date' : "1800 01 01.3  " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date']) == e_info.value.message

    def test_bad_day5(self):

        rdict = { 'date' : "1800 01 01.33  " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date']) == e_info.value.message

    def test_bad_day6(self):

        rdict = { 'date' : "1800 01 01.333  " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date']) == e_info.value.message

    def test_bad_day7(self):

        rdict = { 'date' : "1800 01 01.33333  " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date'][:-1]) == e_info.value.message

    def test_bad_day8(self):

        rdict = { 'date' : "1800 01 01.333333 " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date'][:-1]) == e_info.value.message

    def test_bad_day9(self):

        rdict = { 'date' : "1800 01 01.3333333 " }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date'][:-2]) == e_info.value.message

    def test_bad_day9a(self):

        rdict = { 'date' : "1800 01 01.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date'][:-1]) == e_info.value.message

    def test_bad_day9b(self):

        rdict = { 'date' : "1920 01 01.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date'][:-1]) == e_info.value.message

    def test_bad_day9c(self):

        rdict = { 'date' : "1920 09 01.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date'][:-1]) == e_info.value.message

    def test_bad_day9d(self):

        rdict = { 'date' : "1920 10 01.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date'][:-1]) == e_info.value.message

    def test_bad_day9e(self):

        rdict = { 'date' : "1920 11 01.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date'][:-1]) == e_info.value.message

    def test_bad_day9f(self):

        rdict = { 'date' : "1920 12 01.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message2 % (rdict['date'], rdict['date'][:-1]) == e_info.value.message

    def test_bad_day10(self):

        rdict = { 'date' : "2101 03 32.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message + rdict['date'] == e_info.value.message

    def test_bad_day11(self):

        rdict = { 'date' : "2101 02 30.333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message3 + rdict['date'] == e_info.value.message

    def test_bad_day12(self):

        rdict = { 'date' : "2019 02 29.333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message3 + rdict['date'] == e_info.value.message

    def test_bad_day13(self):

        rdict = { 'date' : "1900 02 29.333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message3 + rdict['date'] == e_info.value.message

    def test_bad_month1(self):

        rdict = { 'date' : "1920 1030 01.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message + rdict['date'] == e_info.value.message

    def test_bad_month2(self):

        rdict = { 'date' : "1920 102 01.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message + rdict['date'] == e_info.value.message

    def test_bad_month3(self):

        rdict = { 'date' : "1920 13 01.3333333" }
        with pytest.raises(RuntimeError) as e_info:
            data = checkDate(rdict)
        assert self.expected_message + rdict['date'] == e_info.value.message


    def test_good_day1(self):

        rdict = { 'date' : "1800 01 01.3333  " }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day2(self):

        rdict = { 'date' : "2001 01 01.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day3(self):

        rdict = { 'date' : "2001 01 11.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day4(self):

        rdict = { 'date' : "2001 01 21.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day5(self):

        rdict = { 'date' : "2001 01 28.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day6(self):

        rdict = { 'date' : "2001 01 31.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day7(self):

        rdict = { 'date' : "2001 01 30.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day8(self):

        rdict = { 'date' : "2901 01 01.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day9(self):

        rdict = { 'date' : "2101 01 01.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day10(self):

        rdict = { 'date' : "2101 02 01.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day11(self):

        rdict = { 'date' : "2101 03 01.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day12(self):

        rdict = { 'date' : "2101 03 31.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day13(self):

        rdict = { 'date' : "2101 03 21.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day14(self):

        rdict = { 'date' : "2018 02 28.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day15(self):

        rdict = { 'date' : "2020 02 29.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

    def test_good_day16(self):

        rdict = { 'date' : "2000 02 29.333333" }
        try:
            checkDate(rdict)
        except RuntimeError:
            pytest.fail("Unexpected raise of RuntimeError")

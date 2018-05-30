import os

import pytest

from astrometrica2ades.main import parse_args

class TestParseArgs(object):

    def test_parser_bad_input(self):

        with pytest.raises(SystemExit) as e_info:
            input_file, output_file = parse_args(['code name',])

    def test_parser_no_output_specified(self):
        expected_input = 'MPCReport.txt'
        expected_output = 'MPCReport.psv'

        input_file, output_file = parse_args(['code name', 'MPCReport.txt'])

        assert expected_input == input_file
        assert expected_output == output_file

    def test_parser_output_specified(self):
        expected_input = 'MPCReport.txt'
        expected_output = 'MPCReport_foo.psv'

        input_file, output_file = parse_args(['code name', 'MPCReport.txt', 'MPCReport_foo.psv'])

        assert expected_input == input_file
        assert expected_output == output_file

    def test_parser_path_input_no_output_specified(self):
        path = os.path.join(os.sep, 'tmp', 'foo')
        expected_input = os.path.join(path, 'MPCReport.txt')
        expected_output = os.path.join(path, 'MPCReport.psv')

        input_file, output_file = parse_args(['code name',  os.path.join(path, 'MPCReport.txt')])

        assert expected_input == input_file
        assert expected_output == output_file

    def test_parser_path_input_output_specified(self):
        in_path = os.path.join(os.sep, 'tmp', 'foo')
        out_path = os.path.join(os.sep, 'tmp', 'bar')
        expected_input = os.path.join(in_path, 'MPCReport.txt')
        expected_output = os.path.join(out_path, 'MPCReport_foo.psv')

        input_file, output_file = parse_args(['code name', os.path.join(in_path, 'MPCReport.txt'), os.path.join(out_path, 'MPCReport_foo.psv')])

        assert expected_input == input_file
        assert expected_output == output_file

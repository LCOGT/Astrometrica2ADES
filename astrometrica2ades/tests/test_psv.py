import os

import pytest
import pkg_resources

from astrometrica2ades.utils import *

class Test_ParseHeader(object):

    def setup_method(self):
        test_mpcreport = pkg_resources.resource_filename(__package__, os.path.join('data', 'MPCReport.txt'))

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

        expected_header = ("# version=2022" + "\n"
                           "# observatory" + "\n"
                           "! mpcCode G96" + "\n"
                           "! name Catalina Sky Survey" + "\n"
                           )

        header_line = "COD G96"

        header = parse_header(header_line)

        assert expected_header == header

    def test_COD_header_no_name(self):

        expected_header = ("# version=2022" + "\n"
                           "# observatory" + "\n"
                           "! mpcCode G99" + "\n"
                           )

        header_line = "COD G99"

        header = parse_header(header_line)

        assert expected_header == header

    def test_OBS_header(self):

        expected_header = ("# version=2022" + "\n"
                           "# observers" + "\n"
                           "! name R. L. Seaman" + "\n"
                           )

        header_line = "OBS R. L. Seaman"

        header = parse_header(header_line)

        assert expected_header == header

    def test_OBS_header_multi_observers(self):

        expected_header = ("# version=2022" + "\n"
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

        expected_header = ("# version=2022" + "\n"
                           "# submitter" + "\n"
                           "! name R. L. Seaman" + "\n"
                           "# measurers" + "\n"
                           "! name R. L. Seaman" + "\n"
                           )

        header_line = "MEA R. L. Seaman"

        header = parse_header(header_line)

        assert expected_header == header

    def test_MEA_header_multi_observers(self):

        expected_header = ("# version=2022" + "\n"
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
        expected_header = ("# version=2022" + "\n"
                           "# telescope" + "\n"
                           "! aperture 1.5" + "\n"
                           "! design reflector" + "\n"
                           "! detector CCD" + "\n"
                           )

        header_line = "TEL 1.5-m reflector + CCD"

        header = parse_header(header_line)

        assert expected_header == header

    def test_TEL_header_fRatio(self):
        expected_header = ("# version=2022" + "\n"
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
        expected_header = ( "# version=2022" + "\n"
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
        expected_header = ( "# version=2022" + "\n"
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
        test_mpcreport = pkg_resources.resource_filename(__package__, os.path.join('data', 'MPCReport.txt'))

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
        assert expected_message == str(e_info.value)

    def test_line_not_a_line(self):

        data_line = None
        expected_data = {}

        data = parse_dataline(data_line)
        assert expected_data == data

    def test_line_satellite_line(self):

        data_line = '     K13J22N  S2018 02 28.02505 16 47 10.53 +01 01 26.6          19   RLEE024C51'
        expected_message = 'Invalid MPC80COL line (no match for line) in line:\n' + data_line

        with pytest.raises(RuntimeError) as e_info:
            data = parse_dataline(data_line)
        assert expected_message == str(e_info.value)

    def test_line_invalid_note(self):

        data_line = '     K13J22N ZC2018 02 28.02505 16 47 10.53 +01 01 26.6          19.0 RLEE024F51'
        expected_message = 'Invalid MPC80COL line (invalid note Z in line ) in line:\n' + data_line

        with pytest.raises(RuntimeError) as e_info:
            data = parse_dataline(data_line)
        assert expected_message == str(e_info.value)

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

class Test_ReadAstrometricaLog(object):

    def setup_method(self):
        self.test_log = pkg_resources.resource_filename(__package__, os.path.join('data', 'Astrometrica.log'))

    def test_read(self):
        expected_version = 'Astrometrica 4.10.0.431'
        expected_images = [('lsc1m005-fl15-20180215-0129-e11.fits',
                             {u'dRA': '0.12', u'dDec': '0.10', u'dMag' : '0.10', u'nstars': '439'}),
                           ('lsc1m005-fl15-20180215-0130-e11.fits',
                             {u'dRA': '0.15', u'dDec': '0.09', u'dMag' : '0.09', u'nstars': '383'})
                          ]
        expected_asteroids = [{u'totalid' : '     P10GvKl', u'obsTime' : u'2018-02-16T04:45:22.06Z', u'rmsRA' : '0.15', u'rmsDec' : '0.10', u'rmsMag' : '0.11', u'snr' : '4.3', u'fwhm' : '0.0', u'photAp': 1.56},
                              {u'totalid' : '     P10GvKl', u'obsTime' : u'2018-02-16T04:53:15.88Z', u'rmsRA' : '0.16', u'rmsDec' : '0.11', u'rmsMag' : '0.14', u'snr' : '1.4', u'fwhm' : '0.0', u'photAp': 1.56},
                              {u'totalid' : '     P10GvKl', u'obsTime' : u'2018-02-16T05:03:48.76Z', u'rmsRA' : '0.13', u'rmsDec' : '0.12', u'rmsMag' : '0.04', u'snr' : '7.9', u'fwhm' : '0.9', u'photAp': 1.56},
                              {u'totalid' : '     K17BC1T', u'obsTime' : u'2018-02-16T04:45:22.06Z', u'rmsRA' : '0.16', u'rmsDec' : '0.10', u'rmsMag' : '0.02', u'snr' : '18.9', u'fwhm' : '1.1', u'photAp': 1.56},
                              {u'totalid' : 'W2017       ', u'obsTime' : u'2018-02-16T04:45:22.06Z', u'rmsRA' : '0.16', u'rmsDec' : '0.11', u'rmsMag' : '0.02', u'snr' : '16.2', u'fwhm' : '1.1', u'photAp': 1.56},
                              {u'totalid' : 'W2017       ', u'obsTime' : u'2018-02-16T04:53:15.88Z', u'rmsRA' : '0.16', u'rmsDec' : '0.11', u'rmsMag' : '0.02', u'snr' : '18.9', u'fwhm' : '1.0', u'photAp': 1.56},
                              {u'totalid' : '     K17BC1T', u'obsTime' : u'2018-02-16T04:53:15.88Z', u'rmsRA' : '0.16', u'rmsDec' : '0.12', u'rmsMag' : '0.02', u'snr' : '19.0', u'fwhm' : '1.9', u'photAp': 1.56},
                              {u'totalid' : '     K17BC1T', u'obsTime' : u'2018-02-16T05:03:48.76Z', u'rmsRA' : '0.12', u'rmsDec' : '0.11', u'rmsMag' : '0.02', u'snr' : '19.3', u'fwhm' : '1.0', u'photAp': 1.56},
                              {u'totalid' : 'W2017       ', u'obsTime' : u'2018-02-16T05:03:48.76Z', u'rmsRA' : '0.12', u'rmsDec' : '0.11', u'rmsMag' : '0.02', u'snr' : '17.5', u'fwhm' : '1.0', u'photAp': 1.56},
                              {u'totalid' : 'l8269       ', u'obsTime' : u'2018-02-16T04:45:22.06Z', u'rmsRA' : '0.15', u'rmsDec' : '0.10', u'rmsMag' : '0.13', u'snr' : '1.1', u'fwhm' : '0.0', u'photAp': 1.56},
                              {u'totalid' : 'l8269       ', u'obsTime' : u'2018-02-16T04:53:15.88Z', u'rmsRA' : '0.17', u'rmsDec' : '0.13', u'rmsMag' : '0.06', u'snr' : '7.3', u'fwhm' : '1.3', u'photAp': 1.56},
                              {u'totalid' : 'l8269       ', u'obsTime' : u'2018-02-16T05:03:48.76Z', u'rmsRA' : '0.13', u'rmsDec' : '0.11', u'rmsMag' : '0.09', u'snr' : '5.4', u'fwhm' : '0.6', u'photAp': 1.56},
                              {u'totalid' : 'K8785       ', u'obsTime' : u'2018-02-16T04:45:22.06Z', u'rmsRA' : '0.15', u'rmsDec' : '0.10', u'rmsMag' : '0.05', u'snr' : '6.6', u'fwhm' : '0.0', u'photAp': 1.56},
                              {u'totalid' : 'K8785       ', u'obsTime' : u'2018-02-16T04:53:15.88Z', u'rmsRA' : '0.16', u'rmsDec' : '0.12', u'rmsMag' : '0.02', u'snr' : '13.6', u'fwhm' : '1.0', u'photAp': 1.56},
                              {u'totalid' : 'K8785       ', u'obsTime' : u'2018-02-16T05:03:48.76Z', u'rmsRA' : '0.15', u'rmsDec' : '0.14', u'rmsMag' : '0.03', u'snr' : '8.7', u'fwhm' : '1.8', u'photAp': 1.56},
                              {u'totalid' : 'm1820       ', u'obsTime' : u'2018-02-16T04:45:22.06Z', u'rmsRA' : '0.23', u'rmsDec' : '0.20', u'rmsMag' : '0.05', u'snr' : '6.7', u'fwhm' : '2.7', u'photAp': 1.56},
                              {u'totalid' : 'm1820       ', u'obsTime' : u'2018-02-16T04:53:15.88Z', u'rmsRA' : '0.19', u'rmsDec' : '0.16', u'rmsMag' : '0.05', u'snr' : '6.5', u'fwhm' : '1.6', u'photAp': 1.56},
                              {u'totalid' : 'm1820       ', u'obsTime' : u'2018-02-16T05:03:48.76Z', u'rmsRA' : '0.13', u'rmsDec' : '0.12', u'rmsMag' : '0.06', u'snr' : '5.4', u'fwhm' : '0.7', u'photAp': 1.56},
                             ]

        version, images, asteroids = read_astrometrica_logfile(self.test_log)

        assert expected_version == version
        assert expected_images == images
        assert expected_asteroids == asteroids

    def test_read_moving_objects(self):
        test_log = pkg_resources.resource_filename(__package__, os.path.join('data', 'Astrometrica_moving_obj.log'))
        expected_version = 'Astrometrica 4.10.0.431'
        expected_images = [('elp0m411-kb80-20180305-0769-e91.fits',
                             {u'dRA': '0.12', u'dDec': '0.10', u'dMag' : '0.13', u'nstars': '35'}),
                          ]
        expected_asteroids = [{u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:47:45.20Z', u'rmsRA' : '0.16', u'rmsDec' : '0.15', u'rmsMag' : '0.01', u'snr' : '54.8', u'fwhm' : '2.1', u'photAp': 3.42},
                              {u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:47:52.54Z', u'rmsRA' : '0.16', u'rmsDec' : '0.18', u'rmsMag' : '0.01', u'snr' : '55.5', u'fwhm' : '2.1', u'photAp': 3.42},
                              {u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:47:59.28Z', u'rmsRA' : '0.13', u'rmsDec' : '0.12', u'rmsMag' : '0.01', u'snr' : '54.7', u'fwhm' : '2.1', u'photAp': 3.42},
                              {u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:48:06.19Z', u'rmsRA' : '0.14', u'rmsDec' : '0.15', u'rmsMag' : '0.01', u'snr' : '59.4', u'fwhm' : '1.9', u'photAp': 3.42},
                              {u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:48:13.02Z', u'rmsRA' : '0.10', u'rmsDec' : '0.15', u'rmsMag' : '0.01', u'snr' : '53.0', u'fwhm' : '2.2', u'photAp': 3.42},
                              {u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:48:19.76Z', u'rmsRA' : '0.13', u'rmsDec' : '0.14', u'rmsMag' : '0.01', u'snr' : '57.2', u'fwhm' : '2.0', u'photAp': 3.42},
                              {u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:48:26.58Z', u'rmsRA' : '0.16', u'rmsDec' : '0.17', u'rmsMag' : '0.01', u'snr' : '60.5', u'fwhm' : '1.9', u'photAp': 3.42},
                              {u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:48:33.41Z', u'rmsRA' : '0.13', u'rmsDec' : '0.13', u'rmsMag' : '0.01', u'snr' : '60.7', u'fwhm' : '1.9', u'photAp': 3.42},
                              {u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:48:40.23Z', u'rmsRA' : '0.11', u'rmsDec' : '0.14', u'rmsMag' : '0.01', u'snr' : '57.9', u'fwhm' : '2.0', u'photAp': 3.42},
                              {u'totalid' : '     K17V12R', u'obsTime' : u'2018-03-06T09:48:47.15Z', u'rmsRA' : '0.12', u'rmsDec' : '0.10', u'rmsMag' : '0.01', u'snr' : '61.6', u'fwhm' : '1.9', u'photAp': 3.42},
                             ]
        version, images, asteroids = read_astrometrica_logfile(test_log)

        assert expected_version == version
        assert expected_images == images
        assert expected_asteroids == asteroids

class Test_FindAstrometricaLog(object):

    def test_existing(self):

        expected_log = pkg_resources.resource_filename(__package__, os.path.join('data', 'Astrometrica.log'))

        mpcreport =  pkg_resources.resource_filename(__package__, os.path.join('data', 'MPCReport.txt'))

        log = find_astrometrica_log(mpcreport)

        assert expected_log == log

    def test_non_existing(self):

        expected_log = None

        mpcreport =  pkg_resources.resource_filename(__package__, os.path.join('tests', 'MPCReport.txt'))

        log = find_astrometrica_log(mpcreport)

        assert expected_log == log

    def test_non_existing_none(self):

        expected_log = None

        log = find_astrometrica_log(None)

        assert expected_log == log

class Test_DataModify(object):

    def test_round_mag(self):

        line = '     K18D01E KC2018 03 01.16162913 06 26.33 -23 24 51.0          20.78G      W87'

        expected_data = {u'astCat': ' ',
                         u'photCat' : ' ',
                         u'remarks' : u'',
                         u'band': 'G',
                         u'bl1': '         ',
                         u'code': 'C',
                         u'date': '2018 03 01.161629',
                         u'dec': u'-23.41417',
                         u'decSexagesimal': '-23 24 51.0 ',
                         u'disc': ' ',
                         u'mag': '20.8 ',
                         u'mode': u'CCD',
                         u'notes': 'K',
                         u'obsTime': u'2018-03-01T03:52:44.75Z',
                         u'packedref': '      ',
                         u'permID': u'',
                         u'precDec': 0.1,
                         u'precRA': 0.01,
                         u'precTime': 1,
                         u'prog': u'  ',
                         u'provID': u'2018 DE1',
                         u'ra': u'196.60971',
                         u'raSexagesimal': '13 06 26.33 ',
                         u'stn': 'W87',
                         u'subFmt': u'M92',
                         u'totalid': '     K18D01E',
                         u'trkSub': u''}

        data = parse_and_modify_data(line, display=False)

        assert expected_data == data

    def test_round_mag_with_cat(self):

        line = '     K18D01E KC2018 03 01.16162913 06 26.33 -23 24 51.0          20.78G      W87'

        expected_data = {u'astCat': 'Gaia1',
                         u'photCat' : 'Gaia1',
                         u'remarks' : u'',
                         u'band': 'G',
                         u'bl1': '         ',
                         u'code': 'C',
                         u'date': '2018 03 01.161629',
                         u'dec': u'-23.41417',
                         u'decSexagesimal': '-23 24 51.0 ',
                         u'disc': ' ',
                         u'mag': '20.8 ',
                         u'mode': u'CCD',
                         u'notes': 'K',
                         u'obsTime': u'2018-03-01T03:52:44.75Z',
                         u'packedref': '      ',
                         u'permID': u'',
                         u'precDec': 0.1,
                         u'precRA': 0.01,
                         u'precTime': 1,
                         u'prog': u'  ',
                         u'provID': u'2018 DE1',
                         u'ra': u'196.60971',
                         u'raSexagesimal': '13 06 26.33 ',
                         u'stn': 'W87',
                         u'subFmt': u'M92',
                         u'totalid': '     K18D01E',
                         u'trkSub': u''}

        data = parse_and_modify_data(line, ast_catalog='Gaia1', display=False)

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

        self.test_mpcreport = pkg_resources.resource_filename(__package__, os.path.join('data', 'MPCReport.txt'))
        self.test_log = pkg_resources.resource_filename(__package__, os.path.join('data', 'Astrometrica.log'))

        test_psv = pkg_resources.resource_filename(__package__, os.path.join('data', 'MPCReport.psv'))
        self.test_psv_lines = self.read_file_lines(test_psv)
        test_psv_rms = pkg_resources.resource_filename(__package__, os.path.join('data', 'MPCReport_rms.psv'))
        self.test_psv_rms_lines = self.read_file_lines(test_psv_rms)
        test_psv_multisite = pkg_resources.resource_filename(__package__, os.path.join('data', 'MPCReport_multisite.psv'))
        self.test_psv_multisite_lines = self.read_file_lines(test_psv_multisite)

        self.outfile = os.path.join(self.tmpdir, 'out.psv')

    def test_convert(self):
        num_objects = convert_mpcreport_to_psv(self.test_mpcreport, self.outfile, display=False)

        outfile_lines = self.read_file_lines(self.outfile)
        assert outfile_lines == self.test_psv_lines

    def test_convert_with_rms(self):
        num_objects = convert_mpcreport_to_psv(self.test_mpcreport, self.outfile, True, self.test_log, display=False)

        outfile_lines = self.read_file_lines(self.outfile)
        for (in_line, out_line) in zip(self.test_psv_rms_lines, outfile_lines):
            assert out_line == in_line

    def test_missing_file(self):
        num_objects = convert_mpcreport_to_psv('foobarbiff', self.outfile)

        assert -1 == num_objects

    def test_no_asteroids(self):
        self.test_log = pkg_resources.resource_filename(__package__, os.path.join('data', 'Astrometrica_noasts.log'))
        num_objects = convert_mpcreport_to_psv(self.test_mpcreport, self.outfile, True, self.test_log, display=False)

        outfile_lines = self.read_file_lines(self.outfile)
        for (in_line, out_line) in zip(self.test_psv_lines, outfile_lines):
            assert out_line == in_line

    def test_multiple_sites(self):
        self.test_mpcreport = pkg_resources.resource_filename(__package__, os.path.join('data', 'MPCReport_multisite.txt'))
        self.test_log = pkg_resources.resource_filename(__package__, os.path.join('data', 'Astrometrica_multisite.log'))
        num_objects = convert_mpcreport_to_psv(self.test_mpcreport, self.outfile, True, self.test_log, display=False)

        outfile_lines = self.read_file_lines(self.outfile)
        for (in_line, out_line) in zip(self.test_psv_multisite_lines, outfile_lines):
            assert out_line == in_line

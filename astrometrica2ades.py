#!/usr/bin/env python

from __future__ import print_function
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

def parse_header(header_lines):

    version_string = "# version=2017"
    observatory = observers = measurers = telescope = ''

    if type(header_lines) != list:
        header_lines = [header_lines,]
    for line in header_lines:
        if line[0:3] == 'COD':
            observatory = parse_obscode(line[4:])
        elif line[0:3] == 'OBS':
            observers = parse_observers(line[4:])
        elif line[0:3] == 'MEA':
            measurers = parse_measurers(line[4:])
        elif line[0:3] == 'TEL':
            measurers = parse_telescope(line[4:])
    header = version_string + '\n'
    if observatory != '':
        header += observatory
    if observers != '':
        header += observers
    if measurers != '':
        header += measurers
    return header

def parse_obscode(code_line):
    config = configparser.ConfigParser()
    config.read('config.ini')

    site_code = code_line.strip()
    try:
        site_name = config.get('OBSERVATORY', site_code + '_SITE_NAME')
    except configparser.NoOptionError:
        site_name = None
    observatory = ( "# observatory" + "\n"
                    "! mpcCode " + site_code + "\n")
    if site_name:
        observatory += "! name " + site_name +"\n"

    return observatory

def parse_observers(code_line):

    observers = ''

    obs = code_line.split(',')
    if len(obs) >= 1:
        observers = '# observers\n'
        for observer in obs:
            observers += "! name " + observer.strip() + "\n"
    return observers

def parse_measurers(code_line):

    measurers = ''

    meas = code_line.split(',')
    if len(meas) >= 1:
        measurers = '# measurers\n'
        for measurer in meas:
            measurers += "! name " + measurer.strip() + "\n"
    return measurers

def parse_telescope(code_line):

    telescope = ''
    tel_string, detector = code_line.split('+')
    tel_chunks = tel_string.strip().split(' ')
    aperture = tel_chunks[0][:-2]
    if len(tel_chunks) == 2:
        design = tel_chunks[1]
        f_ratio = ''
    elif len(tel_chunks) == 3:
        f_ratio = tel_chunks[1]
        design = tel_chunks[2]

    telescope = ("# telescope" + "\n"
                 "! aperture " + aperture + "\n"
                 "! design " + design + "\n"
                 "! detector " + detector.strip() + "\n"
                )

    if f_ratio != '':
        telescope += "! fRatio " + f_ratio + "\n"

    return telescope

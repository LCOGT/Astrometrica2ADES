*******************************
Astrometrica2ADES Documentation
*******************************

This code is a converter for MPC1992 80 column format produced by Herbert Raab's 
Astrometrica program into the Minor Planet Center (MPC)'s new Astrometry Data 
Exchange Standard (ADES) format.

Installation
============
The Python code is written as a standalone package and be installed in the 
usual way::

    python setup.py install

Running the code
================

After installation, you can run the code by typing::

    astrometrica2ades <MPCReport file> [output PSV file]

where <MPCReport file> can include a path. By default the output file is named 
'MPCReport.psv' and will appear in the same directory. This can be overridden
by specifying the [output PSV file].

If an 'Astrometrica.log' file can be found in the same directory as the
MPCReport.txt file, additional information on the software version, the RMS in
RA, Dec and magnitude, the aperture size used, the signal-to-noise ratio and
the seeing/FWHM of the measured asteroid will be included.


Reference/API
=============

.. automodapi:: astrometrica2ades

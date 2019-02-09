from __future__ import absolute_import, print_function, unicode_literals
import pytest

from astrometrica2ades.packUtil import *

class Test_pack_unpack_prog_id(object):

    def test_pack_no_note(self):
        expected_prog = '20'

        notes = ' '

        prog = packProgID(notes)

        assert expected_prog == prog

    def test_pack_I_note(self):
        expected_prog = '49'

        notes = 'I'

        prog = packProgID(notes)

        assert expected_prog == prog

    def test_pack_prog_code(self):
        expected_prog = '25'

        notes = '%'

        prog = packProgID(notes)

        assert expected_prog == prog

    def test_unpack_no_note(self):
        expected_prog = ' '

        notes = '20'

        prog = unpackProgID(notes)

        assert expected_prog == prog

    def test_unpack_I_note(self):
        expected_prog = 'I'

        notes = '49'

        prog = unpackProgID(notes)

        assert expected_prog == prog

    def test_unpack_prog_code(self):
        expected_prog = '%'

        notes = '25'

        prog = unpackProgID(notes)

        assert expected_prog == prog


class TestConversions(object):

    @pytest.mark.skip()
    def testConverter(self, string, expected, converter, stream=sys.stdout):
       """ test the converter, such as packedID -> (permID, provID, trkSub) translation 
           Inputs:
             string: string to be converted
             expected: expected conversion,  or None if invalid
             converter: converter, such as packedTupleID
             stream: streaom on which to print result
           Errors: None
    
           This routine prints the result on stream
       """
       if expected is None:  # expect error
          try:
             val = converter(string)
             print (val, file=stream)
             raise RuntimeError("BAD")
          except RuntimeError as e:
                if str(e) == "BAD":
                   print ("  BAD: EXPECTED ERROR AND GOT NONE FOR", string, file=stream)
                else:
                   print ("  OK: ", e, file=stream)
       else:      # expect OK
          try:
             val = converter(string)
             assert val == expected, "  BAD:  expected " + repr(expected) + " and got " + repr(val) + " for " + repr(string)
          except RuntimeError as e:
                print ("  BAD: ", e, file=stream)
    
    @pytest.mark.skip()
    def testPackedRoundTrip(self, s):  # test for round-trip
        """ testPackedRoundTrip checks to see whether packed ID s round-trips
            Input:
              s:  a packed ID
            Output:
              True
            Errors:
              RuntimeError if s does not round-trip
        """
            
        try:
          t = unpackPackedID(s)
        except:
          t = None
        try:
          u = packTupleID(t)
        except:
          u = None
        assert s == u, "Bad RoundTrip: " + repr(s) + " vs. " + repr(u) + " through " + repr(t)
        return True
    
    def testCases(self, stream=sys.stdout):
       """ testCases is a collection of test cases """
       #
       # demonstrate conversions
       #
       print (file=stream)
       print ("test to demonstrate A-Za-z number conversion", file=stream)
       for i in range(len(packLetters)):
          print(i, packLetters[i], unpackLetters[packLetters[i]], file=stream)
    
       #
       # test broken test report
       #
       print (file=stream)
       print ("test error handler for good cases marked as bad", file=stream)
       self.testConverter('00001       ', None, unpackPackedID, stream) # test error handler
       
    
       #
       # test full packed ID
       #
       print (file=stream)
       print ("test packed ID -> unnpacked", file=stream)
       self.testConverter("     K14A00A", (None, '2014 AA', None), unpackPackedID, stream)
       self.testConverter("00001       ", ('1', None, None), unpackPackedID, stream)
       self.testConverter("12345       ", ('12345', None, None), unpackPackedID, stream)
       self.testConverter("z9999       ", ('619999', None, None), unpackPackedID, stream)
       self.testConverter("B0001       ", ('110001', None, None), unpackPackedID, stream)
       self.testConverter("C1234K14A00A", ('121234', '2014 AA', None), unpackPackedID, stream)
       self.testConverter("00001K14A00A", ('1', '2014 AA', None), unpackPackedID, stream)
       self.testConverter("     K14A00A", (None, '2014 AA', None), unpackPackedID, stream)
       self.testConverter("     K14B01A", (None, '2014 BA1', None), unpackPackedID, stream)
       self.testConverter("     K14Aa0A", (None, '2014 AA360', None), unpackPackedID, stream)
       self.testConverter("     K14Az9Q", (None, '2014 AQ619', None), unpackPackedID, stream)
       self.testConverter("     J97B06A", (None, '1997 BA6', None), unpackPackedID, stream)
    
       self.testConverter('     PLS4007', (None, '4007 P-L', None), unpackPackedID, stream)
       self.testConverter('     T1S4568', (None, '4568 T-1', None), unpackPackedID, stream)
       self.testConverter('     T2S1238', (None, '1238 T-2', None), unpackPackedID, stream)
       self.testConverter('     T3S1438', (None, '1438 T-3', None), unpackPackedID, stream)
       self.testConverter('01234PLS4007', ('1234', '4007 P-L', None), unpackPackedID, stream)
       self.testConverter('01234T1S4568', ('1234', '4568 T-1', None), unpackPackedID, stream)
       self.testConverter('01234T2S1238', ('1234', '1238 T-2', None), unpackPackedID, stream)
       self.testConverter('01234T3S1438', ('1234', '1438 T-3', None), unpackPackedID, stream)
    
       self.testConverter("a0001K14A00A", ('360001', '2014 AA', None), unpackPackedID, stream)
       self.testConverter("07968J96N020", ('7968', 'A/1996 N2', None), unpackPackedID, stream)
       self.testConverter("     T1S4007", (None, '4007 T-1', None), unpackPackedID, stream)
       self.testConverter("     I98V00F", (None, '1898 VF', None), unpackPackedID, stream)
       self.testConverter("     A      ", (None, None, 'A'), unpackPackedID, stream)
       self.testConverter("     A000   ", (None, None, 'A000'), unpackPackedID, stream)
       self.testConverter("     A00001 ", (None, None, 'A00001'), unpackPackedID, stream)
       self.testConverter("     P00001 ", (None, None, 'P00001'), unpackPackedID, stream)
       self.testConverter("     PL0001 ", (None, None, 'PL0001'), unpackPackedID, stream)
       self.testConverter("     T10001 ", (None, None, 'T10001'), unpackPackedID, stream)
       self.testConverter("     A00001X", (None, None, 'A00001X'), unpackPackedID, stream)
       self.testConverter("     KA0001X", (None, None, 'KA0001X'), unpackPackedID, stream)
       self.testConverter("     K0A001X", (None, None, 'K0A001X'), unpackPackedID, stream)
       self.testConverter("     K00001X", (None, None, 'K00001X'), unpackPackedID, stream)
       self.testConverter("     K0a00", (None, None, 'K0a00'), unpackPackedID, stream)
       self.testConverter("     K0a00xx", (None, None, 'K0a00xx'), unpackPackedID, stream)
       self.testConverter("     K00a01X", (None, None, 'K00a01X'), unpackPackedID, stream)
       self.testConverter("     K00H01X", (None, '2000 HX1', None), unpackPackedID, stream)
       self.testConverter("     K00001X", (None, None, 'K00001X'), unpackPackedID, stream)
       self.testConverter("     K00I01X", (None, None, 'K00I01X'), unpackPackedID, stream)
       self.testConverter("     K00A0AX", (None, None, 'K00A0AX'), unpackPackedID, stream)
       self.testConverter("     K00001x", (None, None, 'K00001x'), unpackPackedID, stream)
       self.testConverter("     J000013", (None, None, 'J000013'), unpackPackedID, stream)
       self.testConverter("     P00001A", (None, None, 'P00001A'), unpackPackedID, stream)
       self.testConverter("     P00001z", (None, None, 'P00001z'), unpackPackedID, stream)
       self.testConverter("     P000010", (None, None, 'P000010'), unpackPackedID, stream)
       self.testConverter("     T000010", (None, None, 'T000010'), unpackPackedID, stream)
       self.testConverter("     PL0001X", (None, None, 'PL0001X'), unpackPackedID, stream)
       self.testConverter("     T30001Q", (None, None, 'T30001Q'), unpackPackedID, stream)
       self.testConverter("     T200010", (None, None, 'T200010'), unpackPackedID, stream)
       self.testConverter("     PLSa210", (None, None, 'PLSa210'), unpackPackedID, stream)
       self.testConverter("     PLS2a10", (None, None, 'PLS2a10'), unpackPackedID, stream)
       self.testConverter("     PLS20x0", (None, None, 'PLS20x0'), unpackPackedID, stream)
       self.testConverter("     PLS001X", (None, None, 'PLS001X'), unpackPackedID, stream)
       self.testConverter("     T3S001Q", (None, None, 'T3S001Q'), unpackPackedID, stream)
    
       self.testConverter("0073P       ", ('73P', None, None), unpackPackedID, stream)
       self.testConverter("1234P       ", ('1234P', None, None), unpackPackedID, stream)
       self.testConverter("0003D       ", ('3D', None, None), unpackPackedID, stream)
       self.testConverter( '    CJ95A010', (None, 'C/1995 A1', None), unpackPackedID, stream)
       self.testConverter( '    PJ94P01b', (None, 'P/1994 P1-B', None), unpackPackedID, stream)
       self.testConverter( '    CJ94P010', (None, 'C/1994 P1', None), unpackPackedID, stream)
       self.testConverter( '    CK48X130', (None, 'C/2048 X13', None), unpackPackedID, stream)
       self.testConverter( '    CK33L89c', (None, 'C/2033 L89-C', None), unpackPackedID, stream)
       self.testConverter( '    CK88AA30', (None, 'C/2088 A103', None), unpackPackedID, stream)
       self.testConverter( '    CJ99K070', (None, 'C/1999 K7', None), unpackPackedID, stream)
       self.testConverter( '    DJ99K070', (None, 'D/1999 K7', None), unpackPackedID, stream)
       self.testConverter( '    PI86S010', (None, 'P/1886 S1', None), unpackPackedID, stream)
       self.testConverter( '    DJ94P01b', (None, 'D/1994 P1-B', None), unpackPackedID, stream)
       self.testConverter( '    PJ94P01b', (None, 'P/1994 P1-B', None), unpackPackedID, stream)
       self.testConverter( '    PJ96J01a', (None, 'P/1996 J1-A', None), unpackPackedID, stream)
       self.testConverter( '    PJ98Q54P', (None, 'P/1998 QP54', None), unpackPackedID, stream)
       self.testConverter( '    CJ97B06A', (None, 'C/1997 BA6', None), unpackPackedID, stream)
       self.testConverter( '    PJ98Q00P', (None, 'P/1998 QP', None), unpackPackedID, stream)
       self.testConverter( '    PK01ND10', (None, 'P/2001 N131', None), unpackPackedID, stream)
       self.testConverter( '    PK10V10b', (None, 'P/2010 V10-B', None), unpackPackedID, stream)
       self.testConverter( '    DI94F010', (None, 'D/1894 F1', None), unpackPackedID, stream)
       self.testConverter( '    DJ93F02e', (None, 'D/1993 F2-E', None), unpackPackedID, stream)
       self.testConverter( '    XJ87A020', (None, 'X/1987 A2', None), unpackPackedID, stream)
       self.testConverter( '    AJ87A020', (None, 'A/1987 A2', None), unpackPackedID, stream)
       self.testConverter( '    IK20A020', (None, 'I/2020 A2', None), unpackPackedID, stream)
       self.testConverter( '0141PJ94P01a', ('141P-A', 'P/1994 P1-A', None), unpackPackedID, stream)
       self.testConverter( '0001PI35P010', ('1P', 'P/1835 P1', None), unpackPackedID, stream)
       self.testConverter( '0073P     af', ('73P-AF', None, None), unpackPackedID, stream)
       self.testConverter( '0073P      g', ('73P-G', None, None), unpackPackedID, stream)
    
       self.testConverter("J001S       ", ('Jupiter 1', None, None), unpackPackedID, stream)
       self.testConverter("S005S       ", ('Saturn 5', None, None), unpackPackedID, stream)
       self.testConverter("N013S       ", ('Neptune 13', None, None), unpackPackedID, stream)
       self.testConverter("U101S       ", ('Uranus 101', None, None), unpackPackedID, stream)
       self.testConverter("J001SG10J010", ('Jupiter 1', 'S/1610 J 1', None), unpackPackedID, stream)
    
       self.testConverter("    SG10J010", (None, 'S/1610 J 1', None), unpackPackedID, stream)
       self.testConverter("    SK10JB10", (None, 'S/2010 J 111', None), unpackPackedID, stream)
       self.testConverter('    SK01U090', (None, 'S/2001 U 9', None), unpackPackedID, stream)
       self.testConverter('    SK01S310', (None, 'S/2001 S 31', None), unpackPackedID, stream)
       self.testConverter('    SK01JD10', (None, 'S/2001 J 131', None), unpackPackedID, stream)
       self.testConverter('    SK01ND10', (None, 'S/2001 N 131', None), unpackPackedID, stream)
    
       self.testConverter("    SAab102 ", None, unpackPackedID, stream)
       self.testConverter("0a001K14A00A", None, unpackPackedID, stream)
    
       self.testConverter( '    Pbb12   ', None, unpackPackedID, stream)
       self.testConverter("0a001K14A00A", None, unpackPackedID, stream)
       self.testConverter("1234C       ", None, unpackPackedID, stream)
       self.testConverter("1234X       ", None, unpackPackedID, stream)
       self.testConverter("1234A       ", None, unpackPackedID, stream)
       self.testConverter("00000       ", None, unpackPackedID, stream)
       self.testConverter("0000P       ", None, unpackPackedID, stream)
       self.testConverter("U000S       ", None, unpackPackedID, stream)
       self.testConverter("K221S       ", None, unpackPackedID, stream)
       self.testConverter("_0000       ", None, unpackPackedID, stream)
       self.testConverter("     A00 01 ", None, unpackPackedID, stream)  # bogus
       self.testConverter("            ", None, unpackPackedID, stream)
    
       #
       # test packing ID
       #
       print (file=stream)
       print ("test unpacked ID -> packed", file=stream)
       self.testConverter( (None, '2014 AA', None), "     K14A00A", packTupleID, stream)
       self.testConverter( ('1', None, None), "00001       ", packTupleID, stream)
       self.testConverter( ('121234', '2014 AA', None), "C1234K14A00A", packTupleID, stream)
       self.testConverter( ('1', '2014 AA', None), "00001K14A00A", packTupleID, stream)
       self.testConverter( ('360001', '2014 AA', None), "a0001K14A00A", packTupleID, stream)
       self.testConverter( ('7968', 'A/1996 N2', None), "07968J96N020", packTupleID, stream)
    
       self.testConverter( (None, '4007 T-1', None), "     T1S4007", packTupleID, stream)
       self.testConverter( (None, None, 'A'), "     A      ", packTupleID, stream)
       self.testConverter( (None, None, 'A000'), "     A000   ", packTupleID, stream)
       self.testConverter( (None, None, 'A00001'), "     A00001 ", packTupleID, stream)
    
       self.testConverter( ('73P', None, None), "0073P       ", packTupleID, stream)
       self.testConverter( ('3D', None, None), "0003D       ", packTupleID, stream)
       self.testConverter( (None, 'C/1995 A1', None), '    CJ95A010', packTupleID, stream)
       self.testConverter( (None, 'P/1994 P1-B', None), '    PJ94P01b', packTupleID, stream)
       self.testConverter( (None, 'C/1994 P1', None), '    CJ94P010', packTupleID, stream)
       self.testConverter( (None, 'C/2048 X13', None), '    CK48X130', packTupleID, stream)
       self.testConverter( (None, 'C/2033 L89-C', None), '    CK33L89c', packTupleID, stream)
       self.testConverter( (None, 'C/2088 A103', None), '    CK88AA30', packTupleID, stream)
       self.testConverter( (None, 'C/1999 K7', None), '    CJ99K070', packTupleID, stream)
       self.testConverter( (None, 'D/1999 K7', None), '    DJ99K070', packTupleID, stream)
       self.testConverter( (None, 'P/1886 S1', None), '    PI86S010', packTupleID, stream)
       self.testConverter( (None, 'D/1994 P1-B', None), '    DJ94P01b', packTupleID, stream)
       self.testConverter( (None, 'P/1994 P1-B', None), '    PJ94P01b', packTupleID, stream)
       self.testConverter( (None, 'P/1996 J1-A', None), '    PJ96J01a', packTupleID, stream)
       self.testConverter( (None, 'P/1998 QP54', None), '    PJ98Q54P', packTupleID, stream)
       self.testConverter( (None, 'P/2014 QP', None), '    PK14Q00P', packTupleID, stream)
       self.testConverter( (None, 'C/1997 BA6', None), '    CJ97B06A', packTupleID, stream)
       self.testConverter( (None, 'P/2001 N131', None), '    PK01ND10', packTupleID, stream)
       self.testConverter( (None, 'P/2010 V10-B', None), '    PK10V10b', packTupleID, stream)
       self.testConverter( (None, 'D/1894 F1', None), '    DI94F010', packTupleID, stream)
       self.testConverter( (None, 'D/1993 F2-E', None), '    DJ93F02e', packTupleID, stream)
       self.testConverter( (None, 'X/1987 A2', None), '    XJ87A020', packTupleID, stream)
       self.testConverter( (None, 'I/2020 A2', None), '    IK20A020', packTupleID, stream)
       self.testConverter( ('141P-A', 'P/1994 P1-A', None), '0141PJ94P01a', packTupleID, stream)
       self.testConverter( ('1P', 'P/1835 P1', None), '0001PI35P010', packTupleID, stream)
       self.testConverter( ('73P-AF', None, None), '0073P     af', packTupleID, stream)
       self.testConverter( ('73P-G', None, None), '0073P      g', packTupleID, stream)
       self.testConverter( (None, None, 'bb12'), '     bb12   ',  packTupleID, stream)
       self.testConverter( (None, 'P/1996 P620-A', None), None, packTupleID, stream)
    
       self.testConverter( ('Jupiter 1', None, None), "J001S       ", packTupleID, stream)
       self.testConverter( ('Saturn 1', None, None), "S001S       ", packTupleID, stream)
       self.testConverter( ('Neptune 13', None, None), "N013S       ", packTupleID, stream)
       self.testConverter( ('Uranus 101', None, None), "U101S       ", packTupleID, stream)
       self.testConverter( ('Jupiter 1', 'S/1610 J 1', None), "J001SG10J010", packTupleID, stream)
       self.testConverter( ('Jupiter 1001', None, None), None, packTupleID, stream)
       self.testConverter( ('Neptune 0', None, None), None, packTupleID, stream)
    
       self.testConverter( (None, 'S/1610 J 1', None), "    SG10J010", packTupleID, stream)
       self.testConverter( (None, 'S/2010 J 111', None), "    SK10JB10", packTupleID, stream)
       self.testConverter( (None, None, 'Aab102'), "     Aab102 ", packTupleID, stream)
       self.testConverter( (None, None, None), None, packTupleID, stream)
       self.testConverter( ('Wibble', None, None), None, packTupleID, stream)
    
       self.testConverter( ('0', None, None), None, packTupleID, stream)
       self.testConverter( ('620000', None, None), None, packTupleID, stream)
       self.testConverter( "bogus", None, packTupleID, stream)
       self.testConverter( ('1', 'P/1994 P1-A', None), None, packTupleID, stream)
       self.testConverter( ('141P', 'P/1994 P1-A', None), None, packTupleID, stream)
       self.testConverter( ('141P-C', 'P/1994 P1-A', None), None, packTupleID, stream)
       self.testConverter( ('141P-AB', 'P/1994 P1-A', None), None, packTupleID, stream)
       self.testConverter( ('12345P', None, None), None, packTupleID, stream)
       self.testConverter( ('0P', None, None), None, packTupleID, stream)
       self.testConverter( ('0P-A', None, None), None, packTupleID, stream)
       self.testConverter( ('10000P-A', None, None), None, packTupleID, stream)
       
       self.testConverter( ('(45) 1', None, None), None, packTupleID, stream)
       self.testConverter( (None, 'S/1610 J 1', 'Abcde'), None, packTupleID, stream)
       self.testConverter( (None, 'Invalid88', None), None, packTupleID, stream)
       self.testConverter( (None, None, 'A1234567'), None, packTupleID, stream)
       self.testConverter( (None, None, ''), None, packTupleID, stream)
       self.testConverter( (None, None, 'Ab3%xx'), None, packTupleID, stream)
       self.testConverter( (None, 'S/2010 J 111'), None, packTupleID, stream)
       self.testConverter( (None, 'S/2010 J 111', None, "Too long"), None, packTupleID, stream)
    
       self.testConverter( (None, '568 T-1', None), None, packTupleID, stream)
       self.testConverter( (None, '2014 AA620', None), None, packTupleID, stream)
       self.testConverter( (None, '2014 AA12345', None), None, packTupleID, stream)
       self.testConverter( (None, 'C/1997 B620', None), None, packTupleID, stream)
       self.testConverter( (None, 'P/1998 QP54-A', None), None, packTupleID, stream)
       self.testConverter( (None, '1700 AA', None), None, packTupleID, stream)
       self.testConverter( (None, '6200 AX', None), None, packTupleID, stream)
       self.testConverter( (None, '2001 IA', None), None, packTupleID, stream)
       self.testConverter( (None, '2001 ZA', None), None, packTupleID, stream)
       self.testConverter( (None, '2001 AI', None), None, packTupleID, stream)
       self.testConverter( (None, 'S/2001 N 620', None), None, packTupleID, stream)
       self.testConverter( (None, 'S/2001 N 0', None), None, packTupleID, stream)
       self.testConverter( (None, 'S/2008 (41) 1', None), None, packTupleID, stream)
       self.testConverter( (None, 'S/2001 (1998 WW31)) 1', None), None, packTupleID, stream)
    
       #
       # test packed ID round-trip
       #
       print (file=stream)
       print ("test packed ID roundTrip", file=stream)
       self.testConverter("     K14A00A", True, self.testPackedRoundTrip, stream)
       self.testConverter("00001       ", True, self.testPackedRoundTrip, stream)
       self.testConverter("C1234K14A00A", True, self.testPackedRoundTrip, stream)
       self.testConverter("00001K14A00A", True, self.testPackedRoundTrip, stream)
       self.testConverter("a0001K14A00A", True, self.testPackedRoundTrip, stream)
       self.testConverter("07968J96N020", True, self.testPackedRoundTrip, stream)
       self.testConverter("    AJ96N020", True, self.testPackedRoundTrip, stream)
       self.testConverter("     T1S4007", True, self.testPackedRoundTrip, stream)
       self.testConverter("     A      ", True, self.testPackedRoundTrip, stream)
       self.testConverter("     A000   ", True, self.testPackedRoundTrip, stream)
       self.testConverter("     A00001 ", True, self.testPackedRoundTrip, stream)
       self.testConverter("     A00001X", True, self.testPackedRoundTrip, stream)
       self.testConverter("     K00001X", True, self.testPackedRoundTrip, stream)
       self.testConverter("     K00001x", True, self.testPackedRoundTrip, stream)
       self.testConverter("     J000013", True, self.testPackedRoundTrip, stream)
       self.testConverter("     P00001A", True, self.testPackedRoundTrip, stream)
       self.testConverter("     P00001z", True, self.testPackedRoundTrip, stream)
    
       self.testConverter("0073P       ", True, self.testPackedRoundTrip, stream)
       self.testConverter("0003D       ", True, self.testPackedRoundTrip, stream)
       self.testConverter( '    CJ95A010', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    PJ94P01b', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    CJ94P010', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    CK48X130', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    CK33L89c', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    CK88AA30', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    CJ99K070', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    DJ99K070', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    PI86S010', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    DJ94P01b', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    PJ94P01b', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    PJ96J01a', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    PJ98Q54P', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    CJ97B06A', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    PK01ND10', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    PK10V10b', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    DI94F010', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    DJ93F02e', True, self.testPackedRoundTrip, stream)
       self.testConverter( '    XJ87A020', True, self.testPackedRoundTrip, stream)
       self.testConverter( '0141PJ94P01a', True, self.testPackedRoundTrip, stream)
       self.testConverter( '0001PI35P010', True, self.testPackedRoundTrip, stream)
       self.testConverter( '0073P     af', True, self.testPackedRoundTrip, stream)
       self.testConverter( '     bb12   ', True, self.testPackedRoundTrip, stream)
    
       self.testConverter("J001S       ", True, self.testPackedRoundTrip, stream)
       self.testConverter("S001S       ", True, self.testPackedRoundTrip, stream)
       self.testConverter("N013S       ", True, self.testPackedRoundTrip, stream)
       self.testConverter("U101S       ", True, self.testPackedRoundTrip, stream)
       self.testConverter("J001SG10J010", True, self.testPackedRoundTrip, stream)
    
       self.testConverter("    SG10J010", True, self.testPackedRoundTrip, stream)
       self.testConverter("    SK10JB10", True, self.testPackedRoundTrip, stream)


import PeakQL

def checkPeakErr(errVec):
    if errVec.size() > 0:
        raise Exception(errVec[0])

def initPeak():
    errVec = PeakQL.Str_Vec(0)
    PeakQL.pk_InitializeAddin(errVec)
    checkPeakErr(errVec)

def cleanupPeak():
    errVec = PeakQL.Str_Vec(0)
    PeakQL.pk_Cleanup(errVec)
    checkPeakErr(errVec)    

def testCalendar():
    dateVec = PeakQL.PkInt_Vec(1)
    dateVec[0] = 42252
    errVec = PeakQL.Str_Vec(0)
    resultVec = PeakQL.PkInt_Vec(0)
    PeakQL.pk_CalendarAdjust('China.IB', dateVec, PeakQL.PK_NULL_STR, resultVec, errVec)
    checkPeakErr(errVec)
    if resultVec.size() != 1:
        raise Exception('Unexpected resultVec size: ' + str(resultVec.size()))
    if (resultVec[0] != 42253):
        raise Exception('Unexpected result: ' + str(resultVec[0]))
    print 'Passed'

def main():
    initPeak()
    testCalendar()
    cleanupPeak()

main()

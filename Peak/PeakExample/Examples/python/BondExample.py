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


_holidays = 'd:/ChinaHolidays.csv'
_workingWeekend = 'd:/ChinaIBWorkingWeekends.csv'

def _checkAndRaiseErr(errVec):
    if errVec.size() > 0:
        raise Exception(errVec[0])


def loadHolidayCalendars(holidayFile=None, workingWeekendFile=None):
    import os
    errVec = PeakQL.Str_Vec()
    dir = os.path.dirname(__file__) + os.path.sep
    if not holidayFile:
        holidayFile = dir + _holidays
    print '...Loading holidays from file %s...' % holidayFile
    try:
        f = open(holidayFile)
        data = f.read()
    finally:
        if f:
            f.close()

    PeakQL.pk_LoadChinaHolidays(len(data), data, errVec)
    checkPeakErr(errVec)

    if not workingWeekendFile:
        workingWeekendFile = dir + _workingWeekend
    print '...Loading working weekends from file %s...' % workingWeekendFile
    try:
        f = open(workingWeekendFile)
        data = f.read()
    finally:
        if f:
            f.close()

    PeakQL.pk_LoadChinaWorkingWkends(len(data), data, errVec)
    checkPeakErr(errVec)



def loadContract():
    recursive = 0
    overwrite = 0
    times = PeakQL.Str_Vec()
    users = PeakQL.Str_Vec()
    files = PeakQL.Str_Vec()
    bondContract = PeakQL.Str_Vec()
    errVec = PeakQL.Str_Vec()
    objPtterns = PeakQL.Str_Vec()
    print "=== start to load contract from local drive === "
    PeakQL.pk_ObjectLoad("D:/", "ContractCache_PK_20180803.bin", recursive, overwrite, times, users, files, bondContract, errVec)
    checkPeakErr(errVec)

    print bondContract.size()
    for index in range(bondContract.size()):
        print bondContract[index]




def bondCalculation():
    bondId = "170215.IB_PKBond"
    cleanPrice = 99
    errVec = PeakQL.Str_Vec()
    startDate = PeakQL.pk_BondStartDate(bondId, errVec)
    checkPeakErr(errVec)
    errVec.clear()
    maturity = PeakQL.pk_BondMaturityDate(bondId, errVec)

    settlementDate = (startDate + maturity)/2
    print "bond clean price to yield"
    yield1 = PeakQL.pk_BondYieldFromCleanPrice(bondId, "", cleanPrice, PeakQL.PK_NULL_STR, settlementDate, PeakQL.PK_NULL_DOUBLE, PeakQL.PK_NULL_INT, PeakQL.PK_NULL_DOUBLE, errVec)

    print yield1

def main():
    initPeak()
    loadHolidayCalendars(_holidays, _workingWeekend)
    loadContract()
    bondCalculation()

    cleanupPeak()


main()

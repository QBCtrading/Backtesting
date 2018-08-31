from functools import wraps
import PeakQL as pk

def checkPeakErr(errVec):
    if errVec.size() > 0:
        raise Exception(errVec[0])

def initPeak():
    errVec = pk.Str_Vec(0)
    pk.pk_InitializeAddin(errVec)
    checkPeakErr(errVec)

def cleanupPeak():
    errVec = pk.Str_Vec(0)
    pk.pk_Cleanup(errVec)
    checkPeakErr(errVec)

def setupPeak(func):
    @wraps(func)
    def call_it(*args, **kwds):
        initPeak()
        retVal = func(*args, **kwds)
        cleanupPeak()
        return retVal
    return call_it

def testLPSolve(solver):
    """   Maximize       10x + 15y + 20z
        Subject to  0 <=   x +  3y +  5z <= 50
                    0 <=  2x +  4y +  2z <= 50
                    0 <=   x,    y,    z <= 10
    """
    lp_maximize = 1
    
    m = 2
    n = 3
    
    retVal = pk.Param_VecVec()
    errVec = pk.Str_Vec(0)
    
    A = pk.Double_VecVec(m, pk.Double_Vec(n))
    A[0] = pk.Double_Vec([1.0, 3.0, 5.0])
    A[1] = pk.Double_Vec([2.0, 4.0, 2.0])
    
    AType = pk.Str_Vec(0)
    vType = pk.Str_Vec(0)
    
    Alb = pk.Double_Vec(m, 0.0)
    Aub = pk.Double_Vec(m, 50.0)
    xlb = pk.Double_Vec(n, 0.0)
    xub = pk.Double_Vec(n, 10.0)
    c = pk.Double_Vec([10.0, 15.0, 20.0])
    
    pk.pkLPSolve(retVal, A, Aub, c, AType, xlb, xub, lp_maximize, pk.PK_NULL_INT,
                 vType, Alb, False, 1000.0, 1, solver, errVec)
    
    for row in retVal:
        print ''.join(cell.toString().center(15) for cell in row)
    
    checkPeakErr(errVec)
    if retVal.size() != max(m, n) + 2:
        raise Exception('Unexpected result size: %s' % retVal.size())
    if (retVal[0][0].toDouble() != 275.0):
        raise Exception('Objective value mismatch: %s' % retVal[0][0].toDouble())
    print 'Passed\n'

@setupPeak
def main():
    for solver in [pk.LP_GLPK, pk.LP_CPLEX]:
        testLPSolve(solver)
    
if __name__ == '__main__':
    main()

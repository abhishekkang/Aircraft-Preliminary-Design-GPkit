import gpkit 
from gpkit import Model, parse_variables, Vectorize, SignomialEquality,Variable,units
from mission import *
from solwriter import *
import math
import numpy as np
import matplotlib.pyplot as plt
from decimal import *
pi = math.pi
#from sens_chart import *


def RegularSolve():
#for blownwing
    M = Mission(wingmode ='blownwing')
    M.cost =1/M.R
    sol = M.localsolve(solver='cvxopt')
    # M.substitutions.update({M.aircraft.bw.wing.planform.S:134.22})
    #sd = get_highestsens(M, sol, N=10)
    #f, a = plot_chart(sd)
    #f.savefig("sensbar.pdf", bbox_inches="tight")
    print (sol(M.R))
    print (sol(M.aircraft.mass))
    print (sol(M.cruise.perf.P))
    print(sol(M.loading.wingl.w))
    #print(M.aircraft)
    print(sol(M.CLmax))
    #print (sol["sensitivities"]["constants"]["CLCmax"])
    writeSolBW(sol)
    writePropBW(sol,M)
    writeWgtBW(sol,M)
    #for conventional wing
    M = Mission(wingmode ='na')
   # M.substitutions.update({M.aircraft.bw.wing.planform.S:134.22})
   # M.substitutions.update({M.aircraft.bw.wing.planform.AR:8.79})
   # M.substitutions.update({M.aircraft.bw.wing.planform.b:34.34})
    M.cost =1/M.R
    sol = M.localsolve(solver='cvxopt')
    # print M.program.gps[-1].result.summary()
    # print sol.summary()
    #sd = get_highestsens(M, sol, N=10)
    #f, a = plot_chart(sd)
    #f.savefig("sensbar.pdf", bbox_inches="tight")
    print (sol(M.R))
    print (sol(M.aircraft.mass))
    print(sol(M.CLmax))
   # print(sol(M.aircraft.bw.wing.spar.laoding.w))
    #print(sol(M.AircraftLoading.Sparloading))
    #print (sol["sensitivities"]["constants"]["CLmax"])
    writeSolNW(sol)
    writePropNW(sol,M)
    writeWgtNW(sol,M)

    
def RangeMassplot():
   M = Mission(wingmode='na')
   Mass_sweep = np.linspace(30000,50000,10)
   M.substitutions.update({M.aircraft.battery.E_capacity:('sweep',Mass_sweep)})
   M.cost = M.aircraft.mass
   sol = M.localsolve(solver='cvxopt',skipsweepfailures=True)
   #print (sol.summary())
   plt.plot(sol(M.aircraft.mass),sol(M.R),label='Wing')
   M = Mission(wingmode="blownwing")
   M.substitutions.update({M.aircraft.mass:('sweep',Mass_sweep)})
   M.cost =M.aircraft.mass
   sol = M.localsolve(solver='cvxopt',skipsweepfailures=True)
   plt.plot(sol(M.aircraft.mass),sol(M.R),label='Blown Wing')
   plt.legend()
   plt.title("Mass-range diagram")
   plt.ylabel("Range [nmi]" , size = 16) # weight = "medium"
   plt.xlabel("Mass [kg]", size = 16) # weight = "medium"
   plt.savefig("mass-range.png", bbox_inches="tight", format='png', dpi=1000)
   plt.grid()
   plt.show()

def MassRunway():
    M = Mission(wingmode='na')
    Mass_sweep = np.linspace(50,500,10)
    M.substitutions.update({M.Srunway:('sweep',Mass_sweep)})
    M.cost = M.aircraft.mass
    sol = M.localsolve(solver='cvxopt',skipsweepfailures=True)
    print (sol(M.aircraft.mass))
    plt.plot(sol(M.Srunway),sol(M.aircraft.mass),label='Wing')
    M = Mission(wingmode="blownwing")
    Mass_sweep = np.linspace(10,200,10)
    M.substitutions.update({M.Srunway:('sweep',Mass_sweep)})
    M.cost =M.aircraft.mass
    sol = M.localsolve(solver='cvxopt',skipsweepfailures=True)
    plt.plot(sol(M.Srunway),sol(M.aircraft.mass),label='Blown Wing')
    print (sol(M.aircraft.mass))
    plt.legend()
    plt.title("Mass-range diagram")
    plt.xlabel("Srunway" , size = 16) # weight = "medium"
    plt.ylabel("Mass [kg]", size = 16) # weight = "medium"
    plt.savefig("mass-range.png", bbox_inches="tight", format='png', dpi=1000)
    plt.grid()
    plt.show()
    
def Powerusage():
    M=Mission(wingmode="na")
    Mass_sweep = np.linspace(50,500,10)
    M.substitutions.update({M.Srunway:('sweep',Mass_sweep)})
    M.cost = M.aircraft.mass
    sol = M.localsolve(solver='cvxopt',skipsweepfailures=True)
    print (sol(M.aircraft.dynamic.P))
    plt.plot(sol(M.Srunway),sol(M.aircraft.mass),label='Wing')
    M = Mission(wingmode="blownwing")
    Mass_sweep = np.linspace(10,200,10)
    M.substitutions.update({M.Srunway:('sweep',Mass_sweep)})
    M.cost =M.aircraft.mass
    sol = M.localsolve(solver='cvxopt',skipsweepfailures=True)
    plt.plot(sol(M.Srunway),sol(M.aircraft.mass),label='Blown Wing')
    print (sol(M.aircraft.mass))
    plt.legend()
    plt.title("Mass-range diagram")
    plt.xlabel("Srunway" , size = 16) # weight = "medium"
    plt.ylabel("Mass [kg]", size = 16) # weight = "medium"
    plt.savefig("mass-range.png", bbox_inches="tight", format='png', dpi=1000)
    plt.grid()
    plt.show()
if __name__ == "__main__":
  # RangeMassplot()
   #MassRunway()
   RegularSolve()
   
import gpkit
from gpkit import Model, parse_variables, Vectorize, SignomialEquality,Variable,units
from battm import *
from wing_struct import Planform,WingSkin,CapSpar
import math
import numpy as np
pi = math.pi 

class Wing(Model):
    """
    Wing Model
    Variables
    ---------
    W                   [lbf]       wing weight
    mfac        1.2     [-]         wing weight margin
    n_plies     5       [-]         number of plies on skin

    Upper Unbounded
    ---------------
    W, planform.tau

    Lower Unbounded
    ---------------
    planform.b, spar.Sy

    LaTex Strings
    -------------
    mfac                m_{\\mathrm{fac}}

    """

    sparModel = CapSpar
    fillModel = False
    skinModel = WingSkin
    @parse_variables(__doc__,globals())
    def setup(self, N=4):
        self.N = N

        self.planform = Planform(N)
        self.b = self.planform.b
        self.components = []

        if self.skinModel:
            self.skin = self.skinModel(self.planform)
            self.components.extend([self.skin])
        if self.sparModel:
            self.spar = self.sparModel(N, self.planform)
            self.components.extend([self.spar])
            self.Sy = self.spar.Sy
        if self.fillModel:
            self.foam = self.fillModel(self.planform)
            self.components.extend([self.foam])

        constraints = [
        self.spar.t[0:-2] == self.spar.t[-1],
        self.spar.w[0:-2] == self.spar.w[-1],
        self.skin.t >= n_plies*self.skin.material.tmin,
        W/mfac >= sum(c["W"] for c in self.components)]
        return constraints, self.planform, self.components

    
class NormalWing(Model):
    """
    Variables
    ---------
    n_prop    1     [-]             number of powertrains/propellers
    m               [kg]            mass
    """
    @parse_variables(__doc__,globals())
    def setup(self):

        self.powertrain = Powertrain()
        N =14
        self.wing = Wing(N)
        self.wing.substitutions[self.wing.planform.tau]=0.12
        self.wing.substitutions[self.wing.planform.lam]=1
        constraints = [
            m >= self.powertrain["m"] + self.wing.W/2.02462*units('kg/lbf')#("W")/g,
        ]
        return constraints,self.powertrain,self.wing
    def dynamic(self,state,wingmode="na"):
        return NormalWingP(self,state)

class NormalWingP(Model):

    """
    Variables
    ---------
    C_L             [-]             total lift coefficient
    C_Di            [-]             induced drag coefficient
    C_Dp            [-]             profile drag
    C_D             [-]             total drag coefficient
    Re              [-]             Reynolds number
    e       0.8     [-]             span efficiency
    mfac    1.2     [-]             profile drag margin
    Kf      1.180   [-]             form factor
    C_f             [-]             friction coefficient
    CLmax    2.5    [-]             max coefficinet of lift
    T               [N]             propeller thrust
    P               [kW]            power draw
    C_T             [-]             thrust coefficient
    eta_prop        [-]             propeller efficiency
    RPMmax          [rpm]           max RPM of propeller
    r               [m]             propeller radius
    a         343   [m/s]           speed of sound
    Mlim      0.5   [-]             tip Mach limit
    A_disk          [m**2]          area of propeller disk
    C_LC      0     [-]             not required
    C_J       0      [-]             jet momentum coefficient
    C_E       0      [-]             energy momentum coefficient
    """
    @parse_variables(__doc__,globals())
    def setup(self,bw,state):
        #bw is a BlownWing object
        #state is a FlightState

        with gpkit.SignomialsEnabled():
            constraints = [
               bw.powertrain.r>=0.1*units("m"),
               A_disk == bw.n_prop*pi*bw.powertrain.r**2,
               C_L <= CLmax,
               C_Di*(pi*bw.wing["AR"]*e ) >= (C_L**2),
               C_D >= C_Di  + C_Dp,
               C_f**5 == (mfac*0.074)**5 /(Re),
               C_Dp == C_f*2.1*Kf,
               Re == state["V"]*state["rho"]*(bw.wing["S"]/bw.wing["AR"])**0.5/state["mu"],
               
               C_T == T / (0.5 * state.rho * bw.wing["S"] * state.V**2),
               P >= T * state.V / (eta_prop * bw.powertrain.eta),
               bw.powertrain.RPMmax * bw.powertrain.r <= a * Mlim,
               P <= bw.n_prop * bw.powertrain["Pmax"],
               T >= 0.5 * state.rho * bw.wing["S"] * state.V**2 * C_D,
               ]
            
        return constraints
    

class BlownWing(Model):
    """
    Variables
    ---------
    n_prop     10   [-]             number of powertrains/propellers
    m               [kg]            mass
    """
    @parse_variables(__doc__,globals())
    def setup(self,seg="cruise"):
        self.powertrain = Powertrain()
        N = 14
        self.wing = Wing(N)
        self.wing.substitutions[self.wing.planform.tau]=0.12
        self.wing.substitutions[self.wing.planform.lam]=1
        
        constraints = [
            m >= n_prop*self.powertrain["m"] + self.wing.W/2.02462*units('kg/lbf')#("W")/g,
        ]
        return constraints,self.powertrain,self.wing
    def dynamic(self,state,seg =False):
        return BlownWingP(self,state,seg=seg)

class BlownWingP(Model):
    #Built from Mark Drela's Powered-Lift and Drag Calculation
    #and Thin Airfoil Theory for Blown 2D Airfoils notes

    """
    Variables
    ---------
    C_L             [-]             total lift coefficient
    C_LC            [-]             lift coefficient due to circulation
    C_Q             [-]             mass momentum coefficient
    C_J             [-]             jet momentum coefficient
    C_E             [-]             energy momentum coefficient
    C_Di            [-]             induced drag coefficient
    C_Dp            [-]             profile drag
    C_D             [-]             total drag coefficient
    C_T             [-]             thrust coefficient
    Re              [-]             Reynolds number
    e       0.8     [-]             span efficiency
    mfac    1.2     [-]             profile drag margin
    m_dotprime      [kg/(m*s)]      jet mass flow per unit span
    J_prime         [kg/(s**2)]     momentum flow per unit span
    E_prime         [J/(m*s)]       energy flow per unit span
    rho_j   1.225   [kg/m**3]       density in jet flow
    u_j             [m/s]           velocity in jet flow
    h               [m]             Wake height
    T               [N]             propeller thrust
    P               [kW]            power draw
    eta_prop        [-]             prop efficiency loss after blade disk actuator
    A_disk          [m**2]          area of prop disk
    Mlim      0.5   [-]             tip limit
    a         343   [m/s]           speed of sound at sea level
    RPMmax          [rpm]           maximum rpm of propeller
    Kf        1.180 [-]             form factor
    C_f             [-]             friction coefficient
    CLCmax    3.5   [-]             clc max
    """
    @parse_variables(__doc__,globals())
    def setup(self,bw,state,seg):
        #bw is a BlownWing object
        #state is a FlightState
        n_active = 2 if seg else bw["n_prop"]
        with gpkit.SignomialsEnabled():
            constraints = [
            A_disk == n_active*pi*bw.powertrain.r**2,
            ((P*eta_prop*bw.powertrain.eta)/(0.5*T*state["V"]) - 1)**2 >= (T/(A_disk*(state.V**2)*state.rho/2)+1),
            (u_j/state.V)**2 <= (T/(A_disk*(state.V**2)*state.rho/2) + 1),
            u_j >= state.V,
            P <= n_active*bw.powertrain["Pmax"],

            C_L <= C_LC*(1+2*C_J/(pi*bw.wing["AR"]*e)),
            C_L >= C_LC,
            C_LC <= CLCmax,
            bw.powertrain.RPMmax*bw.powertrain.r <= a*Mlim,
            C_T == T/((0.5*state.rho*bw.wing["S"]*state.V**2)),
            m_dotprime == rho_j*u_j*h,
            J_prime ==  m_dotprime*u_j,
            E_prime == 0.5*m_dotprime*u_j**2,
            C_Q ==  m_dotprime/(state.rho*state.V* bw.wing["cmac"]),
            C_J == J_prime/(0.5*state.rho*state.V**2 * bw.wing["cmac"]),
            C_E == E_prime/(0.5*state.rho*state.V**3 * bw.wing["cmac"]),
            h == pi*bw.powertrain.r/2,
            C_Di*(pi*bw.wing["AR"]*e + 2*C_J) >= (C_L**2),
            C_D >= C_Di  + C_Dp,
            C_f**5 == (mfac*0.074)**5 /(Re),
            C_Dp == C_f*2.1*Kf,
            Re == state["V"]*state["rho"]*(bw.wing["S"]/bw.wing["AR"])**0.5/state["mu"],
            ]
        return constraints
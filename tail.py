import numpy as np
from numpy import pi
from gpkit import Model, parse_variables, Variable, VectorVariable, units,Vectorize
from beam import Beam
from gpkitmodels import g
from tube_spar import TubeSpar
from wing_struct import *

class TailAero(Model):
    """Tail Aero Model

    Variables
    ---------
    Re          [-]     Reynolds number
    Cd          [-]     drag coefficient

    Upper Unbounded
    ---------------
    Cd, Re, S, V, b, rho

    Lower Unbounded
    ---------------
    S, tau, V, b, rho

    LaTex Strings
    -------------
    Cd      C_d

    """
    @parse_variables(__doc__, globals())
    def setup(self, static, state):
        self.state = state

        cmac = self.cmac = static.planform.cmac
        b = self.b = static.planform.b
        S = self.S = static.planform.S
        tau = self.tau = static.planform.tau
        rho = self.rho = state.rho
        V = self.V = state.V
        mu = self.mu = state.mu
        constraints = [
            Re == V*rho*S/b/mu,
            Cd>= 0.339937756*Re**(-0.181990628)*tau**(0.774603933),
            Cd>= 5.446864658*Re**(-0.484866619)*tau**(0.246341522),
            Cd>= 16.2594679*Re**(-0.539943202)*tau**(0.466384455),
            Cd>=9.509193806*Re**(-0.482346958)*tau**(0.467466389),
            Cd>= 218.7365501*Re**(-0.603870895)*tau**(1.312443752),
            ]
        return constraints

class TailBoomAero(Model):
    """ Tail Boom Aero Model

    Variables
    ---------
    Cf          [-]     tail boom skin friction coefficient
    Re          [-]     tail boom reynolds number

    Upper Unbounded
    ---------------
    Re, Cf, l, V, rho

    Lower Unbounded
    ---------------
    l, V, rho

    LaTex Strings
    -------------
    Cf      C_f

    """
    @parse_variables(__doc__, globals())
    def setup(self, static, state):
        self.state = state

        l = self.l = static.l
        rho = self.rho = state.rho
        V = self.V = state.V
        mu = self.mu = state.mu

        return [Re == V*rho*l/mu,
                Cf >= 0.455/Re**0.3,
               ]

class HorizontalTail(Wing):
    """ Horizontal Tail Model

    Variables
    ---------
    Vh                          [-]     horizontal tail volume coefficient
    lh                          [ft]    horizontal tail moment arm
    CLhmin              0.75    [-]     max downlift coefficient
    mh                          [-]     horizontal tail span effectiveness

    Upper Unbounded
    ---------------
    lh, Vh, W, planform.tau

    Lower Unbounded
    ---------------
    lh, Vh, planform.b, mh, planform.tau (if not sparModel)
    spar.Sy (if sparModel), spar.J (if sparJ)

    LaTex Strings
    -------------
    Vh          V_{\\mathrm{h}}
    lh          l_{\\mathrm{h}}
    CLmin       C_{L_{\\mathrm{min}}}
    mh          m_{\\mathrm{h}}

    """
    flight_model = TailAero
    sparModel = CapSpar
    skinModel = WingSkin
    fillModel = None

    @parse_variables(__doc__, globals())
    def setup(self, N=5):
        self.ascs = Wing.setup(self, N)
        #self.Sy =Wing.sparModel.Sy
        self.planform.substitutions.update(
            {self.planform.AR: 4, self.planform.lam: 0.8})
        

        return self.ascs, mh*(1+2.0/self.planform["AR"]) <= 2*np.pi

    
" vertical tail "
class VerticalTail(Wing):
    """ Vertical Tail Model

    Variables
    ---------
    Vv                  [-]         vertical tail volume coefficient
    lv                  [ft]        vertical tail moment arm

    Upper Unbounded
    ---------------
    lv, Vv, W, planform.tau

    Lower Unbounded
    ---------------
    lv, Vv, planform.b, planform.tau (if not sparModel)
    spar.Sy (if sparModel), spar.J (if sparJ)

    LaTex Strings
    -------------
    Vv      V_{\\mathrm{v}}
    lv      l_{\\mathrm{v}}

    """

    flight_model = TailAero
    sparModel = CapSpar
    skinModel = WingSkin
    fillModel = None

    @parse_variables(__doc__, globals())
    def setup(self, N=5):
        self.ascs = Wing.setup(self, N)
        self.planform.substitutions.update(
            {self.planform.lam: 0.8, self.planform.AR: 4})
    
        return self.ascs
    
class TailBoomBending(Model):
    """ Tail Boom Bending

    Variables
    ---------
    F                       [N]     tail force
    th                      [-]     tail boom deflection angle
    kappa           0.1     [-]     max tail boom deflection
    Nsafety         1.0     [-]     safety load factor

    Variables of length tailboom.N-1
    --------------------------------
    Mr                      [N*m]   section root moment


    Upper Unbounded
    ---------------
    tailboom.I0, tailboom.Sy
    tailboom.J (if tailboomJ), tailboom.I

    Lower Unbounded
    ---------------
    htail.planform.S, htail.planform.CLmax
    tailboom.l, tailboom.deta
    state.qne

    LaTex Strings
    -------------
    th      \\theta
    thmax   \\theta_{\\mathrm{max}}

    """
    @parse_variables(__doc__, globals())
    def setup(self, tailboom, htail, state):
        N = self.N = tailboom.N
        self.state = state
        self.htail = htail
        self.tailboom = tailboom

        Beam.qbarFun = [1e-10]*N
        Beam.SbarFun = [1.]*N
        beam = self.beam = Beam(N)

        I = tailboom.I
        tailboom.I0 = I[0]
        l = tailboom.l
        S = htail.planform.S
        E = tailboom.material.E
        Sy = tailboom.Sy
        qne = state.qne
        CLmax = htail.planform.CLmax
        deta = tailboom.deta
        sigma = tailboom.material.sigma

        constraints = [beam.dx == deta,
                       F >= qne*S,
                       beam["\\bar{EI}"] <= E*I/F/l**2/2,
                       Mr >= beam["\\bar{M}"][:-1]*F*l,
                       sigma >= Mr/Sy,
                       th == beam["\\theta"][-1],
                       beam["\\bar{\\delta}"][-1]*CLmax*Nsafety <= kappa]

        self.tailboomJ = hasattr(tailboom, "J")
        if self.tailboomJ:
            constraints.append(tailboom.J >= 1e-10*units("m^4"))

        return constraints, beam

class TailBoom(TubeSpar):
    """ Tail Boom Model

    Variables
    ---------
    l                           [ft]        tail boom length
    S                           [ft^2]      tail boom surface area
    b                           [ft]        twice tail boom length
    deta          1./(N-1)      [-]         normalized segment length
    tau           1.0           [-]         thickness to width ratio
    rhoA          0.15          [kg/m^2]    total aerial density

    Variables of length N-1
    -----------------------
    cave                        [in]        average segment width

    """

    flight_model = TailBoomAero
    tailLoad = TailBoomBending
    secondaryWeight = None

    @parse_variables(__doc__, globals())
    def setup(self, N=5):
        self.N = N
        self.spar = super(TailBoom, self).setup(N, self)

        if self.secondaryWeight:
            self.weight.right += rhoA*g*S

        d0 = self.d0 = self.d[0]

        return self.spar, [S == l*pi*d0, b == 2*l]


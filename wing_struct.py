
import numpy as np
from gpkit import Model, parse_variables,units
from gpkitmodels.GP.materials import cfrpud, cfrpfabric, foamhd
from gpkitmodels import g
from numpy import pi


class Planform(Model):
    """ Planform Area Definition

    Scalar Variables
    ---------
    S                                   [ft^2]  surface area
    AR                                  [-]     aspect ratio
    b                                   [ft]    span
    tau                                 [-]     airfoil thickness ratio
    CLmax           1.39                [-]     maximum lift coefficient
    CM              0.14                [-]     wing moment coefficient
    croot                               [ft]    root chord
    cmac                                [ft]    mean aerodynamic chord
    lam             0.5                 [-]     taper ratio
    cbarmac         self.return_cmac    [-]     non-dim MAC

    Variables of length N
    ---------------------
    eta         np.linspace(0,1,N)      [-]     (2y/b)
    cbar        self.return_c           [-]     non-dim chord at nodes

    Variables of length N-1
    -----------------------
    cave                                [ft]    mid section chord
    cbave       self.return_avg         [-]     non-dim mid section chord
    deta        self.return_deta        [-]     \\Delta (2y/b)

    Upper Unbounded
    ---------------  # bounding any pair of variables will work
    cave, b, tau

    Lower Unbounded
    ---------------
    cave, b, tau

    LaTex Strings
    -------------
    tau         \\tau
    CLmax       C_{L_{\\mathrm{max}}}
    CM          C_M
    croot       c_{\\mathrm{root}}
    cmac        c_{\\mathrm{MAC}}
    lam         \\lambda
    cbarmac     \\bar{c}_{\\mathrm{MAC}}

    """
    def return_c(self, c):
        " return normalized chord distribution "
        lam = c(self.lam).to("dimensionless").magnitude
        eta = c(self.eta).to("dimensionless").magnitude
        return np.array([2./(1+lam)*(1+(lam-1)*e) for e in eta])

    def return_cmac(self, c):
        " return normalized MAC "
        cbar = self.return_c(c)
        lam = cbar[1:]/cbar[:-1]
        maci = 2./3*cbar[:-1]*(1 + lam + lam**2)/(1 + lam)
        deta = np.diff(c(self.eta).to("dimensionless").magnitude) 
        num = sum([(cbar[i] + cbar[i+1])/2*maci[i]*deta[i] for i
                   in range(len(deta))])
        den = sum([(cbar[i] + cbar[i+1])/2*deta[i] for i in range(len(deta))])
        return num/den/cbar[0]

    return_avg = lambda self, c: (self.return_c(c)[:-1]
                                  + self.return_c(c)[1:])/2.
    return_deta = lambda self, c: np.diff(c(self.eta).to("dimensionless").magnitude)

    @parse_variables(__doc__, globals())
    def setup(self, N):
        return [b**2 == S*AR,
                cave == cbave*S/b,
                croot == S/b*cbar[0],
                cmac == croot*cbarmac]




class SparLoading(Model):
    """ Spar Loading Model

    Variables
    ---------
    Nmax            5              [-]     max loading
    Nsafety         1.0            [-]     safety load factor
    kappa           0.2            [-]     max tip deflection ratio
    W                              [lbf]   loading weight
    N                              [-]     loading factor
    twmax           15.*pi/180     [-]     max tip twist
    Stip            1e-10          [N]     tip loading
    Mtip            1e-10          [N*m]   tip moment
    throot          1e-10          [-]     root deflection angle
    wroot           1e-10          [m]     root deflection

    Variables of length wing.N
    --------------------------
    q                       [N/m]   distributed wing loading
    S                       [N]     shear along wing
    M                       [N*m]   wing section root moment
    th                      [-]     deflection angle
    w                       [m]     wing deflection

    Variables of length wing.N-1
    ----------------------------
    Mtw                     [N*m]   local moment due to twisting
    theta                   [-]     twist deflection
    EIbar                   [-]     EIbar
    Sout                    [-]     outboard variable

    LaTex Strings
    -------------
    Nmax                N_{\\mathrm{max}}
    kappa               \\kappa
    Mr                  M_r

    """
    def new_qbarFun(self, c):
        " define qbar model for chord loading "
        barc = self.wing.planform.cbar
        return [f(c) for f in self.wing.substitutions[barc]]

    new_SbarFun = None

    @parse_variables(__doc__, globals())
    def setup(self, wing, state, out=False):
        self.wing = wing

        b = self.b = self.wing.planform.b
        I = self.I = self.wing.spar.I
        Sy = self.Sy = self.wing.spar.Sy
        cave = self.cave = self.wing.planform.cave
        cbar = self.cbar = self.wing.planform.cbar
        E = self.wing.spar.material.E
        sigma = self.wing.spar.material.sigma
        deta = self.wing.planform.deta

        constraints = []
        if not out:
            constraints.extend([
                S[:-1] >= S[1:] + 0.5*deta*(b/2.)*(q[:-1] + q[1:]),
                M[:-1] >= M[1:] + 0.5*deta*(b/2)*(S[:-1] + S[1:])])

        constraints.extend([
            N == Nsafety*Nmax, q >= N*W/b*cbar,
            S[-1] >= Stip, M[-1] >= Mtip, th[0] >= throot,
            th[1:] >= th[:-1] + 0.5*deta*(b/2)*(M[1:] + M[:-1])/E/I,
            w[0] >= wroot, w[1:] >= w[:-1] + 0.5*deta*(b/2)*(th[1:] + th[:-1]),
            sigma >= M[:-1]/Sy, w[-1]/(b/2) <= kappa,
            ])

        self.wingSparJ = hasattr(self.wing.spar, "J")

        if self.wingSparJ:
            qne = self.qne = state.qne
            J = self.J = self.wing.spar.J
            G = self.wing.spar.shearMaterial.G
            cm = self.wing.planform.CM
            constraints.extend([
                Mtw >= cm*cave**2*qne*deta*b/2*Nsafety,
                theta[0] >= Mtw[0]/G/J[0]*deta[0]*b/2,
                theta[1:] >= theta[:-1] + Mtw[1:]/G/J[1:]*deta[1:]*b/2,
                twmax >= theta[-1]
                ])
        return constraints

class CapSpar(Model):
    """ Cap Spar Model

    Scalar Variables
    ----------------
    E               2e7     [psi]       Young modulus of CFRP
    W                       [lbf]       spar weight
    wlim            0.15    [-]         spar width to chord ratio
    mfac            0.97    [-]         curvature knockdown factor

    Variables of length N-1
    -----------------------
    hin                     [in]        height between caps
    I                       [m^4]       spar x moment of inertia
    Sy                      [m^3]       section modulus
    dm                      [kg]        segment spar mass
    w                       [in]        spar width
    t                       [in]        spar cap thickness
    tshear                  [in]        shear web thickness

    Upper Unbounded
    ---------------
    W, cave, tau

    Lower Unbounded
    ---------------
    Sy, b, surface.deta

    LaTex Strings
    -------------
    wlim                    w_{\\mathrm{lim}}
    mfac                    m_{\\mathrm{fac}}
    hin                     h_{\\mathrm{in}_i}
    I                       I_i
    Sy                      S_{y_i}
    dm                      \\Delta{m}
    w                       w_i
    t                       t_i
    tshear                  t_{\\mathrm{shear}_i}

    """
    loading = SparLoading
    material = cfrpud
    shearMaterial = cfrpfabric
    coreMaterial = foamhd



    @parse_variables(__doc__, globals())
    def setup(self, N, surface):
        self.surface = surface

        cave = self.cave = surface.cave
        b = self.b = surface.b
        deta = surface.deta
        tau = self.tau = surface.tau
        rho = self.material.rho
        rhoshear = self.shearMaterial.rho
        rhocore = self.coreMaterial.rho
        tshearmin = self.shearMaterial.tmin

        return [I/mfac <= 2*w*t*(hin/2)**2,
                dm >= (rho*(2*w*t) + 2*tshear*rhoshear*(hin + 2*t)
                       + rhocore*w*hin)*b/2*deta,
                W >= 2*dm.sum()*g,
                w <= wlim*cave,
                cave*tau >= hin + 2*t,
                Sy*(hin/2 + t) <= I,
                tshear >= tshearmin,
               ]
    
class WingSkin(Model):
    """ Wing Skin model

    Variables
    ---------
    W                           [lbf]           wing skin weight
    t                           [in]            wing skin thickness
    Jtbar           0.01114     [1/mm]          torsional moment of inertia
    Cmw             0.121       [-]             negative wing moment coeff
    rhosl           1.225       [kg/m^3]        sea level air density
    Vne             45          [m/s]           never exceed vehicle speed

    Upper Unbounded
    ---------------
    W, surface.croot

    Lower Unbounded
    ---------------
    surface.S

    LaTex Strings
    -------------
    W       W_{\\mathrm{skin}}
    t       t_{\\mathrm{skin}}
    Jtbar   \\bar{J/t}
    Cmw     C_{m_w}
    rhosl   \\rho_{\\mathrm{SL}}
    Vne     V_{\\mathrm{NE}}

    """
    material = cfrpfabric

    @parse_variables(__doc__, globals())
    def setup(self, surface):
        self.surface = surface

        croot = surface.croot
        S = surface.S
        rho = self.material.rho
        tau = self.material.tau
        tmin = self.material.tmin

        return [W >= rho*S*2*t*g,
                t >= tmin,
                tau >= 1/Jtbar/croot**2/t*Cmw*S*rhosl*Vne**2]

class WingCore(Model):
    """ Wing Core Model

    Variables
    ---------
    W                           [lbf]       wing core weight
    Abar            0.0753449   [-]         normalized cross section area

    Upper Unbounded
    ---------------
    W

    Lower Unbounded
    ---------------
    cave, b, surface.deta

    LaTex Strings
    -------------
    rhocore                 \\rho_{\\mathrm{core}}
    Abar                    \\bar{A}

    """
    material = foamhd

    @parse_variables(__doc__, globals())
    def setup(self, surface):
        self.surface = surface

        cave = self.cave = surface.cave
        b = self.b = surface.b
        deta = surface.deta
        rho = self.material.rho

        return [W >= 2*(g*rho*Abar*cave**2*b/2*deta).sum()]


class Wing(Model):
    """
    Wing Model

    Variables
    ---------
    W                   [lbf]       wing weight
    mfac        1.2     [-]         wing weight margin factor
    n_plies     5       [-]         number of plies on skin

    SKIP VERIFICATION

    Upper Unbounded
    ---------------
    W, planform.tau (if not sparJ)

    Lower Unbounded
    ---------------
    planform.b, spar.Sy (if sparModel), spar.J (if sparJ)

    LaTex Strings
    -------------
    mfac                m_{\\mathrm{fac}}

    """

    sparModel = CapSpar
    fillModel = WingCore
    #flight_model = WingAero
    skinModel = WingSkin
    sparJ = False

    @parse_variables(__doc__, globals())
    def setup(self, N=5):
        self.N = N
        self.planform = Planform(N)
        self.components = []

        if self.skinModel:
            self.skin = self.skinModel(self.planform)
            self.components.extend([self.skin])
        if self.sparModel:
            self.spar = self.sparModel(N, self.planform)
            self.components.extend([self.spar])
            self.sparJ = hasattr(self.spar, "J")
        if self.fillModel:
            self.foam = self.fillModel(self.planform)
            self.components.extend([self.foam])

        constraints = [
        self.spar.t[0:-2] == self.spar.t[-1],
        self.spar.w[0:-2] == self.spar.w[-1],
        self.skin.t >= n_plies*self.skin.material.tmin,
        W/mfac >= sum(c["W"] for c in self.components)]
        return constraints, self.planform, self.components

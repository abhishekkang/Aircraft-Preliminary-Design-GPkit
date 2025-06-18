from gpkit import Model, parse_variables 
class Gear(Model):
    """Gear
    Variables
    ---------
    m         [lb]    total landing gear mass
    l         [ft]    landing gear length
    """
    @parse_variables(__doc__,globals())
    def setup(self):

        return []

class Equipment(Model):
    """Equipment
    Variables
    ---------
    m             [lb]       total equipment mass, without battery
    """
    @parse_variables(__doc__,globals())
    def setup(self):

        return []

class Fuselage(Model):
    """ Fuselage

    Variables
    ---------
    m                    [lb]    mass of fuselage
    l       24.26        [ft]    fuselage length
    w       5.67         [ft]    width
    h       8.57         [ft]    fuselage height
    f                    [-]     fineness ratio
    Swet                 [ft^2]  wetted area of fuselage
    """
    @parse_variables(__doc__,globals())
    def setup(self):

        return [
                f == l/h,
                Swet >=2.1*(l*w+l*h),# Raymer’s approximation for wetted area
                ]
    def dynamic(self,state):
        return FuselageP(self,state)

class FuselageP(Model):
    """FuselageP
    Variables
    ---------
    Cd              [-]     drag coefficient
    FF              [-]     form factor
    C_f             [-]     friction coefficient
    mfac     1.2    [-]     friction margin
    Re              [-]     Reynolds number
    """
    @parse_variables(__doc__,globals())
    def setup(self,fuse,state):
        constraints = [
                       FF ==fuse.l/fuse.h,
                       C_f >= 0.455/Re**0.3,
                       Cd/mfac == C_f*FF,
                       Re == state["V"]*state["rho"]*fuse.l/state["mu"],
                    ]
        return constraints

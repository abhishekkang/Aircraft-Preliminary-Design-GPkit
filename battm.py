from gpkit import Model, parse_variables, Vectorize, SignomialEquality,Variable,units
import gpkit
class Powertrain(Model):
    """ Powertrain
    Variables
    ---------
    m                       [kg]            single powertrain mass
    Pmax                    [kW]            maximum power
    P_m_sp_cont             [W/kg]          continuous motor specific power
    P_m_sp_max              [W/kg]          maximum motor specific power
    tau_sp_max              [N*m/kg]        max specific torque
    RPMmax                  [rpm]           max rpm
    r                       [m]             propeller radius
    eta                     [-]             powertrain efficiency
    a             1         [W/kg]          dum
    RPM_margin    0.9       [-]             rpm margin
    tau_margin    0.95      [-]             torque margin
    P_margin      0.5       [-]             power margin
    """
    @parse_variables(__doc__,globals())
    def setup(self):
        with gpkit.SignomialsEnabled():
            constraints = [P_m_sp_cont <= P_margin*(61.8*units("W/kg**2")*m + 6290*units("W/kg")), #magicALL motor fits
                           P_m_sp_max <= P_margin*(86.2*units("W/kg**2")*m + 7860*units("W/kg")),  #magicALL motor fits
                           eta/1*units("kg**(0.0134)") <= 0.906*m**(0.0134),
                           (RPMmax/RPM_margin)*m**(0.201) == 7939*units("rpm*kg**0.201"),
                           Pmax <= m*P_m_sp_max]
        return constraints

class Battery(Model):
    """ Battery
    Variables
    ---------
    m                   [kg]            battery total mass
    Estar       200     [Wh/kg]         battery cell specific energy
    E_capacity          [Wh]            battery total energy capacity
    P_max_cont  2160    [W/kg]          battery cell continuous specific power
    P_max_burst 5190    [W/kg]          battery cell burst specific power
    eta_pack    0.8     [-]             battery packing efficiency
    """
    @parse_variables(__doc__,globals())
    def setup(self):

        with gpkit.SignomialsEnabled():
            constraints = [m >= E_capacity/(eta_pack*Estar),
                        ]
        return constraints
    def dynamic(self,state,powermode=True):
        return BatteryP(self,state,powermode)
    
class BatteryP(Model):
    """BatteryP
    Variables
    ---------
    P                   [kW]        battery power draw
    """
    @parse_variables(__doc__,globals())
    def setup(self,batt,state,powermode):
        if powermode == True:
         constraints = [P <= batt.m*batt.P_max_burst*batt.eta_pack,]
        else:
         constraints = [P <= batt.m*batt.P_max_cont*batt.eta_pack, ]
        return constraints

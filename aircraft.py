import gpkit
from gpkit import Model, parse_variables, Vectorize, SignomialEquality,Variable,units
from fusegear import *
from battm import *
from wing import *
from tail import *
import math
import numpy as np

class Aircraft(Model):
    """ Aircraft

    Variables
    ---------
    mass               [kg]    aircraft mass 
    n_pax       2       [-]     number of passengers
    mpax        86      [kg]    single passenger mass
    mbaggage    10       [kg]    single baggage mass
    tangamma    0.5     [-]     tan of the gamma climb angle
    d                   [in]    spar diam
    """
    @parse_variables(__doc__,globals())
    def setup(self,wingmode):
        self.equipment = Equipment()
        self.battery = Battery()
        self.fuselage = Fuselage()
        self.htail = HorizontalTail()
        self.vtail = VerticalTail()
        self.boom =  TailBoom()
        self.gear = Gear()
        self.vtail.substitutions[self.vtail.planform.tau] = 0.08
        self.htail.substitutions[self.htail.planform.tau] = 0.08
        self.htail.substitutions[self.htail.mh] = 0.8
        self.htail.substitutions[self.vtail.Vv] = 0.1
        self.htail.substitutions[self.htail.planform.CLmax] = 3
        self.vtail.substitutions[self.vtail.planform.CLmax] = 3
        
        if wingmode =="na":
         self.bw = NormalWing()
        elif wingmode =="blownwing":
         self.bw = BlownWing()
        else: print("choose between  na or blownwing , invalid input")

        self.components = [self.bw,self.fuselage,self.gear,self.equipment,self.battery]

        constraints = [

                       self.htail.Vh == (self.htail["S"]*self.htail.lh/self.bw.wing["S"]**2 *self.bw.wing["b"]),
                       self.vtail.Vv == (self.vtail["S"]*self.vtail.lv/self.bw.wing["S"]/self.bw.wing["b"]),
                       
                       self.boom["l"] >= self.htail.lh + self.htail.planform.croot,
                       self.boom["l"] >= self.vtail.lv + self.vtail.planform.croot,

                       self.fuselage.m >= 0.14*(sum(c.m for c in self.components) + (self.boom.W + self.vtail.W + self.htail.W)/2.20462*units('kg/lbf') + (mpax+mbaggage)*n_pax),
                       self.mass >= sum(c.m for c in self.components) + (self.boom.W + self.vtail.W + self.htail.W)/2.20462*units('kg/lbf') + (mpax+mbaggage)*n_pax,
                       self.gear.m >=0.04*self.mass,
                       self.equipment.m>=0.15*self.mass,
                       self.gear.l==0.16*self.fuselage.l,#Source: Raymer, D. P. – Aircraft Design: A Conceptual Approach (5th Edition), Section on Landing Gear Sizing.
                      # self.mass == 750*units("kg"),
                       #self.mass>= self.battery.m
                       ]
        for s in self.boom.d:
            constraints+=[s == d]
        with gpkit.SignomialsEnabled():
            constraints += [self.boom["l"]*0.36 <= self.gear.l + self.fuselage.h,
                            self.bw.wing.b - Variable("w_fuse",50,"in") >= self.bw.n_prop*2*self.bw.powertrain.r]
        return constraints, self.components, self.htail, self.vtail, self.boom
    
    def dynamic(self,state,groundroll=False,powermode=True,wingmode ="blownwing",seg =False):
        return AircraftP(self,state,groundroll=groundroll,powermode=powermode,wingmode=wingmode,seg=seg)

    def loading(self,state,Wcent,Wh,Wv):
        return AircraftLoading(self,state)
    
class AircraftP(Model):
    """ AircraftP

    Variables
    ---------
    P                   [kW]    total power draw
    CD                  [-]     total CD, referenced to wing area
    P_charge            [kW]    battery charging power
    P_avionics  0.25    [kW]    avionics continuous power draw
    C_chrg              [1/hr]  battery charge rate
    CDfrac              [-]     fuselage drag fraction
    L_D                 [-]     aircraft lift-to-drag ratio
    """
    @parse_variables(__doc__,globals())
    def setup(self,aircraft,state,groundroll=False,powermode=True,wingmode="blownwing",seg=False):
        self.fuse_perf = aircraft.fuselage.dynamic(state)

        self.bw_perf = aircraft.bw.dynamic(state)
        self.batt_perf = aircraft.battery.dynamic(state,powermode)
        self.htail_perf = aircraft.htail.flight_model(aircraft.htail, state)
        self.vtail_perf = aircraft.vtail.flight_model(aircraft.vtail, state)
        self.boom_perf = aircraft.boom.flight_model(aircraft.boom, state)
        self.perf_models = [self.fuse_perf,self.bw_perf,self.batt_perf,self.htail_perf,self.vtail_perf,self.boom_perf]
        self.fs = state

        constraints = [P >= self.bw_perf["P"] + P_avionics,
                       CD >= self.bw_perf.C_D + ((aircraft.htail.planform.S/aircraft.bw.wing.planform.S)*self.htail_perf.Cd + (self.fuse_perf.Cd*aircraft.fuselage.Swet/aircraft.bw.wing.planform.S) + (aircraft.vtail.planform.S/aircraft.bw.wing.planform.S)*self.vtail_perf.Cd) + (aircraft.boom.S/aircraft.bw.wing.planform.S)*self.boom_perf.Cf,
                       CDfrac == (self.fuse_perf.Cd*aircraft.fuselage.Swet/aircraft.bw.wing.planform.S)/CD,
                       L_D == self.bw_perf.C_L/CD,
                       state.V <= state.Vne
                    ]
        if wingmode =="blownwing":
         constraints+=[self.bw_perf.C_T >= CD,]
         if seg ==True:aircraft.bw.substitutions.update({aircraft.bw.n_prop :2})
         else: aircraft.bw.substitutions.update({aircraft.bw.n_prop :10})
        #If we're not in groundroll, apply lift=weight and fuselage drag
        if groundroll == False:
            constraints += [0.5*self.bw_perf.C_L*state.rho*aircraft.bw.wing["S"]*state.V**2 >= aircraft.mass*g]
        constraints += [self.batt_perf.P >= P]
        
        

        return constraints,self.perf_models
    
    
class AircraftLoading(Model):
    
    def setup(self,aircraft,state):
        self.hbend = aircraft.boom.tailLoad(aircraft.boom,aircraft.htail,state)
        self.vbend = aircraft.boom.tailLoad(aircraft.boom,aircraft.vtail,state)
        self.wingl = aircraft.bw.wing.spar.loading(aircraft.bw.wing, state)
        self.hl = aircraft.htail.spar.loading(aircraft.htail, state)
        self.vl = aircraft.vtail.spar.loading(aircraft.vtail, state)
        loading = [self.wingl,self.hbend,self.vbend,self.hl,self.vl]
        
        return loading

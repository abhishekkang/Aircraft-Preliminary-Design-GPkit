from gpkitmodels import g

def writeSolNW(sol):
    with open('solveNW11.txt', 'w') as output:
        output.write(sol.table())

def writeWgtNW(sol,M):

        # output.write(str('{:10.4f}'.format(float(sol(M.aircraft.mass).magnitude))) + '\n')

        m_tot   = sol(M.aircraft.mass       )
        m_wing  = sol(M.aircraft.bw.wing.W/g).to("kg")
        m_htail = sol(M.aircraft.htail.W/g  ).to("kg")
        m_vtail = sol(M.aircraft.vtail.W/g  ).to("kg")
        m_boom  = sol(M.aircraft.boom.W/g   ).to("kg")
        m_fuse  = sol(M.aircraft.fuselage.m ).to("kg")
        m_equip = sol(M.aircraft.equipment.m).to("kg")
        m_gear  = sol(M.aircraft.gear.m     ).to("kg")
        m_batt  = sol(M.aircraft.battery.m  )
        m_mot   = sol(M.aircraft.bw.powertrain.m     )
        m_pax   = sol(M.aircraft.mpax       )
        m_bag   = sol(M.aircraft.mbaggage   )
        n_prop  = sol(M.aircraft.bw.n_prop  )
        n_pax   = sol(M.aircraft.n_pax      )
        m_mot_tot = n_prop * m_mot
        m_pax_tot = n_pax  * m_pax
        m_bag_tot = n_pax  * m_bag

        output  = open('weightsNW.csv','w')

        output.write(str(m_tot  .magnitude) + '\n')
        output.write(str(m_wing .magnitude) + '\n')
        output.write(str(m_htail.magnitude) + '\n')
        output.write(str(m_vtail.magnitude) + '\n')
        output.write(str(m_boom .magnitude) + '\n')
        output.write(str(m_fuse .magnitude) + '\n')
        output.write(str(m_equip.magnitude) + '\n')
        output.write(str(m_gear .magnitude) + '\n')
        output.write(str(m_batt .magnitude) + '\n')
        output.write(str(m_mot_tot.magnitude) + '\n')
        output.write(str(m_pax_tot.magnitude) + '\n')
        output.write(str(m_bag_tot.magnitude) + '\n')

        output.close

        output  = open('weightsNW.txt','w')

        output.write('Mass Summary\n')
        output.write('individual motor and passenger-related masses shown\n\n')
        output.write('m_tot   = ' + str(m_tot  ) + '\n')
        output.write('m_wing  = ' + str(m_wing ) + '\n')
        output.write('m_htail = ' + str(m_htail) + '\n')
        output.write('m_vtail = ' + str(m_vtail) + '\n')
        output.write('m_boom  = ' + str(m_boom ) + '\n')
        output.write('m_fuse  = ' + str(m_fuse ) + '\n')
        output.write('m_equip = ' + str(m_equip) + '\n')
        output.write('m_gear  = ' + str(m_gear ) + '\n')
        output.write('m_batt  = ' + str(m_batt ) + '\n')
        output.write('m_mot   = ' + str(m_mot  ) + '\n')
        output.write('m_pax   = ' + str(m_pax  ) + '\n')
        output.write('m_bag   = ' + str(m_bag  ) + '\n')
        output.write('n_prop  = ' + str(n_prop ) + ' [-]' + '\n')
        output.write('n_pax   = ' + str(n_pax  ) + ' [-]' + '\n')

        output.close

def writePropNW(sol,M):

        output  = open('propNW.txt','w')

        A_str = '{:5.3f}'
        T_str = '{:9.0f}'
        U_str = '{:7.2f}'
        R_str = '{:7.0f}'
        t_str = '{:7.2f}'

        A_disk = sol(M.cruise.perf.bw_perf.A_disk).magnitude

        T_TO1 = sol(M.takeoff.perf.bw_perf.T[0]    ).magnitude
        T_TO2 = sol(M.takeoff.perf.bw_perf.T[1]    ).magnitude
        T_TO3 = sol(M.takeoff.perf.bw_perf.T[2]    ).magnitude
        T_TO4 = sol(M.takeoff.perf.bw_perf.T[3]    ).magnitude
        T_CL1 = sol(M.obstacle_climb.perf.bw_perf.T).magnitude
        T_CL2 = sol(M.climb.perf.bw_perf.T         ).magnitude
        T_CR  = sol(M.cruise.perf.bw_perf.T        ).magnitude
        T_L   = sol(M.landing.perf.bw_perf.T       ).magnitude

        U_TO1 = sol(M.takeoff.perf.fs.V[0]    ).to("m/s").magnitude
        U_TO2 = sol(M.takeoff.perf.fs.V[1]    ).to("m/s").magnitude
        U_TO3 = sol(M.takeoff.perf.fs.V[2]    ).to("m/s").magnitude
        U_TO4 = sol(M.takeoff.perf.fs.V[3]    ).to("m/s").magnitude
        U_CL1 = sol(M.obstacle_climb.perf.fs.V).to("m/s").magnitude
        U_CL2 = sol(M.climb.perf.fs.V         ).to("m/s").magnitude
        U_CR  = sol(M.cruise.perf.fs.V        ).to("m/s").magnitude
        U_L   = sol(M.landing.perf.fs.V       ).to("m/s").magnitude

       
        V_TO1 = sol(M.takeoff.perf.fs.V[0]    ).to("kts").magnitude
        V_TO2 = sol(M.takeoff.perf.fs.V[1]    ).to("kts").magnitude
        V_TO3 = sol(M.takeoff.perf.fs.V[2]    ).to("kts").magnitude
        V_TO4 = sol(M.takeoff.perf.fs.V[3]    ).to("kts").magnitude
        V_CL1 = sol(M.obstacle_climb.perf.fs.V).to("kts").magnitude
        V_CL2 = sol(M.climb.perf.fs.V         ).to("kts").magnitude
        V_CR  = sol(M.cruise.perf.fs.V        ).to("kts").magnitude
        V_L   = sol(M.landing.perf.fs.V       ).to("kts").magnitude

        D_TO1 = sol(M.takeoff.Sto[0]          ).to("ft").magnitude
        D_TO2 = sol(M.takeoff.Sto[1]          ).to("ft").magnitude
        D_TO3 = sol(M.takeoff.Sto[2]          ).to("ft").magnitude
        D_TO4 = sol(M.takeoff.Sto[3]          ).to("ft").magnitude
        D_CL1 = sol(M.obstacle_climb.Sclimb   ).to("ft").magnitude
        D_CL2 = sol(M.climb.Sclimb            ).to("ft").magnitude
        D_CR  = sol(M.cruise.R                ).to("ft").magnitude
        D_L   = sol(M.landing.Sgr             ).to("ft").magnitude

        s_TO1 = sol(M.takeoff.t[0]            ).to("s").magnitude
        s_TO2 = sol(M.takeoff.t[1]            ).to("s").magnitude
        s_TO3 = sol(M.takeoff.t[2]            ).to("s").magnitude
        s_TO4 = sol(M.takeoff.t[3]            ).to("s").magnitude
        s_CL1 = sol(M.obstacle_climb.t        ).to("s").magnitude
        s_CL2 = sol(M.climb.t                 ).to("s").magnitude
        s_CR  = sol(M.cruise.t                ).to("s").magnitude
        s_L   = sol(M.landing.t               ).to("s").magnitude
    

        R_TO1 =         D_TO1
        R_TO2 = R_TO1 + D_TO2
        R_TO3 = R_TO2 + D_TO3
        R_TO4 = R_TO3 + D_TO4
        R_CL1 = R_TO4 + D_CL1
        R_CL2 = R_CL1 + D_CL2
        R_CR  = R_CL2 + D_CR
        R_L   = R_CR  + D_L
      #  R_R   =         D_R

        t_TO1 =         s_TO1
        t_TO2 = t_TO1 + s_TO2
        t_TO3 = t_TO2 + s_TO3
        t_TO4 = t_TO3 + s_TO4
        t_CL1 = t_TO4 + s_CL1
        t_CL2 = t_CL1 + s_CL2
        t_CR  = t_CL2 + s_CR
        t_L   = t_CR  + s_L
    #    t_R   =         s_R

        output.write('A_disk = ' + str(A_str.format(float(A_disk))) + ' m^2' + '\n\n')

        output.write('       T_tot [N]  V [m/s]  V [kt]   R [ft]   t [s] R_tot [ft] t_tot [s]')
        output.write('\n' + 'TO1 = ' + str(T_str.format(float(T_TO1)))
                          + '  '     + str(U_str.format(float(U_TO1)))
                          + '  '     + str(U_str.format(float(V_TO1)))
                          + '  '     + str(R_str.format(float(D_TO1)))
                          + '  '     + str(t_str.format(float(s_TO1)))
                          + '  '     + str(R_str.format(float(R_TO1)))
                          + '  '     + str(t_str.format(float(t_TO1))))
        output.write('\n' + 'TO2 = ' + str(T_str.format(float(T_TO2)))
                          + '  '     + str(U_str.format(float(U_TO2)))
                          + '  '     + str(U_str.format(float(V_TO2)))
                          + '  '     + str(R_str.format(float(D_TO2)))
                          + '  '     + str(t_str.format(float(s_TO2)))
                          + '  '     + str(R_str.format(float(R_TO2)))
                          + '  '     + str(t_str.format(float(t_TO2))))
        output.write('\n' + 'TO3 = ' + str(T_str.format(float(T_TO3)))
                          + '  '     + str(U_str.format(float(U_TO3)))
                          + '  '     + str(U_str.format(float(V_TO3)))
                          + '  '     + str(R_str.format(float(D_TO3)))
                          + '  '     + str(t_str.format(float(s_TO3)))
                          + '  '     + str(R_str.format(float(R_TO3)))
                          + '  '     + str(t_str.format(float(t_TO3))))
        output.write('\n' + 'TO4 = ' + str(T_str.format(float(T_TO4)))
                          + '  '     + str(U_str.format(float(U_TO4)))
                          + '  '     + str(U_str.format(float(V_TO4)))
                          + '  '     + str(R_str.format(float(D_TO4)))
                          + '  '     + str(t_str.format(float(s_TO4)))
                          + '  '     + str(R_str.format(float(R_TO4)))
                          + '  '     + str(t_str.format(float(t_TO4))))
        output.write('\n' + 'CL1 = ' + str(T_str.format(float(T_CL1)))
                          + '  '     + str(U_str.format(float(U_CL1)))
                          + '  '     + str(U_str.format(float(V_CL1)))
                          + '  '     + str(R_str.format(float(D_CL1)))
                          + '  '     + str(t_str.format(float(s_CL1)))
                          + '  '     + str(R_str.format(float(R_CL1)))
                          + '  '     + str(t_str.format(float(t_CL1))))
        output.write('\n' + 'CL2 = ' + str(T_str.format(float(T_CL2)))
                          + '  '     + str(U_str.format(float(U_CL2)))
                          + '  '     + str(U_str.format(float(V_CL2)))
                          + '  '     + str(R_str.format(float(D_CL2)))
                          + '  '     + str(t_str.format(float(s_CL2)))
                          + '  '     + str(R_str.format(float(R_CL2)))
                          + '  '     + str(t_str.format(float(t_CL2))))
        output.write('\n' + 'CR  = ' + str(T_str.format(float(T_CR )))
                          + '  '     + str(U_str.format(float(U_CR )))
                          + '  '     + str(U_str.format(float(V_CR )))
                          + '  '     + str(R_str.format(float(D_CR )))
                          + '  '     + str(t_str.format(float(s_CR )))
                          + '  '     + str(R_str.format(float(R_CR )))
                          + '  '     + str(t_str.format(float(t_CR ))))
        output.write('\n' + 'L   = ' + str(T_str.format(float(T_L  )))
                          + '  '     + str(U_str.format(float(U_L  )))
                          + '  '     + str(U_str.format(float(V_L  )))
                          + '  '     + str(R_str.format(float(D_L  )))
                          + '  '     + str(t_str.format(float(s_L  )))
                          + '  '     + str(R_str.format(float(R_L  )))
                          + '  '     + str(t_str.format(float(t_L  ))))
        output.write('\n')
#      )

        output.close
def writeSolBW(sol):
    with open('solveBW11.txt', 'w') as output:
        output.write(sol.table())

def writeWgtBW(sol,M):

        # output.write(str('{:10.4f}'.format(float(sol(M.aircraft.mass).magnitude))) + '\n')

        m_tot   = sol(M.aircraft.mass       )
        m_wing  = sol(M.aircraft.bw.wing.W/g).to("kg")
        m_htail = sol(M.aircraft.htail.W/g  ).to("kg")
        m_vtail = sol(M.aircraft.vtail.W/g  ).to("kg")
        m_boom  = sol(M.aircraft.boom.W/g   ).to("kg")
        m_fuse  = sol(M.aircraft.fuselage.m ).to("kg")
        m_equip = sol(M.aircraft.equipment.m).to("kg")
        m_gear  = sol(M.aircraft.gear.m     ).to("kg")
        m_batt  = sol(M.aircraft.battery.m  )
        m_mot   = sol(M.aircraft.bw.powertrain.m     )
        m_pax   = sol(M.aircraft.mpax       )
        m_bag   = sol(M.aircraft.mbaggage   )
        n_prop  = sol(M.aircraft.bw.n_prop  )
        n_pax   = sol(M.aircraft.n_pax      )
        m_mot_tot = n_prop * m_mot
        m_pax_tot = n_pax  * m_pax
        m_bag_tot = n_pax  * m_bag

        output  = open('weightsBW.csv','w')

        output.write(str(m_tot  .magnitude) + '\n')
        output.write(str(m_wing .magnitude) + '\n')
        output.write(str(m_htail.magnitude) + '\n')
        output.write(str(m_vtail.magnitude) + '\n')
        output.write(str(m_boom .magnitude) + '\n')
        output.write(str(m_fuse .magnitude) + '\n')
        output.write(str(m_equip.magnitude) + '\n')
        output.write(str(m_gear .magnitude) + '\n')
        output.write(str(m_batt .magnitude) + '\n')
        output.write(str(m_mot_tot.magnitude) + '\n')
        output.write(str(m_pax_tot.magnitude) + '\n')
        output.write(str(m_bag_tot.magnitude) + '\n')

        output.close

        output  = open('weightsBW.txt','w')

        output.write('Mass Summary\n')
        output.write('individual motor and passenger-related masses shown\n\n')
        output.write('m_tot   = ' + str(m_tot  ) + '\n')
        output.write('m_wing  = ' + str(m_wing ) + '\n')
        output.write('m_htail = ' + str(m_htail) + '\n')
        output.write('m_vtail = ' + str(m_vtail) + '\n')
        output.write('m_boom  = ' + str(m_boom ) + '\n')
        output.write('m_fuse  = ' + str(m_fuse ) + '\n')
        output.write('m_equip = ' + str(m_equip) + '\n')
        output.write('m_gear  = ' + str(m_gear ) + '\n')
        output.write('m_batt  = ' + str(m_batt ) + '\n')
        output.write('m_mot   = ' + str(m_mot  ) + '\n')
        output.write('m_pax   = ' + str(m_pax  ) + '\n')
        output.write('m_bag   = ' + str(m_bag  ) + '\n')
        output.write('n_prop  = ' + str(n_prop ) + ' [-]' + '\n')
        output.write('n_pax   = ' + str(n_pax  ) + ' [-]' + '\n')

        output.close
def writePropBW(sol,M):

           output  = open('propBW.txt','w')

           A_str = '{:5.3f}'
           T_str = '{:9.0f}'
           U_str = '{:7.2f}'
           R_str = '{:7.0f}'
           t_str = '{:7.2f}'

           A_disk = sol(M.cruise.perf.bw_perf.A_disk).magnitude

           T_TO1 = sol(M.takeoff.perf.bw_perf.T[0]    ).magnitude
           T_TO2 = sol(M.takeoff.perf.bw_perf.T[1]    ).magnitude
           T_TO3 = sol(M.takeoff.perf.bw_perf.T[2]    ).magnitude
           T_TO4 = sol(M.takeoff.perf.bw_perf.T[3]    ).magnitude
           T_CL1 = sol(M.obstacle_climb.perf.bw_perf.T).magnitude
           T_CL2 = sol(M.climb.perf.bw_perf.T         ).magnitude
           T_CR  = sol(M.cruise.perf.bw_perf.T        ).magnitude
           T_L   = sol(M.landing.perf.bw_perf.T       ).magnitude
          # T_R   = sol(M.reserve.perf.bw_perf.T       ).magnitude

           U_TO1 = sol(M.takeoff.perf.fs.V[0]    ).to("m/s").magnitude
           U_TO2 = sol(M.takeoff.perf.fs.V[1]    ).to("m/s").magnitude
           U_TO3 = sol(M.takeoff.perf.fs.V[2]    ).to("m/s").magnitude
           U_TO4 = sol(M.takeoff.perf.fs.V[3]    ).to("m/s").magnitude
           U_CL1 = sol(M.obstacle_climb.perf.fs.V).to("m/s").magnitude
           U_CL2 = sol(M.climb.perf.fs.V         ).to("m/s").magnitude
           U_CR  = sol(M.cruise.perf.fs.V        ).to("m/s").magnitude
           U_L   = sol(M.landing.perf.fs.V       ).to("m/s").magnitude
          # U_R   = sol(M.reserve.perf.fs.V       ).to("m/s").magnitude

           u_j_TO1 = sol(M.takeoff.perf.bw_perf.u_j[0]    ).to("m/s").magnitude
           u_j_TO2 = sol(M.takeoff.perf.bw_perf.u_j[1]    ).to("m/s").magnitude
           u_j_TO3 = sol(M.takeoff.perf.bw_perf.u_j[2]    ).to("m/s").magnitude
           u_j_TO4 = sol(M.takeoff.perf.bw_perf.u_j[3]    ).to("m/s").magnitude
           u_j_CL1 = sol(M.obstacle_climb.perf.bw_perf.u_j).to("m/s").magnitude
           u_j_CL2 = sol(M.climb.perf.bw_perf.u_j         ).to("m/s").magnitude
           u_j_CR  = sol(M.cruise.perf.bw_perf.u_j        ).to("m/s").magnitude
           u_j_L   = sol(M.landing.perf.bw_perf.u_j       ).to("m/s").magnitude
        #   u_j_R   = sol(M.reserve.perf.bw_perf.u_j       ).to("m/s").magnitude

           V_TO1 = sol(M.takeoff.perf.fs.V[0]    ).to("kts").magnitude
           V_TO2 = sol(M.takeoff.perf.fs.V[1]    ).to("kts").magnitude
           V_TO3 = sol(M.takeoff.perf.fs.V[2]    ).to("kts").magnitude
           V_TO4 = sol(M.takeoff.perf.fs.V[3]    ).to("kts").magnitude
           V_CL1 = sol(M.obstacle_climb.perf.fs.V).to("kts").magnitude
           V_CL2 = sol(M.climb.perf.fs.V         ).to("kts").magnitude
           V_CR  = sol(M.cruise.perf.fs.V        ).to("kts").magnitude
           V_L   = sol(M.landing.perf.fs.V       ).to("kts").magnitude
      #     V_R   = sol(M.reserve.perf.fs.V       ).to("kts").magnitude

           D_TO1 = sol(M.takeoff.Sto[0]          ).to("ft").magnitude
           D_TO2 = sol(M.takeoff.Sto[1]          ).to("ft").magnitude
           D_TO3 = sol(M.takeoff.Sto[2]          ).to("ft").magnitude
           D_TO4 = sol(M.takeoff.Sto[3]          ).to("ft").magnitude
           D_CL1 = sol(M.obstacle_climb.Sclimb   ).to("ft").magnitude
           D_CL2 = sol(M.climb.Sclimb            ).to("ft").magnitude
           D_CR  = sol(M.cruise.R                ).to("ft").magnitude
           D_L   = sol(M.landing.Sgr             ).to("ft").magnitude
         #  D_R   = sol(M.reserve.R               ).to("ft").magnitude

           s_TO1 = sol(M.takeoff.t[0]            ).to("s").magnitude
           s_TO2 = sol(M.takeoff.t[1]            ).to("s").magnitude
           s_TO3 = sol(M.takeoff.t[2]            ).to("s").magnitude
           s_TO4 = sol(M.takeoff.t[3]            ).to("s").magnitude
           s_CL1 = sol(M.obstacle_climb.t        ).to("s").magnitude
           s_CL2 = sol(M.climb.t                 ).to("s").magnitude
           s_CR  = sol(M.cruise.t                ).to("s").magnitude
           s_L   = sol(M.landing.t               ).to("s").magnitude
         #  s_R   = sol(M.reserve.t               ).to("s").magnitude

           R_TO1 =         D_TO1
           R_TO2 = R_TO1 + D_TO2
           R_TO3 = R_TO2 + D_TO3
           R_TO4 = R_TO3 + D_TO4
           R_CL1 = R_TO4 + D_CL1
           R_CL2 = R_CL1 + D_CL2
           R_CR  = R_CL2 + D_CR
           R_L   = R_CR  + D_L
         #  R_R   =         D_R

           t_TO1 =         s_TO1
           t_TO2 = t_TO1 + s_TO2
           t_TO3 = t_TO2 + s_TO3
           t_TO4 = t_TO3 + s_TO4
           t_CL1 = t_TO4 + s_CL1
           t_CL2 = t_CL1 + s_CL2
           t_CR  = t_CL2 + s_CR
           t_L   = t_CR  + s_L
       #    t_R   =         s_R

           output.write('A_disk = ' + str(A_str.format(float(A_disk))) + ' m^2' + '\n\n')

           output.write('       T_tot [N]  V [m/s]  uj [m/s]  V [kt]   R [ft]   t [s] R_tot [ft] t_tot [s]')
           output.write('\n' + 'TO1 = ' + str(T_str.format(float(T_TO1)))
                             + '  '     + str(U_str.format(float(U_TO1)))
                             + '  '     + str(U_str.format(float(u_j_TO1)))
                             + '  '     + str(U_str.format(float(V_TO1)))
                             + '  '     + str(R_str.format(float(D_TO1)))
                             + '  '     + str(t_str.format(float(s_TO1)))
                             + '  '     + str(R_str.format(float(R_TO1)))
                             + '  '     + str(t_str.format(float(t_TO1))))
           output.write('\n' + 'TO2 = ' + str(T_str.format(float(T_TO2)))
                             + '  '     + str(U_str.format(float(U_TO2)))
                             + '  '     + str(U_str.format(float(u_j_TO2)))
                             + '  '     + str(U_str.format(float(V_TO2)))
                             + '  '     + str(R_str.format(float(D_TO2)))
                             + '  '     + str(t_str.format(float(s_TO2)))
                             + '  '     + str(R_str.format(float(R_TO2)))
                             + '  '     + str(t_str.format(float(t_TO2))))
           output.write('\n' + 'TO3 = ' + str(T_str.format(float(T_TO3)))
                             + '  '     + str(U_str.format(float(U_TO3)))
                             + '  '     + str(U_str.format(float(u_j_TO3)))
                             + '  '     + str(U_str.format(float(V_TO3)))
                             + '  '     + str(R_str.format(float(D_TO3)))
                             + '  '     + str(t_str.format(float(s_TO3)))
                             + '  '     + str(R_str.format(float(R_TO3)))
                             + '  '     + str(t_str.format(float(t_TO3))))
           output.write('\n' + 'TO4 = ' + str(T_str.format(float(T_TO4)))
                             + '  '     + str(U_str.format(float(U_TO4)))
                             + '  '     + str(U_str.format(float(u_j_TO4)))
                             + '  '     + str(U_str.format(float(V_TO4)))
                             + '  '     + str(R_str.format(float(D_TO4)))
                             + '  '     + str(t_str.format(float(s_TO4)))
                             + '  '     + str(R_str.format(float(R_TO4)))
                             + '  '     + str(t_str.format(float(t_TO4))))
           output.write('\n' + 'CL1 = ' + str(T_str.format(float(T_CL1)))
                             + '  '     + str(U_str.format(float(U_CL1)))
                             + '  '     + str(U_str.format(float(u_j_CL1)))
                             + '  '     + str(U_str.format(float(V_CL1)))
                             + '  '     + str(R_str.format(float(D_CL1)))
                             + '  '     + str(t_str.format(float(s_CL1)))
                             + '  '     + str(R_str.format(float(R_CL1)))
                             + '  '     + str(t_str.format(float(t_CL1))))
           output.write('\n' + 'CL2 = ' + str(T_str.format(float(T_CL2)))
                             + '  '     + str(U_str.format(float(U_CL2)))
                             + '  '     + str(U_str.format(float(u_j_CL2)))
                             + '  '     + str(U_str.format(float(V_CL2)))
                             + '  '     + str(R_str.format(float(D_CL2)))
                             + '  '     + str(t_str.format(float(s_CL2)))
                             + '  '     + str(R_str.format(float(R_CL2)))
                             + '  '     + str(t_str.format(float(t_CL2))))
           output.write('\n' + 'CR  = ' + str(T_str.format(float(T_CR )))
                             + '  '     + str(U_str.format(float(U_CR )))
                             + '  '     + str(U_str.format(float(u_j_CR )))
                             + '  '     + str(U_str.format(float(V_CR )))
                             + '  '     + str(R_str.format(float(D_CR )))
                             + '  '     + str(t_str.format(float(s_CR )))
                             + '  '     + str(R_str.format(float(R_CR )))
                             + '  '     + str(t_str.format(float(t_CR ))))
           output.write('\n' + 'L   = ' + str(T_str.format(float(T_L  )))
                             + '  '     + str(U_str.format(float(U_L  )))
                             + '  '     + str(U_str.format(float(u_j_L  )))
                             + '  '     + str(U_str.format(float(V_L  )))
                             + '  '     + str(R_str.format(float(D_L  )))
                             + '  '     + str(t_str.format(float(s_L  )))
                             + '  '     + str(R_str.format(float(R_L  )))
                             + '  '     + str(t_str.format(float(t_L  ))))
           output.write('\n')
   #        output.write('\n' + 'R   = ' + str(T_str.format(float(T_R  )))
                 #            + '  '     + str(U_str.format(float(U_R  )))
               #              + '  '     + str(U_str.format(float(u_j_R  )))
                #             + '  '     + str(U_str.format(float(V_R  )))
               # #             + '  '     + str(R_str.format(float(D_R  )))
                #             + '  '     + str(t_str.format(float(s_R  )))
                #             + '  '     + str(R_str.format(float(R_R  )))
                #             + '  '     + str(t_str.format(float(t_R  ))))

           output.close     
      
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QLabel, QComboBox, QGridLayout, QTextEdit
)
from gpkit import units
from mission import Mission

class InputsTab(QWidget):
    def __init__(self, parent_callback):
        super().__init__()
        self.inputs = {}
        self.parent_callback = parent_callback
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout()

        self.wing_selector = QComboBox()
        self.wing_selector.addItems(["blownwing", "na"])
        main_layout.addWidget(QLabel("Select Wing Type:"))
        main_layout.addWidget(self.wing_selector)

        grid = QGridLayout()

        # Input fields (curated and renamed)
        group_fields = {
            "Wing": {
                "AR": "Wing Aspect Ratio",
                "b": "Wing Span (ft)",
                "lam": "Taper Ratio",
                "tau": "Thickness Ratio"
            },
            "Tail": {
                "V_h": "Horizontal Tail Volume Coeff.",
                "V_v": "Vertical Tail Volume Coeff."
            },
         
            "Fuselage": {
                "l_fus": "Length (m)",
                "w_fus": "Width (m)",
                "h_fus": "Height (m)"
            },
            "Aerodynamics": {
                "C_Lmax": "Max Lift Coeff.",
                "C_D0": "Parasite Drag Coeff.",
                "e": "Oswald Efficiency",
                "V_cruise": "Cruise Speed (kt)",
                "V_stall": "Stall Speed (kt)"
            },
            "Battery & Propulsion": {
                "m_batt": "Battery Mass (kg)",
                "E_batt": "Battery Energy (kWh)",
                "eta": "Powertrain Efficiency",
                "n_prop": "No. of Blown Wing Propellers",
                "E_Star":"battery specific energy",
                "b_eta":"battery packing efficiency" 
            },
            "Flight Conditions": {
                "rho": "Air Density (kg/m^3)",
                "mu": "Viscosity (kg/m/s)"
            },
            
        }

        row, col = 0, 0
        for group_name, fields in group_fields.items():
            box = QGroupBox(group_name)
            form = QFormLayout()
            for key, label in fields.items():
                le = QLineEdit()
                le.setPlaceholderText(label)
                self.inputs[key] = le
                form.addRow(QLabel(label), le)
            box.setLayout(form)
            grid.addWidget(box, row, col)
            col = (col + 1) % 2
            if col == 0:
                row += 1

        main_layout.addLayout(grid)

        self.solve_button = QPushButton("🔁 Solve Mission")
        self.solve_button.clicked.connect(self.run_solve)
        main_layout.addWidget(self.solve_button)

        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        main_layout.addWidget(QLabel("✈️ Mission Summary:"))
        main_layout.addWidget(self.summary_box)

        self.setLayout(main_layout)

    def run_solve(self):
        try:
            wingtype = self.wing_selector.currentText()
            M = Mission(wingmode=wingtype)

            # Variable mapping from string key to model variable
            varmap = {
                "AR": M.aircraft.bw.wing.planform.AR,
                "b": M.aircraft.bw.wing.planform.b,
                "lam": M.aircraft.bw.wing.planform.lam,
                "tau": M.aircraft.bw.wing.planform.tau,
                "V_h": M.aircraft.htail.Vh,
                "V_v": M.aircraft.vtail.Vv,
                "l_fus": M.aircraft.fuselage.l,
                "w_fus": M.aircraft.fuselage.w,
                "h_fus": M.aircraft.fuselage.h,
                "C_Lmax": M.CLmax,
                "C_D0": M.cruise.perf.bw_perf.C_D,
                "e": M.cruise.perf.bw_perf.e,
                "V_cruise": M.cruise.flightstate.V,
                "V_stall": M.Vstall,
                "m_batt": M.aircraft.battery.m,
                "E_batt": M.aircraft.battery.E_capacity,
                "eta": M.aircraft.bw.powertrain.eta,
                "n_prop": M.aircraft.bw.n_prop,
                "rho": M.cruise.flightstate.rho,
                "mu": M.cruise.flightstate.mu,
                "E_Star":M.aircraft.battery.Estar,
                "b_eta":M.aircraft.battery.eta_pack
            }

            unitmap = {
                "b": units.ft,
                "V_cruise": units.kts,
                "V_stall": units.kts,
                "l_boom": units.m,
                "l_fus": units.m,
                "w_fus": units.m,
                "h_fus": units.m,
                "m_batt": units.kg,
                "E_batt": units.kWh,
                "rho": units.kg / units.m**3,
                "mu": units.kg / (units.m * units.s),
                "E_Star":units("Wh/kg")
            }

            substitutions = {}
            for key, field in self.inputs.items():
                val = field.text().strip()
                if val:
                    try:
                        parsed = float(val)
                        var = varmap[key]
                        unit = unitmap.get(key, 1)
                        substitutions[var] = parsed * unit
                    except Exception as e:
                        print(f"⚠️ Invalid input for '{key}': {e}")

            if substitutions:
                M.substitutions.update(substitutions)

            M.cost = 1 / M.R
            sol = M.localsolve("cvxopt")

            self.mission = M
            self.solution = sol

            self.parent_callback(M, sol)

            # Summary output
            try:
                total_mass = sol(M.aircraft.mass).to("kg").magnitude
                cruise_speed = sol(M.cruise.flightstate.V).to("kt").magnitude
                range_nmi = sol(M.R).to("nmi").magnitude
                energy_kwh = sol(M.aircraft.battery.E_capacity).to("kWh").magnitude
                payload = sol(M.aircraft.n_pax*M.aircraft.mpax+M.aircraft.mbaggage).to("kg").magnitude


                self.summary_box.setText(f"""✅ Mission Results:
- Aircraft Mass: {total_mass:.1f} kg
- Cruise Speed: {cruise_speed:.1f} kt
- Range: {range_nmi:.1f} nmi
- Battery Capacity: {energy_kwh:.1f} kWh
-Payload Mass: {payload:.1f} kg
""")
            except Exception as e:
                self.summary_box.setText(f"❌ Failed to generate summary: {e}")

        except Exception as e:
            self.summary_box.setText(f"❌ Solve failed: {e}")

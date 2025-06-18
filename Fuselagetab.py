from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit
)

class FuselageTab(QWidget):
    def __init__(self):
        super().__init__()
        self.M = None
        self.sol = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        layout.addWidget(QLabel("Fuselage and Gear Summary:"))
        layout.addWidget(self.summary_box)
        self.setLayout(layout)

    def update_from_solution(self, mission, solution):
        self.M = mission
        self.sol = solution
        self.build_summary()

    def build_summary(self):
        try:
            fuselage = self.M.aircraft.fuselage
            gear = self.M.aircraft.gear
            equip = self.M.aircraft.equipment
            sol = self.sol

            l = sol(fuselage.l).to("m").magnitude
            w = sol(fuselage.w).to("m").magnitude
            h = sol(fuselage.h).to("m").magnitude
            Swet = sol(fuselage.Swet).to("m^2").magnitude

            m_gear = sol(gear.m).to("kg").magnitude
            l_gear = sol(gear.l).to("m").magnitude
            
            m_equip = sol(equip.m).to("kg").magnitude

            self.summary_box.setText(f"""✅ Fuselage & Gear Summary:
- Fuselage: {l:.2f} m x {w:.2f} m x {h:.2f} m
- Wetted Area: {Swet:.2f} m²
- Gear Mass: {m_gear:.2f} kg, Length: {l_gear:.2f} m
--- Equipment ---
- Avionics Mass: {m_equip:.2f} kg""")
        except Exception as e:
            self.summary_box.setText(f"❌ Summary failed: {e}")

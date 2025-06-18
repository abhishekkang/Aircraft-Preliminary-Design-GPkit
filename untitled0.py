import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QTabWidget
)

from inputtab import InputsTab  # ✅ New central input tab
from wingtab import WingDesignTab
from tailtab import TailSizingTab
from tailboom import TailBoomTab
from Fuselagetab import FuselageTab
from aerotab import AerodynamicsTab
from proptab import PropulsionTab  # You can add later
# from missiontab import MissionTab
# from comparison import ComparisonTab
# from plots_tab import PlotsTab

class GPkitGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPkit Aircraft Design GUI")
        self.setGeometry(100, 100, 1000, 700)

        # Hold shared model/solution for global access
        self.mission = None
        self.solution = None

        # Tabs
        self.tabs = QTabWidget()
        self.init_tabs()

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def init_tabs(self):
        # ✅ Inputs tab: solves everything
        self.inputs_tab = InputsTab(self.handle_solve_callback)
        self.tabs.addTab(self.inputs_tab, "Inputs + Solve")

        # ✅ Other tabs: initially empty, populated after solve
        self.wing_tab = WingDesignTab()
        self.tabs.addTab(self.wing_tab, "Wing Design")

        self.tail_tab = TailSizingTab()
        self.tabs.addTab(self.tail_tab, " Tail Sizing")

        self.boom_tab = TailBoomTab()
        self.tabs.addTab(self.boom_tab, " Tail Boom")

        self.fuselage_tab = FuselageTab()
        self.tabs.addTab(self.fuselage_tab, " Fuselage + Gear")

        self.aero_tab = AerodynamicsTab()
        self.tabs.addTab(self.aero_tab, " Aerodynamics")
        
        self.prop_tab = PropulsionTab()
        self.tabs.addTab(PropulsionTab(), "Propulsion")
        # Add more if needed:
        # self.tabs.addTab(MissionTab(), "Mission")
        # self.tabs.addTab(ComparisonTab(), "Comparison")
        # self.tabs.addTab(PlotsTab(), "Plots")

    def handle_solve_callback(self, mission, solution):
        """Distribute solved data to all tabs"""
        self.mission = mission
        self.solution = solution
        
        self.aero_tab.update_from_solution(mission, solution)
        self.wing_tab.update_from_solution(mission, solution)
        self.tail_tab.update_from_solution(mission, solution)
        self.boom_tab.update_from_solution(mission, solution)
        self.fuselage_tab.update_from_solution(mission, solution)
        self.prop_tab.update_from_solution(mission, solution)
        # Add other tab updates if needed


# === MAIN ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = GPkitGUI()
    gui.show()
    sys.exit(app.exec_())

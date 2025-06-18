import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTabWidget, QLabel
)

from inputtab import InputsTab
from wingtab import WingDesignTab
from tailtab import TailSizingTab
from tailboom import TailBoomTab
from Fuselagetab import FuselageTab
from aerotab import AerodynamicsTab
from missiontab import MissionTab
from proptab import PropulsionTab
from senstivity_tab import SensitivityTab
# from plots_tab import PlotsTab (optional)


class GPkitGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GPkit Aircraft Design GUI")
        self.setGeometry(100, 100, 1100, 750)

        self.solution = None
        self.mission = None

        self.tabs = QTabWidget()
        self.init_tabs()

        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def init_tabs(self):
        # Input Tab (Triggers Solve)
        self.inputs_tab = InputsTab(self.handle_solution)
        self.tabs.addTab(self.inputs_tab, "Inputs + Solve")

        # Result Tabs (Display only after solve)
        self.wing_tab = WingDesignTab()
        self.tabs.addTab(self.wing_tab, "Wing")

        self.tail_tab = TailSizingTab()
        self.tabs.addTab(self.tail_tab, "Tail")

        self.tailboom_tab = TailBoomTab()
        self.tabs.addTab(self.tailboom_tab, "Tail Boom")

        self.fuselage_tab = FuselageTab()
        self.tabs.addTab(self.fuselage_tab, "Fuselage + Gear")

        self.aero_tab = AerodynamicsTab()
        self.tabs.addTab(self.aero_tab, "Aerodynamics")

        self.mission_tab = MissionTab()
        self.tabs.addTab(self.mission_tab, "Mission")

        
        self.propulsion_tab = PropulsionTab()
        self.tabs.addTab(self.propulsion_tab, "Propulsion")
        
        self.sensitivity_tab = SensitivityTab()
        self.tabs.addTab(self.sensitivity_tab, "Sensitivity")

        # self.plots_tab = PlotsTab()
        # self.tabs.addTab(self.plots_tab, "Extra Plots")

    def handle_solution(self, mission_model, solution_data):
        """Callback called by InputsTab after a solve."""
        self.mission = mission_model
        self.solution = solution_data

        # Propagate to all result tabs
        self.wing_tab.update_from_solution(mission_model, solution_data)
        self.tail_tab.update_from_solution(mission_model, solution_data)
        self.tailboom_tab.update_from_solution(mission_model, solution_data)
        self.fuselage_tab.update_from_solution(mission_model, solution_data)
        self.aero_tab.update_from_solution(mission_model, solution_data)
        self.mission_tab.update_from_solution(mission_model, solution_data)
        self.propulsion_tab.update_from_solution(mission_model, solution_data)
        self.sensitivity_tab.update_from_solution(mission_model, solution_data)

        # self.plots_tab.update_from_solution(...)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GPkitGUI()
    window.show()
    sys.exit(app.exec_())

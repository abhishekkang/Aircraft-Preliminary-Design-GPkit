from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QLabel,
    QPushButton, QComboBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class PlotsTab(QWidget):
    def __init__(self, data_bw, data_nw):
        super().__init__()
        self.data_bw = data_bw
        self.data_nw = data_nw
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.tabs = QTabWidget()

        # Add sub-tabs
        self.tabs.addTab(self.make_structural_tab(), "Structural")
        #self.tabs.addTab(self.make_propulsion_tab(), "Propulsion")
        self.tabs.addTab(self.make_mission_tab(), "Mission")
        self.tabs.addTab(self.make_mass_tab(), "Mass Breakdown")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    # ---------- STRUCTURAL TAB ----------
    def make_structural_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(QLabel("Structural Plot: Wing Spar Inertia"))
        layout.addWidget(canvas)

        ax = canvas.figure.add_subplot(111)
        x = np.linspace(0, 1, len(self.data_nw.get("wing_I", [])))

        ax.plot(x, self.data_nw.get("wing_I", []), label="Normal Wing", lw=2)
        ax.plot(x, self.data_bw.get("wing_I", []), label="Blown Wing", lw=2)
        ax.set_title("Spar Inertia Along Wing Span")
        ax.set_xlabel("Normalized Span")
        ax.set_ylabel("Inertia (m⁴)")
        ax.grid(True)
        ax.legend()

        tab.setLayout(layout)
        return tab

    # ---------- PROPULSION TAB ----------
    def make_propulsion_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(QLabel("Mission Phase Thrust Comparison"))
        layout.addWidget(canvas)

        ax = canvas.figure.add_subplot(111)
        phases = self.data_bw.get("phases", ["TO", "Climb", "Cruise", "Landing"])
        T_bw = self.data_bw.get("thrusts", [0]*4)
        T_nw = self.data_nw.get("thrusts", [0]*4)

        ax.plot(phases, T_bw, marker='o', label="Blown Wing")
        ax.plot(phases, T_nw, marker='s', label="Normal Wing")
        ax.set_title("Thrust per Mission Phase")
        ax.set_ylabel("Thrust (N)")
        ax.grid(True)
        ax.legend()

        tab.setLayout(layout)
        return tab

    # ---------- MISSION TAB ----------
    def make_mission_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(QLabel("Mission Summary: Range & Time"))
        layout.addWidget(canvas)

        ax = canvas.figure.add_subplot(111)
        categories = ["Range (km)", "Time (s)", "Cruise L/D", "Climb L/D", "Landing L/D"]
        values_nw = [
            self.data_nw.get("range", 0),
            self.data_nw.get("time", 0),
            self.data_nw.get("ld_cruise", 0),
            self.data_nw.get("ld_climb", 0),
            self.data_nw.get("ld_landing", 0)
        ]
        values_bw = [
            self.data_bw.get("range", 0),
            self.data_bw.get("time", 0),
            self.data_bw.get("ld_cruise", 0),
            self.data_bw.get("ld_climb", 0),
            self.data_bw.get("ld_landing", 0)
        ]

        x = np.arange(len(categories))
        bar_width = 0.35
        ax.bar(x - bar_width/2, values_nw, width=bar_width, label="Normal Wing")
        ax.bar(x + bar_width/2, values_bw, width=bar_width, label="Blown Wing")
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=30)
        ax.set_title("Mission Metrics Comparison")
        ax.grid(True)
        ax.legend()

        tab.setLayout(layout)
        return tab

    # ---------- MASS BREAKDOWN TAB ----------
    def make_mass_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(QLabel("Aircraft Mass Comparison"))
        layout.addWidget(canvas)

        ax = canvas.figure.add_subplot(111)
        categories = ["Total Mass", "Battery", "Wing", "Tail", "Fuselage", "Gear"]
        mass_nw = [
            self.data_nw.get("mass", 0),
            self.data_nw.get("mass_batt", 0),
            self.data_nw.get("mass_wing", 0),
            self.data_nw.get("mass_tail", 0),
            self.data_nw.get("mass_fuse", 0),
            self.data_nw.get("mass_gear", 0)
        ]
        mass_bw = [
            self.data_bw.get("mass", 0),
            self.data_bw.get("mass_batt", 0),
            self.data_bw.get("mass_wing", 0),
            self.data_bw.get("mass_tail", 0),
            self.data_bw.get("mass_fuse", 0),
            self.data_bw.get("mass_gear", 0)
        ]

        x = np.arange(len(categories))
        bar_width = 0.35
        ax.bar(x - bar_width/2, mass_nw, width=bar_width, label="Normal Wing")
        ax.bar(x + bar_width/2, mass_bw, width=bar_width, label="Blown Wing")
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=30)
        ax.set_ylabel("Mass (kg)")
        ax.set_title("Mass Breakdown")
        ax.grid(True)
        ax.legend()

        tab.setLayout(layout)
        return tab

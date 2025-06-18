
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit,
    QPushButton, QLabel, QTextEdit, QComboBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gpkit import units
from mission import Mission
import numpy as np
class GearTab(QWidget):
    def __init__(self):
        super().__init__()
        self.user_inputs = {}
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Inputs for Gear Parameters
        input_group = QGroupBox("Optional Gear Inputs")
        form_layout = QFormLayout()
        self.inputs = {}

        fields = {
            "m": "Gear Mass (kg)",
            "l": "Gear Length (m)"
        }

        for key, placeholder in fields.items():
            field = QLineEdit()
            field.setPlaceholderText(placeholder)
            self.inputs[key] = field
            form_layout.addRow(QLabel(key), field)

        self.solve_button = QPushButton("Run Gear Analysis")
        self.solve_button.clicked.connect(self.solve_and_display)
        form_layout.addRow(self.solve_button)
        input_group.setLayout(form_layout)
        layout.addWidget(input_group)

        # Summary box
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        layout.addWidget(QLabel("Gear Summary:"))
        layout.addWidget(self.summary_box)

        # Plot area
        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def solve_and_display(self):
        try:
            M = Mission(wingmode="na")  # Use your wingmode as needed
            gear = M.aircraft.gear

            # Substituting user inputs
            substitutions = {
                "m": gear.m,
                "l": gear.l
            }

            for key, var in substitutions.items():
                val = self.inputs[key].text()
                if val:
                    parsed = float(val)
                    unit = units.kg if key == "m" else units.m
                    M.substitutions.update({var: parsed * unit})
                    self.user_inputs[key] = parsed

            sol = M.localsolve('cvxopt')

            self.summary_box.setText(self.build_summary(gear, sol))
            #self.plot_gear_structure(gear, sol)

        except Exception as e:
            self.summary_box.setText(f"❌ Solve failed: {e}")

    def build_summary(self, gear, sol):
        try:
            m = sol(gear.m).to("kg").magnitude
            l = sol(gear.l).to("m").magnitude

            return f"""✅ Gear Summary:
- Mass: {m:.2f} kg
- Length: {l:.2f} m
"""
        except Exception as e:
            return f"❌ Failed to extract summary: {e}"

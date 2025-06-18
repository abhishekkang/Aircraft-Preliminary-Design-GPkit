from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel, QTextEdit, QComboBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class TailSizingTab(QWidget):
    def __init__(self):
        super().__init__()
        self.M = None
        self.sol = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        layout.addWidget(QLabel("Tail Sizing Summary:"))
        layout.addWidget(self.summary_box)

        self.plot_selector = QComboBox()
        self.plot_selector.addItems([
            "HTail Deflection", "HTail Spar Inertia", "HTail Section Modulus",
            "VTail Deflection", "VTail Spar Inertia", "VTail Section Modulus"
        ])
        self.plot_selector.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(self.plot_selector)

        self.canvas = FigureCanvas(Figure(figsize=(6, 4)))
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def update_from_solution(self, mission, solution):
        self.M = mission
        self.sol = solution
        self.prepare_plot_data()
        self.build_summary()
        self.update_plot()

    def prepare_plot_data(self):
        try:
            sol = self.sol
            M = self.M

            # Horizontal tail
            self.ht_defl = sol(M.loading.hl.w).to("m").magnitude
            self.ht_I = sol(M.aircraft.htail.spar["I"]).to("m^4").magnitude
            self.ht_Sy = sol(M.aircraft.htail.spar["Sy"]).to("m^3").magnitude

            # Vertical tail
            self.vt_defl = sol(M.loading.vl.w).to("m").magnitude
            self.vt_I = sol(M.aircraft.vtail.spar["I"]).to("m^4").magnitude
            self.vt_Sy = sol(M.aircraft.vtail.spar["Sy"]).to("m^3").magnitude

            # Spanwise positions (use linear assumption)
            self.x_ht = np.linspace(0, 1, len(self.ht_defl))
            self.x_vt = np.linspace(0, 1, len(self.vt_defl))

        except Exception as e:
            self.summary_box.setText(f"❌ Failed to extract plot data: {e}")

    def build_summary(self):
        try:
            sol = self.sol
            M = self.M
            W_ht = sol(M.aircraft.htail.W).to("lbf").magnitude
            W_vt = sol(M.aircraft.vtail.W).to("lbf").magnitude
            b_ht = sol(M.aircraft.htail.planform.b).to("ft").magnitude
            b_vt = sol(M.aircraft.vtail.planform.b).to("ft").magnitude
            lh = sol(M.aircraft.htail.lh).to("ft").magnitude
            lv = sol(M.aircraft.vtail.lv).to("ft").magnitude

            self.summary_box.setText(f"""✅ Tail Sizing Summary:
- HTail Span: {b_ht:.2f} ft, Weight: {W_ht:.2f} lbf, Moment Arm: {lh:.2f} ft
- VTail Span: {b_vt:.2f} ft, Weight: {W_vt:.2f} lbf, Moment Arm: {lv:.2f} ft
- HTail Max Deflection: {max(self.ht_defl):.3f} m
- VTail Max Deflection: {max(self.vt_defl):.3f} m
""")

        except Exception as e:
            self.summary_box.setText(f"❌ Failed to build summary: {e}")

    def update_plot(self):
        try:
            self.canvas.figure.clf()
            ax = self.canvas.figure.add_subplot(111)
            selected = self.plot_selector.currentText()

            if selected == "HTail Deflection":
                ax.plot(self.x_ht, self.ht_defl, color="blue")
                ax.set_ylabel("Deflection (m)")
            elif selected == "HTail Spar Inertia":
                ax.plot(self.x_ht[:len(self.ht_I)], self.ht_I, color="green")
                ax.set_ylabel("Spar Inertia (m⁴)")
            elif selected == "HTail Section Modulus":
                ax.plot(self.x_ht[:len(self.ht_Sy)], self.ht_Sy, color="orange")
                ax.set_ylabel("Section Modulus (m³)")
            elif selected == "VTail Deflection":
                ax.plot(self.x_vt, self.vt_defl, color="red")
                ax.set_ylabel("Deflection (m)")
            elif selected == "VTail Spar Inertia":
                ax.plot(self.x_vt[:len(self.vt_I)], self.vt_I, color="purple")
                ax.set_ylabel("Spar Inertia (m⁴)")
            elif selected == "VTail Section Modulus":
                ax.plot(self.x_vt[:len(self.vt_Sy)], self.vt_Sy, color="brown")
                ax.set_ylabel("Section Modulus (m³)")

            ax.set_xlabel("Normalized Span")
            ax.set_title(selected)
            ax.grid(True)
            self.canvas.draw()

        except Exception as e:
            self.summary_box.append(f"❌ Plot update error: {e}")

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QLabel, QTextEdit, QComboBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class WingDesignTab(QWidget):
    def __init__(self):
        super().__init__()
        self.solution = None
        self.mission = None
        self.plot_data = {}
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        summary_group = QGroupBox("Wing Structural Summary")
        summary_layout = QVBoxLayout()
        summary_layout.addWidget(self.summary_box)
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        self.canvas = FigureCanvas(Figure(figsize=(6, 4)))
        layout.addWidget(self.canvas)

        self.plot_selector = QComboBox()
        self.plot_selector.addItems([
            "Deflection", "Bending Moment", "Spar Inertia",
             "Section Modulus", "All (Stacked)"
        ])
        self.plot_selector.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(QLabel("Select Structural Plot:"))
        layout.addWidget(self.plot_selector)

        self.setLayout(layout)

    def update_from_solution(self, mission, solution):
        self.mission = mission
        self.solution = solution

        try:
            wing = mission.aircraft.bw.wing
            S = solution(wing.planform.S).to("ft^2").magnitude
            AR = solution(wing.planform.AR)
            b = solution(wing.planform.b).to("ft").magnitude
            W_skin = solution(wing.skin.W).to("lbf").magnitude
            W_spar = solution(wing.spar.W).to("lbf").magnitude
            W_total = W_skin + W_spar

            self.prepare_plot_data()
            w_tip = self.plot_data["w_defl"][-1]
            M_max = max(self.plot_data["M_bend"])
            q_max = max(self.plot_data["q_dist"])

            self.summary_box.setText(f"""✅ Wing Structural Summary:
- Surface Area: {S:.2f} ft²
- Span: {b:.2f} ft
- Aspect Ratio: {AR:.2f}
- Total Wing Weight: {W_total:.2f} lbf
- Skin Weight: {W_skin:.2f} lbf
- Spar Weight: {W_spar:.2f} lbf
- Max Tip Deflection: {w_tip:.3f} m
- Max Bending Moment: {M_max:.1f} Nm
- Max Distributed Load: {q_max:.1f} N/m
""")

            self.update_plot()

        except Exception as e:
            self.summary_box.setText(f"❌ Failed to extract summary: {e}")

    def prepare_plot_data(self):
        try:
            wing = self.mission.aircraft.bw.wing
            sol = self.solution
            M = self.mission
            span = sol(wing.planform.b).to("m").magnitude
            x = np.linspace(0, 1, len(sol(M.loading.wingl.w).magnitude)) * span / 2

            self.plot_data = {
                "x": x,
                "w_defl": sol(M.loading.wingl.w).to("m").magnitude,
                "M_bend": sol(M.loading.wingl.M).to("N*m").magnitude,
                "I_beam": sol(wing.spar["I"]).to("m^4").magnitude,
                "q_dist": sol(M.loading.wingl.q).to("N/m").magnitude,
                "Sy": sol(wing.spar["Sy"]).to("m^3").magnitude,
            }

        except Exception as e:
            self.summary_box.append(f"\n❌ Failed to prepare plot data: {e}")

    def update_plot(self):
        try:
            if not self.plot_data:
                return

            x = self.plot_data["x"]
            w_defl = self.plot_data["w_defl"]
            M_bend = self.plot_data["M_bend"]
            I_beam = self.plot_data["I_beam"]
            q_dist = self.plot_data["q_dist"]
            Sy = self.plot_data["Sy"]
            x_I = x[:len(I_beam)]

            selected = self.plot_selector.currentText()
            self.canvas.figure.clf()

            if selected == "All (Stacked)":
                fig = self.canvas.figure
                axs = fig.subplots(3, 1, sharex=True)
                axs[0].plot(x, w_defl, color='blue')
                axs[0].set_ylabel("Deflection (m)")
                axs[0].grid(True)

                axs[1].plot(x, M_bend, color='green')
                axs[1].set_ylabel("Moment (Nm)")
                axs[1].grid(True)

                axs[2].plot(x_I, I_beam, color='orange')
                axs[2].set_ylabel("Inertia (m⁴)")
                axs[2].set_xlabel("Spanwise Position (m)")
                axs[2].grid(True)
                fig.tight_layout()

            else:
                ax = self.canvas.figure.add_subplot(111)
                if selected == "Deflection":
                    ax.plot(x, w_defl, lw=2, color='blue')
                    ax.set_ylabel("Deflection (m)")
                elif selected == "Bending Moment":
                    ax.plot(x, M_bend, lw=2, color='green')
                    ax.set_ylabel("Moment (Nm)")
                elif selected == "Spar Inertia":
                    ax.plot(x_I, I_beam, lw=2, color='orange')
                    ax.set_ylabel("Inertia (m⁴)")
                elif selected == "Section Modulus":
                    ax.plot(x_I, Sy, lw=2, color='purple')
                    ax.set_ylabel("Section Modulus (m³)")

                ax.set_xlabel("Spanwise Position (m)")
                ax.set_title(f"Wing Structural: {selected}")
                ax.grid(True)

            self.canvas.draw()

        except Exception as e:
            self.summary_box.append(f"\n❌ Plot update failed: {e}")

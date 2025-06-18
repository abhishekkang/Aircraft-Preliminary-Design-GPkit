from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gpkit.units import units
import numpy as np

class AerodynamicsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.M = None
        self.sol = None
        self.labels = []
        self.CL_vals = []
        self.CD_vals = []
        self.LD_vals = []
        self.CDi_vals = []
        self.CDp_vals = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        layout.addWidget(QLabel("✈️ Aerodynamic Performance Summary"))
        layout.addWidget(self.summary_box)

        self.plot_selector = QComboBox()
        self.plot_selector.addItems([
            "All", 
            "Lift Coefficient (C_L)", 
            "Drag Coefficient (C_D)", 
            "L/D Ratio", 
            "Drag Breakdown (C_Di vs C_Dp)",
            "Induced Drag (C_Di)",
            "Profile Drag (C_Dp)",
        ])
        self.plot_selector.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(QLabel("Select Aerodynamic Parameter to Plot:"))
        layout.addWidget(self.plot_selector)

        self.canvas = FigureCanvas(Figure(figsize=(7, 4)))
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def update_from_solution(self, mission, solution):
        self.M = mission
        self.sol = solution
        self.extract_aero_data()
        self.build_summary()
        self.update_plot()

    def extract_aero_data(self):
        M = self.M
        sol = self.sol
        self.labels = []
        segments = []

        try:
            # Takeoff (4 segments)
            for i in range(4):
                self.labels.append(f"TO{i+1}")
                CL = sol(M.takeoff.perf.bw_perf.C_L[i])
                CD = sol(M.takeoff.perf.bw_perf.C_D[i])
                CDi = sol(M.takeoff.perf.bw_perf.C_Di[i])
                CDp = sol(M.takeoff.perf.bw_perf.C_Dp[i])
                segments.append((CL, CD, CDi, CDp))

            # Remaining segments
            phase_data = [
                ("ObstacleClimb", M.obstacle_climb),
                ("Climb", M.climb),
                ("Cruise", M.cruise),
                ("Landing", M.landing)
            ]
            for name, seg in phase_data:
                self.labels.append(name)
                CL = sol(seg.perf.bw_perf.C_L)
                CD = sol(seg.perf.bw_perf.C_D)
                CDi = sol(seg.perf.bw_perf.C_Di)
                CDp = sol(seg.perf.bw_perf.C_Dp)
                segments.append((CL, CD, CDi, CDp))

            # Store arrays
            self.CL_vals = [s[0] for s in segments]
            self.CD_vals = [s[1] for s in segments]
            self.CDi_vals = [s[2] for s in segments]
            self.CDp_vals = [s[3] for s in segments]
            self.LD_vals = [cl / cd if cd != 0 else 0 for cl, cd in zip(self.CL_vals, self.CD_vals)]

        except Exception as e:
            self.summary_box.append(f"\n❌ Aerodynamic data error: {e}")

    def build_summary(self):
        try:
            sol = self.sol
            M = self.M
            wing = M.aircraft.bw.wing

            CL = sol(M.cruise.perf.bw_perf.C_L)
            CLC = sol(M.cruise.perf.bw_perf.C_LC)
            CD = sol(M.cruise.perf.bw_perf.C_D)
            CDi = sol(M.cruise.perf.bw_perf.C_Di)
            CDp = sol(M.cruise.perf.bw_perf.C_Dp)
            AR = sol(wing.planform.AR)
            e = sol(M.cruise.perf.bw_perf.e)
            CJ = sol(M.cruise.perf.bw_perf.C_J)
            CE = sol(M.cruise.perf.bw_perf.C_E)
            eta_prop = sol(M.cruise.perf.bw_perf.eta_prop)

            self.summary_box.setText(f"""✅ Aerodynamic Summary (Cruise):
- C_L (Total): {CL:.3f}
- C_L (Circulation): {CLC:.3f}
- C_D (Total): {CD:.4f}
  - C_Di (Induced): {CDi:.4f}
  - C_Dp (Profile): {CDp:.4f}
- L/D Ratio: {CL/CD:.2f}
- Aspect Ratio (AR): {AR:.2f}
- Oswald Efficiency (e): {e:.3f}
- Jet Coeffs: C_J = {CJ:.3f}, C_E = {CE:.3f}
- Prop Efficiency (ηₚ): {eta_prop:.3f}
""")
        except Exception as e:
            self.summary_box.setText(f"❌ Error generating summary: {e}")

    def update_plot(self):
        x = np.arange(len(self.labels))
        plot_type = self.plot_selector.currentText()
        fig = self.canvas.figure
        fig.clf()

        try:
            if plot_type == "All":
                ax1 = fig.add_subplot(111)
                ax2 = ax1.twinx()

                ax1.plot(x, self.CL_vals, 'o-', label="C_L", color='blue')
                ax1.plot(x, self.LD_vals, '^-', label="L/D", color='green')
                ax1.set_ylabel("C_L / L/D")

                ax2.plot(x, self.CD_vals, 's-', label="C_D", color='red')
                ax2.set_ylabel("C_D")
                ax1.set_xticks(x)
                ax1.set_xticklabels(self.labels, rotation=45)

                ax1.set_title("Aerodynamic Overview")
                ax1.grid(True)
                ax1.legend(loc="upper left")
                ax2.legend(loc="upper right")

            else:
                ax = fig.add_subplot(111)
                y = []
                if plot_type == "Lift Coefficient (C_L)":
                    y = self.CL_vals
                    ylabel = "C_L"
                elif plot_type == "Drag Coefficient (C_D)":
                    y = self.CD_vals
                    ylabel = "C_D"
                elif plot_type == "L/D Ratio":
                    y = self.LD_vals
                    ylabel = "L/D"
                elif plot_type == "Drag Breakdown (C_Di vs C_Dp)":
                    ax.plot(x, self.CDi_vals, 'x-', label="C_Di", color='orange')
                    ax.plot(x, self.CDp_vals, 'o-', label="C_Dp", color='purple')
                    ylabel = "Drag Coefficients"
                    ax.legend()
                elif plot_type == "Induced Drag (C_Di)":
                    y= self.CDi_vals
                    ylabel = "Induced Drag"
                elif plot_type == "Profile Drag (C_Dp)":
                    y= self.CDp_vals
                    ylabel = "Profile Drag"
                else:
                    return  # Unknown plot type

                if plot_type != "Drag Breakdown (C_Di vs C_Dp)":
                    ax.plot(x, y, marker='o', label=ylabel)
                    ax.legend()

                ax.set_xticks(x)
                ax.set_xticklabels(self.labels, rotation=45)
                ax.set_ylabel(ylabel)
                ax.set_title(f"{plot_type} across Segments")
                ax.grid(True)

            self.canvas.draw()

        except Exception as e:
            self.summary_box.append(f"\n❌ Plot error: {e}")

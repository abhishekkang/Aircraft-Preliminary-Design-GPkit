from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np


class PropulsionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.M = None
        self.sol = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        layout.addWidget(QLabel("🔋 Propulsion & Battery Summary"))
        layout.addWidget(self.summary_box)

        self.plot_selector = QComboBox()
        self.plot_selector.addItems([
            "Motor Power (kW)",
            "Battery Draw (kW)",
            "Estimated Energy Use (kWh)",
            "Energy % by Segment (Pie Chart)"
        ])
        self.plot_selector.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(QLabel("Plot Propulsion Metrics by Segment:"))
        layout.addWidget(self.plot_selector)

        self.canvas = FigureCanvas(Figure(figsize=(6, 4)))
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def update_from_solution(self, mission, solution):
        self.M = mission
        self.sol = solution
        self.build_summary()
        self.update_plot()

    def build_summary(self):
        try:
            ac = self.M.aircraft
            sol = self.sol
            pt = ac.bw.powertrain

            m_batt = sol(ac.battery.m).to("kg").magnitude
            E_batt = sol(ac.battery.E_capacity).to("kWh").magnitude
            eta = sol(pt.eta)
            Pmax = sol(pt.Pmax).to("kW").magnitude
            RPM = sol(pt.RPMmax).magnitude
            radius = sol(pt.r).to("m").magnitude
            m_motor = sol(pt.m).to("kg").magnitude
            N_motors = sol(ac.bw.n_prop)

            self.summary_box.setText(f"""✅ Propulsion System Summary:
- Battery Mass: {m_batt:.2f} kg
- Battery Capacity: {E_batt:.2f} kWh
- Powertrain Efficiency (η): {eta:.3f}
- Max Power per Motor: {Pmax:.1f} kW
- Max RPM: {RPM:.0f}
- Propeller Radius: {radius:.2f} m
- Motor Mass: {m_motor:.2f} kg
- Number of Motors: {N_motors}
""")
        except Exception as e:
            self.summary_box.setText(f"❌ Failed to extract summary: {e}")

    def update_plot(self):
        try:
            M = self.M
            sol = self.sol
            self.canvas.figure.clf()
            ax = self.canvas.figure.add_subplot(111)

            segs = ["TO1", "TO2", "TO3", "TO4", "CL1", "CL2", "CR", "L"]
            bw_perf = M.takeoff.perf.bw_perf
            batt_perf = M.takeoff.perf.batt_perf

            # Values for each segment
            P_motor = [
                sol(bw_perf.P[0]), sol(bw_perf.P[1]), sol(bw_perf.P[2]), sol(bw_perf.P[3]),
                sol(M.obstacle_climb.perf.bw_perf.P),
                sol(M.climb.perf.bw_perf.P),
                sol(M.cruise.perf.bw_perf.P),
                sol(M.landing.perf.bw_perf.P)
            ]
            P_batt = [
                sol(batt_perf.P[0]), sol(batt_perf.P[1]), sol(batt_perf.P[2]), sol(batt_perf.P[3]),
                sol(M.obstacle_climb.perf.batt_perf.P),
                sol(M.climb.perf.batt_perf.P),
                sol(M.cruise.perf.batt_perf.P),
                sol(M.landing.perf.batt_perf.P)
            ]

            T = [sol(bw_perf.T[0]), sol(bw_perf.T[1]), sol(bw_perf.T[2]), sol(bw_perf.T[3]),
                 sol(M.obstacle_climb.perf.bw_perf.T),
                 sol(M.climb.perf.bw_perf.T),
                 sol(M.cruise.perf.bw_perf.T),
                 sol(M.landing.perf.bw_perf.T)]
            V = [sol(M.takeoff.perf.fs.V[0]), sol(M.takeoff.perf.fs.V[1]),
                 sol(M.takeoff.perf.fs.V[2]), sol(M.takeoff.perf.fs.V[3]),
                 sol(M.obstacle_climb.perf.fs.V),
                 sol(M.climb.perf.fs.V),
                 sol(M.cruise.perf.fs.V),
                 sol(M.landing.perf.fs.V)]
            t = [sol(M.takeoff.t[0]), sol(M.takeoff.t[1]), sol(M.takeoff.t[2]), sol(M.takeoff.t[3]),
                 sol(M.obstacle_climb.t),
                 sol(M.climb.t),
                 sol(M.cruise.t),
                 sol(M.landing.t)]

            E_kWh = [(Ti * Vi * ti).to("kWh").magnitude for Ti, Vi, ti in zip(T, V, t)]

            plot_type = self.plot_selector.currentText()

            if plot_type == "Motor Power (kW)":
                values = [Pi.to("kW").magnitude for Pi in P_motor]
                ax.bar(segs, values, color="steelblue")
                ax.set_ylabel("Motor Power (kW)")
                ax.set_title("Motor Power Across Segments")

            elif plot_type == "Battery Draw (kW)":
                values = [Pi.to("kW").magnitude for Pi in P_batt]
                ax.bar(segs, values, color="darkorange")
                ax.set_ylabel("Battery Draw (kW)")
                ax.set_title("Battery Power Draw Across Segments")

            elif plot_type == "Estimated Energy Use (kWh)":
                ax.bar(segs, E_kWh, color="mediumseagreen")
                ax.set_ylabel("Estimated Energy (kWh)")
                ax.set_title("Approximate Energy Use (T × V × t)")

            elif plot_type == "Energy % by Segment (Pie Chart)":
                total = sum(E_kWh)
                if total == 0:
                    ax.text(0.5, 0.5, "Zero energy usage computed", ha="center")
                else:
                    wedges, texts, autotexts = ax.pie(
                        E_kWh, labels=segs, autopct='%1.1f%%',
                        startangle=90, colors=plt.cm.tab20.colors[:len(segs)]
                    )
                    ax.set_title("Segment-Wise Energy Share")
                    ax.axis('equal')
            else:
                return

            if "Pie" not in plot_type:
                ax.set_xlabel("Mission Segment")
                ax.grid(True)

            self.canvas.draw()

        except Exception as e:
            self.summary_box.append(f"\n❌ Plotting error: {e}")

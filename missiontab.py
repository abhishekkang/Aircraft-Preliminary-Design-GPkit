from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gpkit.units import units
import numpy as np

class MissionTab(QWidget):
    def __init__(self):
        super().__init__()
        self.solution = None
        self.mission = None
        self.labels = []
        self.T_vals = []
        self.V_vals = []
        self.P_vals = []
        self.B_vals = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        layout.addWidget(QLabel("Segment-wise Mission Summary"))
        layout.addWidget(self.summary_box)

        self.canvas = FigureCanvas(Figure(figsize=(7, 4)))
        layout.addWidget(self.canvas)

        self.plot_selector = QComboBox()
        self.plot_selector.addItems(["All", "Thrust", "Speed", "Power", "Battery Power"])
        self.plot_selector.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(QLabel("Select Parameter to Plot:"))
        layout.addWidget(self.plot_selector)

        self.setLayout(layout)

    def update_from_solution(self, mission, solution):
        self.mission = mission
        self.solution = solution
        self.extract_segment_data()
        self.display_summary()
        self.update_plot()

    def extract_segment_data(self):
        M = self.mission
        sol = self.solution
        self.labels = []
        segments = []

        try:
            # Takeoff (4 segments)
            for i in range(4):
                self.labels.append(f"TO{i+1}")
                T = sol(M.takeoff.T[i]).to("N").magnitude
                V = sol(M.takeoff.perf.fs.V[i]).to("kt").magnitude
                P = sol(M.takeoff.perf.P[i]).to("kW").magnitude
                B = sol(M.takeoff.perf.batt_perf.P[i]).to("kW").magnitude
                segments.append((T, V, P, B))

            # Remaining segments
            phase_data = [
                ("ObstacleClimb", M.obstacle_climb),
                ("Climb", M.climb),
                ("Cruise", M.cruise),
                ("Landing", M.landing)
            ]
            for name, seg in phase_data:
                self.labels.append(name)
                T = sol(seg.perf.bw_perf.T).to("N").magnitude
                V = sol(seg.perf.fs.V).to("kt").magnitude
                P = sol(seg.perf.P).to("kW").magnitude
                B = sol(seg.perf.batt_perf.P).to("kW").magnitude
                segments.append((T, V, P, B))

            # Store arrays
            self.T_vals = [s[0] for s in segments]
            self.V_vals = [s[1] for s in segments]
            self.P_vals = [s[2] for s in segments]
            self.B_vals = [s[3] for s in segments]

        except Exception as e:
            self.summary_box.append(f"\n❌ Segment data error: {e}")

    def display_summary(self):
        # Keep your text summary implementation here if desired
        self.summary_box.setText("✅ Segment data extracted.\nUse dropdown to plot different parameters.")

    def update_plot(self):
        x = np.arange(len(self.labels))
        plot_type = self.plot_selector.currentText()
        fig = self.canvas.figure
        fig.clf()

        if plot_type == "All":
            ax1 = fig.add_subplot(111)
            ax2 = ax1.twinx()

            ax1.plot(x, self.T_vals, 'o-', label="Thrust (N)", color='blue')
            ax1.plot(x, self.V_vals, 's-', label="Speed (kt)", color='green')
            ax1.set_ylabel("Thrust (N) / Speed (kt)", color='black')

            ax2.plot(x, self.P_vals, '^-', label="Power (kW)", color='purple')
            ax2.plot(x, self.B_vals, 'x-', label="Battery Power (kW)", color='red')
            ax2.set_ylabel("Power (kW)", color='black')

            ax1.set_xticks(x)
            ax1.set_xticklabels(self.labels, rotation=45)
            ax1.set_title("Segment-wise Performance Overview")
            ax1.grid(True)

            ax1.legend(loc="upper left")
            ax2.legend(loc="upper right")

        else:
            ax = fig.add_subplot(111)
            y = {
                "Thrust": self.T_vals,
                "Speed": self.V_vals,
                "Power": self.P_vals,
                "Battery Power": self.B_vals
            }[plot_type]
            ax.plot(x, y, marker='o', label=plot_type)
            ax.set_xticks(x)
            ax.set_xticklabels(self.labels, rotation=45)
            ax.set_ylabel(f"{plot_type}")
            ax.set_title(f"{plot_type} across Segments")
            ax.grid(True)
            ax.legend()

        self.canvas.draw()

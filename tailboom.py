from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox
)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

class TailBoomTab(QWidget):
    def __init__(self):
        super().__init__()
        self.M = None
        self.sol = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.summary_box = QTextEdit()
        self.summary_box.setReadOnly(True)
        layout.addWidget(QLabel("Tail Boom Bending Summary:"))
        layout.addWidget(self.summary_box)

        self.plot_selector = QComboBox()
        self.plot_selector.addItems(["H-Boom Deflection", "V-Boom Deflection"])
        self.plot_selector.currentIndexChanged.connect(self.update_plot)
        layout.addWidget(self.plot_selector)

        self.canvas = FigureCanvas(Figure(figsize=(5, 3)))
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_from_solution(self, mission, solution):
        self.M = mission
        self.sol = solution
        self.build_summary()
        self.update_plot()

    def build_summary(self):
        try:
            sol = self.sol
            hb = self.M.loading.hbend
            vb = self.M.loading.vbend
            th_h = sol(hb.th)
            th_v = sol(vb.th)
            self.summary_box.setText(f"""✅ Boom Summary:
- H-Boom Max Deflection Angle: {th_h:.4f} rad
- V-Boom Max Deflection Angle: {th_v:.4f} rad""")
        except Exception as e:
            self.summary_box.setText(f"❌ Failed to extract summary: {e}")

    def update_plot(self):
     try:
        # Choose between horizontal or vertical boom based on selection
        boom = self.M.loading.hbend if "H-" in self.plot_selector.currentText() else self.M.loading.vbend
        sol = self.sol

        # Extract the deflection and the differential lengths
        delta = sol(boom.beam["\\bar{\\delta}"])  # Deflection (may have length mismatch)
        dx = sol(boom.beam["dx"])  # Differential lengths

        # Ensure that delta and dx have compatible lengths
        if len(delta) != len(dx):
            # We need to match the lengths of delta and dx, let's make sure both are aligned.
            # First, ensure that delta has the same length as dx by either truncating or interpolating
            if len(delta) > len(dx):
                delta = delta[:len(dx)]  # Truncate delta to match dx length
            else:
                # If delta is shorter than dx, we need to interpolate delta to match dx's length
                delta = np.interp(np.cumsum(dx), np.cumsum(dx)[:len(delta)], delta)

        # Calculate positions (x) along the boom by cumulatively summing dx
        x = np.cumsum(dx)

        # Plotting
        self.canvas.figure.clf()
        ax = self.canvas.figure.add_subplot(111)
        ax.plot(x, delta, lw=2)
        ax.set_xlabel("Boom Length (normalized)")
        ax.set_ylabel("Deflection (normalized)")
        ax.set_title("Tail Boom Deflection Profile")
        ax.grid(True)

        # Redraw canvas
        self.canvas.draw()

     except Exception as e:
        self.summary_box.append(f"❌ Plot error: {e}")



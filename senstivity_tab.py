from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from gpkit.repr_conventions import unitstr
import numpy as np

def get_highestsens_safe(res, N=15):
    """
    Extract top-N sensitivities from solution.
    Returns labels and values only, no unit lookups.
    """
    sens_raw = res["sensitivities"]["constants"]
    flat_sens = {}

    for varname, val in sens_raw.items():
        try:
            if hasattr(val, "values"):  # dictionary (e.g., vectorized vars)
                total = sum(val.values())
            elif hasattr(val, "__len__"):  # numpy array
                total = sum(val)
            else:
                total = val
            flat_sens[str(varname)] = total
        except Exception as e:
            print(f"⚠️ Failed to read sensitivity for {varname}: {e}")

    # Sort by abs value
    sorted_items = sorted(flat_sens.items(), key=lambda x: abs(x[1]), reverse=True)[:N]

    labels = [name.replace("Mission3.", "").replace("_", " ") for name, _ in sorted_items]
    values = [v for _, v in sorted_items]
    pos = [v if v > 0 else 0 for v in values]
    neg = [-v if v < 0 else 0 for v in values]
    x = np.arange(len(labels))

    return {
        "labels": labels,
        "indices": x,
        "positives": pos,
        "negatives": neg
    }

class SensitivityTab(QWidget):
    def __init__(self):
        super().__init__()
        self.solution = None
        self.model = None
        self.initUI()

    def initUI(self):
     layout = QVBoxLayout()

     self.selector = QComboBox()
     self.selector.addItems(["Top 10", "Top 15", "Top 20"])
     self.selector.currentIndexChanged.connect(self.update_plot)
     layout.addWidget(QLabel("Select number of top sensitivities:"))
     layout.addWidget(self.selector)

     self.canvas = FigureCanvas(Figure(figsize=(8, 5)))
     layout.addWidget(self.canvas)

     self.summary_label = QLabel("Sensitivity summary will appear here.")
     self.summary_label.setWordWrap(True)
     layout.addWidget(self.summary_label)

     self.setLayout(layout)


    def update_from_solution(self, mission, solution):
        self.model = mission
        self.solution = solution
        self.update_plot()

    def update_plot(self):
     if self.solution is None:
        return
     N = int(self.selector.currentText().split()[-1])
     sensdict = get_highestsens_safe(self.solution, N)
     self.plot_chart(sensdict)

    # Create textual summary
     summary_lines = []
     for label, pos, neg in zip(sensdict["labels"], sensdict["positives"], sensdict["negatives"]):
        val = pos if pos > 0 else -neg
        sign = "+" if pos > 0 else "-"
        summary_lines.append(f"{label}: {sign}{val:.3f}")
     summary_text = "Top Sensitivities:\n" + "\n".join(summary_lines)
     self.summary_label.setText(summary_text)


    def dict_sort(self, vdict):
        return sorted(vdict.items(), key=lambda x: abs(x[1]), reverse=True)

    def plot_chart(self, sensdict):
        fig = self.canvas.figure
        fig.clf()
        ax = fig.add_subplot(111)

        ax.bar(sensdict["indices"], sensdict["positives"], 0.5, color="#4D606E")
        ax.bar(sensdict["indices"], -np.array(sensdict["negatives"]), 0.5, color="#3FBAC2")
        ax.set_xticks(sensdict["indices"])
        ax.set_xticklabels(sensdict["labels"], rotation=45, ha="right")
        ax.set_ylabel("Sensitivity")
        ax.set_title("Top Variable Sensitivities")
        ax.grid(True)

        self.canvas.draw()


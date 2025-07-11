" create bar chart "
import sys
import matplotlib.pyplot as plt
import numpy as np
from numpy import random
from gpkit.repr_conventions import unitstr
from mission import Mission

#pylint: disable=invalid-name, anomalous-backslash-in-string

def get_highestsens(model, res, varnames=None, N=10):
    " plot bar chart of sensitivities "
    pss = []
    ngs = []
    sens = {}
    if varnames:
        for vname in varnames:
            sen = res["sensitivities"]["constants"][vname]
            if hasattr(sen, "__len__"):
                val = max(np.abs(sen.values()))
                vk = [svk for svk in sen if abs(sen[svk]) == val][0]
                sen = sum(sen.values())
            else:
                vk = model[vname].key
            sens[vk] = sen
    else:
        for s in res["sensitivities"]["constants"]:
            sens[model[s].key] = sum(
                np.hstack([res["sensitivities"]["constants"][s]]))

    labels = []
    i = 0
    sorted_sens = dict_sort(sens)

    for s in sorted_sens:
        if i > N:
            break
        i += 1
        vk = s[0]
    if hasattr(res(vk), "magnitude"):
     val = res(vk).magnitude
    else:
     val = res(vk)

# Check if 'val' is a NumPy array before accessing its shape
    if isinstance(val, np.ndarray):
     if len(val.shape) > 0:
        val = val[0]  # Only use the first element if it's an array
    else:
    # 'val' is a scalar (float), no need to check for shape
     pass
    if "units" in vk.descr:
            uts = unitstr(vk.descr["units"])
    else:
        uts = ""
        print (vk)
        lbl = vk.descr["label"]
        labels.append(lbl + "$ =%.2f$ %s" % (val, uts.replace("*", "")))
    if s[1] > 0:
            pss.append(s[1])
            ngs.append(0)
    else:
            ngs.append(abs(s[1]))
            pss.append(0)

    ind = np.arange(0.5, i + 0.5, 1)
    sensdict = {"positives": pss, "negatives": ngs, "indicies": ind,
                "labels": labels}
    return sensdict

def dict_sort(vdict):
    " sort variable sensitivity dict"

    slist = [(0, 0.0)]
    for v in vdict:
        for i, sv in enumerate(slist):
            if abs(vdict[v]) > abs(sv[1]):
                slist.insert(i, (v, vdict[v]))
                break

    del slist[-1]
    return slist

def plot_chart(sensdict):
    "plot sensitivities on bar chart"
    fig, ax = plt.subplots()
    ax.bar(sensdict["indicies"], sensdict["positives"], 0.5, color="#4D606E")
    ax.bar(sensdict["indicies"], -np.array(sensdict["negatives"]), 0.5,
           color="#3FBAC2")
    ax.set_xlim([0.0, sensdict["indicies"][-1]+1])
    ax.set_xticks(sensdict["indicies"])
    ax.set_xticks(range(len(sensdict["labels"])))
    ax.set_xticklabels(sensdict["labels"], rotation=-45, ha="left")
    # ax.legend(["Positive", "Negative"])
    ax.set_ylabel("sensitivities")
    ax.grid()
    return fig, ax

def test():
    " test for integrated testing "
    model = Mission(latitude=[20])
    model.cost = model[model.solar.Wtotal]
    result = model.solve("mosek")
    _ = get_highestsens(model, result)

    vn = {model.solar.Wpay: "$W_{\\mathrm{pay}}$",
          model.solar.battery.etacharge: "$\\eta_{\\mathrm{charge}}$"}
    _ = get_highestsens(model, result, vn)

if __name__ == "__main__":

    M = Mission()
    M.cost = M[M.aircraft.m]
    sol = M.solve("mosek")

    sd = get_highestsens(M, sol, N=15)
    f, a = plot_chart(sd)
    f.savefig("sensbar.pdf", bbox_inches="tight")
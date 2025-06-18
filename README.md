# ✈️ MDO of Battery-Electric Light Aircraft – Blown-Wing vs Conventional Wing

**👨‍💻 Author:** Abhishek Kang  
**📅 Date:** June 2025  
**📍 Institution:** CSIR-National Aerospace Laboratories (NAL), Bangalore  
**🎓 Submitted to:** BITS Pilani, Goa Campus  

---

## 📌 Overview

This project implements a **Multidisciplinary Design Optimization (MDO)** framework using **GPkit** and **Python**, to design and compare two aircraft wing configurations:

- A **Blown Wing (BW)** using Distributed Electric Propulsion (DEP)  
- A **Conventional Wing (CW)**  

The tool enables early-stage sizing and performance analysis of a battery-electric Light Aircraft (LA) within a **750 kg MTOW** constraint.

---

## 🧰 Project Structure

| File / Module | Description |
|---------------|-------------|
| `wing_struct.py`, `beam.py`, `tail.py` | Defines the wing planform, loading, and structural components. Adapted from the [GPkit GPlibrary](https://github.com/convexengineering/gplibrary). |
| `wings.py`, `mission.py` | Defines aerodynamic models and mission segments, adapted from [MIT 16.82 STOL GPkit models](https://github.com/convexengineering/1682stol). |
| `aircraft_gui.py` | PyQt5-based GUI for input handling and output visualization. |
| `mission.py` | (Assumed) Contains definitions of mission architecture including takeoff, climb, cruise, and landing. |

---

## 🔍 Key Features

- Built using **GPkit** – a geometric programming tool for globally optimal sizing.
- Modular and extensible design with support for:
  - Planform and structural design of wings and tail
  - Aerodynamic modeling of fuselage and tail boom
  - Battery and propulsion system sizing
- **User-friendly GUI** built with **PyQt5** for:
  - Selecting wing configuration (BW/CW)
  - Inputting key aircraft parameters (AR, span, CLmax, battery mass, etc.)
  - Displaying mission summary and structural plots

---

## 🖥️ How to Run

### ✅ Prerequisites

Make sure the following are installed:

- Python 3.x  
- `gpkit` and `gpkitmodels` (for geometric programming and material data)  
- `PyQt5`  
- `NumPy`, `Matplotlib`  

### 💻 To Run the GUI

```bash
# From the project root directory
python aircraft_gui.py
```

---

## ✨ Outputs Provided

- ✅ **Optimized aircraft design variables** (mass, range, wing dimensions)
- 📊 **Wing Structural Plots**:
  - Bending Moment  
  - Tip Deflection  
  - Distributed Load  
  - Spar Inertia  
  - Section Modulus  
- ✈️ **Mission Performance Summary**:
  - Cruise / Stall Speed  
  - Estimated Range  
  - Battery Capacity  
  - Mass Breakdown  

---

## 📈 Results Summary (from Thesis)

- **Blown Wing (BW)**:  
  - Enables shorter takeoff distances  
  - Provides enhanced lift via DEP during STOL  
  - Results in higher battery consumption and shorter range  

- **Conventional Wing (CW)**:  
  - Superior cruise efficiency  
  - Offers longer operational range  

✅ Both configurations meet structural safety criteria as validated via FEM simulations.

---

## 📚 Citation

If using this work, please cite:

> Abhishek Kang. *Multidisciplinary Design Optimization of a Battery-Electric Light Aircraft Using Geometric Programming: A Comparative Study of Blown-Wing and Conventional Configurations*. CSIR-NAL / BITS Pilani, 2025.

---

## 📬 Contact

For any questions or collaboration opportunities, feel free to reach out:  
📧 **abh0207@gmail.com**

✈️ **MDO of Battery-Electric Light Aircraft – Blown-Wing vs Conventional Wing**

👨‍💻** Author: Abhishek Kang**
📅 Date: June 2025
📍 Institution: CSIR-National Aerospace Laboratories (NAL), Bangalore
🎓 Submitted to: BITS Pilani, Goa Campus
📌 Overview
**This project implements a Multidisciplinary Design Optimization (MDO) framework using GPkit and Python, to design and compare two aircraft wing configurations:

A Blown Wing (BW) using Distributed Electric Propulsion (DEP)

A Conventional Wing (CW)

The tool enables early-stage sizing and performance analysis of a battery-electric Light Aircraft (LA) within a 750 kg MTOW constraint.
**
🧰 Project Structure
File / Folder	Description
wing_struct.py,beam.py,tail.py is used to define the planform and loading codntions for the wing and is taken from the https://github.com/convexengineering/gplibrary  
aerodynamics and mission is taken from https://github.com/convexengineering/1682stol for blown wing and adjusted as per the new requirement of the new category aircraft

aircraft_gui.py	Frontend PyQt-based GUI interface for input and visualization of the optimization results
mission.py (assumed)	Defines the mission architecture (takeoff, cruise, climb, etc.)

🔍 Key Features
Built using GPkit – a geometric programming tool for globally optimal sizing.

Modular components for:

Planform and structural design of wings and tail

Aerodynamic modeling of fuselage and tail boom

Battery and propulsion system sizing

PyQt5 GUI to:

Select wing type (BW/CW)

Input parameters like AR, span, battery mass, CLmax, cruise speed, etc.

Visualize mission summary and wing structural plots

🖥️ How to Run
✅ Prerequisites:
Python 3.x

GPkit,Gpkitmodels for material data 

PyQt5

NumPy, Matplotlib

💻 Running the GUI:
# Assuming the code is organized correctly in .py files
aircraft_gui.py run this file 
✨ Outputs Provided
✅ Optimized aircraft design variables (mass, range, wing dimensions)

📊 Wing structural plots:

Bending moment

Tip deflection

Distributed load

Inertia and section modulus

✈️ Mission performance summary:

Cruise/stall speed

Estimated range

Battery capacity

Mass breakdown

📈 Results Summary (from Thesis)
Blown Wing: Lower takeoff distance, better lift during STOL, but reduced range due to higher battery demand.

Conventional Wing: Higher cruise efficiency and longer range.

Both designs meet structural safety requirements, validated via FEM.

📚 Citation
If using this work, please cite:

Abhishek Kang. Multidisciplinary Design Optimization of a Battery-Electric Light Aircraft Using Geometric Programming: A Comparative Study of Blown-Wing and Conventional Configurations. CSIR-NAL / BITS Pilani, 2025.

📬 Contact
For any questions or collaboration ideas, reach out to:
📧 abh0207@gmail.com


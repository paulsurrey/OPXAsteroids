"""
basic-digital-output.py: introduction to digital output (trigger out)
Author: Gal Winer - Quantum Machines
Created: 6/1/2021
Revised by Tomer Feld
Revision date: 04/04/2022
"""

import os
os.chdir(r'C:\Users\lablocal\Desktop\OPXAsteroids\tutorial_1')

from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm import SimulationConfig
from configuration import *

qop_ip = '192.168.88.10'
qmm = QuantumMachinesManager(host=qop_ip)
qm = qmm.open_qm(config)

with program() as prog:
    play("const", "qe1")
    wait(500, "qe2")
    play("const", "qe2")
    wait(500, "qe2")
    play("const_trig", "qe2")
    wait(500, "qe2")
    play("const_stutter", "qe2")


job = qmm.simulate(config, prog, SimulationConfig(int(3000)))  # in clock cycles, 4 ns

if False:
    samples = job.get_simulated_samples()
    samples.con1.plot()
else:
    job = qm.execute(prog)
    res = job.result_handles
    res.wait_for_all_values()
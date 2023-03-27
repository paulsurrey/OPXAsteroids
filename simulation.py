from qm.QuantumMachinesManager import QuantumMachinesManager
from qm import SimulationConfig
from qm import LoopbackInterface
from qm.qua import *
import matplotlib.pyplot as plt

qmm = QuantumMachinesManager()

##
# ## Example 1 - No inputs

with program() as prog1:
    a = declare(fixed)
    c = declare(fixed, value=0.4)

    with for_(a, 0.2, a < 0.9, a + 0.1):
        play("const" * amp(a), "qe1")

    save(c, "c")

# simulate program
job = qmm.simulate(config, prog1, SimulationConfig(
    duration=500,                    # duration of simulation in units of 4ns
))

# get DAC and digital samples
samples = job.get_simulated_samples()

# plot all ports:
samples.con1.plot()

# get results
res = job.result_handles
c = res.c.fetch_all()
print(c)

##
# ## Example 2 - Loopback inputs
len_a = len(np.arange(0.1,0.45,0.1))
len_f = len(np.arange(50e6,60e6,1e6))
with program() as prog2:
    I = declare(fixed)
    Q = declare(fixed)
    I_stream = declare_stream()
    Q_stream = declare_stream()
    adc_stream = declare_stream(adc_trace=True)
    f = declare(int)
    a = declare(fixed)

    with for_(a, 0.1, a < 0.45, a + 0.1):
        with for_(f, 50e6, f < 61e6, f + 1e6):
            update_frequency("qe1", f)
            measure("readout"*amp(a), "qe1", adc_stream, demod.full('cos', I), demod.full('sin', Q))
            save(I, I_stream)
            save(Q, Q_stream)
            wait(100)

    with stream_processing():
        I_stream.buffer(len_f).buffer(len_a).save('I')
        Q_stream.buffer(len_f).buffer(len_a).save('Q')
        adc_stream.input1().save_all('adc')

# # simulate program
simulated_job = qmm.simulate(config, prog2, SimulationConfig(
    duration=40000,
    simulation_interface=LoopbackInterface([("con1", 1, "con1", 1)])    # loopback from output 1 to input 1
))


    # get results
res = simulated_job.result_handles
adc = res.get('adc').fetch_all()['value'][0]  # fetch first measurement
I = res.get('I').fetch_all()
Q = res.get('Q').fetch_all()

plt.figure()
plt.plot(adc)
plt.xlabel("Time [ns]")
plt.ylabel("ADC")

plt.figure()
plt.plot(I, Q, '.')
plt.xlabel("I")
plt.xlabel("Q")


##
# ## Example 3:

with program() as prog3:
        d = declare(int)

        with for_(d, 10, d <= 100, d + 10):
                play("const", "qe1")
                play("const", "qe2", duration=d)
                wait(50)


# simulate program
job = qmm.simulate(config, prog3, SimulationConfig(
        duration=1700,                  # duration of simulation in units of 4ns
))


# get DAC and digital samples
samples = job.get_simulated_samples()

# plot analog ports 1 and 3:
samples.con1.plot(analog_ports={'1', '3'}, digital_ports={})

# another way:
# plt.figure()
# plt.plot(samples.con1.analog["1"], "-")
# plt.plot(samples.con1.analog["3"], "--")
# plt.legend(("analog 1", "analog 3"))
# plt.xlabel("Time [ns]")
# plt.ylabel("Signal [V]")
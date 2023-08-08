# Asteroids for the Quantum Machines OPX

Demonstrating the real time capabilities of the [QM OPX](https://www.quantum-machines.co/products/opx/) by implementing and playing [Asteroids](https://de.wikipedia.org/wiki/Asteroids) on its FPGA.

<img src="./Screenshot.png" alt="A photo of an oscilloscope showing a basic implementation of Asteroids and a controller with 4 buttons. The Oscilloscope is placed on top an QM OPX." width="400">

The code that was used in the videos posted is saved at the commit ```9474dc6c```. 

## Installation

### Software

Connecting to the OPX, one can use the [qm-qua package](https://pypi.org/project/qm-qua/). The required python packages can be installed via.
```
pip install qm-qua numpy matplotlib pytest
```

The OPX needs to be reachable from the PC running the python code. The IP of the OPX has to be specified within the asteroids.py file. At the beginning of the asteroids.py file the following line can be found.
``` python
qop_ip = '192.168.88.10'
```
The IP of the OPX has to be updated here.

Then the game can be stated via
```
python asteroids.py
```

### Hardware

The first 3 analog have to be connected to the oscilloscope. The oscilloscope is then configured such that it plots the output of the first two channels as an XY-Plot. The riding edge on the third channel can be used as a trigger for the drawing process.

The controller is the fed from the fourth analog channel is then used as the input to the controller. The two outputs of the controller are then connected to the two inputs of the OPX. With the current state of the project, the controller has then to be calibrated, which can be done by changing the thresholds in line 447, 449, 457, and 459. To choose these thresholds, you can set the ```CALIBRATION``` flag to ```True``` and observe the plot.


## A Closer Look

The [qua](https://docs.quantum-machines.co/0.1/qm-qua-sdk/docs/API_references/qua/dsl_main/) API allows for programming the OPX's FPGA comparably easy and with very little overhead within python. So the challenge of building Asteroids on the OPX can be boiled down solving the following problems:
- How does one output rotated and offseted pulses?
- How does one write the game logic to run on the FPGA?
- How does one obtain some user input?

### Drawing Images

To draw 2D images, the [I/Q output](https://docs.quantum-machines.co/0.1/qm-qua-sdk/docs/Introduction/qua_overview/#mixed-inputs-element) of the OPX is used to not feed a I/Q modulator (e.g. [QM's Octave](https://www.quantum-machines.co/products/octave/)) but to directly feed into two inputs of an Oscilloscope, which then plots these two channels in some XY Display. (the `'lo_frequency'` is set to 0Hz.)
Using the I/Q output of the OPX allows for the usage of the [`amp()`](https://docs.quantum-machines.co/0.1/qm-qua-sdk/docs/API_references/qua/dsl_main/?h=amp#qm.qua._dsl.amp) function, which allows to mix the I and Q outputs using variables:
``` python
play('pulse_name' * amp(v_00, v_01, v_10, v_11), 'element')
```
We can then choose the `v_*` values to describe the rotation in that plain by the angle `a`:
``` python
def get_rot_amp(a):
    return amp(
		Math.cos2pi(a), -Math.sin2pi(a), 
    	Math.sin2pi(a), Math.cos2pi(a)
    	)
```

The position of the sprite is set by changing the DC offset of the channels:
``` python
def move_cursor(x, y):
    # go to the (x, y) position
    set_dc_offset("screen", "I", x)
    set_dc_offset("screen", "Q", y)
```

The sprites themselves are provided to the OPX within the configuration dict in the form of numpy arrays.

### Movements

Qua provides a [Math api](https://docs.quantum-machines.co/0.1/qm-qua-sdk/docs/API_references/qua/math/) that contains an impressive collection of Math functions that can be executed on the FPGA. And with [`assign()`](https://docs.quantum-machines.co/0.1/qm-qua-sdk/docs/API_references/qua/dsl_main/#qm.qua._dsl.assign) one can realize various calculations. 
For the Asteroids demo, the position, angle, and velocity of the ship are stored as [`fixed`](https://docs.quantum-machines.co/0.1/qm-qua-sdk/docs/Guides/demod/?h=fixed#fixed-point-format) variables on the FPGA. They are then changed by
``` python
assign(ship_x, ship_x+ship_vx*dt)
assign(ship_y, ship_y+ship_vy*dt)
assign(ship_vx, ship_vx+Math.cos2pi(ship_a)*ui_forward*ship_acceleration*dt)
assign(ship_vy, ship_vy+Math.sin2pi(ship_a)*ui_forward*ship_acceleration*dt)
clip_velocity(ship_vy)
clip_velocity(ship_vx)
```
Where `dt` is the time step that is to be realized in this frame, `ui_forward` is a [`fixed`](https://docs.quantum-machines.co/0.1/qm-qua-sdk/docs/Guides/demod/?h=fixed#fixed-point-format) variable that is filled with `{0, 1}` based on the users input, and `ship_acceleration` is a python variable containing the acceleration that the ship should have. `clip_velocity` is a function that clips each component of the ship's velocity to some maximal velocity.

For game logic to move the asteroids and rays is slightly different. In the case for the asteroids the logic looks like this:
``` python
# move asteroids
with for_(j, 0, j<N_asteroids, j+1):
    with if_(asteroids_active[j]):
        assign(asteroids_x[j], asteroids_x[j]+Math.cos2pi(asteroids_a[j])*v_asteroid*dt)
        assign(asteroids_y[j], asteroids_y[j]+Math.sin2pi(asteroids_a[j])*v_asteroid*dt)
```

### Collisions

Collisions between rays and asteroids are calculated by
``` python
def get_distance(ax, ay, bx, by):
    distance = declare(fixed)
    distance = Math.sqrt((ax-bx)*(ax-bx)+(ay-by)*(ay-by))
    return distance

def ray_hit(ray_x, ray_y, asteroid_x, asteroid_y):
    hit = declare(bool, False)
    distance = get_distance(ray_x, ray_y, asteroid_x, asteroid_y)
    with if_(distance < R_asteroid):
        assign(hit, True)
    return hit
```
Note that the distance is not calculated using the provided [`qm.qua.lib.Math.pow`](https://docs.quantum-machines.co/0.1/qm-qua-sdk/docs/API_references/qua/math/?h=pow#qm.qua.lib.Math.pow) function, as it is not defined for negative base inputs. The `pow` function does not throw an error when tasked to process inputs outside of its defined input ranges, but outputs some value and the qua program continues with that incorrect result. To work around this, the square is calculated by multiplying the value with themselves. (The here used code has not been optimized or bench marked. I would be interesting to know if saving the result of the subtraction is faster then calculating it twice.)

To process the collisions with the border, the position of the ship, rays, and asteroids are clipped using a function like this one:
```python
def cycle_clip(x, upper, lower):
    with if_(x > upper):
        assign(x, lower)
    with elif_(x < lower):
        assign(x, upper)
    return x

def clip(x, upper, lower):
    with if_(x > upper):
        assign(x, upper)
    with elif_(x < lower):
        assign(x, lower)
    return x

def process_border_collisions(x, y):
    for e in [x, y]:
        cycle_clip(e, field_size, -field_size)
    return x, y

def clip_angle(a):
    return cycle_clip(a, .5, -.5)
    
def clip_velocity(v):
    return clip(v, max_speed, -max_speed)
```

### User Input

**You have to be very sure about what you do! The used Equipment is very expensive.**

To play around with the [measurement functionality](https://docs.quantum-machines.co/0.1/qm-qua-sdk/docs/Guides/features/?h=measure#measure-statement-features) of the OPX, a basic user input to the Asteroids game was investigated. The Implementation **just fulfills the goal** of playing Asteroids on the OPX. For example, the contrast of the readout is (for the positive side of the controller) not stable: The contrast between a not pressed and pressed button on the positive side of the controller is very small. And the levels also drift around, such that one had to reconfigure the thresholds in the order of ~0.002 (for the positive side) (A method to plot these values and measure that drift is can be commented in). 

There are currently a few questions that are related to this problem:
- When measuring for longer duration: Do overflows occur and can one break the long window into smaller ones, e.g. using a IIR low pass, to stay within the variables range?
- How does the common mode voltage on the inputs influence the readout? Is this a small fluctuation that is amplified by the overflowing measurement? Would an 1:1 operational amplifier in front of the OPX inputs as an additional layer of safety (to limit the bandwidth, voltage, and current of the signal) help?
- Can one optimize the circuit of the controller? Does a different choice for the resistors increase the readout contrast? Would a low pass before input to the OPX to smooth the signal increase the stability of the readout method?
- Does the tested circuit apply unnecessary stress to the OPX? Is this setup capable of running for longer times?

To readout the 4 buttons with two input, the following design is tested:
The 4 buttons are grouped into 2 groups, where diodes are used to probe ether side based on the polarity of the readout signal.
Each button is then connected to a voltage divider where it puts the R2 resistor in parallel to the R1 resistor, and thus changes, based on the choice of the resistors, the voltage at the readout point of the voltage divider when measured to ground. The readout point is then connected to one of the OPX inputs. One might further considerations the usage of an low pass or an inline resistor.

<img src="./circuit.svg" alt="A sketch of the controller circuit." width="400">

The choice of the resistor investigated:

| Resistor | Tested Resistance |
|----------|-------------------|
| R1 	   | 	  125kOhm 	   |
| R2 	   |    1kOhm & 0Ohm   |
| R3 	   | 	  125kOhm 	   |

To increase the contrast, the resistor R2 was bridged, where as removing R1 might have been a better approach.

### Binary Encoder
Simon Humpohl suggested to encode the 4 buttons by bridging resistors with increasing resistivity. 5 resistors with doubling resistivity $R_i = 2^i*R_0$ were chosen. The resistor $R_0$ is one resistor in line to limit the current flow when all buttons are pressed, and the resistors $R_1$, ..., $R_4$ are then the resistors that are bridged by the 4 buttons. This way the overall resistivity can be related to the button pressed by means of looking at the binary representation of the measured resistance.

When using a controller based on the binary encoding, only one input of the OPX is required for one user input. Thus two controllers should be supportable. 

## Problems

### Overflows 
As variables can overflow without notifying the user, funky things can happen. One of these things is the burst of rays, that the spaceship fires after the time variable rolls over. 

### Math Functions 
Some math functions are only defined for inputs in certain ranges. If they are given values outside of these ranges, the Math functions will still try to compute something, but the results can then easily be (very) wrong. One has to keep this in mind when writing the programs.

### Flaky Controller
The controller is good enough to have some fun in the lab, but might need to be refined when using more intensively. One could refine the here investigated circuit, or choose some other concepts to sense some user input.

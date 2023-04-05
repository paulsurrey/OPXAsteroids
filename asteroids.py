
import os
os.chdir(r'C:\Users\lablocal\Desktop\OPXAsteroids')


from qm import SimulationConfig
from qm.QuantumMachinesManager import QuantumMachinesManager
from qm.qua import *
from qm.qua.lib import Math

from sprites import *

#%%


# TODO implement some smaller programs for testing.
# TODO fix the configuration
    # TODO setup the user input measurement
# TODO implement handling and evaluation of the user input measurements

# the size of the field
# The field things will be able to move in will be in the range of +- field_size.
field_size = 0.5 # V 

# Number of rays to be handled
N_rays = 10 # 1

# speed with which the rays move
v_ray = 1 # V/s

# the duration before the rays decay
max_ray_age = 2 # s

# the delay between spawning rays
ray_spawn_delay = 0.1 # s

# Number of asteroids to be spawned
N_asteroids = 10 # 1

# radius of the asteroids
R_asteroid = field_size*0.075 # V

# speed with which the asteroids move
v_asteroid = 0.2 # V/s

# acceleration the ship experiences then the play presses the forward button
ship_acceleration = 0.5 # (2*)V/s^2

# Max speed of the ship
max_speed = 1 # V/s

# the rotational speed of the ship
ship_rotation_speed = 2.0 # 2*pi/s

# the amount of time the game is advanced every tick
# as the timing is not implemented yet, this value sets the amount of time that passes for each tick.
time_step_size = 0.01 # s 

# pulse lengths
user_input_pulse_length = 100 # ns

# intermediate_frequency
intermediate_frequency = 0

# sprite pulse length
sprite_length = 1000

wait_time = 1e7 # ns

#%%

configuration = {
'version': 1,
'controllers': {
    'con1': {
        'type': 'opx1',
        'analog_outputs': {
            1: {'offset': +0.0},
            2: {'offset': +0.0},
            3: {'offset': +0.0},
            4: {'offset': +0.0},
        },
        'digital_outputs': {
            1: {},
        },
        'analog_inputs': {
            1: {'offset': +0.0},
            2: {'offset': +0.0},
        }
    }
},
'elements': {
    'screen': {
        'mixInputs': {
            'I': ('con1', 1),
            'Q': ('con1', 2),
            },
        'intermediate_frequency': intermediate_frequency,
        'digitalInputs': {
            'draw_marker': {
                'port': ('con1', 1),
                'delay': 0,
                'buffer': 0,
            },
        },
        'operations': {
            "ship": "ship",
            "ray": "ray",
            "asteroid": "asteroid",
            "border": "border",
        },
    }, 
    'draw_marker_element': {
         'singleInput': {
             'port': ('con1', 3),
             },
         'intermediate_frequency': intermediate_frequency,
         'operations': {
             "marker_pulse": "marker_pulse",
         },
     },
    'user_input_element': {
        'outputs': {
            'a': ('con1', 1),
            'b': ('con1', 2),
            },
        'intermediate_frequency': intermediate_frequency,
        'operations': {
            "measure_user_input": "measure_user_input",
        },
        'time_of_flight': 100,
        'smearing': 0
        # 'integration_weights': {
        #     'integ1': 'cosine_weights',
        # },
    },
    # 'marker': {
    #     'singleInput ': {
    #         'm': ('con1', 3),
    #         },
    #     'intermediate_frequency': intermediate_frequency,
    #     'operations': {
    #         'draw_trigger': 'draw_trigger'
    #     },
    # },
},
'pulses': {
    **{n: {
            'operation': 'control',
            'length': sprite_length,
            'waveforms': {k:f"{n}_{l}" for k, l in zip(["I", "Q"], ["x", "y"])},
        } 
        for n in ["ship", "asteroid", "ray", "border"]},
    "measure_user_input": {
        "operation": "measurement",
        'length': user_input_pulse_length,
        "integration_weights": {
            "constant": "cosine_weights",
        },
    },
    "marker_pulse": {
        "operation": "control",
        'length': sprite_length,
        'waveforms': {"single": "marker_wf"},   
    }
},
'waveforms': {
    **{
        f"ship_{a}":{'type':'arbitrary', 'samples':v}
        for a, v in zip(["x", "y"], get_ship_pulse(sprite_length)*field_size*0.1)
    },
    **{
        f"asteroid_{a}":{'type':'arbitrary', 'samples':v}
        for a, v in zip(["x", "y"], get_asteroid_pulse(sprite_length)*R_asteroid)
    },
    **{
        f"ray_{a}":{'type':'arbitrary', 'samples':v}
        for a, v in zip(["x", "y"], get_ray_pulse(sprite_length)*field_size*0.05)
    },
    **{
        f"border_{a}":{'type':'arbitrary', 'samples':v}
        for a, v in zip(["x", "y"], get_border_pulse(sprite_length)*field_size)
    },
    # 'marker_wf': {'type':'arbitrary', 'samples':[.1]*50+[0]*50},
    'marker_wf': {"type": "constant", "sample": 0.2},
},
'digital_waveforms': {
    'draw_trigger': {
        'samples': [(1, 0)]
    }
},
"integration_weights": {
    "cosine_weights": {
        "cosine": [(1.0, user_input_pulse_length)],
        "sine": [(0.0, user_input_pulse_length)],
    },
    "sine_weights": {
        "cosine": [(0.0, user_input_pulse_length)],
        "sine": [(1.0, user_input_pulse_length)],
    },
},
}

#%%

qop_ip = '192.168.88.10'
qmm = QuantumMachinesManager(host=qop_ip)

#%%

qm = qmm.open_qm(configuration)

#%%

def move_curser(x, y):
    # go to the (x, y) position
    set_dc_offset("screen", "I", x)
    set_dc_offset("screen", "Q", y)

def get_rot_amp(a):
    return amp(Math.cos2pi(a), -Math.sin2pi(a), Math.sin2pi(a), Math.cos2pi(a))

def draw_by_name(name, x, y, a):
    move_curser(x, y)
    play(name * get_rot_amp(a), 'screen')
    align()

def draw_ship(x, y, a):
    move_curser(x, y)
    play('ship' * get_rot_amp(a), 'screen')
    align()

def draw_ray(x, y, a):
    move_curser(x, y)
    play('ray' * get_rot_amp(a), 'screen')
    align()

def draw_asteroid(x, y, a):
    move_curser(x, y)
    play('asteroid' * get_rot_amp(a), 'screen')
    align()

def draw_border():
    move_curser(0, 0)
    play('border', 'screen')
    align()

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

def cycle_clip(x, upper, lower):
    with if_(x > upper):
        assign(x, lower)
    with if_(x < lower):
        assign(x, upper)
    return x

def clip(x, upper, lower):
    with if_(x > upper):
        assign(x, upper)
    with if_(x < lower):
        assign(x, lower)
    return x

def process_border_collisions(x, y):

    for e in [x, y]:
        cycle_clip(e, field_size, -field_size)

    # for e in [x, y]:
    #     with if_(e > field_size):
    #         assign(e, -field_size)
    #     with elif_(e < -field_size):
    #         assign(e, field_size)

    # # with if_(x > field_size):
    # #     assign(x, 0)
    # # with elif_(x < 0):
    # #     assign(x, field_size)
        
    # # with if_(y > field_size):
    # #     assign(y, 0)
    # # with elif_(y < 0):
    # #     assign(y, field_size)

def clip_angle(a):
    return cycle_clip(a, .5, -.5)
    
def clip_velocity(v):
    return clip(v, max_speed, -max_speed)
#%%

rng = np.random.default_rng(seed=1234)
#%%

with program() as game:

    ship_a = declare(fixed, 0)
    ship_x = declare(fixed, 0)
    ship_y = declare(fixed, 0)
    ship_x_old = declare(fixed, 0)
    ship_y_old = declare(fixed, 0)
    ship_x_old2 = declare(fixed, 0)
    ship_y_old2 = declare(fixed, 0)
    ship_vx = declare(fixed, 0)
    ship_vy = declare(fixed, 0)

    rays_active = declare(bool, value=[False]+[False]*(N_rays-1))
    rays_age = declare(fixed, value=[max_ray_age]+[0]*(N_rays-1))
    rays_x = declare(fixed, value=[0]*N_rays)
    rays_y = declare(fixed, value=[0]*N_rays)
    rays_a = declare(fixed, value=[0]*N_rays)
    
    asteroids_active = declare(bool, value=[True]*N_asteroids)
    # TODO check if the "float16" are actually necessary, as the qua object is a 4.28 fixed point number
    asteroids_x = declare(fixed, value=rng.uniform(-field_size, field_size, N_asteroids).astype("float16"))#[.4, .3, .2, .1, 0, .1, .2, .3, .4, .4])#rng.uniform(-field_size, field_size, N_asteroids).astype("float16"))
    asteroids_y = declare(fixed, value=rng.uniform(-field_size, field_size, N_asteroids).astype("float16"))#[-.4, -.3, -.2, -.1, 0, .1, .2, .3, .4, -.4])#rng.uniform(-field_size, field_size, N_asteroids).astype("float16"))
    asteroids_a = declare(fixed, value=rng.uniform(-.5, .5, N_asteroids).astype("float16"))#[.1, .2, .3, .4, .3, .2, .1, .0, -.1, -.2])#rng.uniform(-.5, .5, N_asteroids).astype("float16"))

    t = declare(fixed, 0)
    t_prim = declare(fixed, 0)
    t_last_ray_spawn = declare(fixed, -100)
    dt = declare(fixed, 0)
    i = declare(int, 0)
    j = declare(int, 0)

    user_input_meas_data_1 = declare(fixed)
    user_input_meas_data_2 = declare(fixed)
    ui_phi = declare(fixed, 0)
    ui_forward = declare(fixed, 0)
    ui_fire = declare(bool, False)

    # Game loop
    with while_(True):

        assign(dt, t - t_prim)
        assign(t_prim, t)

        # process user inputs
        assign(ui_phi, 0.05) # The angle update that the user inputted
        assign(ui_forward, 1) # The forward acceleration that is inputted
        assign(ui_fire, True) # The forward acceleration that is inputted

        # TODO
        measure("measure_user_input", "user_input_element", None, integration.full("constant", user_input_meas_data_1, "a"))
        measure("measure_user_input", "user_input_element", None, integration.full("constant", user_input_meas_data_2, "b"))
        with if_(user_input_meas_data_1 > user_input_meas_data_2):
            assign(ui_fire, True)
            
        measure("measure_user_input", "user_input_element", None, integration.full("constant", user_input_meas_data_1, "a"))
        measure("measure_user_input", "user_input_element", None, integration.full("constant", user_input_meas_data_2, "b"))
        with if_(user_input_meas_data_1 > user_input_meas_data_2):
            assign(ui_forward, 1)

        measure("measure_user_input", "user_input_element", None, integration.full("constant", user_input_meas_data_1, "a"))
        measure("measure_user_input", "user_input_element", None, integration.full("constant", user_input_meas_data_2, "b"))
        with if_(user_input_meas_data_1 > user_input_meas_data_2):
            assign(ui_phi, 1)

        # move ship
        # update the rotation
        assign(ship_a, ship_a+ui_phi*ship_rotation_speed*dt)
        clip_angle(ship_a)

        # spawn rays
        with if_(ui_fire):
            with if_(t_last_ray_spawn < t-ray_spawn_delay):
                assign(i, Math.argmin(rays_age))
                assign(rays_active[i], True)
                assign(rays_age[i], max_ray_age)
                assign(rays_x[i], ship_x)
                assign(rays_y[i], ship_y)
                assign(rays_a[i], ship_a)
                assign(t_last_ray_spawn, t)

        # # update the velocity and position
        assign(ship_x, ship_x+ship_vx*dt)
        assign(ship_y, ship_y+ship_vy*dt)
        assign(ship_vx, ship_vx+Math.cos2pi(ship_a)*ui_forward*ship_acceleration*dt)
        assign(ship_vy, ship_vy+Math.sin2pi(ship_a)*ui_forward*ship_acceleration*dt)
        clip_velocity(ship_vy)
        clip_velocity(ship_vx)

        # update the position using Verlet 
        # assign(ship_x_old2, ship_x)
        # assign(ship_y_old2, ship_y)
        # assign(ship_x, 2*ship_x-ship_x_old+Math.cos(ship_a)*ship_acceleration*dt*dt)
        # assign(ship_y, 2*ship_y-ship_y_old+Math.sin(ship_a)*ship_acceleration*dt*dt)
        # assign(ship_x_old, ship_x_old2)
        # assign(ship_y_old, ship_y_old2)

        # process hits
        with for_(i, 0, i<N_rays, i+1):
            with for_(j, 0, j<N_asteroids, j+1):
                with if_(rays_active[i] & asteroids_active[j]):
                    # with if_(ray_hit(rays_x[i], rays_y[i], asteroids_x[j], asteroids_y[j])):
                    with if_((get_distance(rays_x[i], rays_y[i], asteroids_x[j], asteroids_y[j]) < R_asteroid)):
                        assign(rays_active[i], False)
                        assign(rays_age[i], -1)
                        assign(asteroids_active[j], False)

        # move rays
        with for_(i, 0, i<N_rays, i+1):
            with if_(rays_active[i]):
                # check age
                with if_(rays_age[i] > 0): # the ray is still alive
                    assign(rays_age[i], rays_age[i]-dt)
                    # update position
                    assign(rays_x[i], rays_x[i]+Math.cos2pi(rays_a[i])*v_ray*dt)
                    assign(rays_y[i], rays_y[i]+Math.sin2pi(rays_a[i])*v_ray*dt)
                with if_(rays_age[i] < 0):
                    assign(rays_active[i], False)

        # move asteroids
        with for_(j, 0, j<N_rays, j+1):
            with if_(asteroids_active[j]):
                assign(asteroids_x[j], asteroids_x[j]+Math.cos2pi(asteroids_a[j])*v_asteroid*dt)
                assign(asteroids_y[j], asteroids_y[j]+Math.sin2pi(asteroids_a[j])*v_asteroid*dt)

        # process border collisions
        process_border_collisions(ship_x, ship_y)
        with for_(i, 0, i<N_rays, i+1):
            with if_(rays_active[i]):
                process_border_collisions(rays_x[i], rays_y[i])
        with for_(i, 0, i<N_asteroids, i+1):
            with if_(asteroids_active[i]):
                process_border_collisions(asteroids_x[i], asteroids_y[i])

        # draw graphics
        play("marker_pulse", "draw_marker_element")
        draw_ship(ship_x, ship_y, ship_a)
        with for_(i, 0, i<N_rays, i+1):
            with if_(rays_active[i]):
                draw_ray(rays_x[i], rays_y[i], rays_a[i])
        with for_(i, 0, i<N_asteroids, i+1):
            with if_(asteroids_active[i]):
                draw_asteroid(asteroids_x[i], asteroids_y[i], asteroids_a[i])
        draw_border()

        # wait until everything is drawn
        align()
        
        wait(int(wait_time))

        # update time
        assign(t, t+time_step_size)

#%%

SIMULATION = False

if __name__ == '__main__':
        
    if SIMULATION:
        samples = job.get_simulated_samples()
        samples.con1.plot()
    else:
        job = qm.execute(game)
        res = job.result_handles
        res.wait_for_all_values()



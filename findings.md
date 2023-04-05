# OPX findings

---

The errors in the qua program are not linked to a line number or variable name. E.g. when trying to cast a python number (to a string) to an incorrect qua variable.

---
Accationally, the error messages are not clear enough to see what's wrong
> 2023-03-27 11:16:36,596 - qm - ERROR    - CONFIG ERROR in key "elements.draw_marker_element" [elements.allPulsesExist] : Element 'draw_marker_element' has inputs ([single]) but using pulse (marker_pulse -> marker_pulse) with ([marker_wf])

---
Channel names in the element definition are ether I/Q or port. 

---
```
2023-03-27 12:31:01,980 - qm - INFO     - Performing health check
2023-03-27 12:31:01,992 - qm - INFO     - Health check passed
2023-03-27 12:31:02,091 - qm - WARNING  - Open QM ended with warning 0: Opening a new Quantum Machine and closing existing identical Quantum Machine qm-1676305247429
2023-03-27 12:31:02,092 - qm - WARNING  - Open QM ended with warning 0: Quantum Machine qm-1676305247429 is canceling running job 1675865789341.
2023-03-27 12:31:03,294 - qm - INFO     - Sending program to QOP for compilation
2023-03-27 12:31:03,764 - qm - ERROR    - Unexpected error: Failed to compile job
2023-03-27 12:31:03,765 - qm - ERROR    - Internal error. Please report it to QM (ts=1676305299758)
2023-03-27 12:31:03,766 - qm - ERROR    - Job 1675865789342 failed. Failed to execute program.
Traceback (most recent call last):

  File "C:\Users\lablocal\AppData\Local\Temp\ipykernel_16268\799268569.py", line 462, in <cell line: 456>
    job = qm.execute(game)

  File "C:\Users\lablocal\miniconda3\envs\qmqua\lib\site-packages\qm\QuantumMachine.py", line 238, in execute
    pending_job = self._queue.add(program, compiler_options)

  File "C:\Users\lablocal\miniconda3\envs\qmqua\lib\site-packages\qm\jobs\job_queue.py", line 77, in add
    job = self._insert(program, InsertDirection.end, compiler_options)

  File "C:\Users\lablocal\miniconda3\envs\qmqua\lib\site-packages\qm\jobs\job_queue.py", line 145, in _insert
    job_id = self._frontend.add_to_queue(

  File "C:\Users\lablocal\miniconda3\envs\qmqua\lib\site-packages\qm\api\base_api.py", line 32, in wrapped
    return func(*args, **kwargs)

  File "C:\Users\lablocal\miniconda3\envs\qmqua\lib\site-packages\qm\api\frontend_api.py", line 219, in add_to_queue
    raise FailedToAddJobToQueueException(f"Job {job_id} failed. Failed to execute program.")

FailedToAddJobToQueueException: Job 1675865789342 failed. Failed to execute program.

```
This error was raised, then this line of code was stated:
``` python
                    with if_(False & get_distance(rays_x[i], rays_y[i], asteroids_x[j], asteroids_y[j]) < -100):
```

And the following line did not stop with False, thus & seams to be evaluated before <
``` python
                    with if_(get_distance(rays_x[i], rays_y[i], asteroids_x[j], asteroids_y[j]) < -100 & False):
```

---

```pyton
Math.pow(base, x)
```
is very funny. When using it to calculate the distance between two points, it returned values smaller than 0. 
So multiplying the values with each other to get a square is working.

---

Not well documented/investigated findings:
- When playing around with 3 asteroids, some of them start rotating. But their rotation is not actively written to. (There are video clips of that happening)
- The pulses get distorted at the max range of the oscilloscope and the OPX, which had been set to the same voltage. (video clip existing)
- The drawn border is not drawn correctly: at least 2 of the corners (-.5V, .5V) and (.5V, -.5V) are smoothed/concave. And the border is not drawn completely.
- 












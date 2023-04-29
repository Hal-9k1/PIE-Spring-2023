import math

class Motor:
    """Wraps a KoalaBear-controlled motor."""
    __slots__ = "_controller", "_motor", "_robot", "_debug_logger", "_is_inverted"
    def __init__(self, robot, debug_logger, controller_id, motor):
        self._controller = controller_id
        self._motor = motor
        self._robot = robot
        self._debug_logger = debug_logger
        self._is_inverted = False
    
    def set_invert(self, invert):
        self._set("invert", invert)
        self._is_inverted = invert
        return self
    def set_deadband(self, deadband):
        self._set("deadband", deadband)
        return self
    def set_pid(self, p, i, d):
        if not (p or i or d):
            self._set("pid_enabled", False)
            return self
        self._set("pid_enabled", True)
        if p:
            self._set("pid_kp", p)
        if i:
            self._set("pid_ki", i)
        if d:
            self._set("pid_kd", d)
        return self
    def set_velocity(self, velocity):
        self._set("velocity", velocity)
        return self
    def get_velocity(self):
        return self._get("velocity")
    def get_encoder(self):
        return self._get("enc") * (-1 if self._is_inverted else 1)
    def reset_encoder(self):
        self._set("enc", 0)
    
    def _set(self, key, value):
        self._robot.set_value(self._controller, key + "_" + self._motor, value)
    def _get(self, key):
        return self._robot.get_value(self._controller, key + "_" + self._motor)
    
class Wheel:
    """Represents a wheel that may be ran to a goal position."""
    # goal and radius are in meters
    __slots__ = ("_motor", "_radius", "_ticks_per_rot", "_goal_pos", "_velocity", "_debug_logger",
        "_start_pos")
    def __init__(self, debug_logger, motor, radius, ticks_per_rotation):
        self._motor = motor
        self._radius = radius
        self._ticks_per_rot = ticks_per_rotation
        self._debug_logger = debug_logger
        self._start_pos = None
    
    def set_goal(self, goal, velocity):
        self._start_pos = self._motor.get_encoder()
        self._goal_pos = math.ceil(goal / (self._radius * 2 * math.pi) * self._ticks_per_rot) 
        self._motor.set_velocity(math.copysign(velocity, self._goal_pos))
        self._velocity = velocity
    def get_goal_progress(self):
        if :
            return 0
        if self._goal_pos == 0:
            #print("goal progress is 0 for some reason")
            return 1
        #self._debug_logger.print(self._motor.get_encoder())
        return 1 - ((self._goal_pos - self._motor.get_encoder()) / (self._goal_pos - self._start_pos))
    def stop(self):
        self._goal_pos = self._motor.get_encoder()
        self._motor.set_velocity(0)
    def update(self):
        if not self._initialized:
            return # no commands given yet
        if self.get_goal_progress() >= 1:
            self._motor.set_velocity(0)

class Servo:
    __slots__ = "_controller", "_servo", "_robot"
    def __init__(self, robot, controller, servo):
        self._controller = controller
        self._servo = servo
        self._robot = robot
    def set_position(self, position):
        self._robot.set_value(self._controller, "servo" + self._servo, position)

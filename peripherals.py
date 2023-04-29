import devices
import util
import math

class Arm:
    __slots__ = ("_elbow_motor", "_elbow_goal_encoder", "_elbow_start_encoder", "_debug_logger",
        "_forearm_motor")
    _arm_motor_controller = "6_4315277077938590215"
    _forearm_length = util.inches_to_meters(7.5)
    _midarm_length = util.inches_to_meters(18)
    _upperarm_length = util.inches_to_meters(10.1)
    _upperarm_mount_height = util.inches_to_meters(7)
    _upperarm_angle_range = (0, math.pi) # in radians
    _ticks_per_rotation = 475 #64 * 30.125 / 1.42 
    def __init__(self, debug_logger, robot):
        self._elbow_motor = (devices.Motor(robot, debug_logger, self._arm_motor_controller, "a")
            .set_pid(None, None, None))
        self._elbow_motor.reset_encoder()
        self._forearm_motor = devices.Motor(robot, debug_logger, elf._arm_motor_controller, "b")
        self._forearm_wheel = devices.Wheel(debug_logger, self._forearm_motor,
            util.inches_to_meters(1.5), self._ticks_per_rotation)
        self._debug_logger = debug_logger
    def set_goal_height(self, goal_height, velocity):
        if not ((self._upperarm_mount_height + self._upperarm_length - self._midarm_length)
            < goal_height < (self._upperarm_mount_height + self._upperarm_length
            + self._midarm_length)):
            raise ValueError(f"Goal height {goal_height} is out of bounds.")
        theta = math.acos((self._upperarm_length - goal_height + self._upperarm_mount_height)
            / self._midarm_length)
        self._elbow_goal_encoder = theta / (2 * math.pi) * self._ticks_per_rotation
        self._elbow_start_encoder = self._elbow_motor.get_encoder()
    def set_goal_extension(self, goal_extension, velocity):
        if not 0 <= goal_extension <= 1:
            raise ValueError(f"Goal extension {goal_extension} is out of bounds.")
        self._forearm_wheel.set_goal(goal_extension * self._forearm_length, velocity)
    def update(self):
        if self._elbow_start_encoder == None:
            return
        encoder = self._elbow_motor.get_encoder()
        start_encoder_diff = self._elbow_start_encoder - self._elbow_goal_encoder
        encoder_diff = encoder - self._elbow_goal_encoder
        if (not self._is_elbow_in_range()
            or math.copysign(start_encoder_diff, encoder_diff) != start_encoder_diff):
            elbow_velocity = 0
            self._debug_logger.print_once("Arm.update: motion completed", "Arm motion completed."
                f" encoder: {encoder} encoder lower bound: {self._upperarm_angle_range[0] / (2 * math.pi) * self._ticks_per_rotation}"
                f" encoder upper bound: {self._upperarm_angle_range[1] / (2 * math.pi) * self._ticks_per_rotation}"
                f" was in range: {self._is_elbow_in_range()}")
        else:
            elbow_velocity = math.copysign(1, encoder_diff)
        self._elbow_motor.set_velocity(forearm_velocity)
        self._forearm_wheel.update()
        return elbow_velocity != 0
    def update_input(self, input_object):
        self._elbow_motor.set_velocity(input_object.arm_velocity if self._is_elbow_in_range()
            else 0)
        if input_object.forearm_velocity:
            goal = forearm_length if input_object.forearm_velocity > 0 else 0
            self._forearm_wheel.set_goal(goal, input_object.forearm_velocity)
        elif input_object.forearm_goal:
            self._forearm_wheel.set_goal(input_object.forearm_goal, 1)
        self._forearm_wheel.update()

    def _is_elbow_in_range(self):
        encoder = self._elbow_motor.get_encoder()
        return (encoder > (self._upperarm_angle_range[0] / (2 * math.pi) * self._ticks_per_rotation)
            and encoder < (self._upperarm_angle_range[1] / (2 * math.pi) * self._ticks_per_rotation)) 

class Hand:
    __slots__ = "_debug_logger", "_servo", "_position" 
    _move_increment = 5/90 # servo accepts a number in degrees (hopefully)
    def __init__(self, debug_logger, servo):
        self._servo = servo
        self._debug_logger = debug_logger
        self._position = 0
    def open(self):
        self._servo.set_position(0.5) # also try 30 degrees
    def close(self):
        self._servo.set_position(-0.5)
    def update_input(self, input_object):
        self._debug_logger.print(f"hand status: {input_object.hand_status}")
        self._move_to(self._position + input_object.hand_status * self._move_increment)

    def _move_to(self, pos):
        self._servo.set_position(pos)
        self._position = pos

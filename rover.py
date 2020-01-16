from math import sin, cos, pi, pow
from random import randint, choice
from string import digits
from RoverTurtle.Exceptions import *

# ------------------------------- #
# ------Generics and Setup------- #
# ------------------------------- #
from RoverTurtle.Exceptions import FleetError, NavigationError


def bounded(arg, val_range):
    if arg < min(val_range):
        return min(val_range)
    if arg > max(val_range):
        return max(val_range)
    return arg


# ----------------------- #
# -----Lazy Method------- #
# ----------------------- #


class Mission:
    __slots__ = ["range_x", "range_y", "rovers"]

    def __init__(self, range_x, range_y):
        self.validate_mission_control(range_x, range_y)
        self.rovers = []
        self.range_x = range_x
        self.range_y = range_y

    def deploy_rover(self, o, x, y):
        self.rovers.append(Rover(o, bounded(x, range(self.range_x)), bounded(y, range(self.range_y)), self))
        print(self)

    def get_boundaries(self):
        return self.range_x, self.range_y

    def turn(self, rover_id, clockwise=False):
        rover = self.rovers[rover_id]
        if clockwise:
            rover.turn_negative()
        else:
            rover.turn_positive()

    def locate(self, rover_id):
        return self.rovers[rover_id].get_location()

    def command(self, rover_id, command_str=None):
        self.validate_command(rover_id, command_str)
        command_str = ''.join(char for char in command_str if char in "MLR")
        if command_str:
            self.rovers[rover_id].command(command_str)

    def __repr__(self):
        tab = '\t'
        out = f"Area: {self.range_x}x{self.range_y}\nRovers:\n"
        out += '\n'.join(f'{tab}{index}) {repr(rover)}' for index, rover in enumerate(self.rovers))
        out += f"\n\n{self.draw_field()}"
        return out

    def draw_field(self):
        avatar = {
            0: '>',
            1: '^',
            2: '<',
            3: 'V'
        }
        grid = [['~' for _ in range(self.range_x)] for __ in range(self.range_y)]
        for index, rover in enumerate(self.rovers):
            orientation, x, y = self.locate(index)

            if grid[y][x] == '~':
                grid[y][x] = f"{index}{avatar[orientation]}"
            else:
                grid[y][x] += f"{index}{avatar[orientation]}"
                grid[y][x] = ''.join(char for char in grid[y][x] if char in digits)
        for index, row in enumerate(grid):
            row.insert(0, str(index))
        grid.reverse()
        grid.append(["X"] + [str(n) for n in range(self.range_x)])
        return '\n'.join('\t'.join(grid[y]) for y in range(len(grid)))

    ###############
    # VALIDATIONS #
    ###############

    def validate_deploy(self, o, x, y):
        if o not in range(len(Rover.ORIENTATIONS)):
            raise NavigationError(f"Are you going my way, too? This Rover isn't. Try a proper orientation. Pick a "
                                  f"value from {Rover.ORIENTATIONS}")
        if x not in range(self.range_x) or y not in range(self.range_y):
            raise NavigationError(f"You dropped a rover and missed the ground. Nice going hotshot. Try aiming between"
                                  f"(x: [0,{self.range_x}], y: [0,{self.range_y}])")
        if 0 in vars(self).values():
            raise SpaceError("Cannot deploy rover nowhere")

    def validate_command(self, rover_id, command_str):
        if not self.rovers:
            raise FleetError("You wield an army of none. Congratulations. Deploy some rovers first next time")
        if not command_str:
            raise CommunicationError(f"If you want Rover {rover_id} to do something, you need to use your text words")

    def validate_mission_control(self, range_x, range_y):
        fail_test = {'range_x': range_x <= 0, 'range_y': range_y <= 0}
        if any(fail_test.values()):
            raise SpaceError(f"Non-positive space detected. {', '.join(rng for rng in fail_test if fail_test[rng])} "
                             f"must be positive")


class Rover:
    ORIENTATIONS = {index: val for index, val in enumerate("ENWS")}

    __slots__ = ["orientation", "x", "y", "name", "mission"]

    def __init__(self, pos_x, pos_y, orientation, mission, name=None):
        self.orientation = orientation
        self.x = pos_x
        self.y = pos_y
        self.name = name
        self.mission = mission

    def __repr__(self):
        return f"{self.name or ''}{': ' if self.name else ''}{self.ORIENTATIONS[self.orientation]} @ ({self.x}," \
               f" {self.y})"

    def turn_negative(self):
        self.orientation = (self.orientation - 1) % len(self.ORIENTATIONS)

    def turn_positive(self):
        self.orientation = (self.orientation + 1) % len(self.ORIENTATIONS)

    def command(self, command_str):
        for command_key in command_str:
            if command_key == 'M':
                self.move()
            elif command_key == 'R':
                self.turn_negative()
            elif command_key == 'L':
                self.turn_positive()
            else:
                pass

    def move(self):
        range_x, range_y = self.mission.get_boundaries()
        x_step = bounded(self.x + round(cos(2 * self.orientation * pi / len(self.ORIENTATIONS))), (0, range_x - 1))
        y_step = bounded(self.y + round(sin(2 * self.orientation * pi / len(self.ORIENTATIONS))), (0, range_y - 1))
        if (0, 0) != (x_step, y_step):
            self.x += x_step
            self.y += y_step

    def get_location(self):
        return self.orientation, self.x, self.y

##################
# Manual Testing #
##################


class Playground:
    @staticmethod
    def rand_scene():
        rx = randint(1, 21)
        rvr_c = randint(1, 3)
        ry = randint(1, 20 - 2 * rvr_c)
        mc = Mission(rx, ry)
        for i in range(rvr_c):
            mc.rovers.append(Rover(randint(0, rx - 1), randint(0, ry - 1), randint(0, 3)))
        print(mc)
        return mc

    @staticmethod
    def rand_command(context, *rover_ids):
        history = ""
        choices = ["M", "L", "M", "R", "M"]
        rover_ids = rover_ids or range(len(context.rovers))
        for rover_id in rover_ids:
            seq = ""
            for i in range(randint(10, 20)):
                seq += choice(choices)
            context.command(rover_id, seq)
            history += f"\n>Rover {rover_id}: {seq}"
        print(history)


mc = Playground.rand_scene()

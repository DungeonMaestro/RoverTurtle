from math import sin, cos, pi, pow
from random import randint, choice
from string import digits

# ------------------------------- #
# ------Generics and Setup------- #
# ------------------------------- #

def clear():
    for _ in range(50):
        print('\n')



def bounded(arg, val_range):
    if arg < min(val_range):
        return min(val_range)
    if arg > max(val_range):
        return max(val_range)
    return arg


# ----------------------- #
# ------Fun Method------- #
# ----------------------- #

class CoordSys:
    """
    Stores information related to the axes about which the rovers will navigate.
    """
    __slots__ = []

    def __init__(self, axes=None, ranges=None):
        """
        Generates a list of axes and their boundaries from a passed list of axis names and maxima.
        Range minima are assumed to be 0

        WARNING: UNDERSCORES IN AXIS NAMES BREAKS THE IMPLEMENTATION

        Parameters
        ----------
        axes : list[str]
        ranges : list[int or float]
        """
        _axes = [item for item in axes]
        _ranges = [item for item in ranges]
        for index, axis in enumerate(_axes):
            self.__slots__.append(f"range_{axis}")
            setattr(self, f"range_{axis}", range(_ranges[index]) or None)


class Position:
    """
    Stores and handles position data within the passed coordinate system
    """
    __slots__ = ["coordsys", "validator"]

    def __init__(self, system=None, data_validation=None, **position):
        """
        Instantiates the Position class. It takes a coordinate system to build upon, a function to validate any data
        passed to the function, and a kwarg sequence of starting coordinates

        e.g. Position(rectangular, math.ceil, x=0, y=1) starts tracking at (0,1), and takes the ceiling of any
        attribute assignments

        Cyclic systems should use the data validator to wrap the method about the boundaries of the
        coordinate system

        Parameters
        ----------
        system : CoordSys
        data_validation : function
        position : dict[str]
        """
        self.validator = data_validation or (lambda a: a)
        self.coordsys = system or CoordSys()
        for index, axis in enumerate(self.coordsys.__slots__):
            self.__slots__.append(axis.replace("range_", ""))
            setattr(self, self.__slots__[-1], position[axis] or 0)

    def __setattr__(self, key, value):
        """
        Overloads setattr to ensure that only valid position data is committed

        Parameters
        ----------
        key : str
        value : int or float

        Returns
        -------
        None
        """
        object.__setattr__(self, key, bounded(self.validator(value), getattr(self.coordsys, f"range_{key}")))


class Orientation:
    """
    Stores and handles the orientation the actor is facing for navigation context.
    """
    __slots__ = ["coordsys", "span", "data_validator"]

    def __init__(self, system=None, span=None, data_validator=None, **orientation):
        """
        Assembles the orientation structure based on the passed coordinate system. Also takes arguments for radial
        span and data validation. The orientation 'axes' are based on planes of two dimensions, separated by an
        underscore. This is intuitive in
        rectilinear space, but kinda mindfucky when you get into less common systems

        e.g. Orientation(system=Rectangular, data_validator=(lambda a: pi / 2) x_y=pi)) would result in an actor that
        can only look along the positive y axis, and whose initial negative x-axis orientation would be validated
        to positive y

        Parameters
        ----------
        data_validator : function
        system : CoordSys
        span : list[int or float]
        orientation : dict[str]
        """
        self.data_validator = data_validator or (lambda a: a)
        self.coordsys = system or CoordSys()
        for index, _plane in enumerate(
                f"{self.coordsys.__slots__[0]}_{axis.replace('range_', '')}" for axis in self.coordsys.__slots__[1:]
        ):
            plane = ''.join(_plane)
            self.__slots__.append(plane)
            setattr(self, self.__slots__[-1], orientation[plane] or 0)
        _planes = [var for var in self.__slots__ if var not in ["coordsys", "span", "data_validator"]]
        self.span = {plane: span_i or 2 * pi for plane, span_i in zip(_planes, span)}

    def __setattr__(self, key, value):
        """
        Overloads setattr to ensure that the orientation is properly cycled for each plane

        Parameters
        ----------
        key : str
        value : int or float

        Returns
        -------
        None
        """
        object.__setattr__(self, key, self.data_validator(value) % self.span[key])


class NavSystem:
    __slots__ = ["pos", "orientation", "pos_steps", "orientation_steps"]

    # TODO
    def __init__(self, coordsys=None, **initial_condition_kwargs):
        _coordsys = coordsys or CoordSys(['x', 'y'], 5, 5)
        pos_args = [value for key, value in initial_condition_kwargs if '_' not in key and 'initial' in key]
        orientation_args = [value for key, value in initial_condition_kwargs if '_' in key and 'initial' in key]
        self.pos_steps = [value for key, value in initial_condition_kwargs if '_' not in key and 'initial' not in key]
        self.orientation_steps = [value for key, value in initial_condition_kwargs if
                                  '_' in key and 'initial' not in key]
        self.pos = Position(_coordsys, *pos_args)
        self.orientation = Orientation(_coordsys, *orientation_args)

    # TODO: o boi this gon' hurt
    def move(self, dist):
        setattr(self.pos, self.pos.__slots__[0], )
        #TODO: fix calculation to not assume range is τ
        self.pos.x = bounded(self.pos.x + round(dist * sin(2 * pi / self.orientation)), self.pos.sys.range_x)
        self.pos.y = bounded(self.pos.y + round(dist * cos(2 * pi / self.orientation)), self.pos.sys.range_y)

    def turn(self, radians, plane=None, clockwise=False):
        """
        This method implements the logic of the actor rotating left or right by a passed angle along a passed plane
        This method requires an orientation system with at least one plane to execute properly, but also shouldn't be
        called if turning is a logical impossibility anyway so...

        Parameters
        ----------
        radians : by how many radians to turn
        plane : the plane to rotate about
        clockwise : whether the rotation is negative or not

        Returns
        -------

        """
        setattr(
            self.orientation,
            plane or [plane for plane in vars(self.orientation) if "_" in plane][0],
            getattr(self.orientation, plane) + (pow(-1, clockwise) * radians) % self.orientation.span)

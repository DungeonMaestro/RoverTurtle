import unittest
from RoverTurtle.rover import Mission, Rover, Playground
from RoverTurtle.Exceptions import *
from random import randint

ARBITRARY_TESTS_TO_RUN = 5


class TestSpecialCases(unittest.TestCase):
    def test_no_space(self):
        with self.assertRaises(SpaceError):
            null_space = Mission(0, 0)
            null_space.deploy_rover(0, 0, 0)

    def test_no_rovers(self):
        with self.assertRaises(FleetError):
            no_rovers = Mission(5, 5)
            no_rovers.command(rover_id=0, command_str="Move")

    def test_literal_edge_cases(self):
        unit_space = Mission(1, 1)
        unit_space.deploy_rover(0, 0, 0)
        for i in range(1,6):
            unit_space.command(0, "LM")
            self.assertEqual([i % 4, 0, 0], list(vars(unit_space.rovers[0]).values()))

    def test_path_matches_endpoints(self):
        mc = Mission(10, 10)
        for _ in range(4):
            mc.deploy_rover(0, 0, 0)

        self.assertEqual([0, 0, 0], list(vars(mc.rovers[0]).values()))
        mc.command(0, "MMMRMLLMMMMMMMLMRRRMMMMRMMLMMML")
        self.assertEqual([0, 0, 0], list(vars(mc.rovers[0]).values()))

        self.assertEqual([0, 0, 0], list(vars(mc.rovers[1]).values()))
        mc.command(1, "LMMMMMMMM")
        self.assertEqual([1, 0, 8], list(vars(mc.rovers[1]).values()))

        self.assertEqual([0, 0, 0], list(vars(mc.rovers[2]).values()))
        mc.command(2, "MMMMMMMM")
        self.assertEqual([0, 8, 0], list(vars(mc.rovers[2]).values()))

        self.assertEqual([0, 0, 0], list(vars(mc.rovers[3]).values()))
        mc.command(3, "LLLRLLLLL")
        self.assertEqual([3, 0, 0], list(vars(mc.rovers[3]).values()))


class TestRandomCases(unittest.TestCase):
    def test_arbitrary_parameters(self, count=None):
        mc = Playground.rand_scene()
        with self.assertRaises(Exception):
            for _ in range(count or ARBITRARY_TESTS_TO_RUN):
                Playground.rand_command(mc)


def startup(filepath="input.dat"):
    with open(filepath) as file:
        tests = []
        line = None
        while file:
            tmp = []
            while line != "END MISSION":
                tmp.append(file.readline().strip("\n"))
            tests.append(tmp)


if __name__ == '__main__':
    unittest.main()

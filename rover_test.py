import unittest
from RoverTurtle.rover import Mission, Rover, Playground
from RoverTurtle.Exceptions import *
from filecmp import cmp as file_cmp
from os import remove as del_file

ARBITRARY_TESTS_TO_RUN = 5


class TestSpecialCases(unittest.TestCase):

    def test_no_rovers(self):
        with self.assertRaises(FleetError):
            no_rovers = Mission(5, 5)
            no_rovers.command(rover_id=0, command_str="Move")

    def test_literal_edge_cases(self):
        unit_space = Mission(0, 0)
        unit_space.deploy_rover(0, 0, 0)
        rover = unit_space.rovers[0]
        for i in range(1, 6):
            unit_space.command(0, "LM")
            self.assertEqual((0, 0, i % 4), rover.get_location())

    def test_path_matches_endpoints(self):
        mc = Mission(10, 10)
        for _ in range(4):
            mc.deploy_rover(0, 0, 0)

        self.assertEqual((0, 0, 0), mc.rovers[0].get_location())
        mc.command(0, "MMMRMLLMMMMMMMLMRRRMMMMRMMLMMML")
        self.assertEqual((0, 0, 0), mc.rovers[0].get_location())

        self.assertEqual((0, 0, 0), mc.rovers[1].get_location())
        mc.command(1, "LMMMMMMMM")
        self.assertEqual((0, 8, 1), mc.rovers[1].get_location())

        self.assertEqual((0, 0, 0), mc.rovers[2].get_location())
        mc.command(2, "MMMMMMMM")
        self.assertEqual((8, 0, 0), mc.rovers[2].get_location())

        self.assertEqual((0, 0, 0), mc.rovers[3].get_location())
        mc.command(3, "LLLRLLLLL")
        self.assertEqual((0, 0, 3), mc.rovers[3].get_location())


class TestRandomCases(unittest.TestCase):
    def test_arbitrary_parameters(self, count=None):
        mc = Playground.rand_scene()
        for _ in range(count or ARBITRARY_TESTS_TO_RUN):
            Playground.rand_command(mc)


class TestFileIO(unittest.TestCase):
    def set_up(self):
        orientations = {value: index for index, value in Rover.ORIENTATIONS.items()}
        commands = []
        with open("test_files/input.dat", "r") as ifile:
            self.lines = [line.strip('\n') for line in ifile.readlines()]

        mission_params = self.lines.pop(0)
        rover_setups = [(self.lines[i], self.lines[i + 1]) for i, line in enumerate(self.lines) if i % 2 == 0]

        self.mission = Mission(*[int(char) for char in mission_params.split(' ')])
        for start, command in rover_setups:
            start = start.split(' ')
            o = orientations[start.pop()]
            x, y = [int(char) for char in start]
            self.mission.rovers.append(Rover(x, y, o, self.mission))
            commands.append(command)

        for i in range(len(self.mission.rovers)):
            self.mission.command(i, commands[i])

        with open("test_files/output.dat", "w") as ofile:
            for i in range(len(self.mission.rovers)):
                x, y, o = self.mission.locate(i)
                ofile.write(f"{x} {y} {Rover.ORIENTATIONS[o]}\n")

    def test_out_equals_expected(self):
        self.set_up()
        self.assertTrue(file_cmp("test_files/expected_out.dat", "test_files/output.dat"))
        self.assertFalse(file_cmp("test_files/bad_out.dat", "test_files/output.dat"))
        del_file("test_files/output.dat")


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

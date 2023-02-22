from simulation import edgeInfo
class topoMat:
    def __init__(self, _bandWidth) -> None:
        self.bandWidth = _bandWidth
        self.matTest = {
            0 : {
                    1: edgeInfo(10, self.bandWidth),
                    3: edgeInfo(10, self.bandWidth)
                },
            1 : {
                    0: edgeInfo(10, self.bandWidth),
                    2: edgeInfo(10, self.bandWidth),
                    4: edgeInfo(10, self.bandWidth)
                },
            2 : {
                    1: edgeInfo(10, self.bandWidth),
                    3: edgeInfo(10, self.bandWidth),
                    4: edgeInfo(10, self.bandWidth)
                },
            3 : {
                    0: edgeInfo(10, self.bandWidth),
                    2: edgeInfo(10, self.bandWidth),
                    5: edgeInfo(10, self.bandWidth),
                    6: edgeInfo(10, self.bandWidth)
                },
            4 : {
                    1: edgeInfo(10, self.bandWidth),
                    2: edgeInfo(10, self.bandWidth),
                    5: edgeInfo(10, self.bandWidth)
                },
            5 : {
                    3: edgeInfo(10, self.bandWidth),
                    4: edgeInfo(10, self.bandWidth),
                    6: edgeInfo(10, self.bandWidth)
                },
            6 : {
                    3: edgeInfo(10, self.bandWidth),
                    5: edgeInfo(10, self.bandWidth)
                },
        }

        self.matGBN = {
            0 : {
                2: edgeInfo(8, self.bandWidth),
                8: edgeInfo(7, self.bandWidth),
            },
            1 : {
                2: edgeInfo(15, self.bandWidth),
                3: edgeInfo(9, self.bandWidth),
            },
            2 : {
                0: edgeInfo(8, self.bandWidth),
                1: edgeInfo(15, self.bandWidth),
                4: edgeInfo(20, self.bandWidth),
            },
            3 : {
                1: edgeInfo(9, self.bandWidth),
                4: edgeInfo(16, self.bandWidth),
            },
            4 : {
                2: edgeInfo(20, self.bandWidth),
                3: edgeInfo(16, self.bandWidth),
                8: edgeInfo(6, self.bandWidth),
                9: edgeInfo(17, self.bandWidth),
                10: edgeInfo(9, self.bandWidth),
            },
            5 : {
                6: edgeInfo(11, self.bandWidth),
                8: edgeInfo(10, self.bandWidth),
            },
            6 : {
                5: edgeInfo(11, self.bandWidth),
                7: edgeInfo(10, self.bandWidth),
            },
            7 : {
                6: edgeInfo(10, self.bandWidth),
                8: edgeInfo(6, self.bandWidth),
                10: edgeInfo(10, self.bandWidth),
            },
            8 : {
                0: edgeInfo(7, self.bandWidth),
                4: edgeInfo(6, self.bandWidth),
                5: edgeInfo(10, self.bandWidth),
                7: edgeInfo(6, self.bandWidth),
            },
            9 : {
                4: edgeInfo(17, self.bandWidth),
                12: edgeInfo(10, self.bandWidth),
            },
            10 : {
                4: edgeInfo(9, self.bandWidth),
                7: edgeInfo(10, self.bandWidth),
                11: edgeInfo(22, self.bandWidth),
                12: edgeInfo(10, self.bandWidth),
            },
            11 : {
                10: edgeInfo(22, self.bandWidth),
                13: edgeInfo(10, self.bandWidth),
            },
            12 : {
                9: edgeInfo(10, self.bandWidth),
                10: edgeInfo(10, self.bandWidth),
                14: edgeInfo(4, self.bandWidth),
                16: edgeInfo(10, self.bandWidth),
            },
            13 : {
                11: edgeInfo(10, self.bandWidth),
                14: edgeInfo(5, self.bandWidth),
            },
            14 : {
                12: edgeInfo(4, self.bandWidth),
                13: edgeInfo(5, self.bandWidth),
                15: edgeInfo(10, self.bandWidth),
            },
            15 : {
                14: edgeInfo(10, self.bandWidth),
                16: edgeInfo(10, self.bandWidth),
            },
            16 : {
                12: edgeInfo(10, self.bandWidth),
                15: edgeInfo(10, self.bandWidth),
            },
        }
        
        self.matGeant2 = {
                0: {
                    1: edgeInfo(10, self.bandWidth),
                    2: edgeInfo(15, self.bandWidth),
                },
                1: {
                    0: edgeInfo(10, self.bandWidth),
                    3: edgeInfo(14, self.bandWidth),
                    6: edgeInfo(21, self.bandWidth),
                    9: edgeInfo(31, self.bandWidth),
                },
                2: {
                    0: edgeInfo(15, self.bandWidth),
                    3: edgeInfo(17, self.bandWidth),
                    4: edgeInfo(8, self.bandWidth),
                },
                3: {
                    1: edgeInfo(14, self.bandWidth),
                    2: edgeInfo(17, self.bandWidth),
                    5: edgeInfo(30, self.bandWidth),
                    6: edgeInfo(18, self.bandWidth),
                },
                4: {
                    2: edgeInfo(8, self.bandWidth),
                    7: edgeInfo(21, self.bandWidth),
                },
                5: {
                    3: edgeInfo(30, self.bandWidth),
                    8: edgeInfo(19, self.bandWidth),
                },
                6: {
                    1: edgeInfo(21, self.bandWidth),
                    3: edgeInfo(18, self.bandWidth),
                    8: edgeInfo(12, self.bandWidth),
                    9: edgeInfo(34, self.bandWidth),
                },
                7: {
                    4: edgeInfo(21, self.bandWidth),
                    8: edgeInfo(25, self.bandWidth),
                    11: edgeInfo(15, self.bandWidth),
                },
                8: {
                    5: edgeInfo(19, self.bandWidth),
                    6: edgeInfo(12, self.bandWidth),
                    7: edgeInfo(25, self.bandWidth),
                    11: edgeInfo(34, self.bandWidth),
                    12: edgeInfo(18, self.bandWidth),
                    17: edgeInfo(33, self.bandWidth),
                    18: edgeInfo(22, self.bandWidth),
                    20: edgeInfo(40, self.bandWidth),
                },
                9: {
                    1: edgeInfo(31, self.bandWidth),
                    6: edgeInfo(34, self.bandWidth),
                    10: edgeInfo(33, self.bandWidth),
                    12: edgeInfo(25, self.bandWidth),
                    13: edgeInfo(50, self.bandWidth),
                },
                10: {
                    9: edgeInfo(33, self.bandWidth),
                    13: edgeInfo(16, self.bandWidth),
                },
                11: {
                    7: edgeInfo(15, self.bandWidth),
                    8: edgeInfo(34, self.bandWidth),
                    14: edgeInfo(12, self.bandWidth),
                    20: edgeInfo(21, self.bandWidth),
                },
                12: {
                    8: edgeInfo(18, self.bandWidth),
                    9: edgeInfo(25, self.bandWidth),
                    13: edgeInfo(4, self.bandWidth),
                    19: edgeInfo(42, self.bandWidth),
                    21: edgeInfo(26, self.bandWidth),
                },
                13: {
                    9: edgeInfo(50, self.bandWidth),
                    10: edgeInfo(16, self.bandWidth),
                    12: edgeInfo(4, self.bandWidth),
                },
                14: {
                    11: edgeInfo(12, self.bandWidth),
                    15: edgeInfo(34, self.bandWidth),
                },
                15: {
                    14: edgeInfo(34, self.bandWidth),
                    16: edgeInfo(16, self.bandWidth),
                },
                16: {
                    15: edgeInfo(16, self.bandWidth),
                    17: edgeInfo(35, self.bandWidth),
                },
                17: {
                    8: edgeInfo(33, self.bandWidth),
                    16: edgeInfo(35, self.bandWidth),
                    18: edgeInfo(8, self.bandWidth),
                },
                18: {
                    8: edgeInfo(22, self.bandWidth),
                    17: edgeInfo(8, self.bandWidth),
                    21: edgeInfo(35, self.bandWidth),
                },
                19: {
                    12: edgeInfo(42, self.bandWidth),
                    23: edgeInfo(21, self.bandWidth),
                },
                20: {
                    8: edgeInfo(40, self.bandWidth),
                    11: edgeInfo(21, self.bandWidth),
                },
                21: {
                    12: edgeInfo(26, self.bandWidth),
                    18: edgeInfo(35, self.bandWidth),
                    22: edgeInfo(10, self.bandWidth),
                },
                22: {
                    21: edgeInfo(10, self.bandWidth),
                    23: edgeInfo(31, self.bandWidth),
                },
                23: {
                    19: edgeInfo(21, self.bandWidth),
                    22: edgeInfo(31, self.bandWidth),
                },

        }
    def getGBN(self):
        return self.matGBN
    def getmatGeant2(self):
        return self.matGeant2
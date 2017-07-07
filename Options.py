# coding: utf-8
from optparse import OptionParser


# 解析参数
# options, args = Options.parse(params)
# s = options.jar
def parse(params):
    parser = OptionParser()

    parser.add_option(
        "-j", "--jar",
        action="store",
        dest="jar",
        type="string",
        help="input jar file"
    )
    parser.add_option(
        "", "--combinemode",
        action="store_true",
        dest="combinemode",
        help="combinemode"
    )
    parser.add_option(
        "", "--filter ",
        action="store",
        dest="filter",
        type="int",
        help=""
    )

    return parser.parse_args(params)
import json
import logging
from time import time

from lab3.common.instructions import Program
from lab3.machine.control_unit import ControlUnit
from lab3.machine.datapath import DataPath
from lab3.machine.microcode import runtime


logger = logging.getLogger("machine.main")


def main(path_to_file: str, input_stream: str, statistics: bool = False):
    with open(path_to_file, encoding="utf-8") as file:
        data = json.load(file)
    program = Program(**data)
    dp = DataPath(program, list(input_stream))
    cpu = ControlUnit(dp, runtime)

    start = time()
    cpu.run()
    time_taken = time() - start

    if statistics:
        logger.info(
            "Program finished. Instructions executed: %s, ticks taken: %s, time taken: %.2f, tick"
            " rate: %.2f, ticks per instruction: %.2f",
            cpu.total_instructions,
            cpu.total_ticks,
            time_taken,
            cpu.total_ticks / time_taken,
            cpu.total_ticks / cpu.total_instructions,
        )
        logger.info("IO output: %s", "".join(map(chr, cpu.datapath.io_interface.output_buffer)))
        logger.info("IO output raw: %s", cpu.datapath.io_interface.output_buffer)
    print("".join(map(chr, cpu.datapath.io_interface.output_buffer)))


__all__ = ["main"]

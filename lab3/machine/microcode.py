import json
from dataclasses import dataclass, field
from typing import Optional

from lab3.common.instructions import AluOp, OpCode, OperandType
from lab3.machine.common import AluLopSel, AluRopSel, BrMuxSel, DataIoMuxSel, DrMuxSel
from lab3.machine.datapath import DataPath


# pylint: disable=too-many-instance-attributes
@dataclass
class MicroCode:
    """-
    In Python, we must first dispatch all
    select signals then move on to latching.
    In real life it's okay to simultaniously
    dispatch the signals, since everything
    should stabilize during the execution
    cycle for this microcode.
    """

    alu_lop_sel: AluLopSel = AluLopSel.SEL_ZERO
    alu_rop_sel: AluRopSel = AluRopSel.SEL_ZERO
    data_io_mux_sel: DataIoMuxSel = DataIoMuxSel.SEL_DATA
    br_mux_sel: BrMuxSel = BrMuxSel.SEL_ALU
    dr_mux_sel: DrMuxSel = DrMuxSel.SEL_DATA
    alu_op: AluOp = AluOp.ADD

    latch_ac: bool = False
    latch_br: bool = False
    latch_ir: bool = False
    latch_dr: bool = False
    latch_ar: bool = False
    latch_sp: bool = False
    latch_pc: bool = False
    latch_io: bool = False
    latch_data: bool = False
    latch_ps: bool = False
    latch_hlt: bool = False

    alias: Optional[str | OpCode] = None

    def execute(self, data_path: DataPath):
        data_path.sel_alu_lop(self.alu_lop_sel)
        data_path.sel_alu_rop(self.alu_rop_sel)
        data_path.sel_data_io_mux(self.data_io_mux_sel)
        data_path.sel_br_mux(self.br_mux_sel)
        data_path.sel_dr_mux(self.dr_mux_sel)
        data_path.sel_alu_op(self.alu_op)

        if self.latch_ac:
            data_path.latch_ac()
        if self.latch_br:
            data_path.latch_br()
        if self.latch_ir:
            data_path.latch_ir()
        if self.latch_dr:
            data_path.latch_dr()
        if self.latch_ar:
            data_path.latch_ar()
        if self.latch_sp:
            data_path.latch_sp()
        if self.latch_pc:
            data_path.latch_pc()
        if self.latch_io:
            data_path.write_io()
        if self.latch_data:
            data_path.write_data()
        if self.latch_ps:
            data_path.latch_ps()
        if self.latch_hlt:
            data_path.latch_hlt()

    def _format_dr(self) -> str:
        if self.dr_mux_sel == DrMuxSel.SEL_ALU:
            return f"DR <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "
        if self.dr_mux_sel == DrMuxSel.SEL_DATA:
            return f"DR <- {self.data_io_mux_sel} "
        return ""

    def _format_br(self) -> str:
        if self.br_mux_sel == BrMuxSel.SEL_ALU:
            return f"BR <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "
        if self.br_mux_sel == BrMuxSel.SEL_PC:
            return "BR <- PC "
        return ""

    def __str__(self) -> str:
        s = ""

        if self.latch_ac:
            s += f"AC <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_br:
            s += self._format_br()

        if self.latch_ir:
            s += "IR <- INSTR_MEMORY "

        if self.latch_dr:
            s += self._format_dr()

        if self.latch_ar:
            s += f"AR <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_sp:
            s += f"SP <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_pc:
            s += f"PC <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_ps:
            s += f"PS <- NZC({self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel}) "

        if self.latch_io:
            s += f"IO <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_data:
            s += f"DATA <- {self.alu_lop_sel} {self.alu_op} {self.alu_rop_sel} "

        if self.latch_hlt:
            s += "HLT "

        if self.alias is not None:
            s += f"({self.alias})"

        return s

    def __init__(
        self,
        alu_lop_sel,
        alu_rop_sel,
        data_io_mux_sel,
        br_mux_sel,
        dr_mux_sel,
        alu_op,
        latch_ac,
        latch_br,
        latch_ir,
        latch_dr,
        latch_ar,
        latch_sp,
        latch_pc,
        latch_io,
        latch_data,
        latch_ps,
        latch_hlt,
        alias,
    ):
        self.alu_lop_sel = AluLopSel(alu_lop_sel)
        self.alu_rop_sel = AluRopSel(alu_rop_sel)
        self.data_io_mux_sel = DataIoMuxSel(data_io_mux_sel)
        self.br_mux_sel = BrMuxSel(br_mux_sel)
        self.dr_mux_sel = DrMuxSel(dr_mux_sel)
        self.alu_op = AluOp(alu_op)

        self.latch_ac = latch_ac
        self.latch_br = latch_br
        self.latch_ir = latch_ir
        self.latch_dr = latch_dr
        self.latch_ar = latch_ar
        self.latch_sp = latch_sp
        self.latch_pc = latch_pc
        self.latch_io = latch_io
        self.latch_data = latch_data
        self.latch_ps = latch_ps
        self.latch_hlt = latch_hlt

        if alias in OpCode.__members__:
            self.alias = getattr(OpCode, alias)
        else:
            self.alias = alias


@dataclass
class BranchingMicroCode:
    """
    Branching in COMP-3 microcode works as an
    AND formula for all the check parameters.
    The parameters marked as None are not included in
    the logical AND.
    If the result is True, then perform the jump,
    otherwise continue executing.
    """

    branch_target: Optional[int | str]  # Microcode address or alias
    # If None, uses result of op_code decoder

    check_op_code: list[OpCode] = field(default_factory=list)
    check_operand_type: list[OperandType] = field(default_factory=list)
    check_operand: Optional[int] = None
    check_c_flag: Optional[bool] = None
    check_n_flag: Optional[bool] = None
    check_z_flag: Optional[bool] = None

    alias: Optional[str | OpCode] = None

    def execute(self, datapath: DataPath) -> bool:
        res = True

        if (
            len(self.check_op_code) != 0
            and datapath.ir.get_instruction().op_code not in self.check_op_code
        ):
            res = False

        if (
            len(self.check_operand_type) != 0
            and datapath.ir.get_instruction().operand_type not in self.check_operand_type
        ):
            res = False

        if (
            self.check_operand is not None
            and datapath.ir.get_instruction().operand != self.check_operand
        ):
            res = False

        if self.check_c_flag is not None and datapath.ps.c != self.check_c_flag:
            res = False

        if self.check_n_flag is not None and datapath.ps.n != self.check_n_flag:
            res = False

        if self.check_z_flag is not None and datapath.ps.z != self.check_z_flag:
            res = False

        return res

    def __str__(self) -> str:
        s = (
            "JUMP TO"
            f" {self.branch_target if self.branch_target is not None else 'DECODE(OP_CODE)'} IF "
        )

        if len(self.check_op_code) != 0:
            s += f"OP_CODE IN {list(map(lambda x: x.value, self.check_op_code))} "

        if len(self.check_operand_type) != 0:
            s += f"OPERNAD_TYPE IN {list(map(lambda x: x.value, self.check_operand_type))} "

        if self.check_operand is not None:
            s += f"OPERAND = {self.check_operand} "

        if self.check_c_flag is not None:
            s += f"C = {self.check_c_flag} "

        if self.check_n_flag is not None:
            s += f"N = {self.check_n_flag} "

        if self.check_z_flag is not None:
            s += f"Z = {self.check_z_flag} "

        if self.alias is not None:
            s += f"({self.alias})"

        return s

    def __init__(
        self,
        branch_target,
        check_op_code,
        check_operand_type,
        check_operand,
        check_c_flag,
        check_n_flag,
        check_z_flag,
        alias,
    ):
        self.branch_target = branch_target

        op_code = []
        for check in check_op_code:
            op_code.append(getattr(OpCode, check))

        self.check_op_code = op_code

        operand_type = []
        for operand in check_operand_type:
            operand_type.append(getattr(OperandType, operand.upper()))
        self.check_operand_type = operand_type
        self.check_operand = check_operand
        self.check_c_flag = check_c_flag
        self.check_n_flag = check_n_flag
        self.check_z_flag = check_z_flag

        if alias in OpCode.__members__:
            self.alias = getattr(OpCode, alias)
        else:
            self.alias = alias


def json_to_microcode(js):
    microcode_list = []
    for item in js:
        if "branch_target" in item:
            microcode_list.append(
                BranchingMicroCode(
                    item["branch_target"],
                    item["check_op_code"],
                    item["check_operand_type"],
                    item["check_operand"],
                    item["check_c_flag"],
                    item["check_n_flag"],
                    item["check_z_flag"],
                    item["alias"],
                )
            )
        else:
            microcode_list.append(
                MicroCode(
                    item["alu_lop_sel"],
                    item["alu_rop_sel"],
                    item["data_io_mux_sel"],
                    item["br_mux_sel"],
                    item["dr_mux_sel"],
                    item["alu_op"],
                    item["latch_ac"],
                    item["latch_br"],
                    item["latch_ir"],
                    item["latch_dr"],
                    item["latch_ar"],
                    item["latch_sp"],
                    item["latch_pc"],
                    item["latch_io"],
                    item["latch_data"],
                    item["latch_ps"],
                    item["latch_hlt"],
                    item["alias"],
                )
            )
    return microcode_list


with open("lab3/machine/microcode.json", "r") as file:
    json_data = file.read()

json_obj = json.loads(json_data)
runtime: list[MicroCode | BranchingMicroCode] = json_to_microcode(json_obj["runtime"])

commands_alias_to_address_index: dict[str, int] = {}

for index, command in enumerate(runtime):
    if command.alias is not None:
        commands_alias_to_address_index[command.alias] = index

for index, command in enumerate(runtime):
    if isinstance(command, BranchingMicroCode) and isinstance(command.branch_target, str):
        if command.branch_target not in commands_alias_to_address_index:
            raise ValueError(f"Unkonwn alias {command.branch_target} in command {index}")
        command.branch_target = commands_alias_to_address_index[command.branch_target]

if __name__ == "__main__":
    for i, code in enumerate(runtime):
        print(i, code)

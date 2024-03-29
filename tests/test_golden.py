import logging
from io import StringIO

import pytest

from lab3.compiler import compile_pipeline
from lab3.machine import main


@pytest.mark.golden_test("golden_tests/*.yml")
def test_golden(golden, caplog, capsys, tmpdir):
    caplog.set_level(logging.DEBUG)
    log_formatter = logging.Formatter("%(message)s")
    caplog.handler.setFormatter(log_formatter)

    compiled_prog_buffer = StringIO()
    with open(golden["in_source"], encoding="utf-8") as code_source:
        compile_pipeline(code_source, compiled_prog_buffer)
    compiled_prog = compiled_prog_buffer.getvalue()

    assert golden.out["out_prog"] == compiled_prog

    with open(tmpdir / "tmp_prog.json", "w", encoding="utf-8") as file:
        file.write(compiled_prog)

    main(tmpdir / "tmp_prog.json", golden["in"])

    assert "\n".join(caplog.text.splitlines()[:100000]) == golden.out["out_logs"]
    assert capsys.readouterr().out == golden["out"]

from pathlib import Path

from top300.cli import main


def test_demo_creates_ranked_output(tmp_path: Path) -> None:
    code = main(["demo", str(tmp_path)])
    assert code == 0
    assert (tmp_path / "top300.db").exists()
    assert (tmp_path / "ranked.json").exists()


def test_cli_module_executes_demo(tmp_path: Path) -> None:
    import os
    import subprocess
    import sys

    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
    completed = subprocess.run(
        [sys.executable, "-m", "top300.cli", "demo", str(tmp_path)],
        env=env,
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0
    assert (tmp_path / "ranked.json").exists()

from __future__ import annotations

import importlib.metadata
import pathlib
import re
import shutil
import subprocess
import sys


def coerce_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return value


def run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        output = coerce_output(exc.stdout) + coerce_output(exc.stderr)
        raise AssertionError("Command timed out. Output:\n" + output) from exc


def assert_usepr_help() -> None:
    executable = shutil.which("usepr")
    if executable is None:
        raise AssertionError("usepr executable not found in PATH")

    executable_path = pathlib.Path(executable)
    python_bin_dir = pathlib.Path(sys.executable).parent
    try:
        same_env = executable_path.parent.samefile(python_bin_dir)
    except FileNotFoundError:
        same_env = executable_path.parent.resolve() == python_bin_dir.resolve()
    if not same_env:
        raise AssertionError(
            "usepr executable is not from the current environment. "
            f"sys.executable={sys.executable} usepr={executable}"
        )

    result = run_command([executable, "--help"])
    output = coerce_output(result.stdout) + coerce_output(result.stderr)
    if result.returncode != 0:
        raise AssertionError(
            f"usepr --help failed with exit code {result.returncode}. Output:\n{output}"
        )
    if re.search(r"\bgenerate\b", output) is None:
        raise AssertionError(
            "usepr --help output missing 'generate'. Output:\n" + output
        )

    subcommand = run_command([executable, "generate", "--help"])
    sub_output = coerce_output(subcommand.stdout) + coerce_output(subcommand.stderr)
    if subcommand.returncode != 0:
        raise AssertionError(
            "usepr generate --help failed with exit code "
            f"{subcommand.returncode}. Output:\n{sub_output}"
        )


def assert_import() -> None:
    import usepr

    package_file = pathlib.Path(usepr.__file__).resolve()
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    if package_file.is_relative_to(repo_root):
        raise AssertionError(
            "usepr import resolved to the repo checkout. "
            f"repo_root={repo_root} usepr.__file__={usepr.__file__}"
        )

    importlib.metadata.version("usepr")


def main() -> int:
    assert_import()
    assert_usepr_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())

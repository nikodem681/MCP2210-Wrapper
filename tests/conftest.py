import ctypes
import os
import shutil
import subprocess
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HEADER_DIR = os.path.join(ROOT, "instrumentation", "PCBs", "MCP2210")
HEADER = os.path.join(HEADER_DIR, "mcp2210_dll_um.h")
STUB_SRC = os.path.join(os.path.dirname(__file__), "fake_dll", "fake_mcp2210.c")


@pytest.fixture(scope="session")
def fake_dll_build(tmp_path_factory):
    """Compile the fake MCP2210 DLL against the vendor header."""
    if sys.platform == "win32":
        pytest.skip("the fake DLL is built with a Unix C compiler")
    cc = shutil.which("cc") or shutil.which("gcc")
    if cc is None:
        pytest.skip("no C compiler available")
    out = tmp_path_factory.mktemp("fake_dll") / "libfake_mcp2210.so"
    subprocess.run(
        [cc, "-shared", "-fPIC", "-Wall", "-Werror", "-DMCP2210_LIB", "-I", HEADER_DIR, STUB_SRC, "-o", str(out)],
        check=True,
    )
    return out


@pytest.fixture
def fake_dll_path(fake_dll_build, tmp_path, monkeypatch):
    """A private copy of the fake DLL (fresh state per test), loadable through ctypes.WinDLL."""
    path = tmp_path / "fake_mcp2210.so"
    shutil.copy(fake_dll_build, path)
    monkeypatch.setattr(ctypes, "WinDLL", ctypes.CDLL, raising=False)
    from instrumentation.PCBs import mcp2210_wrapper
    monkeypatch.setattr(mcp2210_wrapper, "_DEFAULT_DLL_PATH", str(path))
    return str(path)


@pytest.fixture
def mcp(fake_dll_path):
    from instrumentation.PCBs.mcp2210_wrapper import MCP2210
    return MCP2210()


def spi_log(dll):
    """Return the SPI transfers recorded by the fake DLL as [(bytes, csmask), ...]."""
    count = dll.fake_xfer_count()
    log = []
    for i in range(count):
        buf = (ctypes.c_ubyte * 64)()
        length = ctypes.c_uint()
        csmask = ctypes.c_uint()
        assert dll.fake_get_xfer(i, buf, ctypes.byref(length), ctypes.byref(csmask)) == 0
        log.append((list(buf[:length.value]), csmask.value))
    return log

"""
Smoke test for MCP2210 NVRAM string descriptors.

Steps:
  1. Find the MCP2210 (count + open by index 0).
  2. Read and print all current/default data (version, serial, manufacturer
     string, product string, USB key params).
  3. Round-trip test on the descriptor strings: save originals, write test
     values, read them back, verify, then restore the originals.

The string round-trip writes to NVRAM but restores the originals afterwards,
so the device is left as it was found. USB key params (VID/PID/...) are only
read here -- changing them would change how the device enumerates.

Run from the project root:  python -m sandbox.test_mcp2210_descriptors
Or directly:                python sandbox/test_mcp2210_descriptors.py
"""
import os
import sys

# Make the project root importable so `instrumentation` resolves regardless of cwd.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from instrumentation.PCBs.mcp2210_wrapper import MCP2210


def dump_current_data(mcp, handle):
    print("\n--- Current device data ---")
    print(f"Serial number      : {mcp.get_serial_number(handle)!r}")
    print(f"Manufacturer string: {mcp.get_manufacturer_string(handle)!r}")
    print(f"Product string     : {mcp.get_product_string(handle)!r}")
    params = mcp.get_usb_key_params(handle)
    print(f"USB key params     : VID=0x{params['vid']:04X} PID=0x{params['pid']:04X} "
          f"power_source={params['power_source']} remote_wakeup={params['remote_wakeup']} "
          f"current_load={params['current_load']}")
    return params


def roundtrip_string(name, getter, setter, handle, test_value):
    """Save original -> set test_value -> read back -> verify -> restore original."""
    original = getter(handle)
    print(f"\n[{name}] original = {original!r}")
    try:
        setter(handle, test_value)
        readback = getter(handle)
        ok = (readback == test_value)
        print(f"[{name}] wrote {test_value!r}, read back {readback!r} -> "
              f"{'PASS' if ok else 'FAIL'}")
        return ok
    finally:
        setter(handle, original)
        restored = getter(handle)
        print(f"[{name}] restored original -> {restored!r} "
              f"({'ok' if restored == original else 'MISMATCH'})")


def main():
    mcp = MCP2210()
    print(f"DLL version: {mcp.get_library_version()}")

    count = mcp.get_connected_device_count()
    print(f"Connected MCP2210 devices: {count}")
    if count == 0:
        print("No MCP2210 found. Plug it in and try again.")
        return 1

    handle = mcp.open_device_by_index(index=0)
    print(f"Opened device index 0, handle = {handle}")

    try:
        dump_current_data(mcp, handle)

        results = []
        results.append(roundtrip_string(
            "Manufacturer", mcp.get_manufacturer_string,
            mcp.set_manufacturer_string, handle, "MCP_TEST_MFR"))
        results.append(roundtrip_string(
            "Product", mcp.get_product_string,
            mcp.set_product_string, handle, "MCP_TEST_PROD"))

        print("\n--- Result ---")
        print("ALL PASS" if all(results) else "SOME FAILED")
        return 0 if all(results) else 1
    finally:
        mcp.close_device(handle)
        print("Device closed.")


if __name__ == "__main__":
    sys.exit(main())

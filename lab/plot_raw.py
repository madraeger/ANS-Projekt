from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable

import matplotlib.pyplot as plt
import numpy as np
from PyLTSpice import RawRead

DATA_DIR = Path(__file__).resolve().parent / "data"


def _unique_field_names(trace_info):
    counts: dict[str, int] = {}
    result: list[str] = []
    for info in trace_info:
        base = info.name
        if base in counts:
            field_name = f"{base}__dup{counts[base]}"
            counts[base] += 1
        else:
            field_name = base
            counts[base] = 1
        result.append(field_name)
    return result


def _normalize_trace_selection(traces):
    if traces is None:
        return None
    if isinstance(traces, str):
        traces = [t.strip() for t in traces.split(",") if t.strip()]
    return list(traces)


def load_raw_file(raw_path: Path, traces_to_read=None, verbose=False):
    """Liest eine LTspice *.raw-Datei mit PyLTSpice ein und gibt die Zeitachse plus Trace-Daten zurück."""
    raw = RawRead(raw_path, traces_to_read=None, verbose=verbose)
    plot = raw._plots[0]
    requested_traces = _normalize_trace_selection(traces_to_read)

    trace_info = plot._trace_info
    unique_field_names = _unique_field_names(trace_info)
    if requested_traces is not None:
        requested_set = set(requested_traces)
    else:
        requested_set = None

    dtype_list = []
    for i, info in enumerate(trace_info):
        field_name = unique_field_names[i]
        if i == 0 and plot._has_axis:
            dtype = info.dtype
        elif requested_set is None or info.name in requested_set:
            dtype = info.dtype
        else:
            dtype = f"V{np.dtype(info.dtype).itemsize}"
        dtype_list.append((field_name, dtype))

    record_size = sum(np.dtype(t[1]).itemsize for t in dtype_list)
    with open(raw_path, "rb") as raw_file:
        raw_file.seek(plot._fpos_data)
        raw_data = plot._read_bytes_from_file(raw_file, plot._nPoints * record_size)
        data = np.frombuffer(raw_data, dtype=dtype_list)

    time_axis = data[unique_field_names[0]]
    traces: dict[str, list[np.ndarray]] = {}
    for i, info in enumerate(trace_info[1:], start=1):
        field_name = unique_field_names[i]
        if requested_set is not None and info.name not in requested_set:
            continue
        traces.setdefault(info.name, []).append(data[field_name])

    return time_axis, traces, raw


def list_traces(raw_path: Path):
    raw = RawRead(raw_path, traces_to_read=None, verbose=False)
    plot = raw._plots[0]
    trace_names = plot.get_trace_names()
    duplicates = [name for name in trace_names if trace_names.count(name) > 1]
    unique = sorted(set(trace_names), key=trace_names.index)
    return unique, duplicates


def plot_traces(time_axis: np.ndarray, traces: dict[str, list[np.ndarray]], selected: Iterable[str] | None = None):
    selected = list(selected) if selected is not None else list(traces.keys())
    if not selected:
        raise ValueError("Keine Spuren zum Plotten ausgewählt.")

    fig, ax = plt.subplots(figsize=(10, 6))
    for name in selected:
        arrays = traces.get(name)
        if arrays is None:
            continue
        for idx, values in enumerate(arrays):
            label = name if len(arrays) == 1 else f"{name}[{idx}]"
            ax.plot(time_axis, values, label=label)

    ax.set_xlabel("Zeit [s]")
    ax.set_ylabel("Signal")
    ax.set_title("LTspice RAW Plot")
    ax.grid(True)
    ax.legend(loc="best", fontsize="small")
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LTspice RAW-Dateien mit PyLTSpice einlesen und plotten.")
    parser.add_argument("--file", "-f", type=Path, help="Pfad zur RAW-Datei. Standard: erstes RAW im data-Ordner.")
    parser.add_argument("--trace", "-t", action="append", help="Trace-Name zum Plotten. Mehrfach möglich.")
    parser.add_argument("--list", action="store_true", help="Druckt die verfügbaren Trace-Namen und beendet.")
    parser.add_argument("--verbose", action="store_true", help="Zeigt zusätzliche Debug-Informationen beim Einlesen.")
    args = parser.parse_args()

    raw_path = args.file if args.file is not None else next(DATA_DIR.glob("*.raw"), None)
    if raw_path is None:
        raise FileNotFoundError("Keine RAW-Datei im data-Ordner gefunden.")

    if args.list:
        trace_names, duplicates = list_traces(raw_path)
        print(f"RAW-Datei: {raw_path}")
        print("Verfügbare Traces:")
        for name in trace_names:
            print(f"  {name}")
        if duplicates:
            print("\nAchtung: doppelte Trace-Namen gefunden:")
            for name in sorted(set(duplicates), key=duplicates.index):
                print(f"  {name}")
        raise SystemExit(0)

    time_axis, traces, _ = load_raw_file(raw_path, traces_to_read=args.trace, verbose=args.verbose)
    selected_traces = args.trace if args.trace else list(traces.keys())
    plot_traces(time_axis, traces, selected_traces)

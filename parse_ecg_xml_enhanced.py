#!/usr/bin/env python3
"""
Parse a GE MUSE / Sapphire DCAR ECG XML file (the raw EKG files in your
tempfileRama-HN folders) and:
  1) print patient info + the machine's interpretation
  2) plot the full-resolution 12-lead waveform to a PNG

Usage:
    pip install matplotlib
    python parse_ecg_xml_enhanced.py path/to/file.xml
    python parse_ecg_xml_enhanced.py path/to/file.xml --out my_plot.png

Enhanced version for AI_ECG_CACS project integration.
"""

import sys
import argparse
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import os

NS = {"d": "urn:ge:sapphire:dcar_1"}


def parse_ecg(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # ---- patient info ----
    hn = root.find(".//d:identifier/d:id", NS)
    dob = root.find(".//d:birthDateTime", NS)
    gender = root.find(".//d:gender", NS)
    acq_time = root.find(".//d:testInfo/d:acquisitionDateTime", NS)

    print("HN:", hn.get("V") if hn is not None else None)
    print("DOB:", dob.get("V") if dob is not None else None)
    print("Gender:", gender.get("V") if gender is not None else None)
    print("Acquired:", acq_time.get("V") if acq_time is not None else None)

    # ---- interpretation ----
    print("\nInterpretation:")
    for stmt in root.findall(".//d:interpretation/d:statement", NS):
        text = stmt.get("V", "").strip()
        if text:
            print(" -", text)

    # ---- key intervals (optional but useful) ----
    global_meas = root.find(".//d:medianTemplate/d:measurements/d:global", NS)
    if global_meas is not None:
        print("\nKey intervals:")
        for tag in ["QRS_Duration", "QT_Interval", "QT_Corrected", "PR_Interval"]:
            el = global_meas.find(f"d:{tag}", NS)
            if el is not None:
                print(f"  {tag}: {el.get('V')} {el.get('U', '')}")

    # ---- full-resolution waveform (under <wav>, not the median template) ----
    wav_container = root.find(".//d:testInfo/../d:ecgResting/d:params/d:ecg/d:wav", NS)
    if wav_container is None:
        # fallback: just grab the biggest asizeVT waveforms anywhere in the doc
        leads = root.findall(".//d:ecgWaveform", NS)
    else:
        leads = wav_container.findall(".//d:ecgWaveform", NS)

    # keep only the full-resolution set (asizeVT is large, e.g. 5000),
    # not the ~600-sample median-beat template
    full_res = [el for el in leads if int(el.get("asizeVT", "0")) > 1000]

    sample_rate = root.find(".//d:wav//d:sampleRate", NS)
    hz = float(sample_rate.get("V")) if sample_rate is not None else 500.0

    scale_el = root.find(".//d:wav//d:ecgWaveformMXG", NS)
    scale = float(scale_el.get("S")) if scale_el is not None else 1.0  # uV per unit

    waveforms = {}
    for el in full_res:
        label = el.get("label", el.get("lead"))
        values = [int(v) * scale for v in el.get("V").split()]
        waveforms[label] = values

    return waveforms, hz


def plot_waveforms(waveforms, hz, out_path):
    lead_order = ["I", "II", "III", "aVR", "aVL", "aVF",
                  "V1", "V2", "V3", "V4", "V5", "V6"]
    leads = [l for l in lead_order if l in waveforms] or list(waveforms.keys())

    fig, axes = plt.subplots(len(leads), 1, figsize=(12, 1.4 * len(leads)), sharex=True)
    if len(leads) == 1:
        axes = [axes]

    for ax, lead in zip(axes, leads):
        values = waveforms[lead]
        t = [i / hz for i in range(len(values))]
        ax.plot(t, values, linewidth=0.6, color="black")
        ax.set_ylabel(lead, rotation=0, ha="right", va="center", fontsize=9)
        ax.set_yticks([])
        ax.spines[["top", "right", "left"]].set_visible(False)

    axes[-1].set_xlabel("Time (s)")
    fig.suptitle("12-lead ECG")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    print(f"\nSaved plot to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("xml_path", help="Path to the ECG XML file")
    parser.add_argument("--out", default="ecg_plot.png", help="Output PNG path")
    args = parser.parse_args()

    waveforms, hz = parse_ecg(args.xml_path)
    if waveforms:
        plot_waveforms(waveforms, hz, args.out)
    else:
        print("No full-resolution waveform found in this file.")
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path

getcontext().prec = 50
N_LINES = 70
SITE = Decimal("1")
TARGET_FILE_NAME = "Pt-111-output"
TARGET_KEYWORDS = ["Rforward", "Rreverse", "Rnet"]
CSV_HEADER = [
    "Rforward_read",
    "Rreverse_read",
    "Rnet_read",
]

def fmt_sci(x: Decimal) -> str:
    return f"{x:.16e}"

def find_header_line(lines):
    for i, line in enumerate(lines):
        if all(key in line for key in TARGET_KEYWORDS):
            return i

    raise RuntimeError(
        "没有找到包含 Rforward Rreverse Rnet 的表头行。"
    )

def main():
    script_dir = Path(__file__).resolve().parent

    input_file = script_dir / TARGET_FILE_NAME

    output_file = script_dir / f"{TARGET_FILE_NAME}_rates_read.csv"

    if not input_file.exists():
        raise FileNotFoundError(
            f"没有找到输入文件：\n{input_file}\n\n"
            f"请确认 {TARGET_FILE_NAME} 和本脚本在同一个文件夹中。"
        )

    with input_file.open("r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    header_idx = find_header_line(lines)

    data_lines = lines[header_idx + 1: header_idx + 1 + N_LINES]

    if len(data_lines) < N_LINES:
        raise RuntimeError(
            f"表头后只有 {len(data_lines)} 行，不足 {N_LINES} 行。"
        )

    rows = []

    for offset, line in enumerate(data_lines, start=1):
        line_number = header_idx + offset + 1
        parts = line.split()

        if len(parts) < 5:
            raise RuntimeError(
                f"第 {line_number} 行列数不足，无法读取第 3-5 列：\n{line}"
            )

        try:
            rforward = Decimal(parts[2]) / SITE
            rreverse = Decimal(parts[3]) / SITE
            rnet = Decimal(parts[4]) / SITE
        except InvalidOperation:
            raise RuntimeError(
                f"第 {line_number} 行第 3-5 列无法转换为数字：\n{parts[2:5]}"
            )

        rows.append([
            fmt_sci(rforward),
            fmt_sci(rreverse),
            fmt_sci(rnet),
        ])

    with output_file.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADER)
        writer.writerows(rows)

    print("读取完成！")
    print(f"输入文件：{input_file}")
    print(f"输出文件：{output_file}")
    print(f"读取行数：{len(rows)}")
    print(f"表头所在行：{header_idx + 1}")

if __name__ == "__main__":
    main()
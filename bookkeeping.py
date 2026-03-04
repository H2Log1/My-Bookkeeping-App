#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: H2Log1
Date: 2026-02-14
Description: 个人记账本
"""

import csv
import datetime
import json
import os

import FreeSimpleGUI as sg

sg.theme("LightBlue2")
sg.set_options(font=("微软雅黑", 11))


def formatAmount(value) -> str:
    if value > 1e15 or value < -1e15:
        return f"{value:.2e}"
    return f"{value:,.2f}"


def readData() -> list:
    try:
        with open(r"data.txt", "r", encoding="utf-8") as f:
            jsonData = f.read()
        if jsonData.strip() == "":
            return []
        dataList = json.loads(jsonData)
    except (FileNotFoundError, json.JSONDecodeError):
        dataList = []
    return dataList


def writeData(dataList: list) -> None:
    jsonData = json.dumps(dataList, ensure_ascii=False)
    with open(r"data.txt", "w", encoding="utf-8") as f:
        f.write(jsonData)


def showData() -> list:
    data = readData()
    dataList = []
    for d in data:
        if d["分类"] == "收入":
            dataList.append([d["时间"], d["项目"], formatAmount(d["金额"]), d["分类"]])
        else:
            dataList.append([d["时间"], d["项目"], formatAmount(-d["金额"]), d["分类"]])
    return dataList


def sumAmounts() -> tuple:
    sumin = 0
    sumout = 0
    data = readData()
    for d in data:
        if d["分类"] == "收入":
            sumin += d["金额"]
        else:
            sumout += d["金额"]
    return sumin, sumout, sumin - sumout


def addData(content: str, amount: float, cla: str) -> None:
    data = readData()
    t = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    data.append({"时间": t, "项目": content, "金额": amount, "分类": cla})
    writeData(data)


def deleteData(index: int) -> dict | None:
    data = readData()
    if 0 <= index < len(data):
        deletedItem = data.pop(index)
        writeData(data)
        return deletedItem
    return None


def mainLayout() -> list:
    records = showData()
    sumin, sumout, sumall = sumAmounts()
    statsFrame = [
        sg.Frame(
            "收入",
            [
                [
                    sg.Text(
                        f"￥{formatAmount(sumin)}",
                        key="-in-",
                        text_color="green",
                        font=("微软雅黑", 16, "bold"),
                    )
                ]
            ],
            element_justification="center",
            expand_x=True,
        ),
        sg.Frame(
            "支出",
            [
                [
                    sg.Text(
                        f"￥{formatAmount(sumout)}",
                        key="-out-",
                        text_color="red",
                        font=("微软雅黑", 16, "bold"),
                    )
                ]
            ],
            element_justification="center",
            expand_x=True,
        ),
        sg.Frame(
            "结余",
            [
                [
                    sg.Text(
                        f"￥{formatAmount(sumall)}",
                        key="-balance-",
                        text_color="blue",
                        font=("微软雅黑", 16, "bold"),
                    )
                ]
            ],
            element_justification="center",
            expand_x=True,
        ),
    ]

    tableFrame = sg.Frame(
        "账目明细",
        [
            [
                sg.Table(
                    records,
                    headings=["时间", "项目", "金额", "分类"],
                    key="-show-",
                    justification="center",
                    auto_size_columns=False,
                    col_widths=[18, 12, 16, 8],
                    num_rows=10,
                    enable_events=True,
                    right_click_menu=["&右键", ["删除"]],
                    alternating_row_color="#E8F4F8",
                    header_background_color="#4A90A4",
                    header_text_color="white",
                )
            ]
        ],
        expand_x=True,
        expand_y=True,
    )

    inputFrame = sg.Frame(
        "添加账单",
        [
            [sg.Text("项目：", size=(6, 1)), sg.Input(key="-content-", size=(25, 1))],
            [sg.Text("金额：", size=(6, 1)), sg.Input(key="-amount-", size=(25, 1))],
            [sg.Text("分类：", size=(6, 1))]
            + [sg.Radio(i, group_id=1, key=i) for i in ["收入", "支出"]],
        ],
        expand_x=True,
    )

    buttonFrame = [
        sg.Button("确认提交", size=(10, 1), button_color=("white", "#4CAF50")),
        sg.Button("清空账单", size=(10, 1), button_color=("white", "#FF9800")),
        sg.Button("导出数据", size=(10, 1), button_color=("white", "#2196F3")),
    ]

    Layout = [
        [
            sg.Text(
                "个人记账本",
                font=("微软雅黑", 20, "bold"),
                justification="center",
                expand_x=True,
                pad=(0, 10),
            )
        ],
        [sg.HorizontalSeparator()],
        statsFrame,
        [sg.VPush()],
        [tableFrame],
        [sg.VPush()],
        [inputFrame],
        [sg.Push()] + buttonFrame + [sg.Push()],
    ]
    return Layout


def refreshUI(windows) -> None:
    currentList = showData()
    sum_in, sum_out, sum_all = sumAmounts()
    windows["-show-"].update(currentList)
    windows["-in-"].update(f"￥{formatAmount(sum_in)}")
    windows["-out-"].update(f"￥{formatAmount(sum_out)}")
    windows["-balance-"].update(f"￥{formatAmount(sum_all)}")


def handleSubmit(windows, values) -> None:
    content = values["-content-"].strip()
    if not content:
        sg.popup("请输入项目名称！")
        windows["-content-"].set_focus()
        return

    try:
        amount = float(values["-amount-"])
    except ValueError:
        sg.popup("请输入有效的金额！")
        windows["-amount-"].set_focus()
        return

    if amount <= 0:
        sg.popup("金额必须大于零！")
        windows["-amount-"].set_focus()
        return

    cla = None
    for k, v in values.items():
        if v is True and k not in ["-content-", "-amount-", "-show-"]:
            cla = k
            break

    if cla is None:
        sg.popup("请选择分类（收入/支出）！")
        return

    addData(content, amount, cla)
    sg.popup("账单项目已保存！")
    refreshUI(windows)
    windows["-content-"].update("")
    windows["-amount-"].update("")
    windows["-content-"].set_focus()


def handleDelete(windows, values) -> None:
    selected = values["-show-"]
    if selected:
        index = selected[0]
        deletedItem = deleteData(index)
        if deletedItem:
            sg.popup(f"已删除: {deletedItem['项目']}")
            refreshUI(windows)
    else:
        sg.popup("请先选中要删除的账单项目！")


def handleClear(windows, values) -> None:
    if sg.popup_yes_no("确定要清空所有账单吗？", title="清空") == "Yes":
        writeData([])
        refreshUI(windows)
        sg.popup("账单已清空！")


def handleExport(windows, values) -> None:
    filepath = sg.popup_get_file(
        "保存到",
        save_as=True,
        default_extension=".csv",
        file_types=(
            ("CSV 文件", "*.csv"),
            ("JSON 文件", "*.json"),
            ("文本文件", "*.txt"),
            ("All Files", "*.*"),
        ),
    )
    if not filepath:
        return

    data = readData()
    if not data:
        sg.popup("没有数据可导出！")
        return

    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == ".csv":
            _exportCSV(filepath, data)
        elif ext == ".json":
            _exportJSON(filepath, data)
        else:
            _exportTXT(filepath, data)
        sg.popup(f"已导出到: {filepath}")
    except Exception as e:
        sg.popup_error(f"导出失败：{e}")


def _exportCSV(filepath: str, data: list) -> None:
    with open(filepath, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["时间", "项目", "金额", "分类"])
        for d in data:
            amount = d["金额"] if d["分类"] == "收入" else -d["金额"]
            writer.writerow([d["时间"], d["项目"], amount, d["分类"]])


def _exportJSON(filepath: str, data: list) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _exportTXT(filepath: str, data: list) -> None:
    sumin, sumout, sumall = sumAmounts()
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"{'个人记账本':=^40}\n\n")
        f.write(f"{'时间':<22}{'项目':<12}{'金额':>10}  {'分类'}\n")
        f.write("-" * 56 + "\n")
        for d in data:
            amount = d["金额"] if d["分类"] == "收入" else -d["金额"]
            f.write(f"{d['时间']:<22}{d['项目']:<12}{amount:>10.2f}  {d['分类']}\n")
        f.write("-" * 56 + "\n")
        f.write(
            f"收入合计: ￥{sumin:.2f}  支出合计: ￥{sumout:.2f}  结余: ￥{sumall:.2f}\n"
        )


def main():
    windows = sg.Window(
        "个人记账本",
        mainLayout(),
        return_keyboard_events=True,
        size=(650, 580),
        element_justification="center",
    )

    eventHandlers = {
        "确认提交": handleSubmit,
        "删除": handleDelete,
        "清空账单": handleClear,
        "导出数据": handleExport,
    }

    while True:
        event, values = windows.read()

        if event is None:
            break

        if event.startswith("Return") or event == "\r":
            focused = windows.find_element_with_focus()
            if focused is not None:
                if focused.Key == "-content-":
                    windows["-amount-"].set_focus()
                elif focused.Key == "-amount-":
                    windows["-content-"].set_focus()

        handler = eventHandlers.get(event)
        if handler:
            handler(windows, values)

    windows.close()


if __name__ == "__main__":
    main()

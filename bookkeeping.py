import json
import datetime
import FreeSimpleGUI as sg

sg.theme("LightBlue2")
sg.set_options(font=("微软雅黑", 11))

def readData() -> list:
    try:
        with open(r"data.txt", "r", encoding = "utf-8") as f:
            jsonData = f.read()
        if jsonData.strip() == "":
            return []
        dataList = json.loads(jsonData)
    except (FileNotFoundError, json.JSONDecodeError):
        dataList = []
    return dataList

def writeData(dataList: list) -> None:
    jsonData = json.dumps(dataList, ensure_ascii = False)
    with open(r"data.txt","w", encoding = "utf-8") as f:
        jsonData = f.write(jsonData)
        sg.popup("账单项目已保存！")

def showData(dataList: list) -> list:
    data = readData()
    dataList = []
    for d in data:
        if d["分类"] == "收入":
            dataList.append([d["时间"], d["项目"], d["金额"], d["分类"]])
        else:
            dataList.append([d["时间"], d["项目"], -d["金额"], d["分类"]])
    return dataList

def sum() -> tuple:
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

def deleteData(index: int) -> bool:
    data = readData()
    if 0 <= index < len(data):
        deleted_item = data.pop(index)
        jsonData = json.dumps(data, ensure_ascii=False)
        with open(r"data.txt", "w", encoding="utf-8") as f:
            f.write(jsonData)
        sg.popup(f"已删除: {deleted_item['项目']}")
        return True
    return False


def main():
    list = showData(readData())
    sum_in, sum_out, sum_all = sum()
    
    stats_frame = [
        sg.Frame("收入", [[sg.Text(f"￥{sum_in}", key="-in-", text_color="green", font=("微软雅黑", 16, "bold"))]], 
                 element_justification="center", expand_x=True),
        sg.Frame("支出", [[sg.Text(f"￥{sum_out}", key="-out-", text_color="red", font=("微软雅黑", 16, "bold"))]], 
                 element_justification="center", expand_x=True),
        sg.Frame("结余", [[sg.Text(f"￥{sum_all}", key="-balance-", text_color="blue", font=("微软雅黑", 16, "bold"))]], 
                 element_justification="center", expand_x=True),
    ]
    
    table_frame = sg.Frame("账目明细", [
        [sg.Table(list, headings=["时间", "项目", "金额", "分类"], 
                  key="-show-", 
                  justification="center",
                  auto_size_columns=False,
                  col_widths=[18, 12, 10, 8],
                  num_rows=10,
                  enable_events=True,
                  right_click_menu=["&右键", ["删除"]],
                  alternating_row_color="#E8F4F8",
                  header_background_color="#4A90A4",
                  header_text_color="white"
                  )]
    ], expand_x=True, expand_y=True)
    
    input_frame = sg.Frame("添加账单", [
        [sg.Text("项目：", size=(6, 1)), sg.Input(key="-content-", size=(25, 1))],
        [sg.Text("金额：", size=(6, 1)), sg.Input(key="-amount-", size=(25, 1))],
        [sg.Text("分类：", size=(6, 1))] + [sg.Radio(i, group_id=1, key=i) for i in ["收入", "支出"]],
    ], expand_x=True)
    
    button_frame = [
        sg.Button("确认提交", size=(10, 1), button_color=("white", "#4CAF50")),
        sg.Button("清空账单", size=(10, 1), button_color=("white", "#FF9800")),
        sg.Button("导出数据", size=(10, 1), button_color=("white", "#2196F3")),
    ]
    
    Layout = [
        [sg.Text("个人记账本", font=("微软雅黑", 20, "bold"), 
                 justification="center", expand_x=True, pad=(0, 10))],
        [sg.HorizontalSeparator()],
        stats_frame,
        [sg.VPush()],
        [table_frame],
        [sg.VPush()],
        [input_frame],
        [sg.Push()] + button_frame + [sg.Push()],
    ]
    
    windows = sg.Window("个人记账本", 
                        Layout, return_keyboard_events=True, 
                        size=(650, 580), element_justification="center")
    while True:
        event, values = windows.read()

        if event == None:
            break

        if event.startswith("Return") or event == "\r":
            focused = windows.find_element_with_focus()
            if focused is not None:
                if focused.Key == "-content-":
                    windows["-amount-"].set_focus()
                elif focused.Key == "-amount-":
                    windows["-content-"].set_focus()
        
        if event == "确认提交":
            content = values["-content-"]
            amount = float(values["-amount-"])
            for k,v in values.items():
                if v == True:
                    cla = k
                    addData(content, amount, cla)
                    list = showData(readData())
                    sum_in, sum_out, sum_all = sum()
                    windows["-show-"].update(list)
                    windows["-in-"].update(f"￥{sum_in}")
                    windows["-out-"].update(f"￥{sum_out}")
                    windows["-balance-"].update(f"￥{sum_all}")
                    windows["-content-"].update("")
                    windows["-amount-"].update("")
                    windows["-content-"].set_focus()
        
        if event == "删除":
            selected = values["-show-"]
            if selected:
                index = selected[0]
                if deleteData(index):
                    list = showData(readData())
                    sum_in, sum_out, sum_all = sum()
                    windows["-show-"].update(list)
                    windows["-in-"].update(f"￥{sum_in}")
                    windows["-out-"].update(f"￥{sum_out}")
                    windows["-balance-"].update(f"￥{sum_all}")
            else:
                sg.popup("请先选中要删除的账单项目！")
        
        if event == "清空账单":
            if sg.popup_yes_no("确定要清空所有账单吗？", title="确认") == "Yes":
                with open(r"data.txt", "w", encoding="utf-8") as f:
                    f.write("[]")
                windows["-show-"].update([])
                windows["-in-"].update("￥0")
                windows["-out-"].update("￥0")
                windows["-balance-"].update("￥0")
                sg.popup("账单已清空！")
        
        if event == "导出数据":
            filepath = sg.popup_get_file("保存到", save_as=True, default_extension=".txt", 
                                         file_types=(("Text Files", "*.txt"), ("All Files", "*.*")))
            if filepath:
                import shutil
                shutil.copy("data.txt", filepath)
                sg.popup(f"已导出到: {filepath}")

    windows.close()

main()
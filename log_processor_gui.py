# -*- coding: utf-8 -*-
"""
Created on 2024-07-07 13:12:00

@title: Log Processor GUI.
@author: Guo Sibei
@contact: guosibei@mail.ustc.edu.cn
@version: 1.0
@description: GUI simulator
"""


from log_processor_functions import *

# ------------------ Operation dicts ------------------
basic_info = {
    'Number of atoms': lambda file_path: get_n_atom(file_path),
    'Log termination type': lambda file_path: get_termination_type(file_path),
    'Last frame coordinates': lambda file_path: std_coords_last_frame(file_path),
}

energy = {
    'Enthalpy': lambda file_path: read_enthalpy(file_path),
    'Enthalpy correction': lambda file_path: read_enthalpy_correction(file_path),
    'Single point energy': lambda file_path: single_point_energy(file_path),
}

spectra = {
    'Frequency': lambda file_path: read_freq(file_path),
    'IR intensity': lambda file_path: read_ir_inten(file_path),
    'Raman activity': lambda file_path: read_raman_act(file_path),
    #'Normal coordinate': lambda file_path: read_normal_coords(file_path),
    'Force constant': lambda file_path: read_frc_const(file_path),
    'Reduced mass': lambda file_path: read_red_mass(file_path),
    'NMR shielding': lambda file_path: read_NMR_iso(file_path)
}

operations = {
    'Basic information': basic_info,
    'Energy': energy,
    'Spectra': spectra
    }

# ------------------ tkinter for GUI ------------------
import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD

# Main window
root = TkinterDnD.Tk()
root.title("Operation Selector")

# Label and entry
title_label = tk.Label(root, text="Drag and Drop a .log or .out File Here or Enter File Path:")
title_label.pack()

title_entry = tk.Text(root, height=10, width=50)
title_entry.pack()


def handle_drop(event):
    file_path = event.data
    if file_path.endswith('.log') or file_path.endswith('.out'):
        # Update input contents
        title_entry.delete("1.0", tk.END)
        title_entry.insert(tk.END, file_path)
def execute_operation():
    selected_type = operation_type.get()
    selected_operation_name = selected_operation.get()
    operation_function = operations[selected_type][selected_operation_name]
    file_path = title_entry.get("1.0", tk.END).strip()
    result = operation_function(file_path)
    #log_lines = title_entry.get("1.0", tk.END).splitlines()
    #result = operation_function(log_lines)
    result_text.delete("1.0", tk.END)
    result_text.insert(tk.END, result)

# Drag drop event
title_entry.drop_target_register(DND_FILES)
title_entry.dnd_bind('<<Drop>>', handle_drop)

# Update operations
def update_operations(*args):
    selected_type = operation_type.get()
    if selected_type in operations:
        operation_menu["menu"].delete(0, "end")
        for operation in operations[selected_type]:
            operation_menu["menu"].add_command(label=operation, command=tk._setit(selected_operation, operation))
        selected_operation.set(list(operations[selected_type].keys())[0])


# Selection menu 1
operation_type = tk.StringVar(root)
operation_type.set(list(operations.keys())[0])  # 默认值
operation_type.trace("w", update_operations)
operation_type_menu = tk.OptionMenu(root, operation_type, *operations.keys())
operation_type_menu.pack()

# Selection menu 2
selected_operation = tk.StringVar(root)
selected_operation.set(list(operations[operation_type.get()].keys())[0])  # 默认值
operation_menu = tk.OptionMenu(root, selected_operation, *operations[operation_type.get()].keys())
operation_menu.pack()

# Execute
execute_button = tk.Button(root, text="Execute", command=execute_operation)
execute_button.pack()

# Result
result_text = tk.Text(root, height=10, width=50)
result_text.pack()


root.mainloop()

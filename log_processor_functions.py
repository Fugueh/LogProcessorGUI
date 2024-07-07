# -*- coding: utf-8 -*-
"""
Created on 2024-07-07 13:12:00

@title: Gaussian log processor functions for GUI.
@author: Guo Sibei
@contact: guosibei@mail.ustc.com
@version: 1.0
@description: Extract data from Gaussian output .log/ .out file.
"""

import re
import numpy as np
import pandas as pd
from io import StringIO

def array_to_csv_string(array):
    df = pd.DataFrame(array)
    csv_str_io = StringIO()
    df.to_csv(csv_str_io, header=False, index=False)
    csv_string = csv_str_io.getvalue()
    return csv_string

#------------------ Log lines ------------------

def read_log_lines(file_path):
    with open(file_path, 'r') as f:
        log_lines = f.readlines()
    return log_lines

def get_n_atom(file_path):
    log_lines = read_log_lines(file_path)
    for line in log_lines:
        if re.search('NAtoms=', line):
            return int(line.split()[1])
        
#------------------ Normal\Error termination ------------------
def Normal_termination_or_not(file_path):
    log_lines = read_log_lines(file_path)
    if log_lines and re.search('Normal termination', log_lines[-1]):
        return True
    else:
        return False

def Error_termination_type(file_path):
    '''Return the type of the error termination.
       Including normal Gaussian links(e.g. l101, l502, l9999, etc.) errors
       and other abnormal error terminations(e.g. missing part of the file).
    '''
    log_lines = read_log_lines(file_path)
    if Normal_termination_or_not(file_path):
        return False
    normal_error = False
    for line in log_lines[::-1]:
        if re.search('Error termination',line):
            if re.search(r'l\d{1,4}/.exe', line):
                normal_error = True
                return re.search(r'l/d{1,4}', line).group()
    if not normal_error:
        return 'abnormal'

def get_termination_type(file_path):
    if Normal_termination_or_not(file_path):
        return 'Normal termination'
    else:
        return Error_termination_type(file_path)


#------------------ SCF iters ------------------
def single_point_energy(file_path):
    '''Return an ndarray(dtype:float64) of all single-point energies.
       Unit: Hartree/Particle.
    '''
    log_lines = read_log_lines(file_path)
    scf_energies = []
    for line in log_lines:
        if re.search('SCF Done:', line):
            scf_energies.append(float(line.split()[4]))
    result = np.array(scf_energies)
    result = array_to_csv_string(result)
    return result

#------------------ Standard orientation ------------------
def read_log_lines(file_path):
    with open(file_path,'r') as f:
        log_lines = f.readlines()
    return log_lines

def get_std_coords(file_path):
    '''This function reads a log file, return atom corrdinates
       of all optimization frames(Standard orientations).
       Returned type: ndarray, n(frames)*n(atoms)*5. 5=(order + Atomic number + xyz)
    '''
    log_lines = read_log_lines(file_path)
    opt_frames = []
    frame_coords = []
    begin_std = False
    n_split = 0
    for line in log_lines:
        if re.search('Standard orientation', line):
            begin_std = True
            n_split = 0
        else:
            if begin_std:
                if re.search('------------------------------',line):
                    n_split += 1
                if begin_std and n_split == 2:
                    frame_coords.append(line.split()[:2]+line.split()[3:])
            if begin_std and n_split == 3:
                opt_frames.append(frame_coords[1:])
                begin_std = False; n_split = 0; frame_coords = []
    return np.array(opt_frames).astype(str)


def std_coords_first_frame(file_path):
    '''Read a log file, return the last frame of 'Standard orientations'(atom corrdinates) of the opt log file.
        n(atoms)*5 array of str. 0-line number; 1-Atomic number; [2:5]-xyz coordinates.
    '''
    opt_frames = get_std_coords(file_path)
    first_frame = opt_frames[0][:, 1:]
    first_frame = [' '.join(frame) for frame in first_frame]
    first_frame = '\n'.join(first_frame)
    return first_frame

def std_coords_last_frame(file_path):
    '''Read a log file, return the last frame of 'Standard orientations'(atom corrdinates) of the opt log file.
        n(atoms)*5 array of str. 0-line number; 1-Atomic number; [2:5]-xyz coordinates.
        When writing Gaussian input file, just call opt_frames[1:]
    '''
    opt_frames = get_std_coords(file_path)
    last_frame = opt_frames[-1][:, 1:]
    last_frame = [' '.join(frame) for frame in last_frame]
    last_frame = '\n'.join(last_frame)
    return last_frame

def read_enthalpy(file_path):
    '''From the Freq-type calculation output read the thermal Enthalpies
        (E_elec+E_0+enthalpy_correction)
        Unit: Hartree/Particle.
    '''
    log_lines = read_log_lines(file_path)
    for line in log_lines:
        if re.search('Sum of electronic and thermal Enthalpies', line):
            return(float(re.search(r'-\d{1,5}.\d{1,10}',line).group()))

def read_enthalpy_correction(file_path):
    '''From the Freq-type calculation output read the thermal enthalpy correction
        Unit: Hartree/Particle.
    '''
    log_lines = read_log_lines(file_path)
    for line in log_lines:
        if re.search('Thermal correction to Enthalpy=', line):
            return(float(re.search(r'\d{1,5}.\d{1,10}',line).group()))

def read_freq(file_path):
    '''Return a list of vibration frequencies. 
       ndarray, dtype: float64, Unit: (cm**-1)
    '''
    log_lines = read_log_lines(file_path)
    freq = []
    for line in log_lines:
        if re.search('Frequencies',line):
            line = line.split()
            freq.extend([float(x) for x in line[2:]])
    result = np.array(freq)
    result = array_to_csv_string(result)
    return result

def read_red_mass(file_path):
    '''Reduced mass of normal modes (harmonic approximation). 
       ndarray[n(normal modes)], dtype: float64, Unit: (AMU)
    '''
    log_lines = read_log_lines(file_path)
    red_masses = []
    for line in log_lines:
        if re.search('Red. masses',line):
            line = line.split()
            red_masses.extend([float(x) for x in line[3:]])
    result = np.array(red_masses)
    result = array_to_csv_string(result)
    return result

def read_frc_const(file_path):
    '''Vibration frequenciesof normal modes (harmonic approximation). 
       ndarray[n(normal modes)], dtype: float64, Unit: (mDyne/A)
    '''
    log_lines = read_log_lines(file_path)
    frc_consts = []
    for line in log_lines:
        if re.search('Frc consts',line):
            line = line.split()
            frc_consts.extend([float(x) for x in line[3:]])
    result = np.array(frc_consts)
    result = array_to_csv_string(result)
    return result

def read_ir_inten(file_path):
    '''IR intensities of normal modes (harmonic approximation).  
       ndarray[n(normal modes)], dtype: float64, Unit: (KM/Mole)
    '''
    log_lines = read_log_lines(file_path)
    ir_inten = []
    for line in log_lines:
        if re.search(' IR Inten',line):
            line = line.split()
            ir_inten.extend([float(x) for x in line[3:]])
    result = np.array(ir_inten)
    result = array_to_csv_string(result)
    return result

def read_raman_act(file_path):
    '''Raman scattering activities of normal modes (harmonic approximation). 
       ndarray[n(normal modes)], dtype: float64, Unit: (A**4/AMU)
    '''
    log_lines = read_log_lines(file_path)
    raman_act = []
    for line in log_lines:
        if re.search(' Raman Activ',line):
            line = line.split()
            raman_act.extend([float(x) for x in line[3:]])
    result = np.array(raman_act)
    result = array_to_csv_string(result)
    return result

def read_NMR_iso(log_file):
    log_lines = read_log_lines(log_file)
    n_atom = get_n_atom(log_file)
    iso_shielding = []
    for line in log_lines:
        if re.search('Isotropic = ',line):
            iso_shielding.append(float(line.split()[4]))
    result = np.array(iso_shielding)
    result = array_to_csv_string(result)
    return result
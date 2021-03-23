#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 11:36:48 2018

@author: fs
"""

import re

def parseDQDIMACSFile(filename):
  with open(filename) as file:
    return parseDQDIMACS(file)

def parseDQDIMACS(in_stream):
  lines = in_stream.readlines()
  # Strip comment lines
  lines = [line for line in lines if not line.startswith('c')]
  
  # Read header
  [header] = [line for line in lines if line.startswith('p')]
  _, _, nr_vars_string, nr_clauses_string = header.split()
  nr_vars = int(nr_vars_string)
  
  # Read quantifier prefix
  dependency_dict = {}
  prefix_lines = [line for line in lines 
                  if line.startswith('a') or line.startswith('e')]
  universals = []
  for line in prefix_lines:
    line_split = line.split()
    assert(line_split[-1] == '0')
    variables = [int(v_string) for v_string in line_split[1: -1]]
    assert all([v <= nr_vars for v in variables])
    if line.startswith('a'):
      universals += variables
    else:
      for e in variables:
        dependency_dict[e] = list(universals)
  
  # Read explicit dependency lines
  existential_lines = [line for line in lines if line.startswith('d')]
  for line in existential_lines:
    line_split = line.split()
    assert(line_split[-1] == '0')
    e = int(line_split[1])
    assert(e <= nr_vars)
    dependencies = [int(u_string) for u_string in line_split[2:-1]]
    assert all([u <= nr_vars for u in dependencies])
    dependency_dict[e] = dependencies
  
  # Read clauses
  clause_lines = [line for line in lines if not line.startswith('p') and
                  not line.startswith('a') and
                  not line.startswith('e') and
                  not line.startswith('d')]
  # assert len(clause_lines) == nr_clauses
  clauses = []
  for clause_line in clause_lines:
    line_split = clause_line.split()
    if line_split:
      assert line_split[-1] == '0', clause_line
      literals = [int(l_string) for l_string in line_split[:-1]]
      assert all([abs(l) <= nr_vars for l in literals])
      clauses.append(literals)
  return nr_vars, universals, dependency_dict, clauses

def parseModelFile(filename): 
  with open(filename) as file:
    return parseModel(file)
  
def parseModel(in_stream):
  lines = in_stream.readlines()
  [header] = [line for line in lines if line.startswith('p')]
  _, _, nr_vars_string, nr_clauses_string = header.split()
  nof_vars = int(nr_vars_string)
  model_for_variable=None
  model = {}
  clauses = []
  for line in lines:
    if  line.startswith('p') :
      continue
    if  line.startswith('c') :
      x=re.findall("c Model for variable (\d+)", line)
      if len(x)>0:
        model_for_variable=int(x[0])
        if model_for_variable not in model:
          model[model_for_variable] = []
      continue
    if model_for_variable is None:
      return model,clauses
    line_split = line.split()
    if line_split:
      assert line_split[-1] == '0', line
      literals = [int(l_string) for l_string in line_split[:-1]]
      assert all([abs(l) <= nof_vars for l in literals])
      model[model_for_variable].append(literals)
      clauses.append(literals)
  return model,clauses
  
  
  
  
  
  
  
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jun  3 21:39:16 2020

@author: fs
"""

def maxVarIndex(clause_list):
  return max([abs(l) for c in clause_list for l in c], default=0)

def renameLiteral(l, renaming):
  return renaming.get(l, l) if l > 0 else -renaming.get(abs(l), abs(l))

def renameClause(clause, renaming):
  return [renameLiteral(l, renaming) for l in clause]

def renameFormula(clauses, renaming):
  return [renameClause(clause, renaming) for clause in clauses]

def equality(lit1, lit2, switch):
  return [[-switch, lit1, -lit2], 
          [-switch, -lit1, lit2]]
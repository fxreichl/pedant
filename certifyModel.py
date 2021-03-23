#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import argparse
from pysat.solvers import Cadical

from checkModel import checkModelQBF
from dqbf_parse import parseDQDIMACSFile,parseModelFile

from DefinabilityChecker import DefinabilityChecker



def checkModel(filename_formula,filename_model,check_defined=True,check_consistency=True,use_extended_dependencies=True) :
  """
  Checks if the canditate-model given by <filename_model> certifies the trueness
  of the DQBF given by <filename_formula>.
  
  Parameters
  ----------
  filename_formula : string
      The name of a DQDIMACS file.
      Contains the DQBF that shall be certified.
  filename_model : string
      The name of a DIMACS file.
      Contains the candidate-model.
      Additional to the syntactic requirements for a DIMACS file we require that the
      file contains for each existential variable from <filename_formula> a line
      "c Model for variable <var>."
      The clauses following such a line for a variable var up the next such line,
      respectively the end of the file give the CNF encoding of the caditate-model
      for the variable var      
  check_defined : bool
      If true check if each existential from <filename_formula> is defined
      by its dependencies in the formula given by <filename_model>.
      This option is necessary to certify that the candidate-model is indeed a model
      for the DQBF given by <filename_formula>.

      Note: Even if the given candidate model is actually not a model
      it can still certify the trueness of the given DQBF.

      Reference Definition:
      Friedrich Slivovsky: Interpolation-based semantic gate extraction and its applications to QBF preprocessing.
      In CAV (1). Lecture Notes in Computer Science, vol. 12224,
      pp. 508–528. Springer (2020)
  check_consistency : bool
      If true check if for each assignment for the existential variables from <filename_model>
      there is an assignment for the universal variables from <filename_model>
      such that the combined assignment satisfies the candidate-model.

      Note: If this option is set to false then the given DQBF can be false
      even if this method returns true. But if the method returns false
      then the candidate-model does not certify the trueness of the given DQBF
      (remember if <check_defined>=true then the function also returns false
      if there is an undefined existential)
  use_extended_dependencies : bool
      If true, the extended dependencies are used for the check for the occuring variables
      and if check_defined=true it is checked whether the variables are defined with respect
      to the extended dependencies.
  
  Returns
  -------
  True, if the given candidate-model passes all checks.

  """
  _, universals_variables, dependency_dict, matrix = parseDQDIMACSFile(filename_formula) 
  # _, _, _, model = parseDQDIMACSFile(filename_model)
  model,model_clauses=parseModelFile(filename_model)
  existential_variables = list(dependency_dict) 
  if use_extended_dependencies:
    dependencies=computeExtendedDependencies(dependency_dict)
  else:
    dependencies=dependency_dict
  variables_to_consider=universals_variables + existential_variables
  for e in existential_variables:
    if e in model:
      #The candidate-model may contain additional variables as those contained in the matrix.
      #Thus the check shall pass if additional variables occur in the candidate-model --
      #as long as those variables do not occur in the matrix
      variablesOK, false_variables = check_occuring_variables(model[e],variables_to_consider,dependencies[e]+[e])
      if not variablesOK:
        print("The given model for variable {0} contains the invalid variables: {1}.".format(e,false_variables))
        return False 
  #Additional sanity check. If the candidate-model is UNSAT it is necessarily inconsistent.
  #Thus it does not certify that the given DQBF is true.
  model_checker = Cadical(bootstrap_with=model_clauses)
  if not model_checker.solve() :
    print("Model inconsistent")
    return False
  if check_consistency :
    consistent = consistency_checker(model_clauses,universals_variables,existential_variables)
    if not consistent :
      print("Model inconsistent")
      # print("Certificate: {}".format(certificate))
      return False  
  if check_defined:
    definability_checker = DefinabilityChecker(model_clauses, existential_variables)
    for e in existential_variables :
      depends_on = dependencies[e]
      is_defined, counterexample = definability_checker.checkDefinability(depends_on, e)
      if not is_defined:
        print("The model does not uniquely define variable: {}".format(e))
        return False                                                        
  model_ok = check_matrix(model_checker,matrix)
  if model_ok:
    return True
  else:
    model = model_checker.get_model()
    print("Universal assignment: {}".format([l for l in model if abs(l) in universals_variables]))
    print("Existential assignment: {}".format([l for l in model if abs(l) in existential_variables]))
  return model_ok



def consistency_checker(model,universals,existentials):
  """
  Checks if for each assignment to <universals> there is an
  assignment to <existentials> such that <model> is satisfied
  
  Parameters
  ----------
  model : list of list of integers
      The model to check.
      The variables in <model> have to be contained in the 
      union of <universals> and <existentials>.
  universals : list of integers
      The universal variables.
  existentials : list of integers
      The existential variables.
  
  Returns
  -------
  True if foreach assignment for <universals> there is an assignment for 
  <existentials> such that <model> is satisfied by the combined assignment.

  """
  universal_set=set(universals)
  existential_set=set(existentials)
  #Additionally to the universal and existential variables the model may
  #contain additional auxiliary variables -- e.g. for setting default values.
  #We consider these variables such as the existential variables.
  auxiliary_variables_in_model={abs(l) for clause in model for l in clause 
      if (not abs(l) in universal_set) and (not abs(l) in existential_set)}
  existential_set = existential_set.union(auxiliary_variables_in_model)
  result, certificate = checkModelQBF(model, universal_set, existential_set)
  return result


def check_matrix(solver,matrix):
  """
  Checks if the negation of <matrix> is 
  satisfiable with respect to the clauses in <solver>
  
  Parameters
  ----------
  solver : pysat solver
      The SAT solver that shall perform the SAT check
  matrix : list of list of integers
      The formula that shall be checked.
  
  Returns
  -------
  True if (C and not matrix) is unsatisfiable, where C shall 
  denote the clauses in <solver>.

  """
  model_validated = True
  #To check that the negation of the given formula is UNSAT under the clauses 
  #in the solver we check if the negation of each clause is UNSAT under these clauses.
  for clause in matrix:
    negated_claus=[-l for l in clause]
    model_validated = not solver.solve(negated_claus)
    if not model_validated:
      print("Falsified Clause: {}".format(clause))
      return False
  return True
  


def check_occuring_variables(formula,variables_to_consider,allowed_variables) :
  """
  Checks if the intersection of the variables in <formula> with the variables
  in <variables_to_consider> is contained in <allowed_variables>
  
  Parameters
  ----------
  formula : list of list of integers
      The formula to consider.
  variables_to_consider : list of integers
      Those variables in <formula> that shall be considered.
  allowed_variables : list of integers
      Must be contained in <variables_to_consider>. 
      Gives the subset of <variables_to_consider> that may occur in <formula>
  
  Returns
  -------
  True if the intersection of the variables in <formula> with <variables_to_consider>
  is contained in <allowed_variables>

  """
  variable_set=set(allowed_variables)
  for clause in formula :
    variables_in_clause = {abs(l) for l in clause if abs(l) in variables_to_consider}
    if not variables_in_clause <= variable_set:
      return False, [v for v in variables_in_clause if not v in variable_set]   
  return True, []


def computeExtendedDependencies(dependencies):
  """
  Computes the extended dependencies for the given dependencies.
  The extended dependencies are defined as follows:
  In the following let E denote the set of existential variables 
  (i.e. the keys of <dependencies>)
  ext_dep(e):=dep(e) union {v in E | dep(v) < dep(e) or (dep(e) == dep(v) and v < e)}
  
  Parameters
  ----------
  dependencies : dictionary
      The dependencies to consider
  
  Returns
  -------
  A dictionary representing the extended dependencies

  """
  dependency_sets = {v:set(dep) for v,dep in dependencies.items()}
  extended_dependencies = {}
  for v1, dep1 in dependencies.items():
    extended_dependencies[v1]=dep1
    dependency_set=dependency_sets[v1]
    for v2 in extended_dependencies.keys():
      if v1 == v2:
        continue
      dep2=dependency_sets[v2]
      if dependency_set <= dep2:
        if len(dependency_set) == len(dep2):
          if v1 < v2:
            extended_dependencies[v2] = extended_dependencies[v2] + [v1]
          else:
            extended_dependencies[v1] = extended_dependencies[v1] + [v2]
        else:
          extended_dependencies[v2] = extended_dependencies[v2] + [v1]
      elif dep2 < dependency_set:
        extended_dependencies[v1] = extended_dependencies[v1] + [v2]
  return extended_dependencies

  


if __name__ == "__main__":
  """
  We assume that the DQBF given by <filename_formula> was checked by the associated DQBF solver and that the solver returned true.
  Moreover, we assume that "filename_model" represent the file containing the canditate-model that was generated for <filename_formula>.
  """
  parser = argparse.ArgumentParser(description="Pedant DQBF Solver")  
  parser.add_argument('filename_formula', metavar='FORMULA',help='Represents a DQDIMACS file representing the DQBF of interest.')
  parser.add_argument('filename_model', metavar='MODEL', help='Represents a DIMACS file representing the candidate-model.') 
  parser.add_argument('--check-def', action='store_true', help='If true: the defindness of the existentials from FORMULA in MODEL is checked.')
  parser.add_argument('--check-cons', action='store_true', help='If true MODEL is checked for consistency.')
  parser.add_argument('--std-dep', action='store_true', help='If true MODEL may not use variables from the extended dependencies.')
  args = parser.parse_args()
  is_model=checkModel(args.filename_formula,args.filename_model,args.check_def,args.check_cons,not args.std_dep)
  if is_model :
    print("Model validated!")
    sys.exit(0)
  else :
    # print("Model invalid!")
    sys.exit(1)


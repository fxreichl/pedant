# SAT 2021 Submission 50 Supplementary Material

The contents of this repository are intended for reviewing purposes only. It provides

1. Solver logs for the experiments described in the submission, along with an R markdown report that shows how tables and figures in the paper were generated (subfolder [logs](https://github.com/fxreichl/pedant/tree/main/logs)).
2. A static binary (Linux 64-bit) of the DQBF solver **Pedant**, see the documentation below.

## Pedant

Pedant is a solver for dependency quantified boolean formulas (DQBFs) based on interpolation-based definition extraction.

### Usage

This repository provides a statically built binary of Pedant.
On a 64-Bit Linux system it suffices to download the binary and call it with:
```
./pedant
```
To print a help message use:
```
pedant --help
```

Pedant expects the input to be given in DQDIMACS format.
DQDIMACS is based on [QDIMCACS](http://www.qbflib.org/qdimacs.html). 
The only difference between DQDIMACS and QDIMACS is that the prefix of a DQDIMACS file may contain lines starting with the character ***d***.
A line starting with ***d*** introduces an existential variable and explicitly gives its dependencies. In the following we give a simple example of a DQDIMACS file:
```
p cnf 4 2
a 1 2 0
d 3 1 0
d 4 2 0
1 -3 0
2 3 4 0
```
In the above example we introduce universal variables 1 and 2, an existential variable 3 that depends on 1 and an existential variable 4 that depends on 2.

A file ```input``` in DQDIMACS format can be checked by the solver with:
```
./pedant input
```
The solver will give one of the following outputs:
- It will print ```SATISFIABLE``` and exit with code ```10``` if the given formula is true.
- It will print ```UNSATISFIABLE``` and exit with code ```20``` if the given formula is false.
- It will print ```UNKNOWN``` and exit with code ```0``` if it could not conclude a result. This for example happens if the solver receives an abort signal.

Additionally, the program can compute certificates for true DQBFs.
Given a DQDIMACS file ```input``` Pedant writes a certificate for the given formula to a file ```model``` by calling:
```
./pedant input model
```
The solver will print the same messages and exit with the same code as in the previous example.
Additionally, if the solver exited with code ```10``` a certificate in DIMACS format with special comment lines is written to the file ```model```.
Such a certificate file contains comment lines to associate clauses correspond to existential variables. For a variable ```var``` such a comment line has the shape:
```
c Model for variable var.
```
All clauses between the comment for a variable ```var``` and the next comment line, respectively the end of the file are associated to the variable ```var```.

To validate a certificate we provide the python script ```certifyModel.py```. The script can be called by:
```
./certifyModel.py formula model [Options]

Inputs
formula The DQDIMACS file of interest.
model   The generated certificate for formula.
Options
  --check-def  Check if the certificate actually gives a model for the DQBF. 
    Note: If this option is set and the script returns false then this 
    does not mean that the result of pedant was incorrect. 
    Instead it only means that the certificate is not a model.
  --check-cons  Additional sanity check that verifies if for each 
    assignment to the universal variables there is an assignment 
    to the existential variables such that the combined assignment 
    satisfies the certificate.
  --std-dep  Use the "standard" dependencies, instead of the 
    extended dependencies for the check.

Return 
  0 if the certificate could be validated.
  1 if the certificate could not be validated.
```
This script requires [PySAT](https://pysathq.github.io/) to be installed.
To use the option ```--check-cons``` the 2QBF solver [CADET](https://github.com/MarkusRabe/cadet) has to be installed.

Additionally, we provide a bash script ```pedant_check``` that first calls Pedant and then automatically calls ```certifyModel.py``` in case the given formula was true. 
The script can be called by:
```
./pedant_check formula model

Inputs
formula The DQDIMACS file of interest.
model   The file to which the certificate shall be written.

Return
  0   if pedant returned true (10) but the certificate could not be validated 
      or if pedant returns unknown.
  10  if pedant returned true (10) and the certificate could be validated.
  20  if pedant returned false (20).

```

### Example

This repository contains the file ```bloem_mult2.dqdimacs```. 
This file is taken from the [QBFEVAL'20](http://www.qbflib.org/QBFEVAL_20_DATASET.zip) benchmarkset.
We use this file to illustrate the usage of Pedant:
```
./pedant bloem_mult2.dqdimacs model
```
This will print ```SATISFIABLE```. Next we can validate the certificate by:
```
./certifyModel.py bloem_mult2.dqdimacs model
```
This will print ```Model validated!```.






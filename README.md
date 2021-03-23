# pedant
Pedant is a state of the art solver for dependency quantified boolean formulas (DQBFs). 

## Usage

This repository provides a statically built binary of pedant.
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
The only difference between DQDIMACS and QDIMACS is that the prefix of a DQDIMACS file may contain lines starting with the character "d".
A line starting with "d" introduces an existential variable and explicitly gives its dependencies. In the following we give a simple example of a DQDIMACS file:
```
p cnf 4 2
a 1 2 0
d 3 1 0
d 4 2 0
1 -3 0
2 3 4 0
```
In the above example we introduce universal variables 1 and 2, an existential variable 3 that depends on 1 and an existential variable 4 that depends on 2.

Given a file ```input``` in the DQDIMACS format pedant can be applied to the input by calling:
```
./pedant input
```
If the given formula is true the program will print ```SATISFIABLE``` and exit with code ```10```.
If the formula is false pedant will print ```UNSATISFIABLE``` and and exit with code ```20```.
If pedant could not compute an answer the programm will print ```UNKNOWN``` and exit with code ```0```.
Additionally, the program can compute certificates for true DQBFS.
Given a DQDIMACS file ```input``` pedant writes a certificate for the given formula to a file ```model``` by calling:
```
./pedant input model
```
Pedant generates certificates in DIMACS format with special comment lines. Comment lines are used to indicate to which existential variable clauses are associated. For a variable ```var``` the comments have the shape:
```
c Model for variable var.
```
All clauses between the comment for a variable ```var``` and the next comment line, respectively the end of the file are associated to the variable ```var```.

To validate a certificate we provide the python script ```certifyModel.py```. The scipt can be called by:
```
./certifyModel.py formula model [Options]

Inputs
formula The DQDIMACS file of interest
model   The generated certificate for formula
Options
  --check-def   Check if the certificate actually gives a model for the DQBF. 
    Note: If this option is set and the script returns false then this 
    does not mean that the result of pedant was false. 
    Instead it only means that the certificate is not a model.
  --check-cons  Additional sanity check that verifies if for each 
    assignment to the universal variables there is an assignment to the 
    existential variables such that the combined assignment satisfies the certificate.
  --std-dep Use the "standard" dependencies, instead of the 
    extended dependencies for the check.

Return 
  0 if the certificate could be validated
  1 if the certificate could not be validated
```

Additionally, we provide a bash script ```pedant_check``` that first calls pedant and then automatically calls ```certifyModel.py``` in case the given formula was true. 
In order to run this script [PySAT](https://pysathq.github.io/) must be installed.
The scipt can be called by:
```
./pdenat_check formula model

Inputs
formula The DQDIMACS file of interest
model   The generated certificate for formula

Return
  0   if pedant returned true (10) but the certificate could not be validated 
      or if pedant returns unknown
  10  if pedant returned true (10) but the certificate could be validated.
  20  if pedant returned false (2)

```

## Example

This repository contains the file ```bloem_mult2.dqdimacs```. 
This file is taken from the [QBFEVAL'20](http://www.qbflib.org/QBFEVAL_20_DATASET.zip) benchmarkset.
We use this file to illustrate the usage of pedant:
```
./pedant bloem_mult2.dqdimacs model
```
This will print ```SATISFIABLE```. Next we can validate the certificate by:
```
./certifyModel.py bloem_mult2.dqdimacs model
```
This will print ```Model validated!```.






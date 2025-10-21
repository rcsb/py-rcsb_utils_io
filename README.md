# RCSB Python I/O Utility Classes

[![Build Status](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_apis/build/status/rcsb.py-rcsb_utils_io?branchName=master)](https://dev.azure.com/rcsb/RCSB%20PDB%20Python%20Projects/_build/latest?definitionId=13&branchName=master)

## Introduction

This module contains a collection of utility classes for performing I/O operations on common
file formats encountered in the PDB data repository.

### Installation

Download the library source software from the project repository:

```bash

git clone --recurse-submodules https://github.com/rcsb/py-rcsb_utils_io.git

```

Optionally, run test suite (Python versions 2.7, and 3.9) using
[tox](http://tox.readthedocs.io/en/latest/example/platform.html):

```bash
tox
```

Installation is via the program [pip](https://pypi.python.org/pypi/pip).

```bash
pip install rcsb.utils.io

or from the local repository:

pip install .
```

### Usage

The `MarshalUtil` offers an easy way for reading in and writing out files in various formats, including `CSV`, `JSON`, `pickle`, `mmCIF`, `bcif` (BinaryCIF), `fasta `, and "list" files (plain text file in which each row is a list item).

#### Reading files

Let's say you have a JSON file, `"data.json"`. You can read this in by:
```python
from rcsb.utils.io.MarshalUtil import MarshalUtil
mU = MarshalUtil(workDir=".")

dataD = mU.doImport("data.json", fmt="json")
```

The same method works even if the file is compressed (e.g., `"data.json.gz"`):
```python
dataD = mU.doImport("data.json.gz", fmt="json")
```

**_Note that this automatic handling of compressed `gzip` files applies to any type of input format._**

You can also import remote files directly from the command line, e.g.:
```python
dataD = mU.doImport("https://files.rcsb.org/pub/pdb/holdings/current_file_holdings.json.gz", fmt="json")
```

To read in a `pickle` file, `"data.pic"`:
```python
from rcsb.utils.io.MarshalUtil import MarshalUtil
mU = MarshalUtil()

dataD = mU.doImport("data.pic", fmt="pickle")
```

To read in and parse an `mmCIF` file, `"4hhb.cif.gz"`:
```python
from rcsb.utils.io.MarshalUtil import MarshalUtil
mU = MarshalUtil()

# Read all data containers from the mmCIF file into `dataContainerList`
dataContainerList = mU.doImport("https://files.rcsb.org/pub/pdb/data/structures/divided/mmCIF/hh/4hhb.cif.gz", fmt="mmcif")

# Get the first dataContainer (in most cases, there will only be one container in the file)
dataContainer = dataContainerList[0]

# Print the name of the container
eName = dataContainer.getName()
print(eName)

# Get the list of categories
catNameList = dataContainer.getObjNameList()
print(catNameList)

# Iterate over all the categories and attributes and store them in a new dictionary 
cifDataD = {}
for catName in catNameList:
    if not dataContainer.exists(catName):
        continue
    dObj = dataContainer.getObj(catName)
    for ii in range(dObj.getRowCount()):
        dD = dObj.getRowAttributeDict(ii)
        cifDataD.setdefault(eName, {}).setdefault(catName, []).append(dD)
```

**_For more examples, see [testMarshallUtil.py](https://github.com/rcsb/py-rcsb_utils_io/blob/master/rcsb/utils/tests-io/testMarshallUtil.py)._**

#### Writing files

You can use the `MarshalUtil` to write out the following data structures into the corresponding file formats:
```
 Object            |  Output `fmt`
-------------------------------------
 list              |  list
 dict              |  json or pickle
 DataContainerList |  mmcif or bcif
```

For example, if you have a dictionary, `dataD`, you can export it via:
```python
from rcsb.utils.io.MarshalUtil import MarshalUtil
mU = MarshalUtil()

dataD = {"name": "John Doe", "age": "33"}

mU.doExport("data.json", dataD, fmt="json", indent=2)

# Or, to export and compress as gzip:
mU.doExport("data.json.gz", dataD, fmt="json", indent=2)
```

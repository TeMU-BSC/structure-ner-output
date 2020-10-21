# Structure NER tagger output

## Description

- Input: Named Entity Recognition (NER) output

- Steps: 
	1. Parse NER output
	2. Remove unused entities and rename undescriptive ones
	3. Harmonize negation and uncertainty information
	4. Normalize text span: lowercase, remove extra whitespaces, remove punctuation and remove accents
	5. Remove exact duplicated entities: same text position in same filename and with the same entity label
	6. Count term and document frequency of every normalized span
	7. Compute lemma from original text span (lowercased and without the extra whitespaces)
	8. Map the original text span (lowercased and without the extra whitespaces) to Snomed ID
	9. Drop duplicates based on span normalized and filename

- Output: Structured and normalized information

EXTRA: a posteriori we may map the Snomed IDs to UMLS CUI.

## Installation Guide

This repo is tested with python 3.6.4 with valid versions of pandas and numpy 
In addition, you need to install first TEMUnormalizer and SPACCC-POS_Tagger (which needs Docker). 

### Prerequisites

Prerrequisites installation steps: 

1. Install and configure Docker: https://www.docker.com/

2. Create virtual environment and clone TEMUnormalizer here

```
python3 -m venv test
source test/bin/activate
git clone https://github.com/TeMU-BSC/TEMUNormalizer.git
cd TEMUNormalizer
pip install -r requirements.txt
```

3. Configure Med_Tagger inside the virtual environment:

```
cd ..
git clone https://github.com/PlanTL-SANIDAD/SPACCC_POS-TAGGER.git
cd SPACCC_POS-TAGGER
bash compila_freeling.sh
cd Med_Tagger
python setup.py install
```


### Install
Clone this repository and install numpy and pandas

```
cd ../..
git clone https://github.com/TeMU-BSC/structure-ner-output.git
pip install numpy
pip install pandas
```

## Execution

```
python main.py -d $HOME/toy-data -n 5
```

**CAREFUL:** TEMUnormalizer works with absolute paths! 
**NOTE:** TEMUnormalizer is the slowest process here. Therefore, you are asked whether you want to do it everytime, for every label.

## Todos

  - commit scripts
  - add license


License
----




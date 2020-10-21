# Structure NER tagger output

## Description

- Input: Named Entity Recognition (NER) output
- Steps: 
    1. Parse NER output
    2. Remove unused entities and rename undescriptive ones
    3. Normalize text span: lowercase, remove extra whitespaces, remove punctuation and remove accents
    4. Remove exact duplicated entities: same text position in same filename and with the same entity label
    5. Count term and document frequency of every normalized span
    6. Compute lemma from normalized text span
    7. Map the original text span (lowercased and without the extra whitespaces and punctuation) to Snomed ID
    8. Drop duplicates based on span normalized and filename
- Output: Structured and normalized information

EXTRA: a posteriori we may map the Snomed IDs to UMLS CUI.

## Installation Guide
### Prerequisites
### Install
## Execution
```
Execution example here
```
## Todos

  - commit scripts
  - add toy_data
  - show execution example
  - write installation instructions
  - add license


License
----




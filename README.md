# IOE Student School Allocation

Public release of the code for paper 846 of AGILE2023

## Prepare the Anonymised Data

```python
python -m ioe.scripts.prepare_data <file>.xlsx
```

## Prepare the Journey Data

This must be run after the step above.

```python
python -m ioe.scripts.tfl <subject>
```

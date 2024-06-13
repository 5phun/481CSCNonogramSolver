# Nonogram Solver in Prolog

A nonogram solver and display implemented in Prolog, along with an interface connecting connecting to a nonogram generator

## Team Members

- Dennis Phun
- Gordon Luu
- Sean Phun

## Acknowledgments

This project was completed in CSC 481 - Knowledge Based Systems at Cal Poly, instructed by Rodrigo Canaan. We would like to acknowledge Lars Buitinck for their very clean, Prolog Nonogram solver that uses the CLP(FD) library and puzzle-nonograms.com for their puzzle generator.

## Usage

### Requirements:

- Python 3.6 and higher
- SWI-Prolog 8.2 and higher.

### Dependencies:

```
pip install -r requirements.txt
```

You may have to set an environment variable for swipl:

- For Windows:

```
$env:SWI_HOME_DIR = "C:\Program Files\swipl"
```

- For Linux/MacOS:

```
export SWI_HOME_DIR=/usr/lib/swipl
```

assuming the default path was used at installation.

### Running the System:

1. Start up the program

```
python main.py
```

2. Choose from the four options

   - '**start**': Opens a driver to connect the solver to puzzle-nonograms.com.

     - Select a puzzle size ('5', '10', '15', '20', '25', '30', or '50') to be generated and scraped.
     - Select 'solve' or 'return' to either pass the puzzle representation to the Prolog solver or return to the four options.
     - Select 'fill' or 'return' to either fill the puzzle on the site according to the solution or return to the four options.

   - '**example**': Select from the available examples.

     1. A working, rectangular puzzle
     2. A failing (note the first column hint in comparison to the previous example) puzzle
     3. A simple, multi-solutioned puzzle
     4. A more complex, multi-solutioned puzzle

   - '**test**': Opens a driver for each size, running puzzles until a certain number of runs and storing them in test_times.
   - '**quit**': Closes all drivers and stops the program.

## Results

We were able to successfully solve puzzles of various sizes and number of solutions, which can be viewed by running the **'example'** command.

Furthermore, the solves are relatively quick, considering the solver's implementation in Prolog.

| Size of Puzzle | Average Time (seconds) |
| ----------------- | ---------------------- |
| 5x5               | 0.0015625              |
| 10x10             | 0.0328125              |
| 15x15             | 0.0859375              |
| 20x20             | 0.178125               |
| 25x25             | 0.3078125              |

These results are from 500 random-generated puzzles obtained by running the **'test'** command. Note that the site is a random puzzle generator, however, the exact puzzle IDs, along with their solve times can be found in test_times. Also note that the time of solve varies depending on computer specifications.

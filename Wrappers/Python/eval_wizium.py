import argparse
import os
from pathlib import Path
import random
import time
from libWizium import Wizium

PATH = './../../Binaries/Linux/libWizium.so'

def draw (lines: list[str], workdir: str):
    print (f"type(lines): {type(lines)}")
    for l in lines:
        print (l.strip ())
    ## print as html table
    with open (os.path.join(workdir, "output.html"), "w", encoding="utf-8") as f:
        f.write ("<style>\n")
        f.write ("table { border-collapse: collapse; table-layout: fixed; }\n")
        f.write ("table, td { border: 1px solid black; }\n")
        f.write ("td { width: 28px; min-width: 28px; max-width: 28px; height: 28px; min-height: 28px; max-height: 28px; padding: 0; box-sizing: border-box; text-align: center; vertical-align: middle; line-height: 28px; }\n")
        f.write ("</style>\n")
        f.write ("<table>\n")
        for l in lines:
            f.write ("<tr>\n")
            for c in l.strip ():
                if c == '#':
                    f.write ("<td style=\"background-color: #aaa;\"></td>\n")
                else:
                    f.write (f"<td>{c}</td>\n")
            f.write ("</tr>\n")
        f.write ("</table>\n")


def solve (wiz: Wizium, max_black: int = 0, heuristic_level: int = 0, seed: int = 0, black_mode: str = 'DIAG'):
    """Solve the grid

    wiz             Wizium instance
    max_black       Max number of black cases to add (0 if not allowed)
    heuristic_level Heuristic level (0 if deactivated)
    seed            Random Number Generator seed (0: take at random)
    """

    if not seed: seed = random.randint(1, 1000000)

    # Configure the solver
    wiz.solver_start (seed=seed, black_mode=black_mode, max_black=max_black, heuristic_level=heuristic_level)
    t_start = time.time ()

    # Solve with steps of 500ms max, in order to draw the grid content evolution
    while True:
        status = wiz.solver_step (max_time_ms=500)

        lines = wiz.grid_read()
        print (status)

        if status.fillRate == 100:
            print ("SUCCESS !")
            break
        if status.fillRate == 0:
            print ("FAILED !")
            break

    # Ensure to release grid content
    wiz.solver_stop ()

    t_end = time.time ()
    print ("Compute time: {:.01f}s".format (t_end-t_start))
    return lines


def load_grid(grid_path: Path, wiz: Wizium):
    if not grid_path.exists():
        raise FileNotFoundError(f"Grid file '{grid_path}' not found.")
    with open(grid_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f]
    if not lines:
        raise ValueError(f"Grid file '{grid_path}' is empty.")

    width = len(lines[0])
    height = len(lines)
    wiz.grid_set_size(width, height)

    for y_coord, line in enumerate(lines):
        if len(line) != width:
            raise ValueError(f"All lines in the grid file must have the same length. Found a line with length {len(line)} instead of {width}.")
        for x_coord, char in enumerate(line):
            if char == '#':
                wiz.grid_set_box(x_coord, y_coord, 'BLACK')
            elif char == '.':
                pass
            else:
                raise ValueError(f"Invalid character '{char}' in grid file. Only '#' and '.' are allowed.")


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dict', type=str, required=True, help='Path to the dictionary file')
    parser.add_argument('--workdir', type=str, required=True)
    parser.add_argument('--grid', type=str, help='Path to grid file')
    args = parser.parse_args()
    assert isinstance(args.dict, str)
    assert isinstance(args.workdir, str)
    assert isinstance(args.grid, str | None)
    dictionary = sorted([line.strip() for line in open(args.dict, 'r', encoding='utf-8') if line.strip()])
    ## print first 10 words
    print(f"First 10 words in dictionary: {dictionary[:10]}")

    alphabet = "".join(sorted({ch for word in dictionary for ch in word}))

    print(f"Dictionary with {len(dictionary)} words uses alphabet '{alphabet}'")

    # Create a Wizium instance
    wiz = Wizium (os.path.join (os.getcwd (), PATH), alphabet=alphabet)

    # Load dictionary
    wiz.dic_clear()
    entries_added = wiz.dic_add_entries(dictionary)
    print(f"Added {entries_added} entries to the dictionary")

    if args.grid:
        print(f"Loading grid from file: {args.grid}")
        load_grid(Path(args.grid), wiz)

    lines = solve(wiz, max_black=25, heuristic_level=2)
    if lines:
        draw(lines, args.workdir)
    else:
        print ("No grid content do draw")


if __name__ == "__main__":
    run()

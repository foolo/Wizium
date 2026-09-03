import argparse
import os
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
        f.write ("<table border=\"1\">\n")
        for l in lines:
            f.write ("<tr>\n")
            for c in l.strip ():
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


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dict', type=str, required=True, help='Path to the dictionary file')
    parser.add_argument('--workdir', type=str, required=True)
    args = parser.parse_args()
    assert isinstance(args.dict, str)
    assert isinstance(args.workdir, str)
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

    #set_grid_1 (wiz)
    wiz.grid_set_size(10, 8)
    wiz.grid_set_box (0, 0, 'BLACK')
    wiz.grid_set_box (0, 1, 'BLACK')
    wiz.grid_set_box (1, 0, 'BLACK')
    lines = solve(wiz, max_black=25, heuristic_level=2)
    if lines:
        draw(lines, args.workdir)
    else:
        print ("No grid content do draw")


if __name__ == "__main__":
    run()

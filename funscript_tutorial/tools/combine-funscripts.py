from funscript.funscript import Funscript
import numpy as np
import argparse

def multiply_funscripts(left: Funscript, right: Funscript) -> Funscript:
    x = np.union1d(left.x, right.x)
    y = np.interp(x, left.x, left.y) * np.interp(x, right.x, right.y)
    return Funscript(x, y)


def avg_funscripts(left: Funscript, right: Funscript, ratio) -> Funscript:
    x = np.union1d(left.x, right.x)
    y = (np.interp(x, left.x, left.y) * (ratio - 1) + np.interp(x, right.x, right.y)) / ratio
    return Funscript(x, y)



def main(funscript_file1, funscript_file2, output_file, ratio):
    # Load the funscript files
    funscript1 = Funscript.from_file(funscript_file1)
    funscript2 = Funscript.from_file(funscript_file2)

    # Combine the funscripts
    combined_actions = avg_funscripts(funscript1, funscript2, ratio)

    # Save the combined funscript
    combined_actions.save_to_path(output_file)
    print(f"Combined Funscript saved to {output_file}")

if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Combine two Funscript files by multiplying their position values.")
    parser.add_argument('funscript_file1', type=str, help="The path to the first input Funscript file.")
    parser.add_argument('funscript_file2', type=str, help="The path to the second input Funscript file.")
    parser.add_argument('output_file', type=str, help="The path to save the combined Funscript file.")
    #parser.add_argument('filename', type=str, help="The file name. We combine filename.volume_ramp.funscript with filename.speed.funscript into filename.volume.funscript")
    parser.add_argument('ratio', type=int, help="The ratio between scripts, 2 for 50/50, 4 for 75/25 etc", default=2)
    
    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with the provided arguments
    main(args.funscript_file1, args.funscript_file2, args.output_file, args.ratio)
    #main(args.filename + ".volume_ramp.funscript", args.filename + ".speed.funscript", args.filename + ".volume.funscript", args.ratio)
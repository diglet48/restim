from funscript.funscript import Funscript
import numpy as np
import argparse




def calculate_speed(funscript):
    """Calculate the absolute speed of change between consecutive points."""
    x = []
    y = []
    max_speed = 0

    # Iterate over consecutive points
    for i in range(1, len(funscript.x)):
        time_diff = (funscript.x[i] - funscript.x[i - 1]) * 1000  # Time difference in milliseconds
        pos_diff = abs(funscript.y[i] - funscript.y[i - 1])  # Absolute position change

        # Avoid division by zero if time_diff is zero
        if time_diff != 0:
            speed = pos_diff / time_diff  # Speed (change per millisecond)
        else:
            speed = 0

        if speed > max_speed:
            max_speed = speed




        # Append the new action with speed as the 'pos' value and original timestamp
        x.append((funscript.x[i]))
        y.append(speed)

    factor = 1 / max_speed
    for i in range(1, len(y)):
        y[i] = y[i] * factor
    return Funscript(x, y)


def calculate_speed_windowed(funscript, seconds):
    """Calculate the rolling average speed of change over the last n seconds."""
    x = []
    y = []
    max_speed = 0
    time_window = seconds

    # Iterate over each point
    for i in range(1, len(funscript.x)):
        current_time = funscript.x[i - 1]
        pos_current = funscript.y[i]

        # Initialize variables for rolling sum
        total_speed = 0
        count = 0

        # Look back at all points within the last n seconds
        for j in range(i, -1, -1):
            if current_time - funscript.x[j] > time_window:
                break  # Stop if we're outside the n-second window

            time_diff = funscript.x[j] - funscript.x[j-1]  # Time difference in milliseconds
            pos_diff = abs(funscript.y[j] - funscript.y[j-1])  # Absolute position change

            # Avoid division by zero if time_diff is zero
            if time_diff != 0:
                speed = pos_diff / time_diff  # Speed (change per millisecond)
                total_speed += speed
                count += 1

        # Calculate the average speed over the rolling window
        avg_speed = (total_speed / count) if count > 0 else 0

        if avg_speed > max_speed:
            max_speed = avg_speed

        # Append the new action with average speed as the 'pos' value

        x.append((funscript.x[i]))
        y.append(avg_speed)

    factor = 1 / max_speed
    for i in range(len(y)):
        y[i] = y[i] * factor

    return Funscript(x, y)




def main(funscript_file, output_file, seconds):
    # Load the funscript files
    funscript = Funscript.from_file(funscript_file)

    # Combine the funscripts
    speed = calculate_speed_windowed(funscript, seconds)

    # Save the combined funscript
    speed.save_to_path(output_file)
    print(f"Speed Funscript saved to {output_file}")


if __name__ == "__main__":
    # Set up argument parsing
    parser = argparse.ArgumentParser(description="Convert speed of input funscript to output.")
    parser.add_argument('funscript_input', type=str, help="The path to the input Funscript file.")
    parser.add_argument('funscript_output', type=str, help="The path to the output Funscript file.")
    
    parser.add_argument('seconds', type=int,
                        help="Size of window over which to measure speed (in seconds)", default=10)

    # Parse the arguments
    args = parser.parse_args()

    # Call the main function with the provided arguments
    # main(args.funscript_file1, args.funscript_file2, args.output_file)
    main(args.funscript_input, args.funscript_output, args.seconds)

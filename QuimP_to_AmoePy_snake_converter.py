#!/usr/bin/env python3
"""
Jupyter Notebook: Snake CSV Format Converter
Converts snake outline data from frame-based format to time-series format
"""

import pandas as pd
import numpy as np

def convert_snake_csv(input_file, output_file, time_per_frame=1, pixel_size_um=1):
    """
    Convert snake CSV from frame-based format to time-series format.
    
    Parameters:
    input_file (str): Path to input CSV file
    output_file (str): Path to output CSV file
    """
    
    # Dictionary to store data for each frame
    frames_data = {}
    current_frame = None
    
    # Read the input file line by line
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    # Parse the data
    for line in lines:
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
            
        # Check if this is a frame header
        if line.startswith('#frame'):
            current_frame = int(line.split()[1])
            frames_data[current_frame] = []
        else:
            # This is a data line - split by tabs
            parts = line.split('\t')
            if len(parts) >= 6:  # Ensure we have enough columns
                try:
                    # Extract node_x and node_y (columns 4 and 5, 0-indexed)
                    node_x = float(parts[4]) / pixel_size_um  # Convert to micrometers
                    node_y = float(parts[5]) / pixel_size_um  # Convert to micrometers
                    frames_data[current_frame].append((node_x, node_y))
                except (ValueError, IndexError):
                    # Skip lines that can't be parsed as numbers
                    continue
    
    # Convert to output format
    output_lines = []
    
    # Add header line
    header = "# time_0 & X_0,0 & Y_0,0 & X_0,1 & Y_0,1 & X_0,2 & ... // time_1 & X_1,0 & Y_1,0 & X_1,1 & Y_1,1 & X_1,2 & ... // ...; Units: $s, \\mu m$, (Seconds, Mikrometer)"
    output_lines.append(header)

    # Sort frames by frame number
    sorted_frames = sorted(frames_data.keys())
    
    for frame_num in sorted_frames:
        coordinates = frames_data[frame_num]
        
        # Convert frame number to time in seconds
        time_seconds = (frame_num - 1) * time_per_frame  # Convert to 0-based time indexing
        
        # Create the output line: time followed by alternating x,y coordinates
        # line_parts = [str(frame_num - 1)]  # Convert to 0-based time indexing
        line_parts = [f"{time_seconds:.6f}"]
        
        for x, y in coordinates:
            line_parts.extend([f"{x:.6f}", f"{y:.6f}"])
        
        output_lines.append(' '.join(line_parts)) # sepparate items with a space
    
    # Write to output file
    with open(output_file, 'w') as f:
        f.write('\n'.join(output_lines))
    
    print(f"Conversion complete!")
    print(f"Processed {len(sorted_frames)} frames")
    print(f"Output saved to: {output_file}")
    
    return frames_data

def preview_data(frames_data, num_frames=3):
    """
    Preview the first few frames of data for verification.
    
    Parameters:
    frames_data (dict): Dictionary containing frame data
    num_frames (int): Number of frames to preview
    """
    print("\n" + "="*60)
    print("DATA PREVIEW")
    print("="*60)
    
    sorted_frames = sorted(frames_data.keys())[:num_frames]
    
    for frame_num in sorted_frames:
        coordinates = frames_data[frame_num]
        print(f"\nFrame {frame_num} ({len(coordinates)} nodes):")
        print("Node#\tX\tY")
        print("-" * 30)
        
        for i, (x, y) in enumerate(coordinates[:5]):  # Show first 5 nodes
            print(f"{i}\t{x:.4f}\t{y:.4f}")
        
        if len(coordinates) > 5:
            print(f"... and {len(coordinates) - 5} more nodes")

def main():
    """
    Main execution function for Jupyter notebook
    """
    # File paths
    input_file = "snake.csv"
    output_file = "snake_converted.csv"
    
    print("Snake CSV Format Converter")
    print("=" * 40)
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    
    try:
        # Convert the file
        frames_data = convert_snake_csv(input_file, output_file)
        
        # Preview the data
        preview_data(frames_data)
        
        # Show sample output format
        print("\n" + "="*60)
        print("SAMPLE OUTPUT FORMAT")
        print("="*60)
        print("time\tX_0\tY_0\tX_1\tY_1\tX_2\tY_2\t...")
        
        # Read and display first few lines of output
        with open(output_file, 'r') as f:
            output_lines = f.readlines()
        
        for i, line in enumerate(output_lines[:3]):
            parts = line.strip().split('\t')
            preview_parts = parts[:7] if len(parts) > 7 else parts
            if len(parts) > 7:
                preview_parts.append('...')
            print('\t'.join(preview_parts))
        
        return frames_data
        
    except FileNotFoundError:
        print(f"Error: Could not find input file '{input_file}'")
        print("Please make sure the file exists in the current directory.")
        return None
    except Exception as e:
        print(f"Error during conversion: {str(e)}")
        return None

# Execute the conversion
if __name__ == "__main__":
    frames_data = main()

# Additional utility functions for analysis
def analyze_snake_data(frames_data):
    """
    Analyze the snake data to provide insights.
    
    Parameters:
    frames_data (dict): Dictionary containing frame data
    """
    if not frames_data:
        print("No data to analyze.")
        return
    
    print("\n" + "="*60)
    print("DATA ANALYSIS")
    print("="*60)
    
    frame_numbers = sorted(frames_data.keys())
    node_counts = [len(frames_data[frame]) for frame in frame_numbers]
    
    print(f"Number of frames: {len(frame_numbers)}")
    print(f"Frame range: {min(frame_numbers)} to {max(frame_numbers)}")
    print(f"Nodes per frame: {min(node_counts)} to {max(node_counts)}")
    print(f"Average nodes per frame: {np.mean(node_counts):.1f}")
    
    # Check for consistency in node count
    unique_counts = set(node_counts)
    if len(unique_counts) == 1:
        print(f"✓ Consistent node count across all frames: {node_counts[0]}")
    else:
        print(f"⚠ Variable node counts detected: {sorted(unique_counts)}")

# Run analysis if data was successfully loaded
if 'frames_data' in locals() and frames_data:
    analyze_snake_data(frames_data)
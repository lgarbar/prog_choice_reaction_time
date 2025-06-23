# 4RT Task Script

## Description

`Stimuli/4rt.py` is a Python script for presenting a cognitive reaction time task with visual stimuli and mouse button responses. The task includes instructions, practice, and test blocks, and can optionally send triggers for EEG recording. The script records timing and accuracy of responses, outputting data to a CSV file.

## Setup and Installation

### Prerequisites

- **Python 3.x**
- **Psychopy**: For experiment display and timing
- **Pygaze**: For experiment control and (optionally) eye tracking
- **Pynput**: For mouse input monitoring
- **Pandas**: For data handling
- **Numpy**: For numerical operations
- **Matplotlib**: (Optional, for visualizations)
- **Pillow (PIL)**: For image handling

Install all required libraries with:

```bash
pip install psychopy pygaze pynput pandas numpy matplotlib pillow
```

## Directory Structure

The script expects the following structure:

- `Stimuli/`
  - `Images/` (with subfolders: `1_option/`, `2_options/`, `4_options/`)
  - `Schedules/`
    - `1_option/`, `2_options/`, `4_options/` (with `.par` schedule files)
    - `practice/` (with `.csv` practice schedule files)
  - `Order/` (not used by default in current script)
  - `trigger_map.json` (required if using EEG triggers)

## Running the Script

Run the script from the project root:

```bash
python Stimuli/4rt.py --filename <output_file_name.csv> [--withEEG True|False] [--portAddress <int>]
```

### Command-Line Arguments

- `--filename` (required): Output CSV file for data.
- `--withEEG` (optional, default: False): Set to True to enable EEG trigger output.
- `--portAddress` (optional, default: 0): Parallel port address for EEG triggers.

## Features and Task Flow

- **Instructions**: Multiple instruction screens guide the participant.
- **Practice Blocks**: Two practice blocks (quad-choice, spatial cue and central presentation). Each must be passed with ≥80% accuracy (up to 3 attempts each).
- **Test Blocks**: Three main blocks (1-option, 2-option, 4-option), each with two sub-blocks (spatial cue and central presentation).
- **Stimulus Presentation**: Images are shown for a fixed duration (default 2s). Mouse button responses are recorded.
- **Response Mapping**: Mouse buttons are mapped to responses (left, middle left, middle right, right). Mapping differs slightly by OS.
- **EEG Triggers**: If enabled, sends triggers for instructions, block starts, stimulus onset, and responses using a parallel port and `trigger_map.json`.
- **Data Output**: All events are logged with timing, response, and accuracy to the specified CSV file.

## Customization

- **Visual Stimuli**: Place images in the appropriate `Stimuli/Images/<block>/` folders. File names must match those referenced in schedule files.
- **Schedules**: Edit or add `.par` files in `Stimuli/Schedules/<block>/` for test blocks, and `.csv` files in `Stimuli/Schedules/practice/` for practice blocks.
- **Response Mapping**: To change which mouse buttons correspond to which responses, edit the `on_click` function in the script.
- **Timing**: Adjust `image_display_duration` in the script for stimulus duration.
- **EEG Triggers**: Edit `trigger_map.json` to match your EEG system's trigger codes.

## Output

The output CSV contains:

- `sectionname`: Name of the event/trial
- `starttime`, `endtime`, `duration`: Timing info
- `responsetime`: Time of participant response
- `delta`: Time from stimulus onset to response
- `condition`: Stimulus condition
- `response`: Which button was pressed
- `accuracy`: 1 (correct) or 0 (incorrect)

## Notes

- Ensure all required images and schedule files are present in the correct folders.
- For EEG, make sure the parallel port address and trigger map are correct.
- The script will end a practice block early if accuracy is sufficient, or after 3 failed attempts.
- Press `escape` during a trial to exit the experiment.



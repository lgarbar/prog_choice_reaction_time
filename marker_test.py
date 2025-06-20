import platform
import psychopy.visual
from psychopy import prefs
from psychopy import core, event, parallel
from pygaze.libinput import Keyboard
from pygaze.libscreen import Display, Screen
import pygaze
import argparse
import pandas as pd
import os
import random
import numpy as np
import json
import stimlsltools as slt

os_type = platform.system()

parser = argparse.ArgumentParser(description='')
parser.add_argument('--filename', dest='filename', type=str, help='name of output data file (.csv)', required=True)
parser.add_argument('--withEEG', dest='withEEG', type=bool, help='True if running with EEG', default=False)
parser.add_argument('--portAddress', dest='portAddress', type=int, help='address of parallel port', default=0)

args = parser.parse_args()

withEEG = args.withEEG

if withEEG:
    p_port = parallel.ParallelPort(address=args.portAddress)
    with open('Stimuli/trigger_map.json', 'r') as f:
        trigger_map = json.load(f)

# Simple test stimuli
visuals = {
    'Start': ['Test starting soon.', 'space', True],
    'Stim1': ['Press left button for this stimulus', 'c', True],
    'Stim2': ['Press right button for this stimulus', 'm', True],
    'End': ['Test complete!', 'space', True]
}

disp = Display(disptype='psychopy', bgc='black')
scr = Screen(disptype='psychopy', bgc='black')
event.Mouse(visible=False)
center_text = psychopy.visual.TextStim(win=pygaze.expdisplay, text='', height=50, wrapWidth=1080)

out_dict = {'sectionname': ['starttime', 'endtime', 'duration', 'responsetime', 'delta', 'condition', 'response', 'accuracy']}

cont = True
visual_screens = list(visuals.keys())
visual_screen_idx = 0
current_rep = 0

task_clock = core.Clock()

while cont:
    if visual_screen_idx < len(visual_screens):
        visual_screen_name = visual_screens[visual_screen_idx]
        visual_screen_data = visuals[visual_screen_name]
        screen_content = visual_screen_data[0]
        screen_wait_condition = visual_screen_data[1]
        log_screen_data = visual_screen_data[2]

        scr.screen.clear()

        # Send LSL marker for onset
        slt.pushToStreamLabel('Onset_' + visual_screen_name)

        # Display text
        center_text.text = screen_content
        scr.screen.append(center_text)
        disp.fill(screen=scr)
        disp.show()

        # Send EEG marker if enabled
        if withEEG:
            p_port.setData(255)  # Simple marker value for testing

        item_starttime = task_clock.getTime()
        item_condition = 'text'
        item_responsetime = None
        item_response = None
        item_accuracy = None

        if screen_wait_condition == 'space':
            keys = event.waitKeys(keyList=['space'])
            item_endtime = task_clock.getTime()
            item_duration = item_endtime - item_starttime
            item_delta = None

            item_key = f"{visual_screen_name}"
            out_dict[item_key] = [item_starttime, item_endtime, item_duration, None, None, item_condition, None, None]

            # Send LSL marker for offset
            slt.pushToStreamLabel('Offset_' + visual_screen_name)

            visual_screen_idx += 1
            if visual_screen_idx >= len(visual_screens):
                cont = False
        else:
            # Wait for response
            keys = event.waitKeys(keyList=['c', 'm', 'escape'])
            if 'escape' in keys:
                cont = False
            else:
                item_responsetime = task_clock.getTime()
                item_response = keys[0]
                item_accuracy = 1 if (item_response == 'c' and screen_wait_condition == 'c') or (item_response == 'm' and screen_wait_condition == 'm') else 0
                item_endtime = task_clock.getTime()
                item_duration = item_endtime - item_starttime
                item_delta = item_responsetime - item_starttime

                item_key = f"{visual_screen_name}"
                out_dict[item_key] = [item_starttime, item_endtime, item_duration, item_responsetime, item_delta, item_condition, item_response, item_accuracy]

                # Send LSL marker for response
                slt.pushToStreamLabel('Response_' + visual_screen_name + '_' + str(item_accuracy))

                visual_screen_idx += 1
                if visual_screen_idx >= len(visual_screens):
                    cont = False

    else:
        cont = False

# Save data
df = pd.DataFrame.from_dict(out_dict, orient='index', columns=['starttime', 'endtime', 'duration', 'responsetime', 'delta', 'condition', 'response', 'accuracy'])
df.index.name = 'sectionname'
df.to_csv(args.filename)

disp.close() 
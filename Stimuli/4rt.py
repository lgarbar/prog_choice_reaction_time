import platform
import psychopy.visual
from psychopy import prefs
from psychopy import core, event, parallel
from pynput import mouse as pynput_mouse
from pygaze.libinput import Keyboard
from pygaze.libscreen import Display, Screen
from pygaze.eyetracker import EyeTracker
import pygaze
import argparse
import pandas as pd
import os
import random
import numpy as np
import matplotlib.pyplot as plt
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

practice_dirs = '/Users/AP-CNL/Desktop/4RT/Stimuli/Schedules/practice'

visuals = {
    '4RTStart': ['Next activity starting soon.', 'space', True],
    'Instructions1': ["You will see images presented on the screen that correspond to the buttons on the device you are holding.\n\nWhen the image appears, press the corresponding button.", 'space', False],
    'Instructions2': ["At first, only the stimulus that matches the left button will appear,\n\nand so you'll only be responding using that left button.\n\nGo ahead and press the left button once you see the diagonal line appear on screen.", 'space', False],
    'Example1': [['line', 'feedback'], 'c', True],
    'Instructions3': ["Next, the stimuli that match the left or right buttons will appear,\n\nso you'll have to respond using the left or right buttons.\n\nGo ahead and press the right button once you see the square appear on screen.", 'space', False],
    'Example2': [['square', 'feedback'], 'c', True],
    'Instructions4': ["In the final phase, you will respond to any of the four stimuli using all four buttons.\n\nGo ahead and press the middle button with the circle once you see the circle appear on screen.", 'space', False],
    'Example4': [['circle', 'feedback'], 'c', True],
    'Instructions5': ['Now you will have a chance to practice the task before moving on to the first phase.\n\nPay attention to the instructions on screen to know which stimuli could appear.', 'space', False],
    'Feedback4': [['options'], 'space', True],
    'Practice': None,
    'Practices': None,
    'Instructions6': ['Good job on the practice trials. You can now move on to the test trials.\n\nYou will do the same task as in the practice, completing a distinct blocks of trials for each of the phases described earlied.\n\nEach block will last about 3-5 minutes long. You will have a short break in between these trials.', 'space', False],
    'Break1': [['options'], 'space', True],
    'Stim1': None,
    'Break1s': [['breaks'], 'space', True],
    'Stim1s': None,
    'Break2': [['break'], 'space', True],
    'Stim2': None,
    'Break2s': [['breaks'], 'space', True],
    'Stim2s': None,
    'Break4': [['break'], 'space', True],
    'Stim4': None,
    'Break4s': [['breaks'], 'space', True],
    'Stim4s': None,
    '4RTEnd': ['Thank you!', 'space', True]
}

def get_sched_df(fpath):
    with open(fpath, 'r') as f:
        lines = f.readlines()
        lines = [line.split() for line in lines]
    schedule = pd.DataFrame(lines, columns=['time', 'stim_code', 'duration', '?', 'stim_type'])
    schedule = schedule.apply(pd.to_numeric, errors='ignore')
    schedule = schedule.drop(columns=['time', 'stim_code', '?'])
    return schedule

def get_order_file(order_dirs):
    order_list = os.listdir(order_dirs)
    order_list = [file for file in order_list if file.endswith('.par')]
    random.shuffle(order_list)
    if not order_list:
        return []
    order_list = order_list[:1]
    return [os.path.join(order_dirs, file) for file in order_list]

image_text = 'Stimuli/Images/{}'
one_opt_dirs = 'Stimuli/Schedules/1_option'
two_opt_dirs = 'Stimuli/Schedules/2_options'
four_opt_dirs = 'Stimuli/Schedules/4_options'

one_opt_fname_list = get_order_file(one_opt_dirs)
one_opt_fname = one_opt_fname_list[0] if one_opt_fname_list else None
schedule1 = get_sched_df(one_opt_fname).reset_index(drop=True) if one_opt_fname else pd.DataFrame()

one_opt_fname_list = get_order_file(one_opt_dirs)
one_opt_fname = one_opt_fname_list[0] if one_opt_fname_list else None
schedule1s = get_sched_df(one_opt_fname).reset_index(drop=True) if one_opt_fname else pd.DataFrame()


two_opt_fname_list = get_order_file(two_opt_dirs)
two_opt_fname = two_opt_fname_list[0] if two_opt_fname_list else None
schedule2 = get_sched_df(two_opt_fname).reset_index(drop=True) if two_opt_fname else pd.DataFrame()

two_opt_fname_list = get_order_file(two_opt_dirs)
two_opt_fname = two_opt_fname_list[0] if two_opt_fname_list else None
schedule2s = get_sched_df(two_opt_fname).reset_index(drop=True) if two_opt_fname else pd.DataFrame()


four_opt_fname_list = get_order_file(four_opt_dirs)
four_opt_fname = four_opt_fname_list[0] if four_opt_fname_list else None
schedule4 = get_sched_df(four_opt_fname).reset_index(drop=True) if four_opt_fname else pd.DataFrame()

four_opt_fname_list = get_order_file(four_opt_dirs)
four_opt_fname = four_opt_fname_list[0] if four_opt_fname_list else None
schedule4s = get_sched_df(four_opt_fname).reset_index(drop=True) if four_opt_fname else pd.DataFrame()

visuals['Stim1'] = [schedule1, 'c', True]
visuals['Stim1s'] = [schedule1s, 'c', True]
visuals['Stim2'] = [schedule2, 'c', True]
visuals['Stim2s'] = [schedule2s, 'c', True]
visuals['Stim4'] = [schedule4, 'c', True]
visuals['Stim4s'] = [schedule4s, 'c', True]

practice_files = [os.path.join(practice_dirs, file) for file in os.listdir(practice_dirs)]
random.shuffle(practice_files)
visuals['Practice'] = [pd.read_csv(practice_files[0], index_col=0, keep_default_na=False), 'c', True]
random.shuffle(practice_files)
visuals['Practices'] = [pd.read_csv(practice_files[0], index_col=0, keep_default_na=False), 'c', True]

disp = Display(disptype='psychopy', bgc='black')
scr = Screen(disptype='psychopy', bgc='black')
event.Mouse(visible=False)
center_text = psychopy.visual.TextStim(win=pygaze.expdisplay, text='', height=50, wrapWidth=1080)
image = psychopy.visual.ImageStim(win=pygaze.expdisplay, image=None)

val_dict = {'line': 1, 'circle': 2, 'triangle': 3, 'square': 4}

last_stim_responsetime = None
last_stim_accuracy = None
last_stim_response = None

response_received = False
correct_value = np.nan
current_value = None

accuracy_list = []

out_dict = {'sectionname': ['starttime', 'endtime', 'duration', 'responsetime', 'delta', 'condition', 'response', 'accuracy']}

def on_click(x, y, button, pressed):
    global current_value, response_received
    if os_type == 'Linux':
        if pressed:
            if button == pynput_mouse.Button.left:
                current_value = 1
            elif button == pynput_mouse.Button.middle:
                current_value = 2
            elif button == pynput_mouse.Button.button8:
                current_value = 3
            elif button == pynput_mouse.Button.right:
                current_value = 4
            response_received = True
    else:
        if pressed:
            if button == pynput_mouse.Button.left:
                current_value = 1
            elif button == pynput_mouse.Button.middle:
                current_value = 2
            elif button == pynput_mouse.Button.x1:
                current_value = 3
            elif button == pynput_mouse.Button.right:
                current_value = 4
            response_received = True
    return True

listener = pynput_mouse.Listener(on_click=on_click)
listener.start()

image_display_duration = 2
practice_blocks = ['Practice', 'Practices']
practice_attempts = {block: 0 for block in practice_blocks}
max_practice_attempts = 3

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

        slt.pushToStreamLabel('Onset_' + visual_screen_name)

        # INSTRUCTIONS DISPLAY
        if isinstance(screen_content, str):
            center_text.text = screen_content
            scr.screen.append(center_text)
            disp.fill(screen=scr)
            disp.show()
            if withEEG:
                p_port.setData(2)  # Instructions Onset

            item_starttime = task_clock.getTime()
            item_condition = 'text'

            if screen_wait_condition == 'space':
                keys = event.waitKeys(keyList=['space'])
                item_endtime = task_clock.getTime()
                item_duration = item_endtime - item_starttime
                item_delta = None

                item_key = f"{visual_screen_name}"
                out_dict[item_key] = [item_starttime, item_endtime, item_duration, None, None, item_condition, None, None]

                slt.pushToStreamLabel('Offset_' + visual_screen_name)

                visual_screen_idx += 1
                if visual_screen_idx >= len(visual_screens):
                    cont = False
            else:
                pass

        elif isinstance(screen_content, pd.DataFrame):
            schedule = screen_content
            if not schedule.empty:
                if current_rep < len(schedule):
                    cur_item = schedule['stim_type'][current_rep]
                    display_time = schedule['duration'][current_rep]

                    item_responsetime = None
                    item_response = None
                    item_accuracy = None
                    item_condition = None
                    item_delta = None

                    item_starttime = task_clock.getTime()
                    item_condition = cur_item

                    # Determine block type (practice vs task)
                    if visual_screen_name[-1] == 's':
                        pre_text = 'singles'
                    else:
                        if 'stim' in visual_screen_name.lower():
                            if '1' in visual_screen_name:
                                pre_text = '1_option'
                                if withEEG and current_rep == 0:
                                    p_port.setData(5)  # Block 1 Start (1-choice)
                            elif '2' in visual_screen_name:
                                pre_text = '2_options'
                                if withEEG and current_rep == 0:
                                    p_port.setData(6)  # Block 2 Start (2-choice)
                            elif '4' in visual_screen_name or 'practice' in visual_screen_name.lower():
                                pre_text = '4_options'
                                if withEEG and current_rep == 0:
                                    if 'practice' in visual_screen_name.lower():
                                        p_port.setData(3)  # Practice Start
                                    else:
                                        p_port.setData(7)  # Block 3 Start (4-choice)
                    
                    # NULL/WAITING STIMULUS DISPLAY
                    if cur_item == 'NULL':
                        image_path = image_text.format(f'{pre_text}/waiting.png')

                        image.setImage(image_path)
                        scr.screen.append(image)
                        disp.fill(screen=scr)
                        disp.show()
                        if withEEG:
                            p_port.setData(1)  # Fixation / Null

                        item_starttime = task_clock.getTime()
                        item_condition = cur_item

                        core.wait(display_time)

                        item_endtime = task_clock.getTime()
                        item_duration = item_endtime - item_starttime
                        item_delta = None

                        item_key = f"{visual_screen_name}_{current_rep}"
                        out_dict[item_key] = [item_starttime, item_endtime, item_duration, item_responsetime, item_delta, item_condition, item_response, item_accuracy]

                        current_rep += 1

                    else:
                        # TASK/PRACTICE STIMULUS DISPLAY
                        image_path = image_text.format(f'{pre_text}/{cur_item}.png')

                        image.setImage(image_path)
                        scr.screen.append(image)
                        disp.fill(screen=scr)
                        disp.show()
                        if withEEG:
                            p_port.setData(10)  # Stimulus Onset

                        item_starttime = task_clock.getTime()
                        item_condition = cur_item

                        if cur_item in val_dict:
                            correct_value = val_dict[cur_item]
                        else:
                            correct_value = np.nan

                        response_received = False
                        current_value = None
                        item_responsetime = None
                        item_response = None
                        item_accuracy = 0

                        if 'break' in visual_screen_name.lower():
                            while task_clock.getTime() - item_starttime < 60:
                                keys = event.getKeys(keyList=['space'])
                                if 'space' in keys:
                                    break
                        else:
                            while task_clock.getTime() - item_starttime < image_display_duration:
                                keys = event.getKeys(keyList=['escape'])
                                if 'escape' in keys:
                                    print("Escape key pressed. Exiting...")
                                    cont = False
                                    break
                                
                                # RESPONSE RECEIVED AND RECORDED
                                if response_received:
                                    item_responsetime = task_clock.getTime()
                                    if current_value == 1: item_response = 'left'
                                    elif current_value == 2: item_response = 'middle_l'
                                    elif current_value == 3: item_response = 'middle_r'
                                    elif current_value == 4: item_response = 'right'
                                    if correct_value is not np.nan and current_value == correct_value:
                                        item_accuracy = 1
                                    else:
                                        item_accuracy = 0
                                    slt.pushToStreamLabel(f'Response: {visual_screen_name}_{current_rep}_{item_accuracy}')
                                    if withEEG:
                                        p_port.setData(128)  # Response (any)
                                    break

                        last_stim_responsetime = item_responsetime
                        last_stim_accuracy = item_accuracy
                        last_stim_response = item_response

                        accuracy_list.append(item_accuracy)

                        item_endtime = task_clock.getTime()
                        item_duration = item_endtime - item_starttime
                        item_delta = item_responsetime - item_starttime if item_responsetime is not None else None

                        item_key = f"{visual_screen_name}_{current_rep}"
                        out_dict[item_key] = [item_starttime, item_endtime, item_duration, item_responsetime, item_delta, item_condition, item_response, item_accuracy]

                        current_rep += 1

                else:
                    slt.pushToStreamLabel('Offset_' + visual_screen_name)
                    
                    if visual_screen_name in practice_blocks:
                        if accuracy_list:
                            mean_accuracy = np.mean(accuracy_list)
                            print(f"{visual_screen_name} Accuracy: {mean_accuracy:.2f}")

                            if mean_accuracy >= 0.8:
                                visual_screen_idx += 1
                            else:
                                practice_attempts[visual_screen_name] += 1
                                if practice_attempts[visual_screen_name] >= max_practice_attempts:
                                    print(f"Maximum practice attempts reached for {visual_screen_name}. Ending experiment.")
                                    cont = False
                                else:
                                    current_rep = 0
                                    accuracy_list = []
                                    center_text.text = "Good job on that practice.\nYou'll now perform another round of that block."
                                    scr.screen.append(center_text)
                                    disp.fill(screen=scr)
                                    disp.show()
                                    core.wait(2.0)
                            accuracy_list = []

                        else:
                            print("No practice trials completed.")
                            cont = False
                    else:
                        visual_screen_idx += 1

                    current_rep = 0
                    if visual_screen_idx >= len(visual_screens):
                        cont = False

        # EXAMPLE STIMULUS DISPLAY
        elif isinstance(screen_content, list):
            if current_rep < len(screen_content):
                cur_item = screen_content[current_rep]

                item_responsetime = None
                item_response = None
                item_accuracy = None
                item_condition = None
                item_delta = None
               
                # FEEDBACK DISPLAY
                if cur_item == 'feedback':
                    if last_stim_responsetime is None:
                        center_text.text = "Too Slow."
                    elif last_stim_accuracy == 1:
                        center_text.text = "Correct!"
                    elif last_stim_accuracy == 0:
                        center_text.text = "Incorrect."

                    scr.screen.append(center_text)
                    disp.fill(screen=scr)
                    disp.show()

                    item_starttime = task_clock.getTime()
                    item_condition = 'feedback'

                    core.wait(1.0)

                    item_endtime = task_clock.getTime()
                    item_duration = item_endtime - item_starttime
                    item_delta = None

                    item_key = f"{visual_screen_name}_{current_rep}"
                    out_dict[item_key] = [item_starttime, item_endtime, item_duration, item_responsetime, item_delta, item_condition, item_response, item_accuracy]
                    current_rep += 1
                else:
                    # EXAMPLE STIMULUS DISPLAY
                    if '1' in visual_screen_name:
                        pre_text = '1_option'
                    elif '2' in visual_screen_name:
                        pre_text = '2_options'
                    else:
                        pre_text = '4_options'
                    image_path = image_text.format(f'{pre_text}/{cur_item}.png')

                    image.setImage(image_path)
                    scr.screen.append(image)
                    disp.fill(screen=scr)
                    disp.show()

                    item_starttime = task_clock.getTime()
                    item_condition = cur_item

                    if cur_item in val_dict:
                        correct_value = val_dict[cur_item]
                    else:
                        correct_value = np.nan

                    response_received = False
                    current_value = None
                    item_responsetime = None
                    item_response = None
                    item_accuracy = 0

                    if 'break' in visual_screen_name.lower():
                        while task_clock.getTime() - item_starttime < 60:
                            keys = event.getKeys(keyList=['space'])
                            if 'space' in keys:
                                break
                    else:
                        while task_clock.getTime() - item_starttime < image_display_duration:
                            keys = event.getKeys(keyList=['escape'])
                            if 'escape' in keys:
                                print("Escape key pressed. Exiting...")
                                cont = False
                                break
                            if response_received:
                                item_responsetime = task_clock.getTime()
                                if current_value == 1: item_response = 'left'
                                elif current_value == 2: item_response = 'middle_l'
                                elif current_value == 3: item_response = 'middle_r'
                                elif current_value == 4: item_response = 'right'
                                if correct_value is not np.nan and current_value == correct_value:
                                    item_accuracy = 1
                                else:
                                    item_accuracy = 0
                                break

                    last_stim_responsetime = item_responsetime
                    last_stim_accuracy = item_accuracy
                    last_stim_response = item_response

                    accuracy_list.append(item_accuracy)

                    item_endtime = task_clock.getTime()
                    item_duration = item_endtime - item_starttime
                    item_delta = item_responsetime - item_starttime if item_responsetime is not None else None

                    item_key = f"{visual_screen_name}_{current_rep}"
                    out_dict[item_key] = [item_starttime, item_endtime, item_duration, item_responsetime, item_delta, item_condition, item_response, item_accuracy]
                    current_rep += 1

            else:
                current_rep = 0
                visual_screen_idx += 1
                if visual_screen_idx >= len(visual_screens):
                    cont = False
        else:
            print(screen_content)
            print("Unexpected data type for visual screen:", type(screen_content))
            cont = False
    else:
        cont = False

listener.stop()

df = pd.DataFrame.from_dict(out_dict, orient='index', columns=['starttime', 'endtime', 'duration', 'responsetime', 'delta', 'condition', 'response', 'accuracy'])
df.index.name = 'sectionname'
df.to_csv(args.filename)

disp.close()
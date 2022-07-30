# -*- coding: utf-8 -*-
"""
Created on Thu Jul 21 13:25:20 2022

@author: yuany
"""

import time
from midiutil import MIDIFile

from brainflow.board_shim import BoardShim, BrainFlowInputParams, LogLevels 
from brainflow.data_filter import DataFilter, FilterTypes, NoiseTypes 

def main():  
    
    board_id = 1
    params = BrainFlowInputParams()
    params.board_id = 1   
    params.serial_port = 'COM3'
    
    
    BoardShim.enable_dev_board_logger ()
    board = BoardShim(board_id, params)
    sampling_rate = BoardShim.get_sampling_rate(board_id)
    eeg_channels = board.get_eeg_channels(board_id)
    
    eeg_channel = eeg_channels[3]
   
    #stream for 5s
    board.prepare_session()
    board.start_stream(45000)
      
    BoardShim.log_message(LogLevels.LEVEL_INFO.value, 'start sleeping in the main thread')
    time.sleep(5)
    
    data = board.get_board_data()

    
    #stop
    board.stop_stream()
    board.release_session()
  
    
    DataFilter.perform_bandpass(data[eeg_channel], BoardShim.get_sampling_rate(board_id), 10.0, 3.0,4,                               FilterTypes.BUTTERWORTH.value, 0)
    DataFilter.remove_environmental_noise(data[eeg_channel], BoardShim.get_sampling_rate(board_id), NoiseTypes.SIXTY.value)
 

    new_data = []
    for window in enumerate(data[eeg_channel]):
        if window[0] % 25 == 0:
            new_data.append(window[1])


    midi_note_numbers = []
    
    #translate to locrian scale from C4 to C5
    for i in new_data:
        if i < -2:
            midi_note_numbers.append(60)
        elif i < -1:
            midi_note_numbers.append(61)
        elif i < 0:
            midi_note_numbers.append(63)
        elif i < 1:
            midi_note_numbers.append(65)
        elif i < 2:
            midi_note_numbers.append(66)
        elif i < 3:
            midi_note_numbers.append(68)
        else:
            midi_note_numbers.append(72)
    
    
    #writing a midi file from the number list
    track     = 0
    channel   = 0
    time_beat = 0   # In beats
    duration  = 1   # In beats
    tempo     = 250  # In BPM
    volume    = 100 # 0-127, as per the MIDI standard

    MyMIDI = MIDIFile(1) 
    MyMIDI.addTempo(track,time_beat, tempo)
    MyMIDI.addTimeSignature(0, 0, 6, 3, 24, notes_per_quarter=8)


    for number in midi_note_numbers:
        MyMIDI.addNote(track, channel, number, time_beat, duration, volume)
        time_beat = time_beat + 1

    with open("brainflow_music_5.mid", "wb") as output_file:
        MyMIDI.writeFile(output_file)



if __name__ == "__main__":
    main()
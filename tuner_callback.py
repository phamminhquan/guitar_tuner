import pyaudio
import numpy as np
import struct

threshold = 10
rate = 16000
input_block_time = 0.128
fft_size = 2048
time_slots = 128
input_frames_per_block = int(rate*input_block_time)

note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

def get_rms(block):
    return np.sqrt(np.mean(np.square(block)))

def note_num_to_freq(note_num):
    return 440*2**((note_num-69)/12)

def freq_to_note_num(freq):
    return int(round(69+12*np.log2(freq/440.0)))

def note_num_to_note_name(note_num):
    return note_names[note_num % 12] + '{:.2f}'.format(note_num/12-1)

class AudioHandler(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.threshold = threshold
    
    def stop(self):
        self.stream.close()
        
    def find_input_device(self):
        dev_index = None
        for i in range(self.pa.get_device_count()):
            dev_info = self.pa.get_device_info_by_index(i)
            print('Device %{}: %{}'.format(i, dev_info['name']))
            
            for keyword in ['mic', 'input']:
                if keyword in dev_info['name'].lower():
                    print('Found an input device {} - {}'.format(i, dev_info['name']))
                    dev_index = i
                    return dev_index
                
        if dev_index == None:
            print('No preferred input found => using default input')
            
        return dev_index
    
    def open_mic_stream(self):
        dev_index = self.find_input_device()
        stream = self.pa.open(format = pyaudio.paInt16,
                             channels = 1,
                             rate = rate,
                             input = True,
                             input_device_index = dev_index,
                             frames_per_buffer = input_frames_per_block,
                             stream_callback=self.callback)
        return stream
       
    def fft_process(self, block):
        freq = np.absolute(np.fft.rfft(block, n=fft_size))
        fundamental = np.argmax(freq)/(len(freq)-1)*rate/2
        note_num = freq_to_note_num(fundamental)
        note_name = note_num_to_note_name(note_num)
        print('Frequency: {:.2f} Hz, Note Number: {}, Note Name: {}'.format(fundamental, note_num, note_name))
       
    def callback(self, in_data, frame_count, time_info, status): 
        count = len(in_data)/2
        format = '%dh' % (count)
        block = np.array(struct.unpack(format, in_data))
        self.fft_process(block)
        return (None, pyaudio.paContinue)

if __name__ == '__main__':
    audio = AudioHandler()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        audio.stop()

import os
from audioop import add, mul
import pygame
import iowave
import numpy as np
from scipy.io.wavfile import read, write
from scipy import signal



class Sample:


    def __init__(self, name):
        
        pygame.mixer.init()
        # self.mixer = pygame.mixer.music
        self.name = name
        self.filepath = 'static/samples/' + name + '.wav'
        self.outpath = 'static/samples/out_' + name + '.wav'
        
        




    def play( self, effects_list ):
        
        # producing outfile
        self.apply_all_effects( effects_list )

        # and then play
        print("Playing... ", self.filepath)
        pygame.mixer.Sound( self.outpath ).play()
        
        # myBuffer = memoryview( self.transformed_bytes )
        



    def duplicate( self ):
        
        os.system( f'cp {self.filepath} {self.outpath}' )



    def apply_all_effects( self, effects_list ):

        # self.transformed_bytes = self.org_bytes

        self.duplicate()

        for effect in effects_list:

            print('Applying', effect['code'], effect['id'])

            if effect['code'] == 'DE':
                self.delay(
                    # audio_bytes=self.transformed_bytes,
                    delay_time = effect['params']['time'],
                    factor = effect['params']['factor'],
                    repeats = effect['params']['repeats']
                )

            elif effect['code'] == 'FL':
                self.flanger(
                    # audio_bytes=self.transformed_bytes,
                    # Fs=self.params.framerate,
                    lfo_freq=effect['params']['lfo_freq'],
                    lfo_amp=effect['params']['lfo_amp']
                )
        


    def delay( self, delay_time, factor, repeats ):

        # filepath.....
        params, audio_bytes = iowave.input_wave( self.outpath )

        factor = int(factor) / 100
        repeats = int(repeats)
        delay_time = int(delay_time)

        offset = params.sampwidth * delay_time * int( params.framerate / 1000 )
        audio_bytes = audio_bytes + b'\0' * offset * repeats
        
        delayed_bytes = audio_bytes
        for i in range(1, repeats+1):
            
            of = i * offset
            beginning = b'\0' * of
            end = audio_bytes[ : -of ]
            mul_end = mul( end, params.sampwidth, factor**i )
            delayed_bytes = add( delayed_bytes, beginning + mul_end, params.sampwidth )
        
        print('Applied delay with params:',
            'delay_time =', delay_time,
            'delay_repeats =', repeats,
            'delay_factor =', factor
        )
        iowave.output_wave( delayed_bytes, params, self.outpath )
        return delayed_bytes



    def flanger( self, lfo_freq, lfo_amp ):



        lfo_freq = float(lfo_freq)
        lfo_amp = float(lfo_amp)
        

        def fl_mono( audio_bytes, Fs     ):
            length = len(audio_bytes)
            nsample = np.array(range(length))
        
            st = 2*np.pi*lfo_freq/Fs
            lfo = 2 + signal.sawtooth((nsample)*st, 0.5) # Generate triangle wave
            
            index = np.around(nsample-Fs*lfo_amp*lfo) # Read-out index
            index[index<0] = 0 # Clip delay
            index[index>(length-1)] = length-1

            flanged_bytes=np.zeros(length) # Input Signal

            rate=0.7
            for j in range(length): # For each sample
                flanged_bytes[j] = rate*np.float(audio_bytes[j]) + rate*np.float(audio_bytes[int(index[j])]) # Add delayed signal
            return flanged_bytes
        
        # print(len(audio_bytes))
        # audio_bytes = np.fromstring(audio_bytes, np.int16)
        # print(len(audio_bytes))

        Fs, data = read( self.outpath )

        bag = []

        for i in range(2):
            data_mono = [d[i] for d in data]
            data_fl = []
            data_fl = fl_mono( data_mono, Fs )
            data_fl = np.asarray(data_fl, dtype=np.int16)
            bag.append(data_fl)

        o = np.array([
            [ lt, rt ] for lt, rt in zip(bag[0], bag[1])
        ])

        write(self.outpath, Fs, o)
        

        
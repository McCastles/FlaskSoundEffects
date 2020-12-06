import math
import os
from audioop import add, mul
import pygame
import numpy as np
from scipy.io.wavfile import read, write




class Sample:


    def __init__(self, name):
        
        
        self.name = name
        self.filepath = 'static/samples/' + name + '.wav'
        self.outpath = 'static/samples/out_' + name + '.wav'
        
        self.rate, _ = read( self.filepath )
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.mixer.init()

        self.effect_mapping = {
            'DE': self.delay,
            'FL': self.flanger,
            'PH': self.phaser,
            'TR': self.tremolo,
            'DI': self.distortion,
        }
        


    def play( self, effects_list ):
        
        # pygame.mixer.Sound( self.outpath ).stop()

        # producing outfile
        self.apply_all_effects( effects_list )

        # and then play
        # print("Playing... ", self.filepath)
        # self.blink()
        # pygame.mixer.Sound( self.outpath ).play()
        
        # myBuffer = memoryview( self.transformed_bytes )
        



    '''======= EFFECTS ======='''

    def delay( self, x, params ):
        
        feedback = int(params['factor']) / 100
        delaytime = int(params['time'])
        
        # someday...
        # num = params['num']

        offset = int( self.rate / 1000 ) * delaytime * 2

        y = np.array( x )

        for i in range( offset, len(x) ):
            if (i-offset)>0:
                y[i] = x[i] + (feedback) * (x[ i-offset ])

        return y
                


    def phaser( self, x, params ):
    
        rnge = int(params['rnge'])
        sweep = float(params['sweep'])

        y = np.zeros( len(x) )
        for i in range( len(x) - rnge ):
            y[i] = x[i] + x[i + round(rnge * math.sin( (2*math.pi*i*sweep)/ self.rate ))]
        return y


    def flanger( self, x, params ):

        sweep_range = int(params['sweep_range'])
        sweep_freq = float(params['sweep_freq'])
        
        given_delay = 15
        y = np.zeros( len(x) )
        for i in range( given_delay+sweep_range, len(x) ):
            y[i] = x[i] + x[ i - given_delay - round(
                sweep_range * math.sin(2*math.pi*i*sweep_freq/self.rate)) ]
        return y


    def distortion( self, x, params ):
        clipVal = float(params['clipVal']) / 100
        y = np.zeros( len(x) )
        for i in range(len(x)):
            if x[i] > clipVal:
                y[i] = clipVal
            elif x[i] < -clipVal:
                y[i] = -clipVal
            else:
                y[i] = x[i]
        return y
                

    def tremolo( self, x, params ):
        
        freq = int(params['freq'])
        y = np.zeros( len(x) )
        for i in range( len(x) ):
            y[i] = math.sin( 2*np.pi*freq/ self.rate *i ) * x[i]
        # print(freq, self.rate)
        # print(y)
        return y





    '''======= APPLYING ======='''

    def apply_effect( self, audio, effect_code, params ):

        # print('Len before:', len(audio[:-5]))
        # print(audio[:-5])

        effect = self.effect_mapping[ effect_code ]

        bag = []
        for i in range(2):
            channel = [p[i] for p in audio]
            print(i+1, f'channel (len={len(channel)}):', channel[:5])
            applied = effect( channel, params )
            bag.append(applied)

        merged = np.array([
            [ lt, rt ] for lt, rt in zip(bag[0], bag[1])
        ])

        # print('\nmerged\n', merged[:-5])
        # print('Len after:', len(merged))
        return merged


        



    def apply_all_effects( self, effects_list ):

        # Duplicate
        os.system( f'cp {self.filepath} {self.outpath}' )

        divided = False

        for effect in effects_list:

            _, audio = read( self.outpath )


            if not divided:

                audio = audio / 32767
                divided = True

            audio = self.apply_effect( audio, effect['code'], effect['params'] )


            print('Applied', effect['code'], effect['id'], 'with params:', effect['params'])
            # if len(audio) != 0:
            write( self.outpath, self.rate, audio )
            print( 'Saved to:', self.outpath )



from audioop import add, mul
import pygame
import iowave




class Sample:


    def __init__(self, name):
        
        pygame.mixer.init()
        # self.mixer = pygame.mixer.music
        self.name = name
        self.filepath = 'static/samples/' + name + '.wav'
        self.params, self.audio_bytes = iowave.input_wave( self.filepath )




    def play( self, effects_list ):


        
                
        self.apply_all_effects( effects_list )
        print(effects_list)


        # and then play
        print("Playing... ", self.filepath)
        
        myBuffer = memoryview(
            self.audio_bytes
        )
        pygame.mixer.Sound(myBuffer).play()
        
        # self.mixer.load( self.filepath )
        # self.mixer.play()


    def apply_all_effects( self, effects_list ):
        for effect in effects_list:

            print('Applying', effect)

            if effect['code'] == 'DE':
                self.audio_bytes = self.delay(
                    audio_bytes = self.audio_bytes,
                    params = self.params,
                    delay_time = effect['params']['time'],
                    factor = effect['params']['factor'],
                    repeats = effect['params']['repeats']
                )
        


    def delay( self, audio_bytes, params, delay_time, factor, repeats ):
    
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
        return delayed_bytes

        
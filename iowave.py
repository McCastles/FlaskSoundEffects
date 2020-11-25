
import wave

def input_wave(filename, frames=10000000, v=False):
    with wave.open(filename,'rb') as wave_file:
        params=wave_file.getparams()
        audio=wave_file.readframes(frames)  
        if params.nchannels!=1:
            raise Exception("The input audio should be mono for these examples")
        if v:
            print(filename.split("/")[-1] + "\nBytes per sample: {}".format(params.sampwidth), 
            "Samples per second: {}".format(params.framerate),
            "First 10 bytes:", audio[:10], sep='\n')
    return params, audio


def output_wave(audio, params, filename):
#     filename=stem.replace('.wav','_{}.wav'.format(suffix))
    with wave.open(filename,'wb') as wave_file:
        wave_file.setparams(params)
        wave_file.writeframes(audio)
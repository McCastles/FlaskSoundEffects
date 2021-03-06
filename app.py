import copy
from sample import Sample

from flask import (Flask, flash, make_response, render_template, request,
                   session, url_for)


app = Flask(__name__)

app.debug = False


existing_modules = {
    'UA': {'id':1, 'code':'UA', 'title': 'Upload Audio', 'colorscheme': 'take_meals_opt'},
    'AE': {'id':2, 'code':'AE', 'title': 'Add Effect', 'colorscheme': 'add'},
    'PA': {'id':3, 'code':'PA', 'title': 'Play Audio', 'colorscheme': 'take_meals_opt'},
                                                                            # 0012, 0.5
    'FL': {'id':None, 'code':'FL', 'title': 'Flanger',
        'params':{'sweep_range':12, 'sweep_freq':0.5},
        'colorscheme': 'flanger'
    },

    'DE': {'id':None, 'code':'DE', 'title': 'Delay',
        'params':{'time':100, 'factor':80},
        # 'params':{'time':100, 'factor':80, 'repeats':1},
        'colorscheme': 'delay'
    },

    'DI': {'id':None, 'code':'DI', 'title': 'Distortion',
        'params':{'clipVal':5},
        'colorscheme': 'distortion'
    },

    'PH': {'id':None, 'code':'PH', 'title': 'Phaser',
        'params':{'rnge':12, 'sweep':0.3125},
        'colorscheme': 'phaser'
    },

    'TR': {'id':None, 'code':'TR', 'title': 'Tremolo',
        'params':{'freq':3},
        'colorscheme': 'tremolo'
    },
}




# Initial pipeline
storage = {
    'pipeline': [ existing_modules[code].copy() for code in ['UA', 'PA'] ],
    'effect_id': 4
}




def get_module_by_id( module_id ):
    
    for m in storage['pipeline']:
        if m['id'] == module_id:
            return m

def get_defaults_for_module( code ):
    print('getting defaults for', code)
    print(existing_modules)
    return existing_modules[code]['params'].copy()



# ROOT ENDPOINT
@app.route('/', methods=['GET', 'POST'])
def index():



    print('Request form:')
    for k, v in request.form.items():
        print('\t', k, '\t', v)

    print('Request args:')
    for k, v in request.args.items():
        print('\t', k, '\t', v)




    


    # SAMPLE CHOSEN
    sample_name = request.args.get('sample')
    if sample_name:
        
        if not storage.get('ae_index'):
            storage['ae_index'] = 1
            storage['pipeline'].insert(1, existing_modules['AE'].copy())

        storage['current_sample'] = Sample(sample_name)
        storage['sample_name'] = sample_name



    # FORM SENT
    module_id = request.args.get('module_id')
    if module_id:
        module_id = int(module_id)
    print('module_id =', module_id)
    
    if len(request.form) != 0:

        # CREATE EFFECT
        if module_id == storage['effect_id']:

            new_effect = copy.deepcopy(
                existing_modules[ request.args.get('new_effect') ]
            ) 


            new_effect['id'] = storage['effect_id']
            storage['effect_id'] += 1


            for k, v in request.form.items():
                new_effect['params'][ k ] = v

            storage['pipeline'].insert(
                storage['ae_index'],
                new_effect
            )

            storage['ae_index'] += 1


        # UPDATE EFFECT
        else:

            old_effect = get_module_by_id( module_id )
            for k, v in request.form.items():
                old_effect['params'][ k ] = v
        
            
    


    # REMOVE
    if request.args.get('remove') == '1':
        pipeline = storage['pipeline']
        # print(pipeline)
        for i, m in enumerate(pipeline):
            if m['id'] == module_id:
                storage['pipeline'] = pipeline[:i] + pipeline[i+1:]
        # print(storage['pipeline'])
        storage['ae_index'] -= 1
        

    html_for = request.args.get('html_for')
    


    # AUDIO PLAYING
    # TODO progress bar?
    
    if html_for == 'PA':

        if storage.get('current_sample') != None:

            all_effects = storage['pipeline'][1: storage['ae_index'] ]
            

            # also pass effect parameters
            storage['current_sample'].play( all_effects )
            storage['saved_msg'] = f'Saved to /static/samples/out_{storage["sample_name"]}.wav'
            html_for = 'AE'



    mem = {}
    if html_for in ['DE', 'FL', 'PH', 'DI', 'TR']:
    
        # module_id = request.args.get('module_id')
        
        if module_id:
            mem['params'] = get_module_by_id( module_id )['params']
            mem['module_id'] = module_id
        else:

            mem['params'] = get_defaults_for_module( html_for )
            mem['module_id'] = storage['effect_id']
        mem['code'] = html_for
    print('Sending mem...', mem)


    return render_template(
        'index.html',
        pipeline = storage['pipeline'],
        html_for = html_for,
        mem=mem,
        saved_msg=storage.get('saved_msg')
    )




if __name__ == '__main__':
    # Listen to every interface
    app.run(host='127.0.0.1', port=5000)

import copy
from sample import Sample

from flask import (Flask, flash, make_response, render_template, request,
                   session, url_for)


app = Flask(__name__)

app.debug = False


existing_modules = {
    'UA': {'id':1, 'code':'UA', 'title': 'Upload Audio'},
    'AE': {'id':2, 'code':'AE', 'title': 'Add Effect'},
    'PA': {'id':3, 'code':'PA', 'title': 'Play Audio'},
    'FL': {'id':None, 'code':'FL', 'title': 'Flanger'},
    'DE': {'id':None, 'code':'DE', 'title': 'Delay', 'params':{'time':250, 'factor':80, 'repeats':1}}
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
        
        storage['ae_index'] = 1
        storage['pipeline'].insert(1, existing_modules['AE'].copy())
        storage['current_sample'] = Sample(sample_name)



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
        
            
    



    # AUDIO PLAYING
    # TODO progress bar?
    html_for = request.args.get('html_for')
    if html_for == 'PA':

        if storage.get('current_sample') != None:

            all_effects = storage['pipeline'][1: storage['ae_index'] ]
            

            # also pass effect parameters
            storage['current_sample'].play( all_effects )
            html_for = 'AE'


    # Remembered params
    # mem = None
    # if module_id:
    #     for module in storage['pipeline']:
    #         if module.get('id') > 3:
    #             if str(module.get('id')) == module_id:
    #                 mem = module
    #                 break
    # print('mem =', mem)



    mem = {}
    if html_for in ['DE']:
    
        
        if module_id:
            mem['params'] = get_module_by_id( module_id )['params']
            mem['module_id'] = module_id
            # mem['command'] = 'Update'
        else:
            mem['params'] = get_defaults_for_module( html_for )
            mem['module_id'] = storage['effect_id']
        mem['code'] = html_for



    print('Sending mem...', mem)

    return render_template(
        'index.html',
        pipeline = storage['pipeline'],
        html_for = html_for,
        mem=mem
    )




if __name__ == '__main__':
    # Listen to every interface
    app.run(host='127.0.0.1', port=5000)

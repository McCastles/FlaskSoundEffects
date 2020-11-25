from sample import Sample

from flask import (Flask, flash, make_response, render_template, request,
                   session, url_for)


app = Flask(__name__)

app.debug = False


existing_modules = {
    'UA': {'code':'UA', 'title': 'Upload Audio'},
    'AE': {'code':'AE', 'title': 'Add Effect'},
    'PA': {'code':'PA', 'title': 'Play Audio'},
    'FL': {'code':'FL', 'title': 'Flanger'},
    'DE': {'code':'DE', 'title': 'Delay'}
    

}


# Initial pipeline
storage = {
    'pipeline': [ existing_modules[code] for code in ['UA', 'PA'] ],
}





# ROOT ENDPOINT
@app.route('/')
def index():


    



    sample_name = request.args.get('sample')
    if sample_name:
        storage['pipeline'] = [ existing_modules[code] for code in ['UA', 'AE', 'PA'] ]
        storage['current_sample'] = Sample(sample_name)
        storage['ae_index'] = 1




    new_effect = request.args.get('new_effect')
    print("new_effect =", new_effect)

    if new_effect != None:
        storage['pipeline'].insert( storage['ae_index'], existing_modules[ new_effect ] )
        storage['ae_index'] += 1
    




    html_for = request.args.get('html_for')
    print("html_for =", html_for)

    # TODO progress bar?
    if html_for == 'PA':

        if storage.get('current_sample') != None:

            all_effects = storage['pipeline'][1: storage['ae_index'] ]
            

            # also pass effect parameters
            storage['current_sample'].play( all_effects )
            html_for = 'AE'

        

    return render_template(
        'index.html',
        pipeline = storage['pipeline'],
        html_for = html_for
    )




if __name__ == '__main__':
    # Listen to every interface
    app.run(host='127.0.0.1', port=5000)

# from Module import Module

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
pipeline = [
    existing_modules[code] for code in ['UA', 'AE', 'PA']
]
ae_index = 1





# ROOT ENDPOINT
@app.route('/')
def index():


    global ae_index

    html_for = request.args.get('html_for')
    print("html_for =",html_for)

    new_effect = request.args.get('new_effect')
    print("new_effect =",new_effect)
    
    if new_effect != None:
        pipeline.insert( ae_index, existing_modules[ new_effect ] )
        ae_index += 1

    
    





    return render_template(
        'index.html',
        pipeline = pipeline,
        html_for = html_for
    )




if __name__ == '__main__':
    # Listen to every interface
    app.run(host='127.0.0.1', port=5000)

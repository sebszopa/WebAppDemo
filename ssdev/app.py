from flask import Flask, render_template

app = Flask(__name__)

# Hone Page
@app.route('/')

# rendering idex.html as home page
# the index.html file uses includ function to dynamically create website menu and content page
# it give and option to keep the code clean and tidy

def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8081, debug=True, use_reloader=False)
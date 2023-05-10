from flask import Flask, render_template, request, redirect, url_for
import hvac
import os
from dotenv import load_dotenv

# Load the environment variables from var.env
load_dotenv('var.env')

# Get the Vault address and token from the environment variables
vault_address = os.environ['VAULT_ADDRESS']
vault_token = os.environ['VAULT_TOKEN']

# Initialize the Vault client with the 'admin' namespace
client = hvac.Client(url=vault_address, token=vault_token, namespace="admin")

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/read_secret', methods=['GET', 'POST'])
def read_secret():
    if request.method == 'POST':
        base_path = request.form.get('path')
        first, second = base_path.split('/', 1)
        secret_path = '{}/data/{}'.format(first, second)
        try:
            secret_response = client.read(secret_path)
            secret_data = secret_response['data']['data']
            return render_template('result.html', message="Secret data: {}".format(secret_data))
        except Exception as e:
            return render_template('result.html', message="Error fetching secret: {}".format(e))
    return '''
        <form method="post">
            Path: <input type="text" name="path"><br>
            <input type="submit" value="Read Secret">
        </form>
    '''

@app.route('/write_secret', methods=['GET', 'POST'])
def write_secret():
    if request.method == 'POST':
        base_path = request.form.get('path')
        first, second = base_path.split('/', 1)
        secret_path = '{}/data/{}'.format(first, second)
        key = request.form.get('key')
        value = request.form.get('value')
        try:
            secret_response = client.read(secret_path)
            if secret_response:
                data = secret_response['data']['data']
                data[key] = value
            else:
                data = {key: value}
            client.write(secret_path, data=data)
            return render_template('result.html', message="Secret written successfully.")
        except Exception as e:
            return render_template('result.html', message="Error writing secret: {}".format(e))
    return '''
        <form method="post">
            Path: <input type="text" name="path"><br>
            Key: <input type="text" name="key"><br>
            Value: <input type="text" name="value"><br>
            <input type="submit" value="Write Secret">
        </form>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

from flask import Flask, render_template, request, redirect, url_for
import hvac
import os
from dotenv import load_dotenv
from requests import post

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



from requests import post

@app.route('/generate_secret_voucher', methods=['GET', 'POST'])
def generate_secret_voucher():
    if request.method == 'POST':
        base_path = request.form.get('path')
        first, second = base_path.split('/', 1)
        secret_path = '{}/data/{}'.format(first, second)
        try:
            secret_response = client.read(secret_path[4:])
            secret_data = secret_response['data']['data']

            # Wrap the secret data using the Vault API
            headers = {'X-Vault-Token': vault_token, 'X-Vault-Namespace': 'admin', 'X-Vault-Wrap-TTL': '120'}
            wrap_response = post(vault_address + '/v1/sys/wrapping/wrap', headers=headers, json=secret_data)
            wrap_token = wrap_response.json()['wrap_info']['token']
            wrap_url = url_for('unwrap_secret', wrap_token=wrap_token, _external=True)
            return render_template('result.html', message="Secret Voucher URL: {}".format(wrap_url))
        except Exception as e:
            return render_template('result.html', message="Error generating secret voucher: {}".format(e))
    return '''
        <form method="post">
            Path: <input type="text" name="path"><br>
            <input type="submit" value="Generate Secret Voucher">
        </form>
    '''




@app.route('/unwrap_secret/<wrap_token>', methods=['GET'])
def unwrap_secret(wrap_token):
    try:
        # Unwrap the secret using the Vault API
        headers = {'X-Vault-Token': vault_token, 'X-Vault-Namespace': 'admin'}
        payload = {'token': wrap_token}
        unwrap_response = post(vault_address + '/v1/sys/wrapping/unwrap', headers=headers, json=payload)
        secret_data = unwrap_response.json()['data']
        return render_template('result.html', message="Unwrapped Secret Data: {}".format(secret_data))
    except Exception as e:
        return render_template('result.html', message="Error unwrapping secret: {}".format(e))




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

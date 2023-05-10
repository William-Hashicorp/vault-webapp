from flask import Flask, render_template, request, redirect, url_for
import hvac

app = Flask(__name__)

# Update these values with your Vault address and token
vault_address = "https://zero-trust-123860-public-vault-8df837fe.aef8576b.z1.hashicorp.cloud:8200"
vault_token = "hvs.xxx"

# Initialize the Vault client with the 'admin' namespace
client = hvac.Client(url=vault_address, token=vault_token, namespace="admin")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/read_secret', methods=['GET', 'POST'])
def read_secret():
    if request.method == 'POST':
        secret_path = request.form.get('path')
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
        secret_path = request.form.get('path')
        key = request.form.get('key')
        value = request.form.get('value')
        try:
            client.write(secret_path, data={key: value})
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

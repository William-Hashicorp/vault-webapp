from flask import Flask
import hvac

app = Flask(__name__)

# Update these values with your Vault address and token
vault_address = "https://zero-trust-123860-public-vault-8df837fe.aef8576b.z1.hashicorp.cloud:8200"
vault_token = "hvs.CAESIDLXrYDNb5JNglYYmr5Yv9q_1TLHFnxfRPnnjjq_kWm7GicKImh2cy4zWnh5a2czNE9kZHVlenJiTThHd1ZSdHEuVzhqVUoQ4xM"

# Initialize the Vault client
client = hvac.Client(url=vault_address, token=vault_token, namespace="admin")

@app.route('/get_secret')
def get_secret():
    secret_path = 'secret/data/my-secret'  # Update this path with your secret path
    try:
        secret_response = client.read(secret_path)
        secret_data = secret_response['data']['data']
        return "Your secret data: {}".format(secret_data)
    except Exception as e:
        return "Error fetching secret: {}".format(e)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

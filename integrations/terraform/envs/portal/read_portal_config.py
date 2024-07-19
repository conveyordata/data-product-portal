import os
import requests
import yaml

# API key of the data product portal
API_KEY = os.getenv('API_KEY')
# URL of where to contact the portal API
API_HOST = "https://portal.acme.com"
FOLDER = './'
proxies = {}

HEADERS = {
    "x-key": f"{API_KEY}"
}
session = requests.Session()
session.proxies = proxies
session.headers = HEADERS

def get_data_products():
    result = session.get(f"{API_HOST}/api/data_products")
    if 'correlation_id' in result.json():
        print(result.json())
        exit(1)
    data_products = {}
    for data_product_info in result.json():
        data_product = session.get(f"{API_HOST}/api/data_products/{data_product_info.get('id')}")
        data_product = data_product.json()
        datasets = []
        for dataset in data_product.get("dataset_links"):
            datasets.append(dataset.get('dataset').get('external_id'))

        members = {}
        for member in data_product.get("memberships"):
            # EXT is never present in user name?"
            role = 'admin' if member.get('role') == 'owner' else 'member'
            members[member.get('user').get('email')] = role
        data_products[data_product.get("external_id")] = {"description": data_product.get("description"), "read_datasets": datasets, "users": members}
    with open(os.path.join(FOLDER, 'config', 'data_product_glossary', 'data_product_glossary.yaml'), 'w') as f:
        yaml.dump(data_products, f, allow_unicode=True)

def get_datasets():
    # TODO Only use approved datasets instead of all requests and rejects
    result = session.get(f"{API_HOST}/api/datasets")

    data_products = {}
    for data_product_info in result.json():
        data_product = session.get(f"{API_HOST}/api/datasets/{data_product_info.get('id')}")
        data_product = data_product.json()
        owners = []
        for owner in data_product.get("owners"):
            owners.append(owner.get('email'))
        data_products[data_product.get("external_id")] = {"data_objects": [data_product.get("external_id")], "owner": owners[0]} # TODO Fix better use of data objects once implemented
    with open(os.path.join(FOLDER, 'config', 'data_glossary', 'datasets.yaml'), 'w') as f:
        yaml.dump(data_products, f, allow_unicode=True)

def generate():
    get_data_products()
    get_datasets()

if __name__ == '__main__':
    generate()
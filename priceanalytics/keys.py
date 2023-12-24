import json, pathlib
p = pathlib.Path(__file__).parent.resolve().parent.resolve()
fn = str(p) + '/secret.json'
obj = ""
with open(fn, 'r') as f:
    obj = json.loads(f.read())
API_KEY = obj['ApiKey']
SECRET_KEY = obj['SecretKey']

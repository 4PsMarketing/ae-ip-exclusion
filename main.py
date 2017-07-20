from __future__ import absolute_import
from flask import Flask, render_template, request, Response
from google.cloud import datastore

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <html>
            <body>
                <p>Use this format to check a specific IP: <a href="/check/192.168.0.101">/check/192.168.0.101</a></p>
                <br>
                <p>Use this format to check the user's IP: <a href="/check">/check</a></p>
                <br>
                <a href="/upload">Upload a CSV of IPs</a>
                <br>
                <p>Use this format to add a single IP: /upload/ip/i.p.addr.ess</p>
            </body>
        </html>
    '''

@app.route('/check/<ip_address>')
def check(ip_address):
    datastore_client = datastore.Client()
    kind = 'IP'
    query = datastore_client.query(kind=kind)
    query.add_filter('address', '=', ip_address)
    results = list(query.fetch())
    if results:
        r = Response('True')
        r.headers['Access-Control-Allow-Origin'] = '*'
        return r
    else:
        r = Response('False')
        r.headers['Access-Control-Allow-Origin'] = '*'
        return r
    
@app.route('/check')
def check_ip():
    ip = request.environ['REMOTE_ADDR']
    datastore_client = datastore.Client()
    kind = 'IP'
    query = datastore_client.query(kind=kind)
    query.add_filter('address', '=', ip)
    results = list(query.fetch())
    if results:
        r = Response('True')
        r.headers['Access-Control-Allow-Origin'] = '*'
        return r
    else:
        r = Response('False')
        r.headers['Access-Control-Allow-Origin'] = '*'
        return r

@app.route('/upload/ip/<ip_address>')
def add_to_datastore(ip_address):
    #if request.headers['auth']:
    import datetime
    datastore_client = datastore.Client()
    key = datastore_client.key('IP')
    entity = datastore.Entity(key = key)
    entity['address'] = ip_address
    entity['dateAdded'] = datetime.datetime.now()
    datastore_client.put(entity)
    return ip_address + ' added'

@app.route('/upload')
def upload():
    return """
        <html>
            <body>
                <h1>Upload Some New IPs</h1>

                <form action="/upload/file" method="post" enctype="multipart/form-data">
                    <input type="file" name="data_file" />
                    <input type="submit" value="Upload File"/>
                </form>
            </body>
        </html>
    """

@app.route('/upload/file', methods =['POST'])
def upload_file():
    data_file = request.files['data_file']
    
    if not data_file:
        return 'No File'
    else:
        r = data_file.read().split(',')
        ip_list = r
        
        import datetime
        datastore_client = datastore.Client()
        ip_add_status = []
        for ip_address in ip_list:
            
            if ip_address:
                
                #handle some funky spacing on the last entry
                ip_address.replace(' ', '')
                
                key = datastore_client.key('IP')
                entity = datastore.Entity(key = key)
                entity['address'] = ip_address.decode('utf-8')
                entity['dateAdded'] = datetime.datetime.now()
                datastore_client.put(entity)
                ip_add_status.append('IP: ' + ip_address)
               
        return render_template('sample.html', list = ip_add_status)
    
    
from flask import Flask, request, render_template, jsonify
import requests
import json
import random
import datetime
app = Flask(__name__)

metrics = dict()


def get_params():
    li = list()
    r = requests.get(url="http://127.0.0.1:5000/generate")
    data = r.json()
    cat_no = str(data['second_data'])
    cat_id = data['data'][cat_no]

    r = requests.get(url="https://api.thecatapi.com/v1/images/search?breed_ids=" + cat_id)
    second_data = r.json()
    second_data = dict(second_data[0])
    info = dict(second_data['breeds'][0])

    li.append(info['name'])
    li.append(second_data['url'])
    li.append(info['temperament'])
    li.append(info['description'])
    li.append("#FF"+str(cat_no)+"30")

    return li


def get_metric(req):

    metric = dict()
    metric['Status'] = req.status_code
    metric['Request'] = str(req.request).replace("<PreparedRequest ","").replace(">","")
    metric['Content-Type'] = req.url

    datetimeFormat = '%a, %d %b %Y %H:%M:%S %Z'
    first_date = req.headers['Date']
    current_date = datetime.datetime.now()
    diff = current_date \
           - datetime.datetime.strptime(first_date, datetimeFormat)

    metric['Latency'] = diff.microseconds
    metrics[str(len(metrics.keys())+1)] = metric
    f = open("log.txt", "a")
    f.write(first_date)
    f.write("\n")
    for i in metric:
        text = " " + str(i) + ": " + str(metric[i]) + "\n"
        f.write(str(text))


@app.route('/')
def hello():
    return render_template("index.html", param=get_params())

@app.route('/metrics')
def return_metrics():
    return jsonify(metrics)

@app.route('/cats')
def list_of_cats_name():
    r = requests.get(url="https://api.thecatapi.com/v1/breeds")
    get_metric(r)
    data = r.json()
    di = dict()
    count = 0
    for i in data:
        di[count] = i['id']
        count += 1
    return json.dumps(di)


@app.route('/random')
def get_rand():
    n = request.args.get('n')
    # data = { "jsonrpc": "2.0", "method": "generateIntegers", "params": {"apiKey": open("config.txt", "r").read(), "n": 1, "min": 0, "max": n}, "id": 42}
    # data_set = json.dumps(data)
    # response = requests.post('https://api.random.org/json-rpc/1/invoke', data_set)
    # get_metric(response)
    #di = dict()
    #di['number'] = response.json()['result']['random']['data'][0]
    return json.dumps(random.randrange(0, int(n)+1))

@app.route('/generate')
def generate():
    di = dict()
    r = requests.get(url="http://127.0.0.1:5000/cats")
    get_metric(r)
    data = r.json()
    n = list(data.keys())[-1]
    r = requests.get(url="http://127.0.0.1:5000/random?n=" + str(n))
    get_metric(r)
    second_data = r.json()

    di['data'] = data
    di['second_data'] = second_data
    return di


if __name__ == '__main__':
    app.run(threaded=True)

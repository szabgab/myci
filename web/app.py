from flask import Flask, request, render_template
import datetime
import os
import re
import json
import yaml

app = Flask(__name__)

with open('server.yml') as fh:
    server = yaml.load(fh)

@app.route("/")
def main():
    jobs = sorted(filter(lambda d: re.search(r'\A\d+\Z', d), os.listdir(server['workdir'])), reverse=True, key=int)
    count = min(len(jobs), 10)
    data = []
    for a in jobs[0:count]:
        results_file = os.path.join(server['db'], a + '.json')
        if os.path.exists(results_file):
            with open(results_file) as fh:
                results = json.load(fh)
                if 'id' not in results:
                    results['id'] = a
            data.append(results)
    return render_template('main.html', results = data[0:count])

@app.route("/job/<jobid>")
def job(jobid):
    if not re.search(r'\A\d+\Z', jobid):
        return "Invalid jobid {}".format(jobid)

    results_file = os.path.join(server['db'], jobid + '.json')
    if os.path.exists(results_file):
        with open(results_file) as fh:
            results = json.load(fh)
        return render_template('job.html', results = results, jobid = jobid)
    return "Could not find results"

@app.route("/raw/<jobid>")
def raw(jobid):
    if not re.search(r'\A\d+\Z', jobid):
        return "Invalid jobid {}".format(jobid)

    results_file = os.path.join(server['db'], jobid + '.json')
    if os.path.exists(results_file):
        with open(results_file) as fh:
            raw = fh.read()
            raw = raw.replace('<', '&lt;')
            raw = raw.replace('>', '&gt;')
            return '<pre>' + raw + '</pre>'

    return "Could not find the results of {}".format(jobid)

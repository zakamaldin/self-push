#!/usr/bin/env python3
import os
import subprocess
import sys
from pathlib import Path
import http.client
import json
from datetime import date
import uuid

COMMIT_MESSAGE = 'Default commit message'
PATH_TO_TOKEN = Path.home() / Path('github_token.txt')
TOKEN = ''
with open(PATH_TO_TOKEN) as f:
    TOKEN = f.read().splitlines()[0]


MASTER_BRANCH = 'main'
OWNER = 'zakamaldin'
REPO = 'self-push'
HOST = 'api.github.com'
FIX_BRANCH = f'fix_{date.today().strftime("%d_%m_%Y")}_{uuid.uuid4().hex.upper()[0:6]}'


BODY = json.dumps({'title': f'New fix from {FIX_BRANCH}','body':'New fix from production server','head': FIX_BRANCH,'base': MASTER_BRANCH})

if len(sys.argv) <= 1:
    exit('ERROR: you MUST enter the commit message as a script parameter')
else:
    COMMIT_MESSAGE = sys.argv[1]

def warn(text):
    print('='*80)
    print(text)
    print('='*80)
    print()

warn(f'Switching to master branch {MASTER_BRANCH}')
subprocess.call(f'git checkout {MASTER_BRANCH}'.split())

warn(f'Creating new banch from master: {FIX_BRANCH}')
subprocess.call(f'git checkout -b {FIX_BRANCH}'.split())

warn('Add all new changes')
subprocess.call('git add .'.split())

warn(f'Commmit with message: {COMMIT_MESSAGE}')
subprocess.call(f"git commit -m '{COMMIT_MESSAGE}'".split())

warn(f'Push new branch {FIX_BRANCH}')
subprocess.call(f'git push origin {FIX_BRANCH}'.split())

warn('Open Pull Request via REST API')
conn = http.client.HTTPSConnection(HOST)
headers = {
    'Host': HOST,
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {TOKEN}',
    'User-Agent': 'request'
    }

conn.request('POST', f'/repos/{OWNER}/{REPO}/pulls', headers=headers, body=BODY)

response = conn.getresponse()

warn('Merge Pull Request via REST API')
PULL_REQUEST_NUMBER = json.loads(response.read().decode())['number']

conn.request('PUT', f'/repos/{OWNER}/{REPO}/pulls/{PULL_REQUEST_NUMBER}/merge', headers=headers)

response = conn.getresponse()


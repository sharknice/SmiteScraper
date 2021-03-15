import json
import urllib.request
import re

with open('item_result.json') as f:
    data = json.load(f)

items = []

sourceItems = data



for sourceItem in sourceItems:
    if sourceItem['stacks']:

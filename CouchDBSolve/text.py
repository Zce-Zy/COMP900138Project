import json
import pandas as pd
from textblob import TextBlob

twitter = pd.read_json("draft1.json")
for index, row in twitter.iterrows():
    print(row[2])
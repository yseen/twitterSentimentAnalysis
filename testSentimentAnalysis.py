#test smileyface transformers sentiment analysis on hardcoded text (variable text). Results printed to standard output.

from transformers import pipeline
import time
#text = "we love you"
#text = "es geht mir gut."
text = "es ist schlecht"
#text = "it is bad"
#text = "ich bin traurig"
#text = "i am sad."
#text = "it is bad"
print("loading pipline")
start = time.time()
nlp = pipeline("sentiment-analysis")
end = time.time()
elapsed = end - start
print(f"pipeline loaded. Time to complete: {elapsed}")

print("Running sentiment analysis")
start = time.time()
result = nlp(text)[0]
end = time.time()
elapsed = end - start
print(f"sentiment analysis completed. Time to complete: {elapsed}")


print(f"label: {result['label']}, with score: {round(result['score'], 4)}")
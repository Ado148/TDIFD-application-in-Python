import os
import math
import json
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
from collections import Counter, defaultdict

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'docs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # set the upload folder



def compute_tf(word_freq, words_cnt):
    tf = {}
    for word, freq in word_freq.items():
        tf[word] = freq / words_cnt
    return tf

def compute_idf(res_folder): 
    docs = []
    for filename in os.listdir(res_folder): # list all files in the result folder
        if filename.endswith('.json'):
            with open(os.path.join(res_folder, filename), 'r') as f:
                docs.append(filename) # add the filename to the list of documents
    total_docs_cnt = len(docs) # total number of documents
    
    # count how many documents each word appears in
    word_doc_freq = defaultdict(int)
    for filename in docs:
        with open(os.path.join(res_folder, filename), 'r') as f:
            unique_words_in_current_doc = set(json.load(f))
            for word in unique_words_in_current_doc:
                word_doc_freq[word] += 1
                
    idf = {}
    for word, freq in word_doc_freq.items():
        idf[word] = math.log(1 + (total_docs_cnt / (1 + freq)))
    return idf
        


@app.route('/', methods=['GET', 'POST'])

def index():
    if request.method == 'POST':
        file = request.files['file']
        if file.filename == '':
            return 'No file selected'
        file_name = secure_filename(file.filename) # secure the filename before saving
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)
        file.save(file_path)
        
        with open(file_path, 'r') as f:
            text = f.read()
        
        words = text.split() # split the text into words
        word_frequency = Counter(words) # count the frequency of each word in file - tf
        word_cnt = len(words) # get the total number of words in file
        
        # save the unique words of the current doc for global IDF
        doc_words_path = os.path.join(RESULT_FOLDER, file_name +  '.json')
        if not os.path.exists(doc_words_path):
            with open(doc_words_path, 'w') as f:
                json.dump(list(set(words)), f)
        
        tf = compute_tf(word_frequency, word_cnt)
        idf = compute_idf(RESULT_FOLDER)
        
        data = []
        for word in tf:
            word_data = {
                'word': word,
                'tf': round(tf[word], 6),
                'idf': round(idf.get(word, 0.0), 6)
            }
            data.append(word_data)
            
        return render_template('index.html', data=data[:50])
    
    return render_template('index.html', data=None)     
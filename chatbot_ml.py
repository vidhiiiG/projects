# -*- coding: utf-8 -*-
"""Chatbot_ml

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/14u_Wey2W8gvXl-uZk_kEgMl5jQOh0rwe

# Import the libraries
"""

import tensorflow
import nltk
nltk.download('punkt')
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout , Activation, Flatten , Conv2D, MaxPooling2D
from tensorflow.keras.optimizers import SGD
import random
import json
import pickle

"""# Declaring Constants"""

words=[]
labels = []
docs = []
ignore_list = ['?', '!']

"""# Loading our dataset that is intents.json file"""

dataset = open('/content/intents.json').read()
intents = json.loads(dataset)

"""## Preprocess Data"""

for intent in intents['intents']:
    for pattern in intent['patterns']:
        #tokenize each word
        word_token = nltk.word_tokenize(pattern)
        words.extend(word_token)
        #add documents in the corpus
        docs.append((word_token, intent['tag']))
        # add to our labels list
        if intent['tag'] not in labels:
            labels.append(intent['tag'])

"""# Lemmatizing Each word"""

# lemmatize each word, and sort words by removing duplicates:
nltk.download('wordnet')
words = [lemmatizer.lemmatize(word.lower()) for word in words if word not in ignore_list]
words = sorted(list(set(words)))
# sort labels:
labels = sorted(list(set(labels)))

"""# Save words and labels list (using pickle)"""

pickle.dump(words,open('words.pkl','wb'))
pickle.dump(labels,open('labels.pkl','wb'))

"""# Creating our Training data"""

# creating our training data:
training_data = []
# creating an empty array for our output (with size same as length of labels):
output = [0]*len(labels)
for doc in docs:
    bag_of_words = []
    pattern_words = doc[0]
    #lemmatize pattern words:
    pattern_words = [lemmatizer.lemmatize(word.lower()) for word in pattern_words]
    
    for w in words:
        if w in pattern_words:
            bag_of_words.append(1)
        else:
            bag_of_words.append(0)
            
    output_row = list(output)
    output_row[labels.index(doc[1])] = 1
    
    training_data.append([bag_of_words,output_row])

"""# Shuffle and Convert our Training data to array"""

# convert training_data to numpy array and shuffle the data:
random.shuffle(training_data)
training_data = np.array(training_data)

"""# Splitting the data into x_train and y_train"""

# Now we have to create training list:
x_train = list(training_data[:,0])
y_train = list(training_data[:,1])

"""# Model Creation"""

# Creating Model:
model = Sequential()
model.add(Dense(128, input_shape=(len(x_train[0]),), activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(64, activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(len(y_train[0]), activation='softmax'))

"""# Model Summary"""

model.summary()

"""# Compile and Fit our model to find the accuracy"""

sgd_optimizer = SGD(lr=0.01, decay=1e-6, momentum=0.9, nesterov=True)
model.compile(loss='categorical_crossentropy', optimizer=sgd_optimizer, metrics=['accuracy'])

# fit the model 
history = model.fit(np.array(x_train), np.array(y_train), epochs=200, batch_size=5, verbose=1)

"""# Save the model"""

model.save('chatbot_Application_model.h5', history)

"""# Final step to predict the sentences and get responses"""

import nltk
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
import pickle
import numpy as np
import json
import random
from keras.models import load_model
model = load_model('chatbot_Application_model.h5')
intents = json.loads(open('intents.json').read())
words = pickle.load(open('words.pkl','rb'))
labels = pickle.load(open('labels.pkl','rb'))

#To run our model we have to provide the input in the same way as we have done while creating our model.
 #So for this we have created a function which will perform text operations and then predict the label.
def bank_of_words(s,words, show_details=True):
    bag_of_words = [0 for _ in range(len(words))]
    sent_words = nltk.word_tokenize(s)
    sent_words = [lemmatizer.lemmatize(word.lower()) for word in sent_words]
    for sent in sent_words:
        for i,w in enumerate(words):
            if w == sent:
                bag_of_words[i] = 1
    return np.array(bag_of_words)

def predict_label(s, model):
    # filtering out predictions
    pred = bank_of_words(s, words,show_details=False)
    response = model.predict(np.array([pred]))[0]
    ERROR_THRESHOLD = 0.25
    final_results = [[i,r] for i,r in enumerate(response) if r>ERROR_THRESHOLD]
    final_results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in final_results:
        return_list.append({"intent": labels[r[0]], "probability": str(r[1])})
    return return_list

#After prediction, now we will create a function which will give responses from the list of intents.
def Response(ints, intents_json):
    tags = ints[0]['intent']
    list_of_intents = intents_json['intents']
    for i in list_of_intents:
        if(i['tag']== tags):
            response = random.choice(i['responses'])
            break
    return response

def chatbot_response(msg):
    ints = predict_label(msg, model)
    response = Response(ints, intents)
    return response

#Now after responses in this we have created a function which will make user and Bot interact:
def chat():
    print("Start chat with ChatBot of ProjectGurukul")
    while True:
        inp = input("You: ")
        if inp.lower() == 'quit':
            break
        response = chatbot_response(inp)
        print("\n BOT: " + response + '\n\n')

chat()
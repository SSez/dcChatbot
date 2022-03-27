# coding=utf-8
import data_controller as d
import nltk

from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()

import numpy
import pickle
import tensorflow as tf
import os
import pandas as pd

def predict(s, words):
    bag = [0 for _ in range(len(words))]
    s_words = nltk.word_tokenize(s)
    s_words = [stemmer.stem(word.lower()) for word in s_words]
    for s in s_words:
        for i, w in enumerate(words):
            if w == s:
                bag[i] = 1
    return numpy.array(bag)

def retrain(epoch, batch, option):
    # Option 0 = patterns, Option 1 = responses
    pickle_name = ""
    model_name = ""
    if option == 0:
        type = "patterns"
        pickle_name = "models/data_patterns.pickle"
        model_name = "models/model_patterns.h5"
    elif option == 1:
        type = "responses"
        pickle_name = "models/data_responses.pickle"
        model_name = "models/model_responses.h5"

    try:
        os.remove(pickle_name)
        os.remove(model_name)
    except:
        pass

    data = d.get_data()
    words = []  #words list
    labels = []  #labels list etc
    docs_x = []
    docs_y = []
    
    for intent in data:
        for x in intent[type]:
            if x:
                wrds = nltk.word_tokenize(x)
                words.extend(wrds)
                docs_x.append(wrds)
                docs_y.append(intent["tag"])

            if intent["tag"] not in labels:
                labels.append(intent["tag"])

    #how many words it has seen
    words = [stemmer.stem(w.lower()) for w in words if w != "?" or "!" or w != "," ]
    words = sorted(list(set(words)))
    labels = sorted(labels)
    training = []
    output = []
    out_empty=[0 for _ in range(len(labels))]

    for x, doc in enumerate(docs_x):
        bag = []
        wrds = [stemmer.stem(w) for w in doc]
        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1
        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)
    with open(pickle_name, "wb") as f:
        pickle.dump((words, labels, training, output), f) # Saving data.

    tf.compat.v1.reset_default_graph()
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Dense(8, activation='relu', input_shape=(len(training[0]),))) # hidden
    model.add(tf.keras.layers.Dense(8, activation="relu")) # hidden
    model.add(tf.keras.layers.Dense(len(output[0]), activation="softmax")) # activate

    model.compile(optimizer=tf.keras.optimizers.Adam(0.01), loss=tf.keras.losses.BinaryCrossentropy(from_logits=True), metrics=['accuracy']) # CategoricalCrossentropy
    model.fit(training, output, epochs=int(epoch), batch_size=int(batch) )
    model.save(model_name)
    model.summary()

def responseModel(data, message):
    words = []
    docs = []
    labels = []
    docs_y = []
    res_list = []
    count = 0
    for response in data:
        if response:
            count += 1
            res_list.append({ "tag": count, "response": response })

    epoch = count * 2
    batch = count / 2
    for intent in res_list:
        for x in intent["response"]:
            wrds = nltk.word_tokenize(x)
            words.extend(wrds)
            docs.append(wrds)
            docs_y.append(intent["tag"])
            if intent["tag"] not in labels:
                labels.append(intent["tag"])

    #how many words it has seen
    words = [stemmer.stem(w.lower()) for w in words if w != "?" or "!" or w != "," ]
    words = sorted(list(set(words)))
    labels = sorted(labels)
    training = []
    output = []
    out_empty=[0 for _ in range(len(labels))]
    
    for x, doc in enumerate(docs):
        bag = []
        wrds = [stemmer.stem(w) for w in doc]
        for w in words:
            if w in wrds:
                bag.append(1)
            else:
                bag.append(0)
        output_row = out_empty[:]
        output_row[labels.index(docs_y[x])] = 1

        training.append(bag)
        output.append(output_row)

    training = numpy.array(training)
    output = numpy.array(output)

    tf.compat.v1.reset_default_graph()
    model_response = tf.keras.Sequential()
    model_response.add(tf.keras.layers.Dense(8, activation='relu', input_shape=(len(training[0]),))) # hidden
    model_response.add(tf.keras.layers.Dense(8, activation="relu")) # hidden
    model_response.add(tf.keras.layers.Dense(len(output[0]), activation="softmax")) # activate

    model_response.compile(optimizer=tf.keras.optimizers.Adam(0.01), loss=tf.keras.losses.BinaryCrossentropy(from_logits=True), metrics=['accuracy']) # CategoricalCrossentropy
    model_response.fit(training, output, epochs=int(epoch), batch_size=int(batch) )

    result = pd.DataFrame([predict(message, words)], dtype=float, index=['input'])
    results = model_response.predict([result])[0]

    results_index = numpy.argmax(results)
    tag = int(labels[results_index])
    prob = results[results_index]
    print ( str("[RESPONSE] Tag: ") + str(tag) )
    print ( str("[RESPONSE] Probability: ") + str(prob) )
    for tg in res_list:
        if tg["tag"] == tag:
            res = tg['response']
    return res
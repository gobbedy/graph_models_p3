#!/usr/bin/python3.4
import numpy as np
from keras import regularizers
from keras.layers import Input, Dense
from keras.models import Model
import csv
import pickle
import os.path



# each column is an entity

# TODO: don't hardcode these values
# 13870 entity vectors of 1000 dimensions each
fname_entity_row_dict='entity_row_dict.pkl'
fname_entity_vecs='entity_vecs.npy'

# GET TABLE OF word2vec VECTORS (maps relation code -> word2vec vector)
if not os.path.isfile(fname_entity_row_dict) or not os.path.isfile(fname_entity_vecs):

    entities = np.zeros((13870,1000))
    #entities = np.array([])
    entity_row_dict = {}
    entity_cnt=0
    with open('data/pruned_vec.csv', newline='') as csvfile:
         #entities_reader = csv.reader(csvfile, delimiter=', ') # use this if space separated only
         entities_reader = csv.reader((line.replace(', ', ' ') for line in csvfile), delimiter=' ')
         for line in entities_reader:
             # extract entity from line
             entity = np.asarray(list(map(float, line[1:])))

             # store entity vector in numpy entities matrix
             entities[entity_cnt] = entity

             # store entity row in dictionary
             entity_row_dict[line[0]] = entity_cnt

             entity_cnt = entity_cnt + 1

    np.save(fname_entity_vecs, entities)

    with open(fname_entity_row_dict, 'wb') as f:
        pickle.dump(entity_row_dict, f)


    #print(entity_cnt)

else:

    entities=np.load(fname_entity_vecs)
    with open (fname_entity_row_dict, 'rb') as f:
        entity_row_dict = pickle.load(f)

# GET TABLE OF ONE-HOT VECTORS FOR EACH RELATIONSHIP
# TODO: don't hardcode these values
# 1311 relation vectors of 1311 dimensions each (one-hot vectors) -- each row is a relationship vector
fname_relationship_row_dict='relationship_row_dict.pkl'
fname_relationship_vecs='relationship_vecs.npy'
if not os.path.isfile(fname_relationship_row_dict) or not os.path.isfile(fname_relationship_vecs):

    relationships = np.zeros((1311,1311))
    relationship_row_dict = {}
    relationship_cnt=0
    with open('data/pruned_relations.txt', newline='') as rfile:
         for line in rfile:
             # initialize relationship vector to all zeros
             relationship = np.zeros((1311))
             
             # set 1-hot value to current line number
             relationship[relationship_cnt] = 1

             # store relationship vector in numpy relationships matrix
             relationships[relationship_cnt] = relationship

             # store relationship row in dictionary
             relationship_row_dict[line[:-1]] = relationship_cnt

             relationship_cnt = relationship_cnt + 1

    np.save(fname_relationship_vecs, relationships)

    with open(fname_relationship_row_dict, 'wb') as f:
        pickle.dump(relationship_row_dict, f)


    #print(relationship_cnt)

else:

    relationships=np.load(fname_relationship_vecs)
    with open (fname_relationship_row_dict, 'rb') as f:
        relationship_row_dict = pickle.load(f)
        


# GET HEAD, RELATIONSHIP TRAINING VECTORS
# TODO: don't hardcode these values
# 388770 training triples each with a head (1000-dimensional word2vec vector) and relationship (1311-dimensional one-hot vector)
# each row represents one head, relation vector
fname_head_relation_training_vecs='head_relation_training_vecs.npy'
if not os.path.isfile(fname_head_relation_training_vecs):

    head_relation_vecs = np.zeros((388770,2311))
    head_relation_vec_cnt=0
    with open('data/train_pruned.txt', newline='') as tfile:
         training_reader = csv.reader(tfile, delimiter='\t')
         for line in training_reader:
             # extract head entity
             head_entity = entities[entity_row_dict[line[0]]]
             
             # extract relationship
             relationship = relationships[relationship_row_dict[line[1]]]
             
             # store head-relation vector in numpy head-relation vector matrix
             head_relation_vecs[head_relation_vec_cnt] = np.concatenate([head_entity, relationship])

             head_relation_vec_cnt = head_relation_vec_cnt + 1

    np.save(fname_head_relation_training_vecs, head_relation_vecs)


    print(head_relation_vec_cnt)

else:

    relationships=np.load(fname_head_relation_training_vecs)      
        
        

print(relationships.shape)
encoding_dim = 200


# 1311 unique relations in training set
# relations represented as 1311-dimensional one-hot vectors
# entities represented as 1000-dimensional word2vec vectors
# input layer therefore has 2311 dimensions

# AUTO ENCODER
input_layer = Input(shape=(2311,))

# add a Dense layer with a L1 activity regularizer
encoded = Dense(encoding_dim, activation='sigmoid')(input_layer)
decoded = Dense(2311, activation='sigmoid')(encoded)

# this model maps an input to its reconstruction
autoencoder = Model(input_layer, decoded)


# ENCODER
# this model maps an input to its encoded representation
encoder = Model(input_layer, encoded)

# DECODER
# create a placeholder for an encoded (200-dimensional) input
encoded_input = Input(shape=(encoding_dim,))
# retrieve the last layer of the autoencoder model
decoder_layer = autoencoder.layers[-1]
# create the decoder model
decoder = Model(encoded_input, decoder_layer(encoded_input))


# TRAIN
autoencoder.compile(optimizer='adadelta', loss='binary_crossentropy')


from keras.datasets import mnist
import numpy as np
(x_train, _), (x_test, _) = mnist.load_data()

x_train = x_train.astype('float32') / 255.
x_test = x_test.astype('float32') / 255.
x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))
x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))
print(x_train.shape)
print(x_test.shape)

x_train = entities

print("haro long time")

# -*- coding: utf-8 -*-
"""Copy of Ass1.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1w2kSRhETJkiNkOX1FtNHt_1b7Xe3z1lm

# Neural Network From Scratch

# Utils
"""

import numpy as np
import copy
from keras.datasets import mnist
import keras
import pandas as pd
import time
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler

# Parameters
SEED = 10
EPSILON = 1e-5
GAMMA = 1
BETA = 0.1
input_num = 784
keep_probability = 0.9

"""# Forward propagation process"""

def initialize_parameters(layer_dims):
    """Initializing parameters of the model
  Arges:
      layer_dims (int): an array of the dimensions of each layer
  return:
      Dictionary. Containing the initialized W and b parameters of each layer 
  """
    np.random.seed(SEED)
    parameters = {
        'weights': {},
        'biases': {}
    }
    for layer_index, current_layer_dim in enumerate(layer_dims[:-1], start=1):
      prev_size = layer_dims[layer_index - 1]
      curr_size = layer_dims[layer_index]
      w_layer = (np.random.randn(curr_size,prev_size))*(np.sqrt(2 / (curr_size + prev_size)))
      b_layer = np.zeros((curr_size, 1))
      parameters['weights'][layer_index] = w_layer
      parameters['biases'][layer_index] = b_layer
    return parameters

def linear_forward(A, W, b):
    """
  Implement the linear part of a layer's forward propagation
  Arges:
    A(list) – the activations of the previous layer
    W(list) – the weight matrix of the current layer
    B(list) – the bias vector of the current layer
  Return:
      Z. the linear component of the activation function
      linear_cache. a dictionary containing A, W, b
  """

    linear_cache = {
        'A': A,
        'W': W,
        'b': b
    }

    Z = np.dot(W, A) + b

    return Z, linear_cache


def softmax(Z):
    """
  Args:
    Z(list) - the linear component of the activation function
  Output:
    A- the activations of the layer
    activation_cache- returns Z
  """
    activation_cache = copy.deepcopy(Z)
    Z = Z - Z.max(axis=0, keepdims=True)
    A = np.exp(Z) / np.exp(Z).sum(axis=0, keepdims=True)
    return A, activation_cache


def relu(Z):
    """
    Args:
      Z(list) - the linear component of the activation function
    Output:
      A. the activations of the layer
      activation_cache. returns Z, which will be useful for the backpropagation
  """
    activation_cache = copy.deepcopy(Z)
    Z[Z < 0] = 0
    return Z, activation_cache



def linear_activation_forward(A_prev, W, B, activation):
    """
  Implement the forward propagation for the LINEAR->ACTIVATION layer
  Args:
    A_prev(list) – activations of the previous layer
    W(list) – the weights matrix of the current layer
    B(list) – the bias vector of the current layer
    Activation(string) – the activation function to be used (a string, either “softmax” or “relu”)
  Output:
    A. the activations of the current layer
    cache. a joint dictionary containing both linear_cache and activation_cache
  """
    Z, linear_cache = linear_forward(A_prev, W, B)
    if activation == 'softmax':
        A, activation_cache = softmax(Z)
    else:
        A, activation_cache = relu(Z)
    cache = {'linear_cache': linear_cache, 'activation_cache': activation_cache}
    return A, cache


def L_model_forward(X, parameters, use_batchnorm, use_dropout):
    """
    Implement forward propagation for the [LINEAR->RELU]*(L-1)->LINEAR->SOFTMAX computation
      Args:
        X(np.array) – the data, numpy array of shape (input size, number of examples)
        parameters(dict) – the initialized W and b parameters of each layer
        use_batchnorm(boolean) - a boolean flag used to determine whether to apply batchnorm after the activation
      Output:
        AL. the last post-activation value
        caches. a list of all the cache objects generated by the linear_forward function
    """
    size = len(parameters['weights'])
    activation = 'relu'
    cache = []
    AL = X
    for layer in range(1, size + 1):
        whights = parameters['weights'][layer]
        biases = parameters['biases'][layer]
        if layer == size:
            activation = 'softmax'

        AL, cache_layer = linear_activation_forward(AL, whights, biases, activation)

        if layer != size:
          if use_batchnorm:
              AL = apply_batchnorm(AL)
          if use_dropout:
              AL = apply_dropout(AL, keep_probability)
              
        cache.append(cache_layer)
    return AL, cache

def compute_cost(AL, Y):
    """
  Implement the cost categorical cross-entropy loss
  Args:
     AL(list) - probability vector corresponding to your label predictions, shape (num_of_classes, number of examples)
     Y(list) – the labels vector
  Output:
     NA. the normalized activation values, based on the formula learned in class
  """

    m = np.shape(Y)[1]
    log = np.log(AL.T + EPSILON)
    sum = np.trace(-1 * (np.dot(Y, log)))
    return (1 / m) * sum


def apply_batchnorm(A):
    """
  Performs batchnorm on the received activation values of a given layer.
  Args:
    A(list) - the activation values of a given layer
  Output:
    NA. the normalized activation values,
  """
    mean = A.mean(axis=0)
    var = A.var(axis=0)
    std = np.sqrt(var + EPSILON)
    normalized_a = mean / std
    reduced_A = A - normalized_a

    out = GAMMA * reduced_A + BETA

    return out

def apply_dropout(A, keep_probability):
  """
  Supporting the dropout functionality
  Args:
  A(np.array) - the activation values of a given layer
  keep_probability(int) - probability of the dropout
  Output:
  A. modified activation values of a given layer
  """

  mask = np.random.rand(A.shape[0], A.shape[1]) < keep_probability
  A_dropout = np.multiply(A, mask) / keep_probability
  return A_dropout

"""# Backward propagation process"""

def linear_backward(dZ, cache):
    """
  	Implements the linear part of the backward propagation process for a single layer Input:
    dZ – the gradient of the cost with respect to the linear output of the current layer (layer l)
    cache – tuple of values (A_prev, W, b) coming from the forward propagation in the current layer

    Output:
    dA_prev -- Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
    dW -- Gradient of the cost with respect to W (current layer l), same shape as W
    db -- Gradient of the cost with respect to b (current layer l), same shape as b

  """
    A_prev, W, b = cache.values()
    m = A_prev.shape[1]
    dw = np.dot(dZ, A_prev.T) / m
    db = np.array(np.sum(dZ, axis=1) / m)
    dA_prev = np.dot(W.T, dZ)

    return dA_prev, dw, db


def linear_activation_backward(dA, cache, activation):
    """
  Description:
  Implements the backward propagation for the LINEAR->ACTIVATION layer. The function first computes dZ and then applies the linear_backward function.

  Some comments:
  •	The derivative of ReLU is
  •	The derivative of the softmax function is: , where  is the softmax-adjusted probability of the class and  is the “ground truth” (i.e. 1 for the real class, 0 for all others)
  •	You should use the activations cache created earlier for the calculation of the activation derivative and the linear cache should be fed to the linear_backward function
  Input:
  dA – post activation gradient of the current layer
  cache – contains both the linear cache and the activations cache
  Output:
  dA_prev – Gradient of the cost with respect to the activation (of the previous layer l-1), same shape as A_prev
  dW – Gradient of the cost with respect to W (current layer l), same shape as W
  db – Gradient of the cost with respect to b (current layer l), same shape as b
  """

    if activation == "softmax":
        linear_cache, activation_cache, Y = cache.values()
        
        DZ = softmax_backward(dA, Y)
    elif activation == "relu":
        linear_cache, activation_cache = cache.values()
        DZ = relu_backward(dA, activation_cache)

    else:
        raise Exception("you can use only relu and softmax activation")

    assert (DZ.shape == dA.shape)
    dA_prev, dW, db = linear_backward(DZ, linear_cache)
    return dA_prev, dW, db


def relu_backward(dA, activation_cache):
    """
  Description:
  Implements backward propagation for a ReLU unit

  Input:
  dA – the post-activation gradient
  activation_cache – contains Z (stored during the forward propagation)

  Output:
  dZ – gradient of the cost with respect to Z
  """
    # dZ = 1 for Z > 0 and 0 otherwise
    Z = activation_cache
    relu = (Z > 0) * 1

    dZ = dA * relu
    return dZ


def softmax_backward(dA, activation_cache):
    """
  Description:
  Implements backward propagation for a softmax unit

  Input:
  dA – the post-activation gradient
  activation_cache – Y

  Output:
  dZ – gradient of the cost with respect to Z
  """
    Y = activation_cache
    dZ = dA - Y
    return dZ


def L_model_backward(AL, Y, caches):
    """
  Description:
  Implement the backward propagation process for the entire network.
  Some comments:
  the backpropagation for the softmax function should be done only once as only the output layers uses it and the RELU should be done iteratively over all the remaining layers of the network.
  Input:
  AL - the probabilities vector, the output of the forward propagation (L_model_forward)
  Y - the true labels vector (the "ground truth" - true classifications)
  Caches - list of caches containing for each layer: a) the linear cache; b) the activation cache
  Output:
  Grads - a dictionary with the gradients
              grads["dA" + str(l)] = ...
              grads["dW" + str(l)] = ...
              grads["db" + str(l)] = ...
  """

    grads = {}
    grads["dW"] = {}
    grads["db"] = {}
    grads["dA"] = {}
    L = len(caches)  # the number of layers
    m = AL.shape[1]
    Y = Y.transpose()
    dA = None
    for layer in range(L - 1, -1, -1):
        layer_cache = caches[layer]
        if layer == L-1:
            layer_cache['Y'] = Y
            dA, dW, db = linear_activation_backward(AL, layer_cache, "softmax")
        else:
            dA, dW, db = linear_activation_backward(dA, layer_cache, "relu")
        
        grads["dW"][layer] = dW
        grads["db"][layer] = db
        grads["dA"][layer] = dA
    return grads

def update_parameters(parameters, grads, learning_rate):
    """
  Description:
  Updates parameters using gradient descent
  Input:
  parameters – a python dictionary containing the DNN architecture’s parameters
  grads – a python dictionary containing the gradients (generated by L_model_backward)
  learning_rate – the learning rate used to update the parameters (the “alpha”)

  Output:
  parameters – the updated values of the parameters object provided as input
  """

    L = len(parameters['weights'])
    
    for i in range(L):
        parameters["weights"][i + 1] = parameters["weights"][i + 1] - learning_rate * grads["dW"][i]
        parameters["biases"][i + 1] = parameters["biases"][i + 1] - learning_rate * grads["db"][i].reshape(grads["db"][i].shape[0], 1)
        
    return parameters

def L_layer_model(X, Y, layers_dims, learning_rate, num_iterations, batch_size, use_batchnorm, use_dropout):
    """
    	Description:
      Implements a L-layer neural network. All layers but the last should have the ReLU activation function,
      and the final layer will apply the softmax a %ctivation function.
      The size of the output layer should be equal to the number of labels in the data.
      Please select a batch size that enables your code to run well (i.e. no memory overflows while still running relatively fast).
      The function uses the earlier functions in the following order:
      initialize -> L_model_forward -> compute_cost -> L_model_backward -> update parameters

      Input:
      X – the input data, a numpy array of shape (height*width , number_of_examples)
      Comment: since the input is in grayscale we only have height and width, otherwise it would have been height*width*3
      Y – the “real” labels of the data, a vector of shape (num_of_classes, number of examples)
      Layer_dims – a list containing the dimensions of each layer, including the input
      batch_size – the number of examples in a single training batch.

      Output:
      parameters – the parameters learnt by the system during the training (the same parameters that were updated in the update_parameters function).
      costs – the values of the cost function (calculated by the compute_cost function).
              One value is to be saved after each 100 training iterations (e.g. 3000 iterations -> 30 values).

    """
    x_train, x_val, y_train, y_val = shuffle_split_data(X, Y, train_size=80)
    x_train = x_train.transpose()
    x_val = x_val.transpose()

    parameters = initialize_parameters(layers_dims)

    batch_loop = int(x_train.shape[1] / batch_size)
    epochs = int(num_iterations / batch_loop)
    costs = []
    steps = 0
    no_improvement_100 = 0
    max_val_cost = 9999
    trash_stop = 0.00001
    stop_training = False
    for epoch in range(epochs):

        for i in range(batch_loop):

            index = i * batch_size
            end = (i + 1) * batch_size

            x_batch = x_train[:, index: end]
            y_batch = y_train[index: end]

            AL_batch, caches_batch = L_model_forward(x_batch, parameters, use_batchnorm, use_dropout)

            grads_batch = L_model_backward(AL_batch, y_batch, caches_batch)

            parameters = update_parameters(parameters, grads_batch, learning_rate)

            steps += 1
            if steps % 100 == 0:
                train_cost = compute_cost(AL_batch, y_batch.T)
                AL_val, cache_val = L_model_forward(x_val, parameters, use_batchnorm,False)
                val_cost = compute_cost(AL_val, y_val.T)
                costs.append(train_cost)
                train_acc_100 = predict(x_train, y_train, parameters, use_batchnorm)
                val_acc_100 = predict(x_val, y_val, parameters, use_batchnorm)
                # print(f'Validation accuracy: {val_acc_100:.3f},'
                #       f' Training Steps {steps},'
                #       f' Training Cost: {train_cost:.3f},'
                #       f' Training Accuracy: {train_acc_100:.3f}')

                diff = max_val_cost - val_cost
                val_acc = predict(x_val, y_val, parameters, use_batchnorm)
                if diff < trash_stop:
                    stop_training = True
                    break;
                max_val_cost = val_cost
        if stop_training:
            break;

   
    train_accuracy = predict(x_train, y_train, parameters, use_batchnorm)
    val_accuracy = predict(x_val, y_val, parameters, use_batchnorm)
    return parameters, costs, train_accuracy, val_accuracy, steps
            

def predict(X, Y, parameters, use_batchnorm =False):
    """
    Description: 
    The function receives an input data and the true labels and calculates the accuracy of the trained neural network on the data.

    Input:
    X – the input data, a numpy array of shape (height*width, number_of_examples)
    Y – the “real” labels of the data, a vector of shape (num_of_classes, number of examples)
    Parameters – a python dictionary containing the DNN architecture’s parameters.
    Output:
    accuracy – the accuracy measure of the neural net on the provided data 
    (i.e. the percentage of the samples for which the correct label receives the hughest confidence score). 
    softmax function was used to normalize the output values.

    """
    
    pred_score, cache = L_model_forward(X, parameters, use_batchnorm=use_batchnorm, use_dropout=False)
    accuracy = calc_accuracy(Y, pred_score)
    return accuracy

"""# Auxiliary functions"""

def calc_accuracy(Y, predictions):
  """
  Description:
  Calculate the the percentage of the samples for which the correct label receives the hughest confidence score
  
  Input:
  predictions – the set of labels predicted, a vector of shape (num_of_classes, number of examples)
  Y – the “real” labels of the data, a vector of shape (num_of_classes, number of examples)

  Output:
  accuracy – Accuracy classification score, the fraction of predictions our model got right.
  """

  Y = np.argmax(Y.T, axis=0)
  predicted_class = predictions.argmax(axis=0)
  accuracy = np.mean(Y ==predicted_class)

  return accuracy

def shuffle_split_data(X, y, train_size):
    """
    Description:
    Split arrays into random train and test subsets

    Input:
    X – sequence of indexables, same length as Y
    Y – sequence of indexables, same length as X
    train_size - the proportion of the dataset to include in the train split

    Output:
    X_train, X_test, y_train, y_test – containing train-test split of inputs
    """
    arr_rand = np.random.rand(X.shape[0])
    split = arr_rand < np.percentile(arr_rand, train_size)

    X_train = X[split]
    y_train = y[split]
    X_test =  X[~split]
    y_test = y[~split]

    return X_train, X_test, y_train, y_test

def load_mnist_data(input_num):
    """
    Description:
    load the MINST train and test sets through the keras API and preprocess the data for the model
    
    Input:
    input_num (int)– the flatten shape of 28*28 picture pixels.


    Output:
    x_test, x_train, y_test, y_train - preprocessed data sets

    """
    (train_X, train_y), (test_X, test_y) = mnist.load_data()
    num_classes = len(np.unique(train_y))
    x_train, y_train = preprocessing(train_X, train_y, input_num, num_classes)
    x_test, y_test = preprocessing(test_X, test_y, input_num, num_classes)
    return x_test, x_train, y_test, y_train

def preprocessing(X, Y, input_num, num_classes):
  """
  
  Description: 
  This function normalizes the data by dividing each cell by 255 since the pixels are grayscale and 
  reshapes the input from 28*28 2D arrays to a 1D array of 784.
  In addition, this function transforms the y to one hot encoder.

  Input:
  X- the input data
  Y-the “real” labels of the data, a vector of shape (1, number of examples)
  input_num (int)- the flatten shape of 28*28 picture pixels.
  num_classes (int)- count of classifier labels

  Output:
  x- a numpy array of shape (height*width, number_of_examples)
  y- a vector of shape (num_of_classes, number of examples)
  
  """
  
  x = X.reshape(X.shape[0], input_num)
  x = x.astype('float')
  x /= 255
  y = keras.utils.to_categorical(Y.reshape(-1,1), num_classes)
  return x,y

def scaling(x_train, x_test):
    scaler = StandardScaler()
    scaler.fit(x_train)
    x_train = scaler.transform(x_train)
    x_test = scaler.transform(x_test)
    return x_train, x_test

def experiment (input_num, learning_rate ,num_iterations, batch_size):
  """
  Description: 
  This function receives the parameters, trains the DNN with the different combinations and tests the model.
  It also measure the time it takes to train the DNN and predicts on the test set.
  The results are saved on dataframe.
  
  Input:
  input_num- the flatten shape of 28*28 picture pixels.
  batch_size- the number of examples in a single training batch.

  Output:
  results (DataFrame)- containing the model performances

  """
  
  
  x_test, x_train, y_test, y_train = load_mnist_data(input_num)
  layers_dims = [input_num, 20, 7, 5, 10]
  results= pd.DataFrame(columns=['index','dropout','batchnorm','train accuracy','validation accuracy','test accuracy',
                                 'training time','inference time','training iterations','costs'])
  i = 0
  dropout = [True, False]
  norm = [True, False] 
  for d in dropout:
    for n in norm:
      i += 1
      start_time = time.time()
      parameters, costs, train_accuracy, val_accuracy,iterations = L_layer_model(x_train, y_train, layers_dims, 0.009, num_iterations, batch_size,use_batchnorm=n,use_dropout=d)
      end_time = time.time()
      train_time =  end_time - start_time
      start_time = time.time()
      testing_accuracy = predict(x_test.T, y_test, parameters)
      end_time = time.time()
      test_time = end_time - start_time
      results=results.append({
                'index':i,'dropout': d,'batchnorm': n,
                'train accuracy': train_accuracy, 'validation accuracy': val_accuracy, 'test accuracy': testing_accuracy,
                'training time' : train_time,'inference time' : test_time ,'training iterations': iterations, 'costs': costs},
                ignore_index=True)
      plotting(i,d,n,costs )
    
    
  return results

def plotting (index,dropout, batchnorm,costs):
  plt.figure(index)
  plt.plot(costs)
  plt.title(f'Cost over iteration, Dropout= {dropout}, Normalization= {batchnorm}')
  plt.ylabel('cost')
  plt.xlabel('iterations (x100)')

  plt.show()

"""# Expiremnt and Results:


"""

df = experiment(784, 0.009, 10 ** 8, 600)
df
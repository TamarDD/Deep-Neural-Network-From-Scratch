# Deep-Neural-Network-from-scratch
Building a simple neural network “from scratch”

## Purpose
The purpose of this work is to experiment with implementation from scratch of a simple Neural Network (NN) and test it on MINST data.
We also used vectorization and a regularization technique

## Auxiliary functions
* calc_accuracy- calculate the the percentage of the samples for which the correct label receives the highest confidence score
* shuffle_split_data-split arrays into random train and test subsets, for creating the validation set.
* load_mnist_data- load the MINST train and test sets through the keras API and preprocess the data for the model
* preprocessing- normalizes and reshapes the data
* experiment- trains the DNN with the different combinations of dropout and
batch normalization and tests the model
* plotting- plot the train loss charts

## Dropout
We randomly dropped each layer except the last, K neurons with probability of 0.1 and reset them to zeros. This action has the effect of making the training process noisy that sometimes allows a better performance of the NN.

## Experiment
After implementing our DNN, we want to examine the  batch normalization and dropout affect on the performance. So, we ran the network many times with varying hyperparameters and saved the results (Figure 1)

We run our NN with the following parameters:
* 4 layers (aside from the input layer), with the following sizes: 20,7,5,10
* Learning rate of 0.009
* We run the NN 4 times with and without using batch normalization and
dropout with probability of 0.9
* Batch size of 600
* Train data was splitted into 80% train and 20% validation
* Seed = 10
* 𝛄=1 and 𝛃=0.1 was the parameters for Batch normalization.

## Results

![Figure 1](https://github.com/TamarDD/Deep-Neural-Network-from-scratch/blob/main/figures/table%20results.png)
Figure 1: The experiments results 



<img src="https://github.com/TamarDD/Deep-Neural-Network-from-scratch/blob/main/figures/charts1.png" width="400">
<img src="https://github.com/TamarDD/Deep-Neural-Network-from-scratch/blob/main/figures/chart2.png" width="400">

Figure 2: The costs over iterations 


## Discussion
The results indicate that the dropout didn't improve the model performances in accuracy terms but it helps the model to converge faster. However, batch normalization improved the results whenever it was used.

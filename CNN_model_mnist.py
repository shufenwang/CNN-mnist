# -*- coding: utf-8 -*-

import tensorflow as tf

# import mnist data
import tensorflow.examples.tutorials.mnist.input_data as input_data
mnist = input_data.read_data_sets("MNIST_data", one_hot=True)

sess = tf.InteractiveSession()

x = tf.placeholder("float", shape=[None, 784])
y_ = tf.placeholder("float", shape=[None, 10])

# initialize weight and bias
def weight_variable(shape):
  initial = tf.truncated_normal(shape, stddev=0.1)
  return tf.Variable(initial)

def bias_variable(shape):
  initial = tf.constant(0.1, shape=shape)
  return tf.Variable(initial)

# define Convolutional Layer
def conv2d(x, W):
  return tf.nn.conv2d(x, W, strides=[1, 1, 1, 1], padding='SAME')

# define max_pool
def max_pool_2x2(x):
  return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding='SAME')

# set the weigth and bias
W_conv1 = weight_variable([5, 5, 1, 32])
b_conv1 = bias_variable([32])
W_conv2 = weight_variable([5, 5, 32, 64])
b_conv2 = bias_variable([64])
W_fc1 = weight_variable([7 * 7 * 64, 1024])
b_fc1 = bias_variable([1024])
W_fc2 = weight_variable([1024, 10])
b_fc2 = bias_variable([10])

# reshape th image into 28*28
x_image = tf.reshape(x, [-1, 28, 28, 1])

# the first layer
# relu the result after convolution
h_conv1 = tf.nn.relu(conv2d(x_image, W_conv1) + b_conv1)
# max_pool
h_pool1 = max_pool_2x2(h_conv1)

# the second layer
h_conv2 = tf.nn.relu(conv2d(h_pool1, W_conv2) + b_conv2)
h_pool2 = max_pool_2x2(h_conv2)

# reshape the image after the second max_pool
h_pool2_flat = tf.reshape(h_pool2, [-1, 7*7*64])
# full connected and relu
h_fc1 = tf.nn.relu(tf.matmul(h_pool2_flat, W_fc1) + b_fc1)

keep_prob = tf.placeholder("float")
# dropout to avoid overfitting
h_fc1_drop = tf.nn.dropout(h_fc1, keep_prob)

# softmax and output
y_conv=tf.nn.softmax(tf.matmul(h_fc1_drop, W_fc2) + b_fc2)

# cross entropy as loss function
with tf.name_scope('cross_entropy'):
    cross_entropy = -tf.reduce_sum(y_*tf.log(y_conv))
    tf.summary.scalar('cross_entropy', cross_entropy)

# Using Adam algorithm to optimize the loss function
train_step = tf.train.AdamOptimizer(1e-3).minimize(cross_entropy)
#train_step = tf.train.GradientDescentOptimizer(0.5).minimize(cross_entropy)


# define accuracy
correct_prediction = tf.equal(tf.argmax(y_conv, 1), tf.argmax(y_, 1))

with tf.name_scope('accuracy'):
    accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))
    tf.summary.scalar('accuracy', accuracy)

# save the data for plot
merged = tf.summary.merge_all()
writer = tf.summary.FileWriter('logs/', sess.graph)

sess.run(tf.global_variables_initializer())
for i in range(2000):
  # train 100 data once
  batch = mnist.train.next_batch(100)
  if i % 100 == 0:
    train_accuracy = accuracy.eval(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0})
    print "step %d, training accuracy %g" % (i, train_accuracy)
    result = sess.run(merged, feed_dict={x: batch[0], y_: batch[1], keep_prob: 0})  # run merged
    writer.add_summary(result, i)

  train_step.run(feed_dict={x: batch[0], y_: batch[1], keep_prob: 0})


print "test accuracy %g" % accuracy.eval(feed_dict={x: mnist.test.images, y_: mnist.test.labels, keep_prob: 0})
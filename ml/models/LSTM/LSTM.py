import tensorflow as tf
from matplotlib import pyplot as plt
import numpy as np
import os
from datetime import datetime

from MLDataTools import MLDataSet


class LSTM:
    def __init__(self, sess, num_layers, lstm_size, feature_len: int, targets_shape: int, num_steps, epochs, plot_dir):
        """
        :param sess: TensorFlow computational session
        :param num_layers: stacked LSTM
        :param lstm_size: how many neurons in layers
        :param feature_len: a vector representing dimensions of the input matrix
        :param num_steps: how far back the RNN is unrolled (for back-in-time-propagation)
        :param epochs: number of epochs to train with
        """
        self.plot_dir = plot_dir
        self.sess = sess
        self.num_layers = num_layers
        self.lstm_size = lstm_size
        self.feature_len = feature_len
        self.num_steps = num_steps
        self.epochs = epochs
        self.targets_shape = targets_shape

    def build_graph(self):
        """
        build computational graph for an LSTM
        :return: void
        """
        self.learning_rate = tf.placeholder(tf.float32, name="learning_rate")
        self.inputs = tf.placeholder(tf.float32, [None, self.num_steps, self.feature_len], name="inputs")
        self.targets = tf.placeholder(tf.float32, [None, self.targets_shape], name="targets")
        self.keep_probability = tf.placeholder(tf.float32, None, name="keep_prob")

        def _create_one_cell():
            lstm_cell = tf.contrib.rnn.LSTMCell(self.lstm_size, state_is_tuple=True)
            lstm_cell = tf.contrib.rnn.DropoutWrapper(lstm_cell, output_keep_prob=self.keep_probability)
            return lstm_cell

        # Run dynamic RNN

        cells = [_create_one_cell() for _ in range(self.num_layers)]
        lstm = tf.contrib.rnn.MultiRNNCell(cells, state_is_tuple=True)
        val, state_ = tf.nn.dynamic_rnn(lstm, self.inputs, dtype=tf.float32, scope="dynamic_rnn")

        # Before transpose, val.get_shape() = (batch_size, num_steps, lstm_size)
        # After transpose, val.get_shape() = (num_steps, batch_size, lstm_size)
        val = tf.transpose(val, [1, 0, 2])
        # turns (num_steps, batch_size, lstm_size) -> (batch_size, lstm_size) to one big matrix i think
        last = tf.gather(val, int(val.get_shape()[0]) - 1, name="lstm_state")

        ws = tf.Variable(tf.truncated_normal([self.lstm_size, self.targets_shape]), name="w")
        bias = tf.Variable(tf.constant(0.1, shape=[self.targets_shape]), name="b")

        self.pred = tf.matmul(last, ws) + bias
        self.loss = tf.reduce_mean(tf.square(self.pred - self.targets), name="loss_mse_train")

        """
          # Use the contrib sequence loss and average over the batches
            loss = tf.contrib.seq2seq.sequence_loss(
            logits,
            input_.targets,
            tf.ones([self.batch_size, self.num_steps], dtype=data_type()),
            average_across_timesteps=False,
            average_across_batch=True)
        """
        self.optim = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss, name="rmsprop_optim")

        # Separated from train loss.
        self.loss_test = tf.reduce_mean(tf.square(self.pred - self.targets), name="loss_mse_test")

    def train(self,
              data_set: MLDataSet,
              init_learning_rate=0.001,
              init_epoch=5,
              learning_rate_decay=0.99,
              batch_size=100,
              keep_probability=0.7,
              train_test_ratio=0.8
              ):
        """
        :param train_test_ratio: size ratio of train/test data set split
        :param batch_size: batch size
        :param keep_probability: dropout probability
        :param learning_rate_decay: learning rate decay
        :param init_epoch: epoch to start the leraning rate decay
        :param init_learning_rate: initial learning rate
        :type data_set: MLDataSet
        :param data_set: data frame containing the data-set

        :return: void
        """
        tf.global_variables_initializer().run(session=self.sess)

        train_set, test_set = data_set.separate(train_test_ratio)  # size ratio of train/data
        test_x, test_y = test_set.time_series_split(self.num_steps)
        test_data_feed = {
            self.learning_rate: 0.0,
            self.keep_probability: 1,
            self.inputs: test_x,
            self.targets: test_y
        }

        for epoch in range(self.epochs):
            learning_rate = init_learning_rate * (
                    learning_rate_decay ** max(float(epoch + 1 - init_epoch), 0.0)
            )

            for X, Y in train_set.generate_epoch(batch_size,
                                                 self.num_steps):  # returns a generator which produces batches
                data_feed = {
                    self.inputs: X,
                    self.targets: Y,
                    self.learning_rate: learning_rate,
                    self.keep_probability: keep_probability
                }
                self.sess.run(self.optim, data_feed)

            test_loss, test_pred = self.sess.run([self.loss_test, self.pred], test_data_feed)
            print("Epoch:%d ---- [Learning rate: %.6f] [test_loss:%.6f] " % (epoch, learning_rate, test_loss))
            date = datetime.now().strftime("%Y-%m-%d.%H:%M:%S")
            image_path = os.path.join(self.plot_dir, "{}_epoch{:02d}.png".format(date, epoch))
            self.plot_samples(test_pred, test_y, image_path)

    def plot_samples(self, preds, targets, figname, multiplier=5):

        def _flatten(seq):
            return np.array([x for y in seq for x in y])

        truths = _flatten(targets)[-200:]
        preds = (_flatten(preds) * multiplier)[-200:]
        days = range(len(truths))[-200:]

        plt.figure(figsize=(12, 6))
        plt.plot(days, truths, label='truth')
        plt.plot(days, preds, label='pred')
        plt.legend(loc='upper left', frameon=False)
        plt.xlabel("day")
        plt.ylabel("normalized price")
        plt.ylim((min(truths), max(truths)))
        plt.grid(ls='--')

        plt.savefig(figname, format='png', bbox_inches='tight', transparent=False)
        plt.close()

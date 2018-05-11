import tensorflow as tf
from matplotlib import pyplot as plt
import numpy as np
import os
from datetime import datetime
from typing import List

from MLDataTools import MLDataSet


class LSTM:
    def __init__(self, sess, num_layers, lstm_size, feature_len: int, targets_shape: int, num_steps: int,
                 plot_dir: str,
                 embed_size: List[int]):
        """
        :param embed_size:[  num stocks:int, num features in embed matrix: int]
        :param sess: TensorFlow computational session
        :param num_layers: stacked LSTM
        :param lstm_size: how many neurons in layers
        :param feature_len: a vector representing dimensions of the input matrix
        :param num_steps: how far back the RNN is unrolled (for back-in-time-propagation)
        """
        self.plot_dir = plot_dir
        self.sess = sess
        self.num_layers = num_layers
        self.lstm_size = lstm_size
        self.feature_len = feature_len
        self.num_steps = num_steps
        self.targets_shape = targets_shape
        self.embed_size = embed_size
        with open('./models/celebs') as file:
            celebs = file.read()[1:-1].split('\\n')
            self.name = np.random.choice(celebs)
            print("LSTM name: ", self.name)
            file.close()
        date = datetime.now().strftime("%Y-%m-%d.%H-%M-%S")
        self.tag = f"{self.name};{date};neurons={self.lstm_size};num_steps={self.num_steps}"
        self.base_dir = './tsboard/LSTM/'
        self.tsdir = self.base_dir + self.tag
        self.predictionsdir = self.base_dir + self.tag + '/predictions'
        os.makedirs(self.tsdir)
        os.makedirs(self.predictionsdir)

    def build_graph(self):
        """
        build computational graph for an LSTM
        :return: void
        """

        self.learning_rate = tf.placeholder(tf.float32, name="learning_rate")
        self.inputs = tf.placeholder(tf.float32, [None, self.num_steps, self.feature_len], name="inputs")
        self.targets = tf.placeholder(tf.float32, [None, self.targets_shape], name="targets")
        self.keep_probability = tf.placeholder(tf.float32, None, name="dropout_keep_prob")
        # ints representing a target (i.e. stock); mapped using LabelEncoder
        self.symbols = tf.placeholder(tf.int32, [None, 1], name="stock_symbols")

        # Embed matrix
        if self.embed_size != [] and self.embed_size is not None:
            # the actual embedding matrix
            with tf.name_scope('embedding_matrix'):
                embedding_matrix = tf.Variable(
                    tf.random_uniform(self.embed_size, -1.0, 1.0),
                    name="embedding_matrix"
                )
                # tile stacks the vector into each other num_step times
                stacked_target_labels = tf.tile(self.symbols, multiples=[1, self.num_steps], name='stacked_stock_labels')
                target_label_embeds = tf.nn.embedding_lookup(embedding_matrix, stacked_target_labels)
                self.inputs_with_embed = tf.concat([self.inputs, target_label_embeds], axis=2, name="inputs_with_embed")
        else:
            self.inputs_with_embed = tf.identity(self.inputs)

        def _create_one_cell():
            with tf.name_scope('LSTM_cell_creation'):
                lstm_cell = tf.contrib.rnn.LSTMCell(self.lstm_size, state_is_tuple=True)
                lstm_cell = tf.contrib.rnn.DropoutWrapper(lstm_cell, output_keep_prob=self.keep_probability)
            return lstm_cell

        # Run dynamic RNN

        cells = [_create_one_cell() for _ in range(self.num_layers)]
        lstm = tf.contrib.rnn.MultiRNNCell(cells, state_is_tuple=True)
        val, state_ = tf.nn.dynamic_rnn(lstm, self.inputs_with_embed, dtype=tf.float32, scope="dynamic_rnn")

        # Before transpose, val.get_shape() = (batch_size, num_steps, lstm_size)
        # After transpose, val.get_shape() = (num_steps, batch_size, lstm_size)
        val = tf.transpose(val, [1, 0, 2])
        # turns (num_steps, batch_size, lstm_size) -> (batch_size, lstm_size) to one big matrix i think
        last = tf.gather(val, int(val.get_shape()[0]) - 1, name="lstm_state")

        ws = tf.Variable(tf.truncated_normal([self.lstm_size, self.targets_shape]), name="w")
        bias = tf.Variable(tf.constant(0.1, shape=[self.targets_shape]), name="b")

        self.pred = tf.matmul(last, ws) + bias

        self.loss = tf.reduce_mean(tf.square(self.pred - self.targets), name="loss_mse_train")

        self.optim = tf.train.AdamOptimizer(self.learning_rate).minimize(self.loss, name="Adam_optim")

        # Separated from train loss.
        self.loss_test = tf.reduce_mean(tf.square(self.pred - self.targets), name="loss_mse_test")

        self.loss_sum = tf.summary.scalar("loss_mse_train", self.loss)
        self.loss_test_sum = tf.summary.scalar("loss_mse_test", self.loss_test)
        self.learning_rate_sum = tf.summary.scalar("learning_rate", self.learning_rate)

        self.last_sum = tf.summary.histogram("lstm_state", last)
        self.w_sum = tf.summary.histogram("Weights", ws)
        self.b_sum = tf.summary.histogram("Biases", bias)
        self.pred_summ = tf.summary.histogram("Prediction", self.pred)

    def train(self,
              data_set: MLDataSet,
              init_learning_rate=0.001,
              init_epoch=5,
              learning_rate_decay=0.99,
              batch_size=100,
              keep_probability=0.7,
              train_test_ratio=0.8,
              epochs=10
              ):

        """
        :param train_test_ratio: size ratio of train/test data set split
        :param batch_size: batch size
        :param epochs: number of epochs to train with
        :param keep_probability: dropout probability
        :param learning_rate_decay: learning rate decay
        :param init_epoch: epoch to start the leraning rate decay
        :param init_learning_rate: initial learning rate
        :type data_set: MLDataSet
        :param data_set: data frame containing the data-set

        :return: void
        """
        self.merged_sum = tf.summary.merge_all()

        train_writer = tf.summary.FileWriter(self.tsdir + '/train',
                                             self.sess.graph)
        test_writer = tf.summary.FileWriter(self.tsdir + '/test')

        tf.global_variables_initializer().run(session=self.sess)

        test_set, true_test_label = data_set.separate()  # size ratio of train/data; eg 0.9
        test_symbols, test_x, test_y = test_set.time_series_split(self.num_steps)

        test_data_feed = {
            self.learning_rate: 0.0,
            self.keep_probability: 1,
            self.inputs: test_x,
            self.targets: test_y,
            self.symbols: test_symbols
        }
        global_step = 0

        for epoch in range(epochs):
            learning_rate = init_learning_rate * (
                    learning_rate_decay ** max(float(epoch + 1 - init_epoch), 0.0)
            )
            for train_series in data_set.generate_epoch():
                for train_symbols, X, Y in train_series.generate_epoch(batch_size,
                                                                       self.num_steps):
                    global_step += 1
                    data_feed = {
                        self.inputs: X,
                        self.targets: Y,
                        self.learning_rate: learning_rate,
                        self.keep_probability: keep_probability,
                        self.symbols: train_symbols  # How do we calculate the symbols huh
                    }
                    train_loss, _, train_merged_sum = \
                        self.sess.run([self.loss, self.optim, self.merged_sum], data_feed)

                    train_writer.add_summary(train_merged_sum, global_step=global_step)

            test_loss, test_pred = self.sess.run([self.loss_test, self.pred], test_data_feed)
            print("Epoch:%d ---- [Learning rate: %.6f] [test_loss:%.6f] " % (epoch, learning_rate, test_loss))
            image_path = os.path.join(self.predictionsdir, "epoch{:02d}.png".format(epoch))
            self.plot_samples(test_pred, test_y, image_path, true_test_label)

    def plot_samples(self, preds, targets, figname, title, multiplier=5):

        def _flatten(seq):
            return np.array([x for y in seq for x in y])

        truths = _flatten(targets)[-200:]
        preds = (_flatten(preds) * multiplier)[-200:]
        days = range(len(truths))[-200:]

        plt.figure(figsize=(12, 6))
        plt.title(title)
        plt.plot(days, truths, label='truth')
        plt.plot(days, preds, label='pred')
        plt.legend(loc='upper left', frameon=False)
        plt.xlabel("day")
        plt.ylabel("normalized price")
        plt.ylim((min(truths), max(truths)))
        plt.grid(ls='--')

        plt.savefig(figname, format='png', bbox_inches='tight', transparent=False)
        plt.close()

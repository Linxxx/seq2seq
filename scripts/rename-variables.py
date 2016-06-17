#!/usr/bin/env python2
# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import tensorflow as tf
import argparse
import cPickle
import os

parser = argparse.ArgumentParser()
parser.add_argument('--input-names', nargs='+', required=True)
parser.add_argument('--output-names', nargs='+', required=True)
parser.add_argument('--input-checkpoint', required=True)
parser.add_argument('--output-checkpoint', required=True)
parser.add_argument('--save-names', action='store_true')
parser.add_argument('--shapes', nargs='+', required=True)


"""
Mapping from old model to new

scripts/rename-variables.py \
--input-names \
learning_rate \
global_step \
proj_w \
proj_b \
many2one_rnn_seq2seq/encoder_fr/RNN/EmbeddingWrapper/embedding \
many2one_rnn_seq2seq/encoder_fr/RNN/BasicLSTMCell/Linear/Matrix \
many2one_rnn_seq2seq/encoder_fr/RNN/BasicLSTMCell/Linear/Bias \
many2one_rnn_seq2seq/decoder_en/embedding \
many2one_rnn_seq2seq/decoder_en/attention_decoder/AttnW_fr_0 \
many2one_rnn_seq2seq/decoder_en/attention_decoder/AttnV_fr_0 \
many2one_rnn_seq2seq/decoder_en/attention_decoder/Linear/Matrix \
many2one_rnn_seq2seq/decoder_en/attention_decoder/Linear/Bias \
many2one_rnn_seq2seq/decoder_en/attention_decoder/BasicLSTMCell/Linear/Matrix \
many2one_rnn_seq2seq/decoder_en/attention_decoder/BasicLSTMCell/Linear/Bias \
many2one_rnn_seq2seq/decoder_en/attention_decoder/Attention_0/Linear/Matrix \
many2one_rnn_seq2seq/decoder_en/attention_decoder/Attention_0/Linear/Bias \
many2one_rnn_seq2seq/decoder_en/attention_decoder/AttnOutputProjection/Linear/Matrix \
many2one_rnn_seq2seq/decoder_en/attention_decoder/AttnOutputProjection/Linear/Bias \
--output-names \
learning_rate \
global_step \
proj_w \
proj_b \
multi_encoder/encoder_fr/embedding \
multi_encoder/encoder_fr/RNN/BasicLSTMCell/Linear/Matrix \
multi_encoder/encoder_fr/RNN/BasicLSTMCell/Linear/Bias \
attention_decoder/embedding \
attention_decoder/attention/W_fr \
attention_decoder/attention/V_fr \
attention_decoder/Linear/Matrix \
attention_decoder/Linear/Bias \
attention_decoder/BasicLSTMCell/Linear/Matrix \
attention_decoder/BasicLSTMCell/Linear/Bias \
attention_decoder/attention/Linear/Matrix \
attention_decoder/attention/Linear/Bias \
attention_decoder/attention_output_projection/Linear/Matrix \
attention_decoder/attention_output_projection/Linear/Bias \
--input-checkpoint model/WMT14_fr-en/checkpoints.fr_en/translate-231263 \
--output-checkpoint model/WMT14_fr-en_new/checkpoints.fr_en/translate-231263 \
--save-names \
--shapes \
"()" \
"()" \
"(1024,30000)" \
"(30000,)" \
"(30000,1024)" \
"(2048,4096)" \
"(4096,)" \
"(30000,1024)" \
"(1,1,1024,1024)" \
"(1024,)" \
"(2048,1024)" \
"(1024,)" \
"(2048,4096)" \
"(4096,)" \
"(2048,1024)" \
"(1024,)" \
"(2048,1024)" \
"(1024,)"
"""


def save_variables(input_names, output_names, shapes, input_checkpoint, output_checkpoint, save_names):
  variables = []

  reader = tf.train.NewCheckpointReader(input_checkpoint)

  with tf.device('/cpu:0'):
    for input_name, output_name, shape in zip(input_names, output_names, shapes):
      shape = shape.strip('()')
      shape = [int(x) for x in shape.split(',') if x]

      value = reader.get_tensor(input_name)

      print(shape)
      print(value.shape)
      print(input_name, output_name)

      value = value.reshape(shape)
      v = tf.Variable(value, name=output_name)
      variables.append(v)

  with tf.Session() as sess:
    sess.run(tf.initialize_all_variables())
    saver = tf.train.Saver()

    print('saving parameters')
    for var in tf.all_variables():
      print('  {} shape {}'.format(var.name, var.get_shape()))

    saver.save(sess, output_checkpoint)

    if save_names:
      var_file = os.path.join(os.path.dirname(output_checkpoint), 'vars.pkl')

      with open(var_file, 'wb') as f:
        var_names = [var.name for var in tf.all_variables()]
        cPickle.dump(var_names, f)

if __name__ == '__main__':
  args = parser.parse_args()
  assert len(args.input_names) == len(args.output_names) == len(args.shapes)

  save_variables(args.input_names, args.output_names, args.shapes, args.input_checkpoint,
                 args.output_checkpoint, args.save_names)

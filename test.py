#coding:utf-8
import tensorflow as tf
import csv

name_dataset = 'name.csv'

train_x = []
train_y = []
with open(name_dataset,"r",encoding="utf-8") as csvfile:
    read = csv.reader(csvfile)
    for sample in read:
        if len(sample) == 2:
            train_x.append(sample[0])
            if sample[1] == '男':
                train_y.append([0, 1])  # 男
            else:
                train_y.append([1, 0])  # 女

max_name_length = max([len(name) for name in train_x])
print("最长名字的字符数: ", max_name_length)
max_name_length = 8


counter = 0
vocabulary = {}
for name in train_x:
    counter += 1
    tokens = [word for word in name]
    for word in tokens:
        if word in vocabulary:
            vocabulary[word] += 1
        else:
            vocabulary[word] = 1

vocabulary_list = [' '] + sorted(vocabulary, key=vocabulary.get, reverse=True)
print(len(vocabulary_list))


vocab = dict([(x, y) for (y, x) in enumerate(vocabulary_list)])
train_x_vec = []
for name in train_x:
    name_vec = []
    for word in name:
        name_vec.append(vocab.get(word))
    while len(name_vec) < max_name_length:
        name_vec.append(0)
    train_x_vec.append(name_vec)

#######################################################

input_size = max_name_length
num_classes = 2

batch_size = 64
num_batch = len(train_x_vec) // batch_size

X = tf.placeholder(tf.int32, [None, input_size])
Y = tf.placeholder(tf.float32, [None, num_classes])

dropout_keep_prob = tf.placeholder(tf.float32)
def neural_network(vocabulary_size, embedding_size=128, num_filters=128):
    # embedding layer
    with tf.name_scope("embedding"):
        W = tf.Variable(tf.random_uniform([vocabulary_size, embedding_size], -1.0, 1.0))
        embedded_chars = tf.nn.embedding_lookup(W, X)
        embedded_chars_expanded = tf.expand_dims(embedded_chars, -1)

    filter_sizes = [3,4,5]
    pooled_outputs = []
    for i, filter_size in enumerate(filter_sizes):
        with tf.name_scope("conv-maxpool-%s" % filter_size):
            filter_shape = [filter_size, embedding_size, 1, num_filters]
            W = tf.Variable(tf.truncated_normal(filter_shape, stddev=0.1))
            b = tf.Variable(tf.constant(0.1, shape=[num_filters]))
            conv = tf.nn.conv2d(embedded_chars_expanded, W, strides=[1, 1, 1, 1], padding="VALID")
            h = tf.nn.relu(tf.nn.bias_add(conv, b))
            pooled = tf.nn.max_pool(h, ksize=[1, input_size - filter_size + 1, 1, 1], strides=[1, 1, 1, 1], padding='VALID')
            pooled_outputs.append(pooled)

    num_filters_total = num_filters * len(filter_sizes)

    h_pool = tf.concat(pooled_outputs,3)
    h_pool_flat = tf.reshape(h_pool, [-1, num_filters_total])

    with tf.name_scope("dropout"):
        h_drop = tf.nn.dropout(h_pool_flat, dropout_keep_prob)

    with tf.name_scope("output"):
        W = tf.get_variable("W", shape=[num_filters_total, num_classes], initializer=tf.contrib.layers.xavier_initializer())
        b = tf.Variable(tf.constant(0.1, shape=[num_classes]))
        output = tf.nn.xw_plus_b(h_drop, W, b)

    return output

def detect_sex(name_list):
    x = []
    for name in name_list:
        name_vec = []
        for word in name:
            name_vec.append(vocab.get(word))
        while len(name_vec) < max_name_length:
            name_vec.append(0)
        x.append(name_vec)

    output = neural_network(len(vocabulary_list))

    saver = tf.train.Saver(tf.global_variables())
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        # 恢复前一次训练
        """
        ckpt = tf.train.get_checkpoint_state('.')
        if ckpt != None:
            print(ckpt.model_checkpoint_path)
        """
        saver.restore(sess, './model/name2sex-200')


        predictions = tf.argmax(output, 1)
        res = sess.run(predictions, {X:x, dropout_keep_prob:1.0})

        i = 0
        for name in name_list:
            print(name, '女' if res[i] == 0 else '男')
            i += 1

detect_sex(["唐宇迪", "褚小花", "刘德华", "韩冬梅"])
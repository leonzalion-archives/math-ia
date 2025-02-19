import functools
from pathlib import Path
import json


def predict(features_of_words, weights):
  predictions = []
  for word_features in features_of_words:
    prediction = 0

    for word_feature, weight in zip(weights, word_features):
      prediction += weight * word_feature

    predictions.append(prediction)
  return predictions


def cost_function(features_of_words, targets, weights):
  N = len(features_of_words)

  predictions = predict(features_of_words, weights)

  sq_error = 0
  for prediction, target in zip(predictions, targets):
    sq_error += (prediction - target) ** 2

  return 1 / N * sq_error


def cost_derivative(features_of_words, targets, weights, feature_index):
  N = len(features_of_words)
  sum = 0

  predictions = predict(features_of_words, weights)

  # Iterating through all words
  for prediction, target, word_features in zip(
    predictions, targets, features_of_words
  ):
    # For each word, find the inner value of the summation
    sum += (target - prediction) * word_features[feature_index]

  return -2.0 / N * sum


def cost_derivative_bias(features_of_words, targets, weights):
  N = len(features_of_words)
  sum = 0

  predictions = predict(features_of_words, weights)

  # Iterating through all words
  for prediction, target in zip(predictions, targets):
    # For each word, find the inner value of the summation
    sum += target - prediction

  return -2.0 / N * sum


def update_weights(features_of_words, targets, weights, learning_rate):
  num_features = len(features_of_words[0])

  weight_derivatives = [
    cost_derivative(features_of_words, targets, weights, feature_index)
    for feature_index in range(num_features)
  ]

  next_weights = []
  for feature_index in range(num_features):
    next_weights.append(
      weights[feature_index] - weight_derivatives[feature_index] * learning_rate
    )

  return next_weights


weights_history = []


def train(weights, features, targets):
  global weights_history

  # Hyperparameters to tweak
  epochs = 100000
  learning_rate = 0.008

  for epoch in range(epochs):
    next_weights = update_weights(features, targets, weights, learning_rate)

    cost = cost_function(features, targets, weights)

    # Printing cost so I can graph a cost history graph later
    print(cost)

    weights = next_weights
    weights_history.append(next_weights)
  return weights


word_stats = json.loads(Path("data/word-stats.json").read_text())


def parse_words(word_stats):
  """
  features_of_word: [
      is_word_common,
      num_capital_letters,
      num_consecutive_fingers,
      num_double_letters,
      num_home_row_letters,
      num_left_hand_letters,
      num_numbers,
      num_right_hand_letters,
      num_shifted_letters,
      word_length
  ]
  """
  targets = []
  features_of_words = []
  num_features = int()

  word_stats = sorted(
    word_stats,
    key=functools.cmp_to_key(
      lambda a, b: a["medianWpmRatio"] - b["medianWpmRatio"]
    ),
  )

  for word in word_stats:
    median_wpm_ratio = word["medianWpmRatio"]
    is_word_common = word["isWordCommon"]
    num_capital_letters = word["numCapitalLetters"]
    num_consecutive_fingers = word["numConsecutiveFingers"]
    num_double_letters = word["numDoubleLetters"]
    num_home_row_letters = word["numHomeRowLetters"]
    num_left_hand_letters = word["numLeftHandLetters"]
    num_right_hand_letters = word["numRightHandLetters"]
    num_shifted_letters = word["numShiftedLetters"]
    word_length = word["wordLength"]
    targets.append(median_wpm_ratio)

    features_of_word = [
      is_word_common,
      num_capital_letters,
      num_consecutive_fingers,
      num_double_letters,
      num_home_row_letters,
      num_left_hand_letters,
      num_right_hand_letters,
      num_shifted_letters,
      word_length,
      1,
    ]
    num_features = len(features_of_word)

    features_of_words.append(features_of_word)

  # Set all weights to 0 initially
  weights = [0 for i in range(num_features)]

  return targets, features_of_words, weights


targets, features_of_words, weights = parse_words(word_stats)

final_weights = train(weights, features_of_words, targets)
print("Final weights: ", final_weights)

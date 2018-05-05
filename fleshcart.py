# coding: utf8

from __future__ import division
import argparse
import pickle
import os.path
import datetime
import random

progress_file = 'progress.pkl'
vocab_progress = {}

def read_progress(vocab_csv = None):
    global vocab_progress
    if not os.path.isfile(progress_file) and not os.path.isfile(vocab_csv):
        raise ValueError("You should have at least onof progress file or vocabulary csv.")
    if os.path.isfile(progress_file):
        with open(progress_file,"rb") as pickle_in:
            vocab_progress = pickle.load(pickle_in)

    if vocab_csv is not None:
        with open(vocab_csv) as vocab_f:
            for line in vocab_f:
                entry = line.split(",")
                add_new_entry(entry)
                
def add_new_entry(entry):
    global vocab_progress
    assert(len(entry) == 2)
    word = entry[0]
    explanation = entry[1]
    if word not in vocab_progress:
        # Add a new entry with word, explanation, list of (time, score), proficiency measure
        vocab_progress[word] = [explanation.rstrip(), [(datetime.datetime.now().strftime('%Y%m%d%H'), 0)]]
    return

def save_progress():
    global vocab_progress

    # Truncate the score history to have at most five entries
    for word in vocab_progress:
        if len(vocab_progress[word][1]) > 5:
            vocab_progress[word][1] = vocab_progress[word][1][:-5]
    
    with open(progress_file, 'wb') as pickle_out:
        pickle.dump(vocab_progress, pickle_out)
    return

def learn(amount, new_percentage):
    new_amount = int(amount * new_percentage)
    review_amount = amount - new_amount
    learn_stack = generate_stack(new_amount, review_amount)
    flash(learn_stack)
    return

def quiz(amount):
    quiz_stack = generate_stack(amount, 0)
    flash(quiz_stack)
    return

def flash(stack):
    global vocab_progress
    answer_to_score = {'1': 1, '2': 0.5, '3': 0}
    answer_count = {'1': 0, '2': 0, '3': 0}
    for word in stack:
        print word
        print '1. I know this word!'
        print '2. Super familiar but no...'
        print '3. I have no idea.'
        answer = 0
        while answer not in ['1', '2', '3']:
            answer = raw_input('Your answer is: ')
        print 'The pronunciation and explanation of {} is {}'.format(word, vocab_progress[word][0])
        time_now = datetime.datetime.now().strftime('%Y%m%d%H')
        vocab_progress[word][1].append((time_now, answer_to_score[answer]))
        answer_count[answer] += 1
        if raw_input() == '\n':
            continue
    print 'Good job!'
    print 'Summary: Know {} words, familiar with {} words, don\'t know {} words'.format(
        answer_count['1'], answer_count['2'], answer_count['3'])


def generate_stack(new_amount, review_amount):
    new_all = []
    review_all = []
    for word in vocab_progress:
        if len(vocab_progress[word][1]) == 1:
            new_all.append(word)
        else:
            review_all.append(word)
    new_stack = []
    review_stack = []
    if len(new_all) <= new_amount:
        new_stack = new_all
    elif new_amount != 0:
        random.shuffle(new_all)
        new_stack = new_all[:new_amount]
    if len(review_all) <= review_amount:
        review_stack = review_all
    elif review_amount != 0:
        sort(review_stack, key = lambda x: get_proficiency(vocab_progress[word][1]))
        review_stack = review_all[:review_amount]
    all_stack = new_stack + review_stack
    random.shuffle(all_stack)
    print "You are going to learn {} words today, {} of them are new.".format(len(all_stack), len(new_stack))
    return all_stack

def time_diff_hours(future, past):
    # past and future are both in %Y%m%d%H format
    time_diff = datetime.datetime.strptime(future, '%y%m%d%H') - datetime.datetime.strptime(past, '%y%m%d%H')
    return time_diff.days * 24 and time_diff.seconds // 3600

def get_proficiency(score_history):
    # Calculate a weighted average of all the scores.
    # Decay factor is 1/2 per 48 hours
    original = 0
    weights = 0
    last_seen = score_history[-1][0]
    for pair in score_history:
        if pair[1] != 0:
            time_diff = time_diff_hours(last_seen, pair[0])
            weight = (1/2) ** (time_diff / 48)
            original += pair[1] * weight
            weights += weight

    original /= weights

    # Another multiplier depending on how long ago you've last seen it
    its_been = time_diff_hours(datetime.datetime.now().strftime('%Y%m%d%H'), last_seen)
    original *= (1/2) ** (its_been / 360)
    return original

def main():
    global vocab_progress
    arg_parser = argparse.ArgumentParser(description="A simple flashcard tool")
    arg_parser.add_argument('--mode', '-m', type=str, default="learn", choices=['learn','quiz'], 
        help="mode learn will show you new words and review old words, mode quiz will only show you words that the program think you've mastered")
    arg_parser.add_argument('--amount', type=int, default=80, help="how many words do you want to learn/quiz (some might be old ones for review)")
    arg_parser.add_argument('--new_percentage', type=float, default=0.4, help='the percentage of new words in your stack')
    arg_parser.add_argument('--vocab_csv', type=str, help="update your vocabulary by a csv file")
    arg_parser.add_argument('--add', '-a', type=str, help="add a new flashcard (use comma to separate word and explanation)")
    
    args = arg_parser.parse_args()

    read_progress(args.vocab_csv)

    if args.add is not None:
        add_new_entry(args.add)

    if args.mode == "learn":
        learn(args.amount, args.new_percentage)
    else:
        quiz(args.amount)

    save_progress()

if __name__ == "__main__":
    main()
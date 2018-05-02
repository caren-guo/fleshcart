# coding: utf8

import argparse
import pickle
import os.path
import datetime

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
        # Add a new entry with word, explanation, list of (time, score)
        vocab_progress[word] = [explanation, [(datetime.date.today().strftime("%Y%m%d"), 0)]]
    return

def save_progress():
    with open(progress_file, 'wb') as pickle_out:
        pickle.dump(vocab_progress, pickle_out)
    return

def learn(amount):
    return

def quiz(amount):
    return

def main():
    global vocab_progress
    arg_parser = argparse.ArgumentParser(description="A simple flashcard tool")
    arg_parser.add_argument('--mode', '-m', type=str, default="learn", choices=['learn','quiz'], 
        help="mode learn will show you new words and review old words, mode quiz will only show you words that the program think you've mastered")
    arg_parser.add_argument('--amount', type=int, default=80, help="how many words do you want to learn/quiz (some might be old ones for review)")
    arg_parser.add_argument('--vocab_csv', type=str, help="update your vocabulary by a csv file")
    arg_parser.add_argument('--add', '-a', type=str, help="add a new flashcard (use comma to separate word and explanation)")
    
    args = arg_parser.parse_args()

    read_progress(args.vocab_csv)

    if args.add is not None:
        add_new_entry(args.add)

    if args.mode == "learn":
        learn(args.amount)
    else:
        quiz(args.amount)

    save_progress()

if __name__ == "__main__":
    main()
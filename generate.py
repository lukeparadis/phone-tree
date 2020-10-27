import random
import os
from datetime import date, timedelta
import json
from collections import defaultdict
import sys

def check_equals_self(pairs):
    for name in pairs:
        if pairs[name] == name:
            return False
    return True

def check_equals_direct(pairs1, pairs2):
    for name in pairs1:
        if pairs1[name] == pairs2[name]:
            return False
    return True

def check_equals_reverse(pairs1, pairs2=None):
    
    pairs2 = pairs1 if pairs2 is None else pairs2

    for name in pairs1:
        if pairs1[pairs2[name]] == name:
            return False
    return True

def check_pairs(assignments, pairs, history_length):

    # if you call yourself
    if not check_equals_self(pairs):
        return False

    # if you call the person who called you
    if not check_equals_reverse(pairs):
        return False

    history_length_max = min(len(assignments),history_length)

    # check for conflicts between current and previous days
    for k in range(history_length_max):
    
        pairs_previous = assignments[-(k+1)]

        # dont call someone if you called them previously
        if not check_equals_direct(pairs_previous, pairs):
            return False

        # dont call someone if they called you recently
        if not check_equals_reverse(pairs_previous, pairs):
            return False

    return True

if __name__ == '__main__':

    config_filename = './config.json'
    output_filename = './assignments.csv' 

    # load config file with participant names, number of rounds,
    # random seed and start date
    with open(config_filename,'r') as fh:
        config = json.load(fh)

    # seed random
    if config['random_seed'] is not None:
        random.seed(config['random_seed'])

    # names and rounds
    names = config['names']
    num_names = len(names)

    num_rounds = config['num_rounds']
    history_length = config['history_length']
    max_tries = int(config['max_tries'])

    # generate dates
    num_days = (num_names-1)*num_rounds
    start_date = date.fromisoformat(config['start_date'])
    dates = [ start_date + timedelta(days=d) for d in range(num_days) ]

    # list to hold call assignments
    assignments = []

    sys.stdout.write('generating')

    for d in range(len(dates)):

        # total number of times through the while loop
        count = 0
        failed = False

        while True:
    
            # get a shuffled order for the person being called
            pairs = { names[k]:name for k,name in enumerate(random.sample(names,num_names)) }

            # check and see if it is a valid assignment
            if check_pairs(assignments, pairs, history_length):
                break
        
            # increment count
            count += 1

            # if count goes above the max count, mark it as a failure
            if count == max_tries:
                print('\n[ERROR] max tries {} reached, increase `max_tries` and run again.'.format(max_tries))
                sys.exit(1)
                break
       
        # add pairs to running assignments
        assignments.append(pairs)

        # print a dot for each day generated
        sys.stdout.write('.')
        sys.stdout.flush()

    print()

    ## generate csv

    # participants header 
    text = 'Donks,'

    # header columns for each date
    text += ','.join([ date.strftime('%m/%d') for date in dates ]) + '\n'

    # write line for each participant
    for name in names:

        # participant's name column
        text += name + ',' 

        # get all calls for a participant
        calls = [ a[name] for a in assignments ]

        # participant's assignments
        text += ','.join(calls) + '\n'

    with open(output_filename,'w') as fh:
        fh.write(text)

    print('results written to :',output_filename)


from typing import Optional
import re
from nltk.corpus import words

import pandas as pd
import string
import random
from collections import Counter


def get_new_word_list(poss, cts, l_in_w, wl):
    hold = []
    for w in wl:
        keep_flag = True
        for l in string.ascii_lowercase:
            if w.count(l) > cts[l]:
                keep_flag = False

        for idx, l in enumerate(w):
            if l not in poss[idx]:
                keep_flag = False

        if (Counter("".join(l_in_w)) - Counter(w)):
           keep_flag = False
        if keep_flag:
            hold.append(w)
    return hold

def evaluate_guess(word, guess):
    result_l = [None, None, None, None, None]
    popped_word = word
    for idx, l in enumerate(guess):
        if word[idx] == l:
            result_l[idx] = "2"
            popped_word = popped_word.replace(l, '', 1)

    for idx, l in enumerate(guess):
        if result_l[idx] is not None:
            continue
        elif l in popped_word:
            result_l[idx] = "1"
            popped_word = popped_word.replace(l, '', 1)
        else:
            result_l[idx] = "0"
    return ''.join(result_l)

def get_word_list():
    return [w for w in words.words() if (len(w) == 5) and not (re.search("[A-Z]", w))]

def get_new_word(wl):
    ct = Counter()
    for w in wl:
        ct += Counter(w)
    word_scores = {}
    for w in wl:
        word_scores[w] = 0
        for l in set(w):
            word_scores[w] += ct[l]
    return max(word_scores, key=word_scores.get)



def wordle_solver(goal_word: Optional[str] = None, seed_word: Optional[str] = None, random_seed_word=False):
    word_list = get_word_list()
    letter_possibilities = {n: list(string.ascii_lowercase) for n in range(6)}
    letter_counts = {l: 5 for l in string.ascii_lowercase}
    for i in range(100):

        if (i == 0) and (seed_word is not None):
            cur_word = seed_word
        elif (i == 0) and random_seed_word:
            cur_word = random.sample(word_list, 1)[0]
        else:
            cur_word = get_new_word(word_list)

        if goal_word is None:
            run_flag = True
            while run_flag:
                print(f"Try: {cur_word}")
                result_l = input("Please enter how I did:")
                if result_l == "no":
                    cur_word = random.sample(word_list, 1)[0]
                    continue
                assert(len(result_l) == 5)
                break
        else:
            print(f"Try: {cur_word}")
            result_l = evaluate_guess(goal_word, cur_word)

        if result_l == '22222':
            print(f"We won in {i + 1} turns!")
            break

        letters_in_cur_word = []
        for idx, res in enumerate(result_l):
            if res == "0":
                # number of letters must equal this
                l_ct = cur_word[:idx].count(cur_word[idx])
                l_ct = 0 if l_ct is None else l_ct
                letter_counts[cur_word[idx]] = min(l_ct, letter_counts[cur_word[idx]])
                if l_ct == 0:
                    for l in letter_possibilities:
                        try:
                            letter_possibilities.pop(cur_word[idx])
                        except:
                            continue
            elif res == "1":
                letters_in_cur_word.append(cur_word[idx])
                letter_possibilities[idx].remove(cur_word[idx])
            elif res == "2":
                letters_in_cur_word.append(cur_word[idx])
                letter_possibilities[idx] = [cur_word[idx]]
                letter_counts[cur_word[idx]] += 1

        word_list = get_new_word_list(letter_possibilities, letter_counts, letters_in_cur_word, word_list)
    return i + 1

def test_seed_words(seed_words):
    results = {}
    random.seed(42)
    for w in random.sample(get_word_list(), 500):
        for seed_word in seed_words + [None]:
            r = wordle_solver(w, seed_word)
            seed_key = seed_word if seed_word is not None else "_random_word"
            try:
                results[seed_key].append(r)
            except:
                results[seed_key] = [r]
    df = pd.DataFrame(results)
    return df


if __name__ == "__main__":
    wordle_solver("siege", random_seed_word=False)


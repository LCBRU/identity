from flask import current_app
from functools import lru_cache

@lru_cache
def levenshtein_distance(string_a, string_b):
    current_app.logger.info(f'levenshtein_distance: a="{string_a}"; b="{string_b}"')
    if string_a == "":
        return len(string_b)
    if string_b == "":
        return len(string_a)
    if string_a[-1] == string_b[-1]:
        cost = 0
    else:
        cost = 1
       
    result = min([
        levenshtein_distance(string_a[:-1], string_b)+1, # Deletion
        levenshtein_distance(string_a, string_b[:-1])+1, # Insertion
        levenshtein_distance(string_a[:-1], string_b[:-1]) + cost, # Substitution
    ])

    return result


def similarity(string_a, string_b):
    return 1 - (levenshtein_distance(string_a, string_b)/ max(len(string_a), len(string_b)))

from flask import current_app
from functools import lru_cache

@lru_cache(maxsize=500, typed=False)
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


# def levenshtein_distance_iter(string_a, string_b):
#     current_app.logger.info(f'levenshtein_distance_iter: a="{string_a}"; b="{string_b}"')
#     # for all i and j, d[i,j] will hold the Levenshtein distance between
#     # the first i characters of s and the first j characters of t

#     Matrix = [[0 for x in range(w)] for y in range(h)] 
    
#     set each element in d to zero
    
#     // source prefixes can be transformed into empty string by
#     // dropping all characters
#     for i from 1 to m + 1:
#         d[i, 0] := i
    
#     // target prefixes can be reached from empty source prefix
#     // by inserting every character
#     for j from 1 to n + 1:
#         d[0, j] := j
    
#     for j from 1 to n + 1:
#         for i from 1 to m + 1:
#             if s[i] = t[j]:
#                 substitutionCost := 0
#             else:
#                 substitutionCost := 1

#             d[i, j] := minimum(d[i-1, j] + 1,                   // deletion
#                                 d[i, j-1] + 1,                   // insertion
#                                 d[i-1, j-1] + substitutionCost)  // substitution
    
#     return d[m + 1, n + 1]
    

def similarity(string_a, string_b):
    return 1 - (levenshtein_distance(string_a, string_b)/ max(len(string_a), len(string_b)))

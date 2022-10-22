from math import *

def euclidean_distance(a, b):
	return sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def manhattan_distance(a, b):
	return abs(a[0] - b[0]) + abs(a[1] - b[1])

def chebyshev_distance(a, b):
	return max(abs(a[0] - b[0]), abs(a[1] - b[1]))

if __name__ == "__main__":
    a = (2, 4)
    b = (3, -1)

    print("euclidean_distance", euclidean_distance(a, b))
    print("manhattan_distance", manhattan_distance(a, b))
    print("chebyshev_distance", chebyshev_distance(a, b))
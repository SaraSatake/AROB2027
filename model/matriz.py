import numpy as np
import math
from pathlib import Path

my_array3 = np.zeros((20, 20)) 
my_array3[0][1] = 2
print(my_array3)
print(my_array3[0][1])
np.savetxt("foo.csv", my_array3, delimiter=",", fmt='%d')
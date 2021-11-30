# Definition of radius
r = 0.43

# Import the math package
import math # DO NOT USE 'I'mport

# Calculate C
C = math.pi*2*r

# Calculate A
A = math.pi*r**2

# Build printout
print("Circumference: " + str(C))
print("Area: " + str(A))

# Definition of radius
r = 192500

#------------------------------------------------------------
# Import radians function of math package
import math
from math import radians

print(math.pi)
print("radians 12 = ", radians(12))

# Travel distance of Moon over 12 degrees. Store in dist.
dist = r * radians(12)

# Print out dist
print(dist)
#-----------------------------------------------------------
# Create list baseball
baseball = [180, 215, 210, 210, 188, 176, 209, 200]

# Import the numpy package as np
import numpy as np

# Create a numpy array from baseball: np_baseball
np_baseball = np.array(baseball)

# Print out type of np_baseball
print(np_baseball)
#----------------------------------------------------------
# height is available as a regular list
print(height_in)
# Import numpy
import numpy as np

# Create a numpy array from height_in: np_height_in
np_height_in = np.array(height_in)

# Print out np_height_in
print(np_height_in)

# Convert np_height_in to m: np_height_m
np_height_m = np_height_in * 0.0254

# Print np_height_m
print(np_height_m)
#--------------------------------------------------
# height and weight are available as regular lists
print("height ", height_in)
print("weight ", weight_lb)
# Import numpy
import numpy as np

# Create array from height_in with metric units: np_height_m
np_height_m = np.array(height_in) * 0.0254

# Create array from weight_lb with metric units: np_weight_kg
np_weight_kg = np.array(weight_lb) * 0.453592

# Calculate the BMI: bmi
bmi = np_weight_kg/(np_height_m ** 2)

# Print out bmi
print("bmi = ", bmi)
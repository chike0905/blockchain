# CONFIGURATION FILE

# log size of the ring
LOGSIZE = 8
SIZE = 1<<LOGSIZE

# successors list size (to continue operating on node failures)
N_SUCCESSORS = 4

# INT = interval in seconds
# RET = retry limit

# Stabilize
STABILIZE_INT = 3
STABILIZE_RET = 10

# Fix Fingers
FIX_FINGERS_INT = 3

# Update Successors
UPDATE_SUCCESSORS_INT = 3
UPDATE_SUCCESSORS_RET = 10

# Find Successors
FIND_SUCCESSOR_RET = 10
FIND_PREDECESSOR_RET = 10

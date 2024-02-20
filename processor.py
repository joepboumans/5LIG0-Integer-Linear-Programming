from pulp import *
import itertools as it
# Number of processors
n_a = 1
n_b = 1
# Processors
processors = ["A"+str(i) for i in range(n_a)]
predecesssors = [0, 0, 1, 0]
time_costs = [
    [821, 334, 754, 679],
]
n_tasks = len(time_costs[0])
I = range(n_tasks)
J = range(len(I))

# Setup full time schedule with all postions and tasks
t = {(i,j): LpVariable(f"x{i}{j}", 0,1, LpBinary) for i,j in it.product(I, J)}
print(f"{t=}")

# Setup timeline
c = {j: LpVariable(f"c{j}", 0, None, LpContinuous) for j in J}
print(f"{c=}")

prob = LpProblem("SingleProcessorSchedulingProblem", LpMinimize)
prob += sum(c[j] for j in J)

# Constraints
# Each tasks needs to be assigned to exactly one position
for task in I:
    prob += (sum(t[(task, position)] for position in J) == 1, f"eq1_{task}")
# Each position needs to be assigned to exactly one task
for position in J:
    prob += (sum(t[(task, position)] for task in I) == 1, f"eq2_{position}")
# Each task needs to be scheduled after its predecessor
for pred, task in zip(predecesssors, I):
    if task == 0:
        prob += (t[(task, 0)] == 1, f"eq_Tstart")
        prob += (c[0] == 0, "eq_Cstart")
        continue
    
    prob += (c[task] >= c[pred] + t, f"eq3_{task}")

print(prob)

result = prob.solve()


            
results = prob.solve(PULP_CBC_CMD(msg=1))
status = LpStatus[results]
print(f"{status=}")
print(f"Model: ", prob)
print(f"objective: {value(prob.objective)}")
print("Decision --- \n", [(variables.name,variables.varValue) for variables in prob.variables() if variables.varValue!=0])
seq = []
for j in J:
    for i in I:
        if t[(i,j)].varValue==1:
            seq.append(i+1)
print(seq)
print(t)
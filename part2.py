from pulp import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def get_cmap(n, name='hsv'):
    return plt.cm.get_cmap(name, n)


if __name__ == '__main__':
    cmap = get_cmap(12 * 2)
    n_a = 1
    n_b = 0
    processors = ["A"+str(i) for i in range(1,1+n_a)] + ["B"+str(i) for i in range(1,1+n_b)]
    tasks = ["T"+str(i) for i in range(1,13)]
    time_costs = [
        [821, 334, 754, 679, 805, 441, 577, 239, 320, 487, 345, 399],
        [576, 297, 567, 362, 339, 267, 409, 197, 239, 765, 498, 274]
    ]
    time_costs_per_processor = [ time_costs[0] if "A" in processor else time_costs[1] for processor in processors ]
    processor = processors[0]
    # Immediate predecessor of each task
    predecesssors = [0, 1, 2, 1, 4, 5, 4, 7, 8, 7, 10, 11, 12]
    # Predecessor of each task
    P = [[] for i in range(len(tasks))]
    Q = [[0 for i in range(len(tasks))] for i in range(len(tasks))]
    for i,task in enumerate(tasks):
        for j,_ in enumerate(tasks):
            if predecesssors[i] == 0:
                P[i].append(0)
                continue
            if predecesssors[i] - 1 == j:
                P[i].append(1)
            else:
                P[i].append(0)
    # All predecessors of each task
    for i in range(len(tasks)):
        for j in range(len(tasks)):
            if P[i][j] == 1:
                Q[i][j] = 1
                for k in range(len(tasks)):
                    if P[j][k] == 1:
                        Q[i][k] = 1

    possible_schedule = [(processor, task) for processor in processors for task in tasks]
    schedule = LpVariable.dicts("schedule", possible_schedule, 0, 1, LpBinary)
        
    starting_times = [LpVariable("T_start" + str(i), 0, None, LpInteger) for i in range(len(tasks))]
    overlapping_jobs = [LpVariable("OJ" + str(i) +'-' + str(j), 0, 1, LpBinary) for i in range(len(tasks)) for j in range(len(tasks))]

    max_makespan = 70000
    makespan = LpVariable("makespan", 0, max_makespan, LpInteger)
    prob = LpProblem("schedule_problem", LpMinimize)

    # Objective funtion
    prob += makespan
    
    # Constraints
    # The makespan is the maximum of all finishing times
    for task in tasks:
        prob += makespan >= starting_times[tasks.index(task)] + time_costs_per_processor[0][tasks.index(task)]

    # Each task is assigned once 
    for task in tasks:
        prob += lpSum([schedule[(processor, task)]]) == 1

    # A task can only be schedule after the end of its predecessor on all processors
    for j, task_j in enumerate(tasks):
        for k, task_k in enumerate(tasks):
            if j == k:
                continue
            if Q[j][k] != 0:
                continue
            prob += schedule[(processor, task_j)] + schedule[(processor, task_k)] + overlapping_jobs[j*len(tasks)+k] + overlapping_jobs[k*len(tasks)+j] <= 3
            prob += starting_times[k] - time_costs_per_processor[0][j] - starting_times[j] >= - max_makespan * overlapping_jobs[j*len(tasks)+k]
            prob += starting_times[k] - time_costs_per_processor[0][j] - starting_times[j] <=  max_makespan * (1 - overlapping_jobs[j*len(tasks)+k])

    # A task can only be schedule after the end of its predecessor on all processors
    for i, task in enumerate(tasks):
        for j, pred in enumerate(tasks):
            if P[i][j] == 0:
                continue
            prob += starting_times[i] >= starting_times[j] + time_costs_per_processor[0][j]
    prob += starting_times[0] == 0

    results = prob.solve()
    status = LpStatus[results]
    print(status)
    print("objective: ", value(prob.objective))
    
    print("starting times: ", [value(starting_times[i]) for i in range(len(tasks))])
    print("makespan: ", value(makespan))
    print("schedule:")
    for processor in processors:
        for task in tasks:
            print(processor, task, value(schedule[(processor, task)]))
            
    # Plot schedule
    fig, ax = plt.subplots()
    ax.set_xlim(0, value(makespan))
    ax.set_ylim(-1, len(processors) + 0.25)
    ax.set_yticks(range(len(processors)))
    ax.set_yticklabels(processors)
    ax.set_xlabel("Time")
    ax.set_ylabel("Processor")
    ax.set_title("Schedule")
    ax.grid(axis='x')
    ax.set_axisbelow(True)

    for task in tasks:
        for processor in processors:
            if value(schedule[(processor, task)]) == 1:
                ax.barh(processors.index(processor),
                        time_costs_per_processor[processors.index(processor)][tasks.index(task)],
                        left=value(starting_times[tasks.index(task)]),
                        edgecolor="black",
                )
                ax.annotate(
                    task,
                    (value(starting_times[tasks.index(task)]) + time_costs_per_processor[processors.index(processor)][tasks.index(task)]/2, processors.index(processor)),
                    color="white",
                    weight="bold",
                    fontsize=10,
                    ha="center",
                    va="center"
                )
    
    fig.savefig("part2.png", dpi=300, bbox_inches="tight")
    plt.show()
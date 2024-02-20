from pulp import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def get_cmap(n, name='hsv'):
    return plt.cm.get_cmap(name, n)


if __name__ == '__main__':
    cmap = get_cmap(12 * 2)
    n_a = 12
    n_b = 0
    processors = ["A"+str(i) for i in range(1,1+n_a)] + ["B"+str(i) for i in range(1,1+n_b)]
    tasks = ["T"+str(i) for i in range(1,13)]
    time_costs = [
        [821, 334, 754, 679, 805, 441, 577, 239, 320, 487, 345, 399],
        [576, 297, 567, 362, 339, 267, 409, 197, 239, 765, 498, 274]
    ]
    time_costs_per_processor = [ time_costs[0] if "A" in processor else time_costs[1] for processor in processors ]
    
    #  predecessor of each task
    predecesssors = [0, 1, 2, 1, 4, 5, 4, 7, 8, 7, 10, 11, 12]
    # predecessor of each task
    P = [[] for i in range(len(tasks))]
    for i,task in enumerate(tasks):
        for j,_ in enumerate(tasks):
            if predecesssors[i] == 0:
                P[i].append(0)
                continue
            if predecesssors[i] - 1 == j:
                P[i].append(1)
            else:
                P[i].append(0)

    possible_schedule = [(processor, task) for processor in processors for task in tasks]
    schedule = LpVariable.dicts("schedule", possible_schedule, 0, 1, LpBinary)
        
    starting_times = [LpVariable("T_start" + str(i), 0, None, LpInteger) for i in range(len(tasks))]

    max_makespan = 70000
    makespan = LpVariable("makespan", 0, max_makespan, LpInteger)
    prob = LpProblem("schedule_problem", LpMinimize)

    # Objective funtion
    prob += makespan
    
    # Only for 12 processors
    for (i,task),(a,processor) in zip(enumerate(tasks), enumerate(processors)):
        prob += schedule[(processor, task)] == 1
    # Constraints
    # The makespan is the maximum of all finishing times
    for task in tasks:
        for processor in processors:
            prob += makespan >= starting_times[tasks.index(task)] + time_costs_per_processor[processors.index(processor)][tasks.index(task)] * schedule[((processor, task))]

    # Each task is assigned to exactly one processor
    for task in tasks:
        prob += lpSum([schedule[(processor, task)] for processor in processors]) == 1
    
    # Every task has its own private processor
    for task, processor in zip(tasks, processors):
        prob += schedule[(processor, task)] == 1

    # A task can only be schedule after the end of its predecessor on all processors
    for i, task in enumerate(tasks):
        for j, pred in enumerate(tasks):
            if P[i][j] == 0:
                continue
            prob += starting_times[i] >= starting_times[j]
            for processor in processors:
                for other_processor in processors:
                    prob += starting_times[i] >= starting_times[j] + time_costs_per_processor[processors.index(processor)][j] * (schedule[(other_processor, task)] + schedule[(processor, pred)] -1 )
    prob += starting_times[0] == 0

    print(prob)
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
    fig.savefig("part1.png", dpi=300, bbox_inches="tight")
    plt.show()
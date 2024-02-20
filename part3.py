from pulp import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def get_schedule(n_a, n_b, max_duration):
    processors = ["A"+str(i) for i in range(1,1+n_a)] + ["B"+str(i) for i in range(1,1+n_b)]
    tasks = ["T"+str(i) for i in range(1,13)]
    time_costs = [
        [821, 334, 754, 679, 805, 441, 577, 239, 320, 487, 345, 399],
        [576, 297, 567, 362, 339, 267, 409, 197, 239, 765, 498, 274]
    ]
    time_costs_per_processor = [ time_costs[0] if "A" in processor else time_costs[1] for processor in processors ]
    
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
    schedule = LpVariable.dicts("schedule", possible_schedule, 0, 1, LpInteger)
        
    max_makespan = 70000
    # warm start starting times based on predecessors execution time and previous found duration
    starting_times = []
    for i,task in enumerate(tasks):
        if i == 0:
            starting_times.append(LpVariable("T_start" + str(i), 0, max_duration, LpInteger))
            continue
        exec_times = []
        for k,j in enumerate(P[i]):
            if j == 1:
                exec_times.append(time_costs[0][k])
                exec_times.append(time_costs[1][k])
        min_start_time = min(exec_times)
        print(f"Adding T_start{i} with min_start_time {min_start_time}")
        starting_times.append(LpVariable("T_start" + str(i), min_start_time, max_duration, LpInteger))
    
    overlapping_jobs = [LpVariable("OJ" + str(i) +'-' + str(j), 0, 1, LpInteger) for i in range(len(tasks)) for j in range(len(tasks))]
    makespan = LpVariable("makespan", 0, max_duration, LpInteger)
    prob = LpProblem("schedule_problem", LpMinimize)

    # Objective funtion
    prob += makespan
    
    # Constraints
    # The makespan is the maximum of all finishing times
    for task in tasks:
        for processor in processors:
            prob += makespan >= starting_times[tasks.index(task)] + time_costs_per_processor[processors.index(processor)][tasks.index(task)] * schedule[((processor, task))]

    # Each task is assigned to exactly one processor
    for task in tasks:
        prob += lpSum([schedule[(processor, task)] for processor in processors]) == 1

    # If a task is schedule on the same processor as another task, they cannot overlap
    for j, task_j in enumerate(tasks):
        for k, task_k in enumerate(tasks):
            for a,processor in enumerate(processors):
                prob += schedule[(processor, task_j)] + schedule[(processor, task_k)] + overlapping_jobs[j*len(tasks)+k] + overlapping_jobs[k*len(tasks)+j] <= 3
            if j == k:
                continue
            if Q[j][k] != 0:
                continue
            prob += starting_times[k] - lpSum([time_costs_per_processor[a][j] * schedule[(processor, task_j)] for a,processor in enumerate(processors)]) - starting_times[j] >= - max_makespan * overlapping_jobs[j*len(tasks)+k]
            prob += starting_times[k] - lpSum([time_costs_per_processor[a][j] * schedule[(processor, task_j)] for a,processor in enumerate(processors)]) - starting_times[j] <=  max_makespan * (1 - overlapping_jobs[j*len(tasks)+k])

    # A task can only be schedule after the end of its predecessor on all processors
    for i, task in enumerate(tasks):
        for j, pred in enumerate(tasks):
            if P[i][j] == 0:
                continue
            for processor in processors:
                prob += starting_times[i] >= starting_times[j] + time_costs_per_processor[processors.index(processor)][j] * schedule[(processor, pred)]
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
    
    # plt.show()
    fig.savefig("na%d-nb%d-schedule-ms%d.png" % (n_a, n_b, value(makespan)), dpi=300, bbox_inches="tight")
    return value(makespan)

if __name__ == "__main__":
    costs = {"A": 62, "B": 89}
    makespans = []
    system_costs = []
    max_duration = 6454
    n_b = 0
    for n_a in range(1, 5):
        makespans.append(get_schedule(n_a, n_b, max_duration + 2))
        system_costs.append(n_a * costs["A"] + n_b * costs["B"])
        max_duration = min(makespans)

    print(makespans)
    print(system_costs)

    makespans = [i / 1000 for i in makespans]
    fig, ax = plt.subplots()

    ax.set_xlabel("Costs ($)")
    ax.set_ylabel("Execution Time (s)")
    ax.grid()
    ax.set_axisbelow(True)

    z = [i * j for i, j in zip(makespans, system_costs)]
    p = ax.scatter(system_costs, makespans, c=z, cmap="plasma", s=100)
    fig.colorbar(p, ax=ax)
    fig.savefig("paretor_part3.png", dpi=300, bbox_inches="tight")
    plt.show()
    

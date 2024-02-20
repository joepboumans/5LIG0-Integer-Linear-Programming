import matplotlib.pyplot as plt
import re
import glob as gl

if __name__ == "__main__":
    makespans = []
    system_costs = []
    costs = {"A": 62, "B": 89}

    # Get image files
    result_path = "part3_results/"
    results = gl.glob(result_path + "na*-nb*-schedule-ms*.png")
    results = [i.replace("part3_results\\", "") for i in results]

    for result in results:
        match = re.findall(r"na(\d+)-nb(\d+)-schedule-ms(\d+).png", result)
        n_a = int(match[0][0])
        n_b = int(match[0][1])
        makespans.append(int(match[0][2]))
        system_costs.append(n_a * costs["A"] + n_b * costs["B"])

    makespans = [i / 1000 for i in makespans]
    fig, ax = plt.subplots()

    ax.set_xlabel("Costs ($)")
    ax.set_ylabel("Execution Time (s)")
    ax.grid()
    ax.set_axisbelow(True)

    z = [i * j for i, j in zip(makespans, system_costs)]
    p = ax.scatter(system_costs, makespans, c=z, cmap="plasma", s=100)
    fig.colorbar(p, ax=ax)
    fig.savefig("pareto_part3.png", dpi=300, bbox_inches="tight")
    
    makespans = []
    system_costs = []

    # Get image files
    result_path = "part4_results/"
    results = gl.glob(result_path + "na*-nb*-schedule-ms*.png")
    results = [i.replace("part4_results\\", "") for i in results]

    for result in results:
        match = re.findall(r"na(\d+)-nb(\d+)-schedule-ms(\d+).png", result)
        n_a = int(match[0][0])
        n_b = int(match[0][1])
        makespans.append(int(match[0][2]))
        system_costs.append(n_a * costs["A"] + n_b * costs["B"])

    makespans = [i / 1000 for i in makespans]
    fig, ax = plt.subplots()

    ax.set_xlabel("Costs ($)")
    ax.set_ylabel("Execution Time (s)")
    ax.grid()
    ax.set_axisbelow(True)

    z = [i * j for i, j in zip(makespans, system_costs)]
    p = ax.scatter(system_costs, makespans, c=z, cmap="plasma", s=100)
    fig.colorbar(p, ax=ax)
    fig.savefig("pareto_part4.png", dpi=300, bbox_inches="tight")
    plt.show()
    
import random
import model
import os

GENERATIONS = 500
POPULATION_SIZE = 5000
N_REPEATS = 3
N_ENVIRONMENTS = 50
MAX_SD = 0.3

experiments = [  # factors ordered by sorted order of factor_defns keys
    # ['BY_LINEAGE', 'CORRELATED', 'N_OFFSPRING', 'P_REPRODUCE', 'P_SELECTION', 'RESTRICTION']
    [0, 1, 0, 0, 0, 1]
]


def get_ar_timeseries(theta, sd, bias, generations):
    value = 0
    t = random.randint(-100, -50)  # initial burn-in period
    for i in range(t, generations):
        value = theta * value + random.gauss(0, sd) + bias  # error term with mean = 0 and sd = sd
        if i >= 0:
            yield value


def init_population(n):
    return [model.Element(x) for x in range(0, n)]  # assign sequential lineage IDs


def get_environment_specification():
    # Environment change is modelled as a change in the relationship between entity and environment.

    # Entity is represented by a fitness and a fidelity (to parent)
    # The difficulty is in how to connect fidelity and fitness (both composites) to environmental change.
    # Without knowing the specifics of the change, and modelling the reaction of each entity to that change,
    # we can only model abstracts.

    # Parental relationships provide a lineage, where related entities should have a similar response to change
    # In other words, environmental change is a change in fitness, but one where the change is conditioned
    # by lineage.

    for i in range(N_ENVIRONMENTS):
        yield random.uniform(-MAX_SD, MAX_SD), random.uniform(0, MAX_SD), random.uniform(-MAX_SD/10, MAX_SD/10)


def generate_environment(spec, by_lineage):
    # deltas for lineages = [delta for t0, delta for t1, delta for t2..., delta for tn]
    # [deltas for population at time 0,deltas at time 1...at final gen]

    if not by_lineage:
        return [[x for x in get_ar_timeseries(*spec, generations=GENERATIONS)]]
    else:
        return [[x for x in get_ar_timeseries(*spec, generations=GENERATIONS)] for i in range(POPULATION_SIZE)]


factor_defns = {
    'P_REPRODUCE': [0, 0.66],
    'P_SELECTION': [0, 0.66],
    'N_OFFSPRING': [2, 5],
    'RESTRICTION': [False, True],
    'CORRELATED': [False, True],
    'BY_LINEAGE': [False, True]
}


def write_environment(run_number, environments):

    if not os.path.exists("environments"):
        os.makedirs("environments")

    with open("environments/environments{}.csv".format(str(run_number)), "w") as e:
        for n in range(len(environments)):  # number of environments
            # [[e0: delta for t0, delta for t1, delta for t2..., delta for tn], [en:] => run, lineage, t0, t1,,...tn
            lineage_environment = [str(delta) for delta in environments[n]]
            e.write(str(run_number) + "," +
                    str(n) + "," +
                    ",".join(lineage_environment) +
                    "\n")


def construct_line(run_number, experiment_number, environment, result, factors):
    line = {
        'experiment': experiment_number,
        'run': run_number,
        'ar_theta': environment[0],
        'ar_sd': environment[1],
        'ar_bias': environment[2]
    }
    line.update(result)
    line.update({k: factor_defns[k].index(v) for k, v in factors.items()})  # convert back from values to factor levels
    return line


def format_results_line(line):
    return ",".join([str(line[x]) for x in sorted(line.keys())])


def format_results_header(line):
    return ",".join([str(x) for x in sorted(line.keys())])


def main():
    assert len(factor_defns) == len(experiments[0])  # Same order - must use appropriate design

    experiment_number = 0
    run_number = 0

    with open("results.csv", "w") as f:
        for experiment in experiments:

            factors = {k: factor_defns[k][v] for k, v in zip(sorted(factor_defns.keys()), experiment)}

            for environment_specification in get_environment_specification():

                environments = generate_environment(environment_specification, factors['BY_LINEAGE'])
                write_environment(run_number, environments)

                for repeat in range(0, N_REPEATS):

                    print("{0}/{1}".format(run_number + 1, N_REPEATS * N_ENVIRONMENTS * len(experiments)))
                    results = model.run(factors=factors,
                                        population=init_population(POPULATION_SIZE),
                                        generations=GENERATIONS,
                                        population_limit=10,
                                        environment=environments)

                    if run_number == 0:
                        f.write(format_results_header(construct_line(run_number,
                                                                     experiment_number,
                                                                     environment_specification,
                                                                     results[0],
                                                                     factors)) + "\n")

                    f.write("\n".join([format_results_line(
                        construct_line(run_number, experiment_number, environment_specification, result, factors)
                    ) for result in results]))
                    f.write("\n")

                    run_number += 1

            experiment_number += 1


if __name__ == "__main__":
    main()


    # # http://www.itl.nist.gov/div898/handbook/pri/section3/eqns/2to6m3.txt
    # experiments = [
    #    [0,  0,  0,  1,  1,  1],
    #    [1,  0,  0,  0,  0,  1],
    #    [0,  1,  0,  0,  1,  0],
    #    [1,  1,  0,  1,  0,  0],
    #    [0,  0,  1,  1,  0,  0],
    #    [1,  0,  1,  0,  1,  0],
    #    [0,  1,  1,  0,  0,  1],
    #    [1,  1,  1,  1,  1,  1]
    # ]

    # http://www.itl.nist.gov/div898/handbook/pri/section3/eqns/2to7m3.txt
    # experiments = [
    #     # X1  X2  X3  X4  X5  X6  X7
    #     #--------------------------
    #     [0,  0,  0,  0,  0,  0,  0],
    #     [1,  0,  0,  0,  1,  0,  1],
    #     [0,  1,  0,  0,  1,  1,  0],
    #     [1,  1,  0,  0,  0,  1,  1],
    #     [0,  0,  1,  0,  1,  1,  1],
    #     [1,  0,  1,  0,  0,  1,  0],
    #     [0,  1,  1,  0,  0,  0,  1],
    #     [1,  1,  1,  0,  1,  0,  0],
    #     [0,  0,  0,  1,  0,  1,  1],
    #     [1,  0,  0,  1,  1,  1,  0],
    #     [0,  1,  0,  1,  1,  0,  1],
    #     [1,  1,  0,  1,  0,  0,  0],
    #     [0,  0,  1,  1,  1,  0,  0],
    #     [1,  0,  1,  1,  0,  0,  1],
    #     [0,  1,  1,  1,  0,  1,  0],
    #     [1,  1,  1,  1,  1,  1,  1]
    # ]

    # http://www.itl.nist.gov/div898/handbook/pri/section3/eqns/2to5m2.txt
    # experiments = [  # factors ordered by sorted order of factor_defns keys
    #     [0, 0, 0, 1, 1],
    #     [1, 0, 0, 0, 0],
    #     [0, 1, 0, 0, 1],
    #     [1, 1, 0, 1, 0],
    #     [0, 0, 1, 1, 0],
    #     [1, 0, 1, 0, 1],
    #     [0, 1, 1, 0, 0],
    #     [1, 1, 1, 1, 1],
    # ]

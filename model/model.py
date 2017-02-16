import random
import math
import statistics
from collections import OrderedDict
from collections import Counter

class Element:

    def __init__(self, lineage, fitness=None, fidelity=None):
        if fitness is None:
            fitness = random.uniform(0.0, 0.3)
        if fidelity is None:
            fidelity = random.uniform(0.0, 0.3)

        assert 0 <= fitness <= 1.0
        assert 0 <= fidelity <= 1.0

        self.fitness = fitness
        self.fidelity = fidelity
        self.lineage = lineage

    def __str__(self):
        return str(self.fitness)


def get_random_boolean(p):
    return random.random() < p


def reproduction(factors, population):

    def derive(source, correlation):
        x = random.gauss(source, 1.0 - correlation)
        while x < 0.0 or x > 1.0:
            x = random.gauss(source, 1.0 - correlation)
        assert 1.0 >= x >= 0.0
        return x

    def get_offspring(factors, parent):
        """
        Core of model - establishes relationship between parent and offspring
        """

        p_reproduce = parent.fitness if factors['P_REPRODUCE'] == 0 else factors['P_REPRODUCE']
        if not get_random_boolean(p_reproduce):
            return []

        fidelity_fidelity = parent.fidelity if factors['CORRELATED'] else random.random()
        offspring = []

        for i in range(random.randint(0, factors['N_OFFSPRING'])):
            fitness = derive(parent.fitness, parent.fidelity)
            fidelity = derive(parent.fidelity, fidelity_fidelity)
            offspring.append(Element(parent.lineage, fitness, fidelity))
        return offspring

    return [x for y in population for x in get_offspring(factors, y)]


def selection(factors, population):
    return [x for x in population if get_random_boolean(
        x.fitness if factors['P_SELECTION'] == 0 else factors['P_SELECTION']
    )]


def apply_environment_change(environment_change, population):

    new_population = []

    for e in population:
        delta = environment_change[e.lineage] if (len(environment_change) > 1) else environment_change[0]
        new_fitness = min(1.0, max(0.0, (e.fitness + delta)))  # bound to [0,1], don't worry about shape
        new_population.append(Element(e.lineage, new_fitness, e.fidelity))

    return new_population


def get_results_summary(population, generation):
    fitness = [x.fitness for x in population]
    fidelity = [x.fidelity for x in population]

    if len(population) > 1:
        sd_fitness = statistics.stdev(fitness)
        sd_fidelity = statistics.stdev(fidelity)
    else:
        sd_fitness = sd_fidelity = "NaN"

    if len(population) > 0:
        ave_fitness = math.fsum(fitness) / len(population)
        ave_fidelity = math.fsum(fidelity) / len(population)
    else:
        ave_fitness = ave_fidelity = "NaN"

    summary = {'gen': generation+1,  # base 1
               'pop': len(population),
               'ave_fit': ave_fitness,
               'sd_fit': sd_fitness,
               'ave_fid': ave_fidelity,
               'sd_fid': sd_fidelity}

    return OrderedDict(sorted(summary.items(), key=lambda t: t[0]))


def run(factors, population, generations, population_limit, environment):

    original_population_size = len(population)
    population_limit *= original_population_size  # stop when population size reaches a multiple of original population

    # starting summary
    results = [get_results_summary(population, 0)]

    for t in range(0, generations):

        parent_population = selection(factors, population)
        offspring_population = reproduction(factors, population)
        population = parent_population + offspring_population

        if len(population) > original_population_size:  # if fixed population size
            population = random.sample(population, original_population_size)
        if len(population) < 3 or len(population) > population_limit:
            break

        # need a vertical slice through environment, [t] element of each
        current_environment = [lineage_environment[t] for lineage_environment in environment]
        population = apply_environment_change(current_environment, population)

        # Results AFTER environment change, with consistent ordering
        results.append(get_results_summary(population, t))

    lineages = [e.lineage for e in population]

    print("g={0} {1}".format(t+1, Counter(lineages)))

    return results

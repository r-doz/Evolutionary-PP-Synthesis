from algorithm.parameters import params
from fitness.base_ff_classes.base_ff import base_ff
from stats.stats import stats
import random
import time

class max_in_list(base_ff):
    """Fitness function for finding the length of the shortest path between
    two nodes in a grade compared to the known shortest path. Takes a path (
    list of node labels as strings) and returns fitness. Penalises output
    that is not the same length as the target."""

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()

    def evaluate(self, ind, **kwargs):
        p = ind.phenotype

        print("\n" + p)

        fitness = 0
        for trial in range(50):
            t0 = time.time()
            self.test_list = generate_list()
            m = max(self.test_list)

            d = {'test_list': self.test_list}

            try:

                exec(p, d)

                guess = d['max_val']
                fitness += len(p)

                if guess not in self.test_list:
                    fitness += 10000

                v = int(abs(m - guess))
                if v <= 10 ** 6:
                    fitness += v
                else:
                    fitness = self.default_fitness

            except:
                fitness = self.default_fitness

                if not hasattr(params['FITNESS_FUNCTION'], "multi_objective"):
                    stats['invalids'] += 1

            t1 = time.time()

            if t1 - t0 > 4:
                fitness = self.default_fitness
                break

        return fitness

def generate_list():
    return [random.randint(0, round(random.random() * 90 + 10)) for i in range(9)]
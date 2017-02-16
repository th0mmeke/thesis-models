import random
import runner
import itertools

MAX_SD = 0.3
with open("../results/environments.csv", "w") as f:
    for i in range(20):
        theta, sd, bias = random.uniform(-MAX_SD, MAX_SD), random.uniform(0, MAX_SD/2), random.uniform(-MAX_SD/4, MAX_SD/4)
        ts = [x for x in runner.get_ar_timeseries(theta, sd, bias, 50)]
        f.write(str(theta) + "," + str(sd) + "," + str(bias) + "," + ",".join([str(x) for x in ts]) + "\n")


with open("../results/environments-factorial.csv", "w") as f:
    for theta, sd, bias in itertools.product([-MAX_SD, 0, MAX_SD], [0, MAX_SD/2], [-MAX_SD/4, 0, MAX_SD/4]):
        ts = [x for x in runner.get_ar_timeseries(theta, sd, bias, 50)]
        f.write(str(theta) + "," + str(sd) + "," + str(bias) + "," + ",".join([str(x) for x in ts]) + "\n")




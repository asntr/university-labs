from distributions import BaseRandomValue, PoissonDistribution, NormalDistribution
from matplotlib import pyplot as plt
import matplotlib.mlab as mlab
import numpy as np


def rand_gen():
    while True:
        yield np.random.rand()


def main():
    brv_generator = BaseRandomValue(65539, 2**31, 65539)
    lambda_range = [6, 9, 12, 15, 18]
    fig, axarr = plt.subplots(len(lambda_range), figsize=(8, 7))
    plt.subplots_adjust(hspace=1)
    fig.suptitle('Poisson approximation')
    for axis, l in zip(axarr, lambda_range):
        poisson_generator = PoissonDistribution(l, brv_generator)
        poisson = np.array([next(poisson_generator) for _ in range(1100)])
        bins = np.bincount(poisson)
        normal_generator = NormalDistribution(brv_generator, sigma=l, mu=l)
        normal = np.array([next(normal_generator) for _ in range(1100)])
        axis.set_title('lambda = {}'.format(l), fontsize=8)
        axis.bar(np.arange(len(bins)), bins / bins.sum(),  color='b', alpha=0.7, width=1)
        axis.hist(normal, 21, normed=True, alpha=0.3, color='g')
        x = np.linspace(l - 3 * np.sqrt(l), l + 3 * np.sqrt(l), 100)
        axis.plot(x, mlab.normpdf(x, l, np.sqrt(l)), alpha=0.3)
        axis.legend(['true normal', 'poisson', 'normal'], prop={'size': 3})
        axis.set_ylabel('f(x)', fontsize=10)
        axis.set_xlabel('x', fontsize=10)
        print('elapse: ', np.mean(poisson), np.mean(normal), l)
        print('variance: ', np.var(poisson), np.var(normal), l)
        print(100 * '-')
    plt.show()

if __name__ == '__main__':
    main()

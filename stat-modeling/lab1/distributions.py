import numpy as np


class BaseRandomValue(object):
    def __init__(self, beta, m, alpha):
        self.__beta = beta
        self.__m = m
        self.__alpha = alpha

    def __next__(self):
        self.__alpha = (self.__alpha * self.__beta) % self.__m
        return self.__alpha / self.__m


class PoissonDistribution(object):
    def __init__(self, _lambda, brv):
        self.__brv = brv
        self.__lambda = _lambda

    def __next__(self):
        prod = next(self.__brv)
        iteration = 0
        while prod >= np.exp(-self.__lambda):
            prod *= next(self.__brv)
            iteration += 1
        return iteration


class NormalDistribution(object):
    def __init__(self, brv, sigma=1, mu=0):
        self.__sigma = sigma
        self.__mu = mu
        self.__brv = brv

    def __next__(self):
        return (np.sqrt(-2 * np.log(next(self.__brv))) * np.cos(2 * np.pi * next(self.__brv)) * np.sqrt(self.__sigma)
                + self.__mu)

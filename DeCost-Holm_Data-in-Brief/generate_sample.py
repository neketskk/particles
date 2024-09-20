#!/usr/bin/env python

import sys
import json
import click
import numpy as np
from scipy.stats import weibull_min
from datetime import datetime

def fit_weibull_dist(loc=1, shape=0.1, nsamples=1e5):
    """ fit a weibull distribution to a given lognormal distribution """
    # get samples from lognormal distribution
    loc = np.log(loc)
    samples = np.random.lognormal(mean=loc, sigma=shape, size=nsamples)
    weibull_params = weibull_min.fit(samples)
    return weibull_min(*weibull_params)

@click.command()
@click.option('-n', '--samplesize', default=10, type=int,
              help='number of particles')
@click.option('-o', '--textfile', default='particles.json', type=click.Path(),
              help='json output path')
@click.option('-d', '--distribution', default='lognormal',
              type=click.Choice(['lognormal', 'normal', 'weibull_fit']),
              help='distribution family to sample from')
@click.option('-m', '--loc', default=0.1, type=float,
              help='distribution scale parameter')
@click.option('-s', '--shape', default=0.5, type=float,
              help='distribution shape parameter')
def generate_sample(samplesize, textfile, distribution, loc, shape):
    """ sample particle sizes from a distribution and make a json file """

    # sample particle  sizes from a specified generating distribution
    if distribution == 'lognormal':
        loc = np.log(loc)
        size = np.random.lognormal(mean=loc, sigma=shape, size=samplesize)
    elif distribution == 'normal':
        size = np.random.normal(loc=loc, scale=shape, size=samplesize)
    elif distribution == 'weibull_fit':
        # fit a weibull distribution to a lognormal distribution
        nsamples = 1e5
        dist = fit_weibull_dist(loc=loc, shape=shape, nsamples=nsamples)
        size = dist.rvs(size=samplesize)
    else:
        sys.exit('error: choose between normal and lognormal distributions')

    # particle positions from uniform distribution
    xx = np.random.uniform(low=0, high=1, size=samplesize)
    yy = np.random.uniform(low=0, high=1, size=samplesize)
    zz = np.random.uniform(low=0, high=1, size=samplesize)

    # serialize everything to json for the blender script
    particles = []
    for s, x, y, z in zip(size, xx, yy, zz):
        particles.append({'size': s, 'x': x, 'y': y, 'z': z})

    data = {
        'distribution': distribution,
        'loc': loc,
        'shape': shape,
        'timestamp': datetime.utcnow().isoformat(),
        'particles': particles
    }

    with open(textfile, 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    generate_sample()

from __future__ import division
import numpy as np
na = np.newaxis
from matplotlib import pyplot as plt
plt.interactive(True)

import predictive_models as pm
import predictive_distributions as pd
import particle_filter as pf

COLORS = ['r','g','c','m','k']

##############
#  examples  #
##############

def dumb_randomwalk_fixednoise():
    noisechol = 30*np.eye(2)
    initial_particles = [
            pf.AR(
                    num_ar_lags=1,
                    previous_outputs=[np.zeros(2)],
                    baseclass=lambda: \
                        pm.RandomWalk(noiseclass=lambda: pd.FixedNoise(noisechol=noisechol))
                    ) for itr in range(10000)]

    def plotfunc(particles,weights):
        plottopk(particles,weights,5)
        plotmeanpath(particles,weights)

    return interactive(initial_particles,2500,plotfunc)

##############
#  back-end  #
##############

def interactive(initial_particles,cutoff,plotfunc):
    sigma = 10.
    def loglikelihood(_,locs,data):
        return -np.sum((locs - data)**2,axis=1)/(2*sigma**2)

    plt.clf()

    points = [np.zeros(2)]

    particlefilter = pf.ParticleFilter(2,cutoff,loglikelihood,initial_particles)

    plt.ioff()

    pts = np.array(points)
    plt.plot(pts[:,0],pts[:,1],'bo-')
    plt.xlim(-100,100)
    plt.ylim(-100,100)
    plt.draw()
    plt.ion()

    while True:
        out = plt.ginput()
        if len(out) == 0:
            break
        else:
            out = np.array(out[0])
            points.append(out)

            plt.ioff()

            plt.clf()

            particlefilter.step(out,resample_method='lowvariance')
            particlefilter.change_numparticles(5000) # TESTING

            plotfunc(particlefilter.particles,particlefilter.weights_norm)

            pts = np.array(points)
            plt.plot(pts[:,0],pts[:,1],'bo--')

            plt.xlim(-100,100)
            plt.ylim(-100,100)
            plt.draw()
            plt.ion()

    return particlefilter

###########
#  utils  #
###########

def topk(items,scores,k):
    return [items[idx] for idx in np.argsort(scores)[:-(k+1):-1]]

def plottopk(particles,weights,k):
    for p in topk(particles,weights,k):
        t = np.array(p.track)
        plt.plot(t[:,0],t[:,1],'rx-')
        print p

def plotmeanpath(particles,weights):
    track = np.array(particles[0].track)*weights[0,na]
    for p,w in zip(particles[1:],weights[1:]):
        track += np.array(p.track) * w
    plt.plot(track[:,0],track[:,1],'k^:')


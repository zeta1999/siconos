print """

FEM simulation using getfem++ and siconos.

"""

import Kernel as Kernel
import numpy as np

ndof = 24;
t0 = 0.0      # start time
T = 5.0      # end time
h = 0.005   # time step
g = 9.81    # gravity
e = 0.9     # restitution coeficient
mu=0.3 # Friction coefficient
theta = 0.5 # theta scheme
m=1

# =======================================
# Create the siconos Dynamical System
# =======================================
# Initial position and velocity
v0 = np.zeros(ndof)
q0 = np.zeros(ndof)
Mass = np.eye(ndof)
K = np.eye(ndof)
weight = np.zeros(ndof)
weight[0:ndof-1:3] = -m*g 

block = Kernel.LagrangianLinearTIDS(q0,v0,Mass)
block.setFExtPtr(weight)
block.setKPtr(K)

diminter = 4
H = np.zeros((diminter,ndof))
H[0,2] = 1.0
H[1,5] = 1.0
H[2,8] = 1.0
H[3,11] = 1.0
dist = 3.0
b = np.repeat([dist], diminter)
nslaw = Kernel.NewtonImpactNSL(e)
relation = Kernel.LagrangianLinearTIR(H,b)
inter = Kernel.Interaction(diminter, nslaw, relation)

# =======================================
# The Model
# =======================================
blockModel = Kernel.Model(t0,T)

# add the dynamical system to the non smooth dynamical system
blockModel.nonSmoothDynamicalSystem().insertDynamicalSystem(block)

# link the interaction and the dynamical system
blockModel.nonSmoothDynamicalSystem().link(inter,block);

# =======================================
# The Simulation
# =======================================

# (1) OneStepIntegrators
OSI = Kernel.Moreau(theta)
OSI.insertDynamicalSystem(block)

# (2) Time discretisation --
t = Kernel.TimeDiscretisation(t0,h)
osnspb = Kernel.LCP()

# (4) Simulation setup with (1) (2) (3)
s = Kernel.TimeStepping(t)
s.insertIntegrator(OSI)
s.insertNonSmoothProblem(osnspb)

# simulation initialization
blockModel.initialize(s)

# ok on ubuntu lucid
inter.y(0).display()

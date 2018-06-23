"""
Copyright 2018 Anqi Fu

This file is part of CVXPY.

CVXPY is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

CVXPY is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with CVXPY.  If not, see <http://www.gnu.org/licenses/>.
"""

import numpy as np
import matplotlib.pyplot as plt
from cvxpy import Variable, Parameter, Problem, Minimize
from cvxpy.atoms import *
from problems import Problems

def compare_results(probs, obj_admm, obj_comb, x_admm, x_comb):
	N = len(probs.variables())
	for i in range(N):
		print "\nADMM Solution:\n", x_admm[i]
		print "Base Solution:\n", x_comb[i]
		print "MSE: ", np.mean(np.square(x_admm[i] - x_comb[i])), "\n"
	print "ADMM Objective: %f" % obj_admm
	print "Base Objective: %f" % obj_comb
	print "Iterations: %d" % probs.solver_stats["num_iters"]
	print "Elapsed Time: %f" % probs.solver_stats["solve_time"]

def plot_residuals(primal, dual):
	resid = np.column_stack((primal, dual))
	iters = range(1, resid.shape[0] + 1)
	plt_resd = plt.plot(iters, resid, label = ["Primal", "Dual"])
	plt.legend(plt_resd, ["Primal", "Dual"])
	plt.xlabel("Iteration")
	plt.ylabel("Residual")
	plt.show()

def test_basic():
	np.random.seed(1)
	m = 100
	n = 10
	MAX_ITER = 100
	x = Variable(n)
	y = Variable(n/2)

	# Problem data.
	alpha = 0.5
	A = np.random.randn(m*n).reshape(m,n)
	xtrue = np.random.randn(n)
	b = A.dot(xtrue) + np.random.randn(m)

	# List of all the problems with objective f_i.
	p_list = [Problem(Minimize(sum_squares(A*x-b)), [norm(x,2) <= 1]),
			  Problem(Minimize((1-alpha)*sum_squares(y)/2))]
	probs = Problems(p_list)
	N = len(p_list)   # Number of problems.
	probs.pretty_vars()
	
	# Solve with consensus ADMM.
	obj_admm = probs.solve(method = "consensus", rho_init = N*[1.0], \
						   max_iter = MAX_ITER, spectral = True)
	x_admm = [x.value for x in probs.variables()]
	# plot_residuals(probs._primal_residual, probs._dual_residual)

	# Solve combined problem.
	obj_comb = probs.solve(method = "combined")
	x_comb = [x.value for x in probs.variables()]

	# Compare results.
	compare_results(probs, obj_admm, obj_comb, x_admm, x_comb)

def test_ols():
	np.random.seed(1)
	N = 2
	m = N*1000
	n = 10
	MAX_ITER = 100
	x = Variable(n)
	
	# Problem data.
	A = np.random.randn(m*n).reshape(m,n)
	xtrue = np.random.randn(n)
	b = A.dot(xtrue) + np.random.randn(m)
	A_split = np.split(A, N)
	b_split = np.split(b, N)
	
	# List of all the problems with objective f_i.
	p_list = []
	for A_sub, b_sub in zip(A_split, b_split):
		p_list += [Problem(Minimize(0.5*sum_squares(A_sub*x-b_sub) + 1.0/N*norm(x,1)))]
		
	probs = Problems(p_list)
	probs.pretty_vars()
	
	# Solve with consensus ADMM.
	obj_admm = probs.solve(method = "consensus", rho_init = N*[0.5], \
						   max_iter = MAX_ITER, spectral = True)
	x_admm = [x.value for x in probs.variables()]
	# probs.plot_residuals()
	
	# Solve combined problem.
	# obj_comb = Problem(Minimize(sum_squares(A*x-b))).solve()
	obj_comb = probs.solve(method = "combined")
	x_comb = [x.value for x in probs.variables()]
	
	# Compare results.
	compare_results(probs, obj_admm, obj_comb, x_admm, x_comb)

def test_lasso():
	np.random.seed(1)
	m = 100
	n = 10
	MAX_ITER = 100
	DENSITY = 0.75
	x = Variable(n)
	
	# Problem data.
	A = np.random.randn(m*n).reshape(m,n)
	xtrue = np.random.randn(n)
	idxs = np.random.choice(range(n), int((1-DENSITY)*n), replace = False)
	for idx in idxs:
		xtrue[idx] = 0
	b = A.dot(xtrue) + np.random.randn(m)
	
	# List of all problems with objective f_i.
	p_list = [Problem(Minimize(sum_squares(A*x-b))),
			  Problem(Minimize(norm(x,1)))]
	probs = Problems(p_list)
	N = len(p_list)
	
	# Solve with consensus ADMM.
	obj_admm = probs.solve(method = "consensus", rho_init = N*[1.0], \
						   max_iter = MAX_ITER, spectral = False)
	x_admm = [x.value for x in probs.variables()]
	# probs.plot_residuals()
	
	# Solve combined problem.
	obj_comb = probs.solve(method = "combined")
	x_comb = [x.value for x in probs.variables()]
	
	# Compare results.
	compare_results(probs, obj_admm, obj_comb, x_admm, x_comb)

def test_logistic():
	# Construct Z given X.
	def pairs(Z):
		m, n = Z.shape
		k = n*(n+1)//2
		X = np.zeros((m,k))
		count = 0
		for i in range(n):
			for j in range(i,n):
				X[:,count] = Z[:,i]*Z[:,j]
				count += 1
		return X
		
	np.random.seed(1)
	n = 10
	k = n*(n+1)//2
	m = 200
	sigma = 1.9
	DENSITY = 1.0
	theta_true = np.random.randn(n,1)
	idxs = np.random.choice(range(n), int((1-DENSITY)*n), replace = False)
	for idx in idxs:
		beta_true[idx] = 0

	Z = np.random.binomial(1, 0.5, size=(m,n))
	Y = np.sign(Z.dot(theta_true) + np.random.normal(0,sigma,size=(m,1)))
	X = pairs(Z)
	X = np.hstack([X, np.ones((m,1))])
	
	# Form model fitting problem with logistic loss and L1 regularization.
	theta = Variable(k+1)
	lambd = 1.0
	MAX_ITER = 55
	loss = 0
	for i in range(m):
		loss += log_sum_exp(vstack(0, -Y[i]*X[i,:].T*theta))
	reg = norm(theta[:k], 1)
	p_list = [Problem(Minimize(loss/m)), Problem(Minimize(lambd*reg))]
	probs = Problems(p_list)
	N = len(p_list)
	
	# Solve with consensus ADMM.
	obj_admm = probs.solve(method = "consensus", rho_init = N*[0.5], \
						   max_iter = MAX_ITER, spectral = True)
	x_admm = [x.value for x in probs.variables()]
	probs.plot_residuals()
	
	# Solve combined problem.
	obj_comb = probs.solve(method = "combined")
	x_comb = [x.value for x in probs.variables()]
	
	# Compare results.
	compare_results(probs, obj_admm, obj_comb, x_admm, x_comb)
	

# print "Basic Test"
# test_basic()

# print "OLS Test"
# test_ols()

# print "Lasso Test"
# test_lasso()

print "Logistic + L1 Regularization"
test_logistic()

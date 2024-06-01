#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Experimental code for liquid-liquid phase equilibria.

# This code is copyright (c) 2024 Patrick B Warren (STFC).
# Email: patrick.warren{at}stfc.ac.uk.

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

# Solve for liquid-liquid coexistence in a DPD binary mixture
# described by mean-field free energy f = fid + fex where
# fid = ρ1 (ln ρ1 - 1) + ρ2 (ln ρ2 - 1),
# fex = π/30 (A11 ρ1² + 2 A12 ρ1 ρ2 + A22 ρ2²).
# Some tweaking of the initial guess may be needed to encourage the
# solver to find distinct coexisting state points.

# To impose NPT we solve a quadratic equation for ρ which is
# π/30 [A11 x² + 2 A12 x(1-x) + A22 (1-x)²] ρ² + ρ - p0 = 0

import argparse
import numpy as np
from numpy import pi as π
from numpy import sqrt, exp
from numpy import log as ln
from scipy.optimize import root

def state_point(x, ρ, A11, A12, A22):
    ρ1, ρ2 = x*ρ, (1-x)*ρ
    μ1ex = π/15*(A11*ρ1 + A12*ρ2)
    μ2ex = π/15*(A12*ρ1 + A22*ρ2)
    pex = π/30*(A11*ρ1**2 + 2*A12*ρ1*ρ2 + A22*ρ2**2)
    return μ1ex, μ2ex, pex

# auxiliary x = 1/(1+exp(-y)) solves to y = ln(x/(1-x))

def fun(y, p0, A11, A12, A22):
    x = 1 / (1 + exp(-y))
    a = π/30*(A11*x**2 + 2*A12*x*(1-x) + A22*(1-x)**2)
    ρ = (sqrt(1 + 4*a*p0) - 1) / (2*a)
    ρ1, ρ2 = x*ρ, (1-x)*ρ
    μ1 = ln(ρ1) + π/15*(A11*ρ1 + A12*ρ2)
    μ2 = ln(ρ2) + π/15*(A12*ρ1 + A22*ρ2)
    return [μ1[1] - μ1[0], μ2[1] - μ2[0]]

ρ0, A11, A12, A22 = 3, 25, 30, 20 # A11 is the reference fluid here

x0 = np.array([0.01, 0.9]) # initial guess

print(f'ρ0, A11, A12, A22 = {ρ0} {A11} {A12} {A22}')

_, _, pex = state_point(1, ρ0, A11, A12, A22)
p0 = ρ0 + pex

print(f'pressure fixed at p0 = {p0}')

soln = root(fun, ln(x0 / (1-x0)), args=(p0, A11, A12, A22))

# print(soln)

xx = 1 / (1 + exp(-soln.x))

for i, x in enumerate(xx):
    a = π/30*(A11*x**2 + 2*A12*x*(1-x) + A22*(1-x)**2)
    ρ = (sqrt(1 + 4*a*p0) - 1) / (2*a)
    ρ1, ρ2 = x*ρ, (1-x)*ρ
    print(f'phase {i}:  x, ρ  = \t{x}\t{ρ}')
    print(f'phase {i}: ρ1, ρ2 = \t{ρ1}\t{ρ2}')
    μ1ex, μ2ex, pex = state_point(x, ρ, A11, A12, A22)
    print(f'phase {i}: μ1, μ2, p = \t{ln(ρ1)+μ1ex}\t{ln(ρ2)+μ2ex}\t{ρ+pex}')

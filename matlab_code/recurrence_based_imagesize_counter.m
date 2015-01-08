% Copyright (C) 2013 Caleb Levy - All Rights Reserved.
%
% The terms of use, license and copyright information for the code and ideas
% contained herein are described in the LICENSE file included with this
% project. For more information please contact me at caleb.levy@berkeley.edu.

%% Recursive Map Density
% Recursively calculate probability that the image of a random function on
% an N element set will have k elements.

% Maintenance
clear all
close all
clc

N = 8;

%% Initialization (This brings first iterate from 2^(n-1) to O(n^2), and dO(n) !)
FirstDist = zeros(N,N);
FirstDist(1,1) = 1;
F = 1;

for I = 2:N
    F_Old = F;
    F = zeros(I,1);
    F(1) = 1; FirstDist(1,I) = I;
    F(I) = 1; FirstDist(I,I) = factorial(I);
    for J = 2:I-1
        F(J) = F_Old(J-1) + J*F_Old(J);
        FirstDist(J,I) = factorial(I)/factorial(I-J)*F(J);
    end
end

MapDist = FirstDist(:,N);




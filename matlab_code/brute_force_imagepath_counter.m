% Copyright (C) 2013 Caleb Levy - All Rights Reserved.
%
% The terms of use, license and copyright information for the code and ideas
% contained herein are described in the LICENSE file included with this
% project. For more information please contact me at caleb.levy@berkeley.edu.

%% Brute Force Iteration Density
% Use brute force caculation of all iterates to find the distribution
% function of set sizes exactly to have a check to compare to

% Maintenance
clear all
close all
% clc

N = 5; % Set dimension (should be no more than ~7)

%% Calculate densities (should take ~O(N^N) operations, i.e. alot)

go = true; % Keep the loop going
V = ones(N,1);
Dist = zeros(N,N-1); % Dist(k,l) = # Number of functions whose lth iterate produces an image of size k

while go
        
    Func = V; % V is the function
    Numf = numel(unique(Func));
    Dist(Numf,1) = Dist(Numf,1) + 1;
    
    for L = 2:N-1
        Func = V(Func);
        Numf = numel(unique(Func));
        Dist(Numf,L) = Dist(Numf,L) + 1;
    end
    
    %% Counting voodoo
    V(N) = V(N) + 1;
    if V(N) > N
        V(N) = 1;
        go = false;
        for J = N-1:-1:1
            V(J) = V(J) + 1;
            if V(J) <= N
                go = true;
                break
            end
            V(J) = 1;
        end
    end
end


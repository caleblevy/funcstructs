%% Brute Force Map Density
% Brute force computation of map density between two sets A and B. Used as
% a check for the "merely" exponential version.

% Maintenance
clear all
close all
clc

N = 6;

%% Initialization
MapDist = zeros(N,1);
V = ones(N,1);
go = true;

while go
    
    DNum = numel(unique(V));
    MapDist(DNum) = MapDist(DNum) + 1;
    
    %% Counting Voodoo
    V(N) = V(N) + 1;
    if V(N) > N
        V(N) = 1;
        go = false;
        for I = N-1:-1:1
            V(I) = V(I) + 1;
            if V(I) <= N % ith counter not at limit
                go = true;
                break;
            end
            V(I) = 1;
        end
    end
end

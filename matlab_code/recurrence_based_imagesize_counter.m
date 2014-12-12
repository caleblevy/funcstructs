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




% Copyright (C) 2013 Caleb Levy - All Rights Reserved.
%
% The terms of use, license and copyright information for the code and ideas
% contained herein are described in the LICENSE file included with this
% project. For more information please contact me at caleb.levy@berkeley.edu.

%% Contraction Density
% Calculate probability distribution of functions on N space with respect
% to size of set limit

% Maintenance
clear all
close all
clc

Save = true;
Show = false;

N = 16; % Set dimension


%% Caclulate densities (should take ~O(2^n) operations)

Ln = zeros(N,1); % The distribution

FacGrid = zeros(N+1,N+1); % Save us factorial computations
for L = 1:N+1 
    for M = 1:L
        FacGrid(L,M) = factorial(L-1)/(factorial(M-1)*factorial(L-M)); 
    end
end
% (N n) = FacGrid(N+1,n+1)

ExpGrid = 1:N;
[GridX,GridY] = meshgrid(ExpGrid,ExpGrid);
ExpGrid = GridX.^GridY; 
ExpGrid = ExpGrid.'; % X^Y = ExpGrid(X,Y)

for n = N-1:-1:1
    
    Ln(n) = factorial(N)/factorial(N-n);
    
    V = zeros(N-n+1,1);
    V(1) = n;
    V(2) = N-n;
    
    tot = 0;
    go = true;
    
    while go == true;
        
        val = 1;
        
        for J = 2:N-n+1 % J=1:N-n shifted by matlab indexing
            
            if V(J) == 0
                break % Very important: keeps cost under super-exponential
            end
            % Most of the cost is actually here
            
            % val = val * V(J-1)^V(J) * factorial(sum(V(J:end)) / (factorial(V(J))*
            % factorial(sum(V(J:end)-V(J)))
            val = val*ExpGrid(V(J-1),V(J)); 
            val = val*FacGrid(sum(V(J:end))+1,V(J)+1);
            
        end
                
        tot = tot + val;
        
        if V(N-n+1) == 1
            go = false;
            break % The only way to be sure is to break out
        end
        
        %% Index shifting
        for K = J:-1:2 % J-1:-1:1 (J has plus one too, so "2" is our "1")
            % Keep descending (backwards) until hitting a "step" you can subtract from
            
            if V(K-1)-1 ~= 0
                V(K-1) = V(K-1) - 1;
                V(K) = V(K) + (J-K+1);
                
                break
            end
            % Haven't hit the target, thus one step back
            
            V(K-1) = V(K-1) - 1;
        end
        
    end
    
    Ln(n) = Ln(n)*tot;
    
end

% We made it!

Ln(N) = factorial(N); % Take care of the last one, with all those screwy indices

plot(Ln)




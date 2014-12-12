%% Map Density
% Find density of functions a set A with N elements to a set B with M
% elements.

% Maintenance
clear all
close all
clc

N = 6; % Size of S

%% Initialization

MapDist = zeros(N,1);

V = ones(N,1); % Tree depth
V(1) = 2; % Shortcircuit the 0 rep option, go top down
go = true;



while go
    val = 1;
    Rep = 0;
    
    for I = 1:N
        if V(I) == 1 % Repetition represented by 1
            val = val*Rep;
        else
            val = val*(N-Rep); % New value by 2
            Rep = Rep + 1;
        end
    end
    
    MapDist(Rep) = MapDist(Rep) + val;
    
    %% Counting Voodoo
    V(N) = V(N) + 1;
    if V(N) > 2
        V(N) = 1;
        go = false;
        for I = N-1:-1:1
            V(I) = V(I) + 1;
            if V(I) <= 2 % ith counter not at limit
                go = true;
                break;
            end
            V(I) = 1;
        end
    end
end


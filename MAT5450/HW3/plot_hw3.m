function [t, x] = plot_hw3(N0, beta, r)
% Solve population diff eqn for fisheries.
%
% Example: plot_hw3()

    tSpan = [0 50];
    
    %% dN/dt

    odeFunction = @(t, N) r*N*exp(-beta*N);
    [t, N] = ode45(odeFunction, tSpan, N0);

    x = N(:,1);
    % Plot solution
    figure;
    plot(t, N, 'LineWidth', 1.5);
    grid on;
    xlabel('t');
    ylabel('x(t)');
    title(sprintf(['Solution is using ode45; beta = %.2f, r = %.2f, N(0) = %.2f'], 
        beta, r, N0));
end

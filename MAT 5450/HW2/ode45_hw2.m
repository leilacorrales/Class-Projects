function [t, x] = ode45_hw2(X0, Xdot0, omega, delta, tRange)
% Solve a damped oscillator using ode45.
%
% Example: ode45_hw2()

    tSpan = linspace(tRange(1), tRange(2), 1000);
    
    if delta == 1
        solution = 'critically damped';
    elseif delta < 1
        solution = 'underdamped';
    else
        solution = 'overdamped';
    end 

    % y1 = x; y2 = x'
    % y1' = y2
    % y2' = -2 delta omega y2 - omega ^2 y1

    odeFunction = @(t, y) [y(2); ...
        -2*delta*omega*y(2) - omega^2*y(1)];
    [t, y] = ode45(odeFunction, tSpan, [X0; Xdot0]);

    x = y(:,1);
    % Plot solution
    figure;
    plot(t, x, 'LineWidth', 1.5);
    grid on;
    xlabel('t');
    ylabel('x(t)');
    title(sprintf(['Solution is %s using ode45; delta = %.2f, omega = %.2f, ' ...
        'X(0) = %.2f, X''(0) = %.2f'], ...
        solution, delta, omega, X0, Xdot0));
end

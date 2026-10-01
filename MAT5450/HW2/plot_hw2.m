function [t, x, solution] = plot_hw2(X_0, Xdot_0, Omega, delta, tRange)
% HW 2 Question 2: Plot the solution of a damped oscillator.
%
% delta selects 'underdamped', 'critically damped', or 'overdamped'.
%   plot_hw2(1, 0, 2, 0.5, [0 10])
%   plot_hw2(1, 0, 2, 2,   [0 10])
%   plot_hw2(1, 0, 2, 3,   [0 10])

    if nargin < 5 || isempty(tRange)
        tRange = [0 10];
    end

    t = linspace(tRange(1), tRange(2), 1000);

    if delta == 1
        solution = 'critically damped';
        x = (X_0 + Xdot_0 .* t + Omega .* t .* X_0) .* exp(-Omega .* t);
    elseif delta < 1
        solution = 'underdamped';
        omegaP = Omega.* sqrt(1-delta^2);
        B = (Xdot_0 + delta .* Omega .* X_0) ./ omegaP;
        x = exp(-delta .* t .* Omega) .* ...
            (X_0 .* cos(omegaP .* t) + B .* sin(omegaP .* t));
    else
        solution = 'overdamped';
        lambda1 = -delta .* Omega + Omega .* sqrt(delta^2 - 1);
        lambda2 = -delta .* Omega - Omega .* sqrt(delta^2 - 1);
        A2 = ((Xdot_0- lambda1 .* X_0)/(lambda2 - lambda1));
        A1 = X_0 - A2;
        x = (A1) .* exp(lambda1 .* t) + (A2) .* exp(lambda2 .* t);
    end

    figure;
    plot(t, x, 'LineWidth', 1.5);
    grid on;
    xlabel('t');
    ylabel('x(t)');
    title(sprintf(['Solution is %s; delta = %.2f, omega = %.2f, ' ...
        'X(0) = %.2f, X''(0) = %.2f'], ...
        solution, delta, Omega, X_0, Xdot_0));
end

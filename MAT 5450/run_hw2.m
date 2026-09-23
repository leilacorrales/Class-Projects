function run_hw2()
% runner for plot_hw2 and ode45_hw2 and save their figures.

    folder = fileparts(mfilename('fullpath'));
    nCases = input('How many cases to run? ');
    tRange = input('Enter the time range, [0 10]: ');

    for k = 1:nCases
        fprintf('\nCase %d\n', k);
        delta = input('delta = ');
        omega = input('omega_n = ');
        X0 = input('x(0) = ');
        Xdot0 = input('xdot(0) = ');

        plot_hw2(X0, Xdot0, omega, delta, tRange);
        figAnalytical = gcf;
        baseName = sprintf('case_%d_delta_%g_analytical', k, delta);
        print(figAnalytical, fullfile(folder, [baseName '.png']), '-dpng', '-r300');

        ode45_hw2(X0, Xdot0, omega, delta, tRange);
        figNumerical = gcf;
        baseName = sprintf('case_%d_delta_%g_ode45', k, delta);
        print(figNumerical, fullfile(folder, [baseName '.png']), '-dpng', '-r300');

        fprintf('Saved case %d plots in %s\n', k, folder);
    end
end

function [t, N] = rB_hw2(r, B, N0)
%   plot N(t) vs t using rB_hw2(r, B, N0)

    t = linspace(0, 20, 1000);
    N = (B .* N0) ./ (N0 + exp(-r .* t) .* (B - N0));

    fig = figure('visible', 'on');
    plot(t, N, 'LineWidth', 1.5);
    grid on;
    xlabel('t');
    ylabel('N(t)');
    title(sprintf('N(t): r = %.4g, B = %.4g, N_0 = %.4g', r, B, N0));

    folder = fileparts(mfilename('fullpath'));
    fileName = sprintf('plot_r_%g_B_%g.png', r, B);
    print(fig, fullfile(folder, fileName), '-dpng', '-r300');

    fprintf('r = %g, B = %g, N0 = %g\n', r, B, N0);
    fprintf('Saved plot as %s\n', fullfile(folder, fileName));
end

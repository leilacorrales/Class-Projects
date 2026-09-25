function [N, Ndot] = rB_phase(r, B)
%   plot dN/dt vs N using rB_phase(r, B)

    N = linspace(0, 2 .* B, 1000);
    Ndot = r .* N .* (1 - N ./ B);

    fig = figure('visible', 'on');
    plot(N, Ndot, 'LineWidth', 1.5);
    grid on;
    xlabel('N');
    ylabel('dN/dt');
    title(sprintf('Phase plot: r = %.4g, B = %.4g', r, B));

    folder = fileparts(mfilename('fullpath'));
    fileName = sprintf('phase_plot_r_%g_B_%g.png', r, B);
    print(fig, fullfile(folder, fileName), '-dpng', '-r300');

    fprintf('r = %g, B = %g\n', r, B);
    fprintf('Saved plot as %s\n', fullfile(folder, fileName));
end

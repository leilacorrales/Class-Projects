function HW4(r_values)
% compare different r vlues given a and b

    x = linspace(-2, 4, 500);
    figure;
    hold on;
    for i = 1:length(r_values)
        r = r_values(i);

        dxdt = r.*x + x.^3;

        plot(x, dxdt, 'LineWidth', 2, ...
             'DisplayName', ['r = ', num2str(r)]);

        if r <= 0
            star_neg = -sqrt(-r);
            star_pos = sqrt(-r);
        plot(star_neg, 0, 'ro', 'MarkerSize', 2, 'LineWidth', 2, 'HandleVisibility', 'off')
        plot(star_pos, 0, 'ro', 'MarkerSize', 2, 'LineWidth', 2, 'HandleVisibility', 'off')
        end
    end

    % Add labels and title
    xlabel('x');
    ylabel('dx/dt');
    title('dx/dt versus x for different values of r');

    % Show a legend and grid
    legend('show');
    grid on;


    r = linspace(-4, 4, 1000)
    x0 = zeros(size(r));

    r_stable= r;
    r_stable(r>=0) = NaN;

    r_unstable = r;
    r_unstable(r <= 0) = NaN;

    x_plus = NaN(size(r));
    x_minus = NaN(size(r));

    for i = 1:length(r)
        if r(i) <= 0
            x_plus(i) = sqrt(-r(i));
            x_minus(i) = -sqrt(-r(i));
        end
    end

    figure;
    hold on;
    plot(r_stable, zeros(size(r_stable)), 'b-', 'LineWidth', 2);
    plot(r_unstable, zeros(size(r_unstable)), 'r--', 'LineWidth', 2);
    plot(r, x_plus, 'r--', 'LineWidth', 2);
    plot(r, x_minus, 'r--', 'LineWidth', 2);

    xlabel('r');
    ylabel('Equilibrium value of x');
    title('Bifurcation Diagram: dx/dt = rx + x^3');
    legend('x = 0', 'x = +sqrt(-r)', 'x = -sqrt(-r)');
    grid on;

end
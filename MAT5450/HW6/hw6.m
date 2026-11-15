function hw6()
% plot phase plane

    % z = (x,y); z_dot = (x + e^{-y}, -y)

    tspan = linspace(0,3,500);

    IC = [3 3; -0.5 1; -3 -1; -3 3; -2  2; -1  3; 0  0; 1 -1; 2 -2; 3 -3];
    
    figure;
    hold on;

    % ode45 needs [t,z] = ode45(function, tvalues, IC)
    f = @(t,z) [z(1) + exp(-z(2)); -z(2)];

    for i = 1:size(IC,1)
        [t,z] = ode45(f, tspan, IC(i,:));
        plot(z(:,1), z(:,2), 'LineWidth', 1.5, 'HandleVisibility','off');

        [t,z] = ode45(f, [0 -3], IC(i,:));
        plot(z(:,1), z(:,2), 'LineWidth', 1.5, 'HandleVisibility','off');
    end

    y = linspace(-5,5,500);
    x =-exp(-y);
    plot(x,y,'k--','LineWidth',2,'DisplayName','x-nullcline');

    yline(0,'b--','LineWidth',2,'DisplayName','y-nullcline');

    % equillibrium
    plot(-1,0,'ro','MarkerFaceColor','r', ...
    'DisplayName','Equilibrium (-1,0)');

    xlabel('x');
    ylabel('y');
    title('Phase Plane and Nullclines');
    grid on;

    legend('Location','bestoutside');
    hold off;

    xlim([-5 5]);
    ylim([-5 5]);
end
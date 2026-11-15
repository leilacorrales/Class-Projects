% HW7 - Question 4

lag = 2;
history = 1;
tspan = [-2 3];

ddefun = @(t,y,Z) 3*Z(1);

% Numerical solution using dde23
sol = dde23(ddefun, lag, history, tspan);

% Evaluate numerical solution
t = linspace(0,3,300);
y_num = deval(sol,t);

% Exact solution from Question 3
y_exact = zeros(size(t));

for i = 1:length(t)
    if t(i) <= 2
        y_exact(i) = 1 + 3*t(i);
    else
        y_exact(i) = 7 + 3*(t(i)-2) ...
                       + (9/2)*(t(i)-2)^2;
    end
end

% Plot both solutions
figure;
plot(t,y_num,'b-','LineWidth',2);
hold on;
plot(t,y_exact,'r--','LineWidth',2);

xlabel('Time t');
ylabel('y(t)');
title('HW7 Q4: DDE Solution Comparison');
legend('dde23 Numerical','Exact Solution');
grid on;

% Calculate numerical error
error = abs(y_exact-y_num);
fprintf('Maximum absolute error: %.8f\n',max(error));

% Plot error
figure;
plot(t,error,'LineWidth',2);
xlabel('Time t');
ylabel('Absolute Error');
title('Numerical Error');
grid on;

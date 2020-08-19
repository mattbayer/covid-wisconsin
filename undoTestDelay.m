function true_tests = undoTestDelay(reports, alpha)
%UNTITLED2 Summary of this function goes here
%   Detailed explanation goes here
%   alpha < 1
% idea here is that each day, you can report (alpha) fraction of the true
% tests + backlog.  Anything you don't report is the backlog for the next
% day.  This simplifies to the formula below.

true_tests = zeros(size(reports));

true_tests(1) = 1/alpha * reports(1);

for kk = 2:numel(reports)
    true_tests(kk) = 1/alpha * reports(kk) - (1-alpha)/alpha * reports(kk-1);
end

end


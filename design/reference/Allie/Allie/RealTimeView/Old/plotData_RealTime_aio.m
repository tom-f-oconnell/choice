
function plotData_RealTime_aio(src,event)

persistent minx maxx; %Persistent variables- local to function, retained between function calls
global j counter V expt;

    j = j + 1; %number of function calls in time interval
    %     timemax = 120; %max time to show on graph (seconds)
    timemax = 2; %max time to show on graph (minutes)
    
    if expt==2
        plot(event.TimeStamps/60,event.Data(:,1), 'Color',[0.5 0 0.9]); hold on;
        maxevent = max(event.Data(:,1));
        V = axis; 
        %scale DAQ ouput command to height of analog input
        tmp = event.Data(:,2); tmp(tmp<0)=0;
        plot(event.TimeStamps/60,((tmp/5)*(.05*(V(4)-V(3))))+V(4)-V(4)*.1,'k-');
    
    else %plot just DAQ command
        plot(event.TimeStamps/60,event.Data(:,1), 'k-');
    end
    
    %refresh figure & axes to save memory
    if j == 1 && min(event.TimeStamps)<1
        minx = 0;
        maxx = timemax;
        hold on;
    elseif j == timemax*60*10*(counter+1)
        counter = counter + 1;
        V = axis;
        %clear axes to update time interval plotted
        cla;
        %hold off;
        
        %ensure axis scaling remains intact
        minx = timemax*counter;
        maxx = minx + timemax;
        axis([minx maxx V(3) V(4)]);
    else
        hold on;
    end
    xlabel('Time (minutes)','FontSize',14);
    if expt==2, ylabel('Amplitude','FontSize',14);
    else ylabel('Command');
    end
    
    title('Realtime Viewer','FontSize',14,'FontWeight','bold');
    %set axis default
    V = axis;
    axis([minx maxx V(3) V(4)]);


end


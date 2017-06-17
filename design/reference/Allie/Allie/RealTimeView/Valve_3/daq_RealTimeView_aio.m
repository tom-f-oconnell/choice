%%%DAQ real-time data acquisition
%%%RealTimeView does not save output
%%%Displays signal in real time
%%%addlistener calls function plotData
%Zhannetta Gugel 10-28-2015

%% reset vars
clearvars;
%% reset aquisition engines
daqreset;

%% define global vars
global j counter s stopfun expt;

%% create folder for output files
local = pwd; %get current directory
%time_now = datetime('now');
foldname = char(date);
% a = num2str(yyyymmdd(time_now));
% b = num2str(hour(time_now)); if length(b)==1, b = ['0',b]; end
% c = num2str(minute(time_now)); if length(c)==1, c = ['0',c]; end
% foldname = [a,'_',b,c]; clear b c;
mkdir(foldname);
%cd(foldname); %access folder directory to save files

stopfun = 0;
rate = 200; %Hz
%% configure data acquisition

expt = menu('Select Expt','Stim Only','Stim + Acquire');

s = daq.createSession('ni'); % create session
if expt == 2, s.addAnalogInputChannel('dev1',3,'Voltage'); 
else s.addAnalogInputChannel('dev1',3,'Voltage'); %DAQ command to AI1;
end 
s.addAnalogOutputChannel('dev1',2,'Voltage');
s.Rate = rate; %Hz

%% data collection parameters

cd('stimuli');%stimname = '3x1sec_iti5sec.mat';
stimname = '5secON_5secOFF_2minDUR.mat';
%stimname = '2secON_4secOFF_20minDUR.mat';
%stimname = '1secON_20secOFF_60.2minDUR.mat';
%stimname = '1secON_20secOFF_480.2minDUR.mat';
%stimname = '1secON_20secOFF_600.25minDUR.mat';
%stimname = '1secON_4secOFF_5minDUR.mat';
load(stimname);

%user params
odor = input('Odor: ','s');
concentration = input('Concentration: ','s');
fly = input('Fly info (geno/gender/age): ','s');
notes = input('Experimental notes: ','s');
params = struct('odor',odor,'concentration',concentration,...
    'fly',fly,'notes',notes,'rate_Hz',rate,'stimname',stimname);

if max(stim)==1
    stim = stim*5;
end
cd(local);%cd(foldname);

%create GUI figure
%figure_setup;

trials = 2;
for acquire_loop = 1:trials
    clear data;
    
    j = 0; %reset number of j function calls
    counter = 0; %reset counter for axes update
    
    %current date-time filename
    time_now = datetime('now');
    a = num2str(yyyymmdd(time_now));
    b = num2str(hour(time_now)); if length(b)==1, b = ['0',b]; end
    c = num2str(minute(time_now)); if length(c)==1, c = ['0',c]; end
    d = num2str(round(second(time_now))); if length(d)==1, d = ['0',d]; end
    filename = [a,'_',b,c,d];
    clear a b c d;
    
    if expt==2
        disp(['Logging session ',num2str(acquire_loop),'...']);
    else
        disp('Running odor stim expt');
    end
    
    %% choose output stimulus
    s.queueOutputData(stim);
    disp(['Expt started ',char(datetime)]);
    disp(['Will run for ',num2str(length(stim)/rate/3600*trials),' hours']);
    
    
    lh = addlistener(s,'DataAvailable',@plotData_RealTime_aio); %,'DataRequired',@queueMoreData);
    
    data = startForeground(s);
    
    if stopfun == 1
        session(acquire_loop).SessionAbort = datetime('now');
        cd(foldname);
        save(filename,'data','params','acquire_loop','stim');
        cd(local);
        break;
    end
    
    %% Executes upon completion
    %hgsave(fig1,filename);
    %close all;
    t = linspace(1,length(stim)/samprate,length(stim))-1;
    cd(foldname);
    save(filename,'data','t','params','acquire_loop','stim');
    cd(local);
    
    cla;
    delete(lh);
    
    
end
%save results from stopped trials
%save results from last recording
%check if last filename was saved
%save session parameters
cd(foldname);
save('session');
cd(local);
%save(filename,'data')

disp('Done');
disp(datetime('now'));
close all;



%Serial communication with alicat MFC
%Set COM- check port under control panel
delete(instrfindall);

%%%textfile save output IN PROGRESS%%%
timenow = datetime('now');
myfile = fopen(['myfile','.txt'],'w');
%%%
%%Main
%delete(instrfindall); %uncomment?
 
%% HFC1

COM1 = 'COM7';
ID = 'A';

aliComm = serial(COM1, 'TimeOut',2,'BaudRate',19200,'Terminator','CR');
fopen(aliComm); 

%set flow 
flow1 = input('Desired flow for HFC1 (mL/min): ');
%convert flow
flow1 = flow1 * 25.5;
%Send desired flow rate to Alicat
fprintf(aliComm,sprintf('%s%d','A',flow1))

pause(10); 
%disp Alicat parameters
IN = fscanf(aliComm); 
disp(IN)

%read flowmeter output
[...
    OUT.ID, ...
    OUT.pressure,...
    OUT.temp,...
    OUT.volumetricFlow,...
    OUT.massFlow,...
    OUT.setPoint,...
    OUT.gas...
    ]=...
    strread(IN,'%s%f%f%f%f%f%s', 'delimiter', ' ');

OUT.ID  = cell2mat(OUT.ID) ;
OUT.gas = cell2mat(OUT.gas);
OUT.time = now;

fprintf('Output Flow of HFC1 (mL/min):')
disp(OUT.setPoint);

%%Close port and delete when finished
% % fclose(aliComm);
% % delete(aliComm);

%% HFC2

COM2 = 'COM10';
ID = 'A';

aliComm = serial(COM2, 'TimeOut',2,'BaudRate',19200,'Terminator','CR');
fopen(aliComm); 

%set flow 
flow2 = input('Desired flow for HFC2 (mL/min): ');
%convert flow
flow2 = flow2 * 25.5;
%Send desired flow rate to Alicat
fprintf(aliComm,sprintf('%s%d','A',flow2))

pause(10); 
%disp Alicat parameters
IN = fscanf(aliComm); 
disp(IN)

%read flowmeter output
[...
    OUT.ID, ...
    OUT.pressure,...
    OUT.temp,...
    OUT.volumetricFlow,...
    OUT.massFlow,...
    OUT.setPoint,...
    OUT.gas...
    ]=...
    strread(IN,'%s%f%f%f%f%f%s', 'delimiter', ' ');

OUT.ID  = cell2mat(OUT.ID) ;
OUT.gas = cell2mat(OUT.gas);
OUT.time = now;

fprintf('Output Flow for HFC2 (mL/min):')
disp(OUT.setPoint);

%% Odor A

COMA = 'COM9';
ID = 'A';

aliComm = serial(COMA, 'TimeOut',2,'BaudRate',19200,'Terminator','CR');
fopen(aliComm); 

%set flow 
flowA = input('Desired flow for odor A (mL/min): ');
%convert flow
flowA = flowA * 64000/500;
%Send desired flow rate to Alicat
fprintf(aliComm,sprintf('%s%d','A',flowA))

pause(10); 
%disp Alicat parameters
IN = fscanf(aliComm); 
disp(IN)

%read flowmeter output
[...
    OUT.ID, ...
    OUT.pressure,...
    OUT.temp,...
    OUT.volumetricFlow,...
    OUT.massFlow,...
    OUT.setPoint,...
    OUT.gas...
    ]=...
    strread(IN,'%s%f%f%f%f%f%s', 'delimiter', ' ');

OUT.ID  = cell2mat(OUT.ID) ;
OUT.gas = cell2mat(OUT.gas);
OUT.time = now;

fprintf('Output Flow for odor A (mL/min):')
disp(OUT.setPoint);

%% Odor B

COMB = 'COM8';
ID = 'B';

aliComm = serial(COMB, 'TimeOut',2,'BaudRate',19200,'Terminator','CR');
fopen(aliComm); 

%set flow 
flowB = input('Desired flow for odor B (mL/min): ');
%convert flow
flowB = flowB * 64000/500; 
%Send desired flow rate to Alicat
fprintf(aliComm,sprintf('%s%d','A',flowB))

pause(10); 
%disp Alicat parameters
IN = fscanf(aliComm); 
disp(IN)

%read flowmeter output
[...
    OUT.ID, ...
    OUT.pressure,...
    OUT.temp,...
    OUT.volumetricFlow,...
    OUT.massFlow,...
    OUT.setPoint,...
    OUT.gas...
    ]=...
    strread(IN,'%s%f%f%f%f%f%s', 'delimiter', ' ');

OUT.ID  = cell2mat(OUT.ID) ;
OUT.gas = cell2mat(OUT.gas);
OUT.time = now;

fprintf('Output Flow for odor B (mL/min):')
disp(OUT.setPoint);
%%

%%%%IN PROGRESS: loop and save parameters to file
%total expt duration
% dur = 5; %seconds
% t = 0;
% while t<=dur
%    
%     IN = fscanf(aliComm); 
%     disp(IN);
%     
%     fwrite(myfile,IN);
%     
%     
%     pause(1);
%     t = t+1;
%     
% end


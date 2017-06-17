%stim generator
%Valve 1
cd('stimuli');

fprintf('Valve 1:');
ON1 = input('ON in seconds: ');
OFF1 = input('OFF in seconds: ');
dur1 = input('Recording duration in min: ');
samprate = 200; %Hz
stim1 = ([ones(1,ON1*samprate),zeros(1,OFF1*samprate)])';

n1 = ceil(dur1*60/(ON1+OFF1));
stim1 = repmat(stim1,n1,1);
stim1 = uint8(stim1); %decrease memory storage

truedur1 = length(stim1)/samprate/60; %time in min
save([num2str(ON1),'secON_',num2str(OFF1),'secOFF_',num2str(truedur1),'minDUR.mat'],...
    'stim1','samprate');

%Valve 2

fprintf('Valve 2:');
ON2 = input('ON in seconds: ');
OFF2 = input('OFF in seconds: ');
dur2 = input('Recording duration in min: ');
samprate = 200; %Hz
stim2 = ([ones(1,ON2*samprate),zeros(1,OFF2*samprate)])';

n2 = ceil(dur2*60/(ON2+OFF2));
stim2 = repmat(stim2,n2,1);
stim2 = uint8(stim2); %decrease memory storage

truedur2 = length(stim2)/samprate/60; %time in min
save([num2str(ON2),'secON_',num2str(OFF2),'secOFF_',num2str(truedur2),'minDUR.mat'],...
    'stim2','samprate');

%Valve 3

fprintf('Valve 3:');
ON3 = input('ON in seconds: ');
OFF3 = input('OFF in seconds: ');
dur3 = input('Recording duration in min: ');
samprate = 200; %Hz
stim3 = ([ones(1,ON3*samprate),zeros(1,OFF3*samprate)])';

n3 = ceil(dur3*60/(ON3+OFF3));
stim3 = repmat(stim3,n3,1);
stim3 = uint8(stim3); %decrease memory storage

truedur3 = length(stim3)/samprate/60; %time in min
save([num2str(ON3),'secON_',num2str(OFF3),'secOFF_',num2str(truedur3),'minDUR.mat'],...
    'stim3','samprate');

%Valve 4

fprintf('Valve 4:');
ON4 = input('ON in seconds: ');
OFF4 = input('OFF in seconds: ');
dur4 = input('Recording duration in min: ');
samprate = 200; %Hz
stim4 = ([ones(1,ON4*samprate),zeros(1,OFF4*samprate)])';

n4 = ceil(dur4*60/(ON4+OFF4));
stim4 = repmat(stim4,n4,1);
stim4 = uint8(stim4); %decrease memory storage

truedur4 = length(stim4)/samprate/60; %time in min
save([num2str(ON4),'secON_',num2str(OFF4),'secOFF_',num2str(truedur4),'minDUR.mat'],...
    'stim4','samprate');
%stim generator

ON = input('ON in seconds: ');
OFF = input('OFF in seconds: ');
dur = input('Recording duration in min: ');
samprate = 200; %Hz
stim = ([ones(1,ON*samprate),zeros(1,OFF*samprate)])';

n = ceil(dur*60/(ON+OFF));
stim = repmat(stim,n,1);
stim = uint8(stim); %decrease memory storage

truedur = length(stim)/samprate/60; %time in min
cd('stimuli');
save([num2str(ON),'secON_',num2str(OFF),'secOFF_',num2str(truedur),'minDUR.mat'],...
    'stim','samprate');
%stim generator

cd('stimuli');

dur = input('Recording duration in min: ');
ON = 0;
OFF = dur;
samprate = 200; %Hz
blank = ([ones(1,ON*samprate),zeros(1,OFF*samprate)])';

n = ceil(dur*60/(ON+OFF));
blank = repmat(blank,n,1);
blank = uint8(blank); %decrease memory storage

truedur = length(blank)/samprate/60; %time in min
save([num2str(ON),'secON_',num2str(OFF),'secOFF_',num2str(truedur),'minDUR.mat'],...
    'blank','samprate');
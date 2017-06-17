%Figure GUI setup
function figure_setup

fig1 = figure('Visible','off','Position',[100,500,100,285]);
ha = axes('Units','Pixels','Position',[100,100,700,400]);

%Control YAxis Scaling
%ymin
htext1 = uicontrol('Style','text','String','Ymin',...
    'Position',[870,300,80,30],'FontWeight','bold','FontSize',14);

hedittext1 = uicontrol('Style','edit',...
    'Position',[895 280 30 30],...
    'Callback',{@edittext1_Callback});

%ymax
htext2 = uicontrol('Style','text','String','Ymax',...
    'Position',[940,300,80,30],'FontWeight','bold','FontSize',14);

hedittext2 = uicontrol('Style','edit',...
    'Position',[955 280 30 30],...
    'Callback',{@edittext2_Callback});

%Stop pushbutton
hstop = uicontrol('Style','pushbutton','String','Stop',...
    'Position',[900,400,90,40],'FontWeight','bold','FontSize',14,...
    'Callback',{@stopbutton_Callback});

fig1.Visible = 'on';

end

function edittext1_Callback(hObject, eventdata, handles)
%control yaxis min
global V;

input = str2double(get(hObject,'string'));
V = axis;
if input<V(4)
    axis([V(1) V(2) input V(4)]);
end
end

function edittext2_Callback(hObject, eventdata, handles)
%control yaxis max
global V;

input = str2double(get(hObject,'string'));
V = axis;
if input>V(3)
    axis([V(1) V(2) V(3) input]);
end
end

function stopbutton_Callback(source,eventdata)
global s stopfun pause_var t;

%session interupted
stop(s);
stopfun = 1;
pause_var = 'off';
if isempty(t)~=1
    stop(t);
end

end
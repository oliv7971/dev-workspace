function []=viS_getpoly()
%----------------------------------------------------------------------------
%   viStaMPS v1.1.1 | August 2013
%   VIsual Stanford Method for Persistent Scatterers
%   Authors:
%   jjsousa(at)utad.pt
%   amrs(at)utad.pt
%   lmagalha(at)utad.pt
%   amruiz(at)ujaen.es
%   v1.0 June 2012
%   v1.1 July 2013
%------------------------------------------------------------------------------
if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

ps_final    = vistamps.DataDisplay.Data;

load psver;                  
psname=['ps',num2str(psver)]; 
ps=load(psname);
%temporal baseline

orbit       = vistamps.Setup.OrbitType;

Nlines      = vistamps.DataDisplay.Rows;
Npixels     = vistamps.DataDisplay.Columns;


delta_r     = vistamps.DataDisplay.AspectRatioColumns;
delta_az    = vistamps.DataDisplay.AspectRatioRows;


figure(vistamps.DataDisplay.Figure);
defaultRenderer = get(gcf, 'Renderer');
set(gcf, 'Renderer', 'opengl');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ps_results=ps_final;

switch orbit
    case 'Descending'
        ps_results(:,1)=Nlines-ps_results(:,1)+1;
        ps_results(:,2)=Npixels-ps_results(:,2)+1;
end


y_radar=ps_results(:,1);
x_radar=ps_results(:,2);
coher=ps_results(:,4);
defo=ps_results(:,3);
phi=ps_results(:,5);
lambda=ps_results(:,6);

ps=[x_radar*delta_r y_radar*delta_az coher defo phi lambda];

hold on;


%-------------------------------------
% Polygon definition
%--------------------------------------
[area.x area.y]=getline(gcf,'closed');  % create polygon for inpolygon
plot(area.x,area.y,'LineWidth',2.5)   ; % verify shape

size(area.x);
size(area.y);


%--------------------------------------
% get all PS inside the polygon
%---------------------------------------
in_idx = inpolygon(ps(:,1),ps(:,2),area.x,area.y);
idd=find(in_idx==1); % Polygon inside the Polygon
ps_polygon=ps(idd,:);

size(ps_polygon);

plot(ps_polygon(:,1),ps_polygon(:,2),'.r');

hold off;

set(gcf, 'Renderer', defaultRenderer);

%return to original coordinates
ps_polygon(:,1)=ps_polygon(:,1)/delta_r;
ps_polygon(:,2)=ps_polygon(:,2)/delta_az;

[file, path] = uiputfile('*.txt','Save polygon area as');
path = fullfile(path, file);

%Send message to viStaMPS output window
viS_message('--------------------------------------------------');
viS_message('PROGRESS: Creating result file: PS INSIDE POLYGON');

fid = fopen(path, 'w');
fprintf(fid,'%3.8f %3.8f %3.8f %3.8f %3.8f %3.8f\n',ps_polygon');

%Add Max and Min Defo values to match colorbar range
indexMinDef = find(vistamps.DataDisplay.Data(:,3) == min(vistamps.DataDisplay.Data(:,3)));
dataMinDef = vistamps.DataDisplay.Data(indexMinDef(1),:);
indexMaxDef = find(vistamps.DataDisplay.Data(:,3) == max(vistamps.DataDisplay.Data(:,3)));
dataMaxDef = vistamps.DataDisplay.Data(indexMaxDef(1),:);
fprintf(fid,'%3.8f %3.8f %3.8f %3.8f %3.8f %3.8f\n',dataMinDef');
fprintf(fid,'%3.8f %3.8f %3.8f %3.8f %3.8f %3.8f\n',dataMaxDef');

fclose(fid);

%Send message to viStaMPS output window 
viS_message(['INFO    : Multilook coordinates are in the file ' file ]);
viS_message('INFO    : DONE SUCCESSFULLY');

%**************************************************************************
%Create colorbar image
[file, path] = uiputfile('*.png','Save colorbar image as');
path = fullfile(path, file);

if isequal(file, 0)
    return;
end;

h=figure(vistamps.DataDisplay.Figure);

hFig=figure;

hBar=copyobj(findobj(get(h,'Children'),'Tag','Colorbar'), gcf);
colormap(colormap(h));

left=1; bottom=100 ; width=100 ; height=500;
pos=[left bottom width height];

set(hFig,'OuterPosition',pos);

set(hBar, 'Position', [0.1 0.1 0.7 0.8]);
set(hFig,'PaperPositionMode','auto');

imwrite(frame2im(getframe(hFig)), path, 'png');
close(hFig);

%Send message to viStaMPS output window 
viS_message(['INFO    : Colorbar image for GE is in the file ' file ]);
viS_message('INFO    : DONE SUCCESSFULLY');



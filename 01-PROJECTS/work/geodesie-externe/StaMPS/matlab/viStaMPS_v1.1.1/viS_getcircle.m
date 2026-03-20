function []=viS_getcircle()
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

%-------------------------------------
% circle definition
%--------------------------------------
%[x,y]=ginput(2);
%plot(x,y, 'LineWidth',2.5); 
hEllipse = imellipse(gca, [round(max(get(gca,'XLim'))/2) round(max(get(gca,'YLim'))/2) 100 100]);
setFixedAspectRatioMode(hEllipse,true);
wait(hEllipse);
%[xmin ymin width height]
rect=getPosition(hEllipse);
delete(hEllipse);

x(1)=rect(1) + rect(3)/2;
y(1)=rect(2) + rect(4)/2;
x(2)=rect(1) + rect(3);
y(2)=rect(2) + rect(4)/2;


radius=sqrt((x(1)-x(2))^2+(y(1)-y(2))^2);

%0.01 is the angle step, bigger values will draw the circle faster but
%you might notice imperfections (not very smooth)
ang=0:0.01:2*pi; 
xp=radius*cos(ang);
yp=radius*sin(ang);
hold on;

plot(x(1)+xp,y(1)+yp,'LineWidth',2.5);  % creates a circle for inpolygon

%--------------------------------------
% get all PS inside the circle
%---------------------------------------
in_idx = inpolygon(ps(:,1),ps(:,2),xp'+x(1),yp'+y(1));
idd=find(in_idx==1); % Polygon inside the Polygon
ps_polygon=ps(idd,:);
size(ps_polygon);

plot(ps_polygon(:,1),ps_polygon(:,2),'.r');

hold off;

set(gcf, 'Renderer', defaultRenderer);


%return to original coordinates
ps_polygon(:,1)=ps_polygon(:,1)/delta_r;
ps_polygon(:,2)=ps_polygon(:,2)/delta_az;


[file, path] = uiputfile('*.txt','Save circular area as');
path = fullfile(path, file);

%Send message to viStaMPS output window 
viS_message('--------------------------------------------------');
viS_message('PROGRESS: Creating result file: PS INSIDE CIRCLE');

ps_circle=ps_polygon;

fid = fopen(path, 'w');
fprintf(fid,'%3.8f %3.8f %3.8f %3.8f %3.8f %3.8f\n',ps_circle');

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



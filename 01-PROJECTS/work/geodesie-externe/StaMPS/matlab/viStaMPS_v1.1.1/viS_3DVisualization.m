function viS_3DVisualization(dist)
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
if ~exist('viS_map.jpg', 'file')
    %Send message to viStaMPS output window 
    viS_message('ERROR: viS_map.jpg not found...');
    return;
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

[FileName, PathName] = uigetfile('*.txt','Select source file');
filename = fullfile(PathName, FileName);

if ~exist(filename, 'file')
    %Send message to viStaMPS output window 
    viS_message('ERROR: File not found...');
    return;
end

h = waitbar(0,'Processing! Please wait...','Interruptible','on');

ps_polygon=load(filename);

waitbar(50/100);

load viS_cmap_defo
cmap = viS_cmap_defo;

Img = double(imread('viS_map.jpg'));

x=(ps_polygon(:,1)*vistamps.DataDisplay.AspectRatioColumns);
y=(ps_polygon(:,2)*vistamps.DataDisplay.AspectRatioRows);
defo=ps_polygon(:,4);
%----------------------
tx=round(min(x)):1:round(max(x));
ty=round(min(y)):1:round(max(y));

%----------------------
[xq,yq] = meshgrid(tx,ty);

%interpolate node values
zq = griddata(x,y,defo,xq,yq);

choice = questdlg('Show 3D surface as:', '3D Visualization', 'Smoothed', 'Original', 'Cancel', 'Smoothed');
switch choice
    case 'Smoothed'
        zq=viS_smoothn(zq, 50);%smoothing deformation using S factor
    case 'Original'
end

if ~strcmp(choice, 'Cancel')
    zq = double(zq);
    viS_mesh(Img, zq, xq, yq, cmap, dist);
    
    axis xy
    axis off;
end

waitbar(100/100);
close(h);



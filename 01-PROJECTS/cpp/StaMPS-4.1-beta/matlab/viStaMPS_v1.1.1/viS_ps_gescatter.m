function viS_ps_gescatter(filename,filecolorbar, data,step,opacity)
% Generate kml from PS results
%
% Andy Hooper, June 2010
%
% ======================================================================
%   10/2010 MA: Initial version
%   06/2011 jjSousa: update to export data inside a polygon extracted by
%   viStaMPS
% ======================================================================

data=load(data);

if nargin < 4
  opacity=0.4;
end

step   % disseminate data
if nargin < 3
  step=1;
end
step   % disseminate data

step=1:step:size(data,1);

%========================================================
%jjSousa
% change colormap
% subsidence (red); uplift (blue)
%=========================================================
if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

clim=[vistamps.DataDisplay.DeformationMin vistamps.DataDisplay.DeformationMax];
cmap=load('viS_cmap_defo');
caxis(clim);

defo=data(:,4);

viS_gescatter(filename,filecolorbar, data(step,6),data(step,5),defo(step,:),'size',1,'colormap',cmap,'opacity',opacity) 


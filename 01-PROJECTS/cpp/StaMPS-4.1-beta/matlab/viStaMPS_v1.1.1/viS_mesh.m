function viS_mesh(Img,zq,xq,yq,cmap,dist)
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
Cmap = [gray(256); cmap];
   
%Making required pieces
Img = double(Img); %Needs to be double for slice() and all other calculations
zq = double(zq);

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end
zq = (zq - vistamps.DataDisplay.DeformationMin)+dist; %Scale so minimum is dist (so it doesn't conflict with image)        

Midx = ceil(min((length(Cmap)-256),round((length(Cmap)-255)*(zq-min(zq(:)))/(max(zq(:))-min(zq(:))))+1))+256;

if any(Img(:)<0)||any(Img(:)>255)
    %Scale whole image to 1:256 for the map (only if it was out of bounds before!
    Img = ceil(min(256,round((255)*(Img-min(Img(:)))/(max(Img(:))-min(Img(:))))+1));
else
    %Else adjust to 1:256 integer increment
    Img = ceil(Img+1);
end

%Plotting
figure;
H(1) = slice(repmat(Img,[1 1 2]),[],[],0); %slice() requires at least 2x2x2
set(H(1),'EdgeColor','none') %required so image isn't just an edge
hold on
contour(xq,yq,zq,'Linewidth',1)

H(2) = mesh(xq,yq,double(zq));

hold off

%Plot Properties
axis vis3d
axis ij
axis tight
colormap(Cmap)
set(H(1),'CData',Img);
set(H(2),'CData',Midx);
caxis([1 length(Cmap)])

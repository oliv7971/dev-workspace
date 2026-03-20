function []=viS_getps_ts()
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
%   2013.10.07 - reject ifgs in the parm: drop_ifgs_index
%------------------------------------------------------------------------------
if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

ps_final    = vistamps.DataDisplay.Data;
ps_ts_final = vistamps.DataDisplay.Data_;

load psver;                  
psname=['ps',num2str(psver)]; 
ps=load(psname);

%temporal baseline
tbl         = ps.day-ps.master_day;
tbl_m       = ps.day;

orbit       = vistamps.Setup.OrbitType;

Nlines      = vistamps.DataDisplay.Rows;
Npixels     = vistamps.DataDisplay.Columns;

lambda=getparm('lambda');

delta_r     = vistamps.DataDisplay.AspectRatioColumns;
delta_az    = vistamps.DataDisplay.AspectRatioRows;

Day         = ps.day;
master_day  = ps.master_day;  

figure(vistamps.DataDisplay.Figure);
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

ps_results=ps_final;

tbl_num=tbl_m;

switch orbit
    case 'Descending'
        ps_results(:,1)=Nlines-ps_results(:,1)+1;
        ps_results(:,2)=Npixels-ps_results(:,2)+1;
end

ps_results(:,2)=ps_results(:,2)*delta_r;
ps_results(:,1)=ps_results(:,1)*delta_az;

% time series before convert ph2dist
ph_uw=ps_ts_final;
%-------------------------

y_radar=ps_results(:,1);
x_radar=ps_results(:,2);
coher=ps_results(:,4);
defo=ps_results(:,3);
phi=ps_results(:,5);
lon=ps_results(:,6);

[x,y]=getpts; % pick a PS coord. from the image

[area.x]=[x-20 x+20 x+20 x-20];
[area.y]=[y-20 y-20 y+20 y+20];

hold on
%plot(area.x,area.y,'LineWidth',2.5)

in_idx = inpolygon(x_radar,y_radar,area.x,area.y);

% find the nearest PS to the picked point
idd=find(in_idx==1);

dist=zeros(length(idd),1);

for kk=1:length(idd)
    dist_x=(x-x_radar(idd(kk)));
    dist_y=(y-y_radar(idd(kk)));

    dist(kk)=sqrt((dist_x*dist_x)+(dist_y*dist_y));
end

[d_min,ix_min]=min(dist);

i=idd(ix_min);   % selected PS no.

%Send message to viStaMPS output window 
viS_message('--------------------------------------------------');
viS_message(sprintf('INFO      : Creating TS plot for PS no. %6.0f', i));


plot(x_radar(i),y_radar(i),'.k','MarkerSize',12)

in=i;

%========================================================
% PLOT TS for given point(s)
ts=-ph_uw(in,:)*lambda*1000/(4*pi);  % Convert ph2dist
G=[ones(size(Day)),Day-master_day] ; % [ 1  a ] --> b + ax

%========================================================
%Rejecting dropped ifgs (parm: drop_ifg_index)
bb=getparm('drop_ifg_index');
[aa,s_drop_ifgs]=size(bb);
if s_drop_ifgs > 0
    G=G';
    
    G(:,bb)=[];
    G=G';
    Day(bb)=[];
end
%==========================================================
x_hat=G\double(ts');

offset=pi*1000*lambda/(4*pi);

ts_hat=G*x_hat;
tsup_hat=ts_hat+offset;
tslo_hat=ts_hat-offset;
%=========================================================

figure
set(axes,'position',[0.13 0.11 0.775 0.7],'LineWidth',3,'FontSize',8)

plot(Day',ts,'o');
hold on
plot(Day,ts_hat,'-*r');
plot(Day,tsup_hat,'-.g');
plot(Day,tslo_hat,'-.g');
hold off

datetick('x','yyyy')
xlim([min(tbl_num)-365 max(tbl_num)+365]);
grid on
set(legend,'FontSize',8,'EdgeColor',[0 0 0])
strlg=['Est. Linear Velocity ' num2str(ps_results(i,3)) ' mm/yr'];
legend('PS point',strlg)

str1=['Deformation time-serie of PS no. ' num2str(i)];
str2=['Range: ' num2str(ps_results(i,1)) '  Azimuth: ' num2str(ps_results(i,2))];
str3=['Latitude: ' num2str(ps_results(i,5)) ' longitude: ' num2str(ps_results(i,6))];
str4=['Coherence: ' num2str(ps_results(i,4))];

set(gca,'LineWidth',1.5)
title({str1 str2 str3 str4},'FontSize',20,'FontName','Arial')
xlabel('Temporal baseline [year]','FontSize',18)
ylabel('Displacement [mm]','FontSize',18)



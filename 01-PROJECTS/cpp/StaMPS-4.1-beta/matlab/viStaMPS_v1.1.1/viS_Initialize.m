function viS_Initialize(isNewProject, scaleFactor)
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

h = waitbar(0,'Processing! Please wait...','Interruptible','on');

format short e

% Reading colormap
load viS_cmap_defo
cmap = viS_cmap_defo;

% Check if mean_amp was already created
amp=exist('amp_mean.mat');
if amp ~= 2
    ps_load_mean_amp
end

% Create mrm image to display
load('amp_mean.mat');
imwrite(amp_mean,'viS_mrm.jpg');

waitbar(50/100);

[vistamps.DataDisplay.Rows, vistamps.DataDisplay.Columns]=size(amp_mean); % Important to visualize and invert (desc case) the image


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
vistamps.DataDisplay.AspectRatioRows = 1*scaleFactor;   
vistamps.DataDisplay.AspectRatioColumns = 5*scaleFactor;
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);

%Send message to viStaMPS output window
viS_message('--------------------------------------------------');

CheckSetupImages(isNewProject);

Initialize(isNewProject);

waitbar(100/100);

close(h);
        
    
%Check background images %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function CheckSetupImages(isNewProject) 

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

hDisplay = vistamps.DataDisplay;

if ~exist([pwd filesep 'viS_black.jpg'], 'file') || isNewProject == 1
    black = zeros([hDisplay.Rows*hDisplay.AspectRatioRows hDisplay.Columns*hDisplay.AspectRatioColumns]);
    imwrite(black,'viS_black.jpg');
    viS_message('INFO      : Image viS_black.jpg created.');
end

if ~exist([pwd filesep 'viS_white.jpg'], 'file') || isNewProject == 1
    white = ones([hDisplay.Rows*hDisplay.AspectRatioRows hDisplay.Columns*hDisplay.AspectRatioColumns]);
    imwrite(white,'viS_white.jpg');
    viS_message('INFO      : Image viS_white.jpg created.');
end

if ~exist([pwd filesep 'viS_map.jpg'], 'file') || isNewProject == 1
    load 'amp_mean.mat'
    im1=imadjust(amp_mean);
    im2=imresize(im1, [hDisplay.Rows*hDisplay.AspectRatioRows hDisplay.Columns*hDisplay.AspectRatioColumns]);
    switch vistamps.Setup.OrbitType
        case 'Descending'
            im2=rot90(im2,2);
    end
    imwrite(im2,'viS_map.jpg');
    viS_message('INFO      : Image viS_map.jpg created.');
end

if ~exist([pwd filesep 'ps_ij.txt'], 'file') || ~exist([pwd filesep 'ps_ll.txt'], 'file') || isNewProject == 1
    ps_output;
end

    
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function Initialize(isNewProject)  
% ----------------------------------------------------------------------
% Initialize
% ----------------------------------------------------------------------

%Send message to viStaMPS output window 
viS_message('INFO      : Computing PS outputs');
viS_message('INFO      : Reading PS results');

load psver
%=========================================
psname=['ps',num2str(psver)];
pmname=['pm',num2str(psver)];
rcname=['rc',num2str(psver)];
rcuwname=['rcuw',num2str(psver)];
phuwname=['phuw',num2str(psver)];
phuwsbname=['phuw_sb',num2str(psver)];
phuwsbresname=['phuw_sb_res',num2str(psver)];
scnname=['scn',num2str(psver)];
apsname=['aps',num2str(psver)];
apssbname=['aps_sb',num2str(psver)];
sclaname=['scla',num2str(psver)];
sclasbname=['scla_sb',num2str(psver)];
sclasmoothname=['scla_smooth',num2str(psver)];
sclasbsmoothname=['scla_smooth_sb',num2str(psver)];
meanvname=['mv',num2str(psver)];
ifgstdname=['./ifgstd',num2str(psver)];
%===========================================
ps=load(psname);
day=ps.day;
master_day=ps.master_day;
xy=ps.xy;
lonlat=ps.lonlat;
n_ps=ps.n_ps;
n_ifg=ps.n_ifg;

master_ix=sum(day<master_day)+1;
ref_ps=0;    
%================================================

value_type(1) = 'v';% VALUE_TYPE %
ifg_list=[];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%        
if strcmp(value_type,'erro')
    close(h)
    return
end

%================================================
drop_ifg_index=getparm('drop_ifg_index');
small_baseline_flag=getparm('small_baseline_flag');
%=================================================
unwrap_ifg_index=getparm('unwrap_ifg_index');

if strcmpi(small_baseline_flag,'y')
    unwrap_ifg_index_sb=setdiff([1:ps.n_ifg],drop_ifg_index);
    if value_type(1)~='w' & value_type(1)~='p'
      warning('off','MATLAB:load:variableNotFound');
      phuw=load(phuwname,'unwrap_ifg_index_sm');
      warning('on','MATLAB:load:variableNotFound');
      if isfield(phuw,'unwrap_ifg_index_sm');
        unwrap_ifg_index=phuw.unwrap_ifg_index_sm;
      else
        unwrap_ifg_index=[1:ps.n_image];
      end
    else
        unwrap_ifg_index=unwrap_ifg_index_sb;
    end

    if length(value_type)>2 & (value_type(1:3)=='usb'|value_type(1:3)=='rsb') & isempty(ifg_list)
        ifg_list=unwrap_ifg_index_sb;
    end
else
    unwrap_ifg_index=setdiff([1:ps.n_ifg],drop_ifg_index);
end
if (value_type(1)=='u' | value_type(1)=='a' | value_type(1)=='w') & isempty(ifg_list)
    ifg_list=unwrap_ifg_index;
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%    VALUE_TYPE
%    'v'      mean LOS velocity (MLV) in mm/yr
%    'v-d'    MLV calculated after removal of dem error (mm/yr)
%    'v-o'    MLV calculated after removal of orbital ramps (mm/yr)
%    'v-do'   MLV calculated after removal of dem error and orbital ramps (mm/yr)
%    'v-dos'  MLV calculated after removal of dem error, orbital ramps and aps (mm/yr)
%    'v-da'   MLV calculated after removal dem error and aps(mm/yr)
%    'v-a'    MLV calculated after removal aps(mm/yr)
%    'v-ds'   MLV calculated after removal dem error and sc slave(mm/yr)
%    'v-das'  MLV calculated after removal dem error, aps and sc slave(mm/yr)
%    'vdrop-d'
%    'vsb'    MLV for sb processing (mm/yr)
%    'vsb-d'  MLV for sb processing calculated after removal of dem error (mm/yr)

value_types = {'v' 'v-d' 'v-o' 'v-do' 'v-dos' 'v-da' 'v-a' 'v-ds' 'v-das'};

for value=1:length(value_types)

    value_type = char(value_types(value));

    if exist(['viS_' value_type '.mat'], 'file') && isNewProject == 0
        continue;
    end;

%###############################################
  % using ps_plot defaults  

    plot_flag=1;
    lims=[];
    ref_ifg=0;
    ifg_list=[];
    n_x=0;
    cbar_flag=0;
    textsize=0;
    textcolor=[0 0 0.004];
    lon_rg=[];
    lat_rg=[];
%################################################
    uw=load(phuwname);
    ph_uw=uw.ph_uw;
    clear uw


    switch(value_type)

        case {'v'}

        case {'v-d'}
            scla=load(sclaname);
            ph_uw=ph_uw - scla.ph_scla;
            clear scla

        case {'v-o'}
            scla=load(sclaname);
            ph_uw=ph_uw - scla.ph_ramp;
            clear scla

        case {'v-do'}
            scla=load(sclaname);
            ph_uw=ph_uw - scla.ph_ramp - scla.ph_scla;
            clear scla

        case {'v-dos'}
            uw=load(phuwname);
            scn=load(scnname);
            scla=load(sclaname);
            ph_uw=uw.ph_uw - scn.ph_scn_slave - repmat(scla.C_ps_uw,1,size(uw.ph_uw,2)) - scla.ph_scla - scla.ph_ramp;
            clear uw scn scla
            ph_uw(:,ps.master_ix)=0;

        case {'v-da'}
            if ~exist(apsname, 'var')
                continue;
            end
            scla=load(sclaname);
            aps=load(apsname);
            ph_uw=ph_uw - scla.ph_scla- aps.ph_aps_slave;
            clear scla aps

        case {'v-a'}
            if ~exist(apsname, 'var')
                continue;
            end
            aps=load(apsname);
            ph_uw=ph_uw - aps.ph_aps_slave;
            clear scla aps

        case {'v-ds'}
            scla=load(sclaname);
            scn=load(scnname);
            ph_uw=ph_uw - scla.ph_scla - scn.ph_scn_slave;
            clear scla scn

        case {'v-das'}   
            if ~exist(apsname, 'var')
                continue;
            end
            scla=load(sclaname);
            aps=load(apsname);
            scn=load(scnname);
            ph_uw=ph_uw - scla.ph_scla - aps.ph_aps_slave - scn.ph_scn_slave;
            clear scla scn

        otherwise
            error('unknown value type')
    end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%2
    ph_all=zeros(n_ps,1);
    ref_ps=ps_setref;

    if unwrap_ifg_index(1)~=ps.master_ix & unwrap_ifg_index(end)~=ps.master_ix
        unwrap_ifg_index=setdiff(unwrap_ifg_index,ps.master_ix); % need to include it if not ifgs either side of master
    end
    if ~isempty(ifg_list)
        unwrap_ifg_index=intersect(unwrap_ifg_index,ifg_list);
        ifg_list=[];
    end
    ph_uw=ph_uw(:,unwrap_ifg_index);
    day=day(unwrap_ifg_index);

    ph_uw=ph_uw-repmat(mean(ph_uw(ref_ps,:),1),n_ps,1);
    % Each ifg has master APS - slave APS, including master 
    % (where slave APS = master APS) so OK to include master in inversion
    if strcmpi(small_baseline_flag,'y')
        phuwres=load(phuwsbresname,'sm_cov');
        if isfield(phuwres,'sm_cov');
            sm_cov=phuwres.sm_cov(unwrap_ifg_index,unwrap_ifg_index);
        else
            sm_cov=eye(length(unwrap_ifg_index));
        end
    else
        if ~exist([ifgstdname,'.mat',],'file')
            sm_cov=eye(length(unwrap_ifg_index));
        else
            ifgstd=load(ifgstdname);
          if isfield(ifgstd,'ifg_std');
            ifgvar=(ifgstd.ifg_std*pi/181).^2;
            sm_cov=diag(ifgvar(unwrap_ifg_index));
          else
            sm_cov=eye(length(unwrap_ifg_index));
          end
        end
    end

    G=[ones(size(day)),day-master_day]; 
    lambda=getparm('lambda');

    if length(value_type)>4 & strcmpi(value_type(1:5),'vdrop') 
        ph_all=zeros(size(ph_uw));
        n=size(ph_uw,2);
        for i=1:n
            m=lscov(G([1:i-1,i+1:end],:),double(ph_uw(:,[1:i-1,i+1:n])',sm_cov));
            ph_all(:,i)=-m(2,:)'*365.25/4/pi*lambda*1000; 
        end
    else 
        m=lscov(G,double(ph_uw'),sm_cov);
        ph_all=-m(2,:)'*365.25/4/pi*lambda*1000; % m(1,:) is master APS + mean deviation from model
    end

    try
        save mean_v m
    catch
        viS_message('Warning: Read access only, velocities were not saved');
        %fprintf('Warning: Read access only, velocities were not saved\n')
    end
    textsize=0;
    units='mm/yr';


    %############################################
    % Convert phase to deformation (mm/y)
    %############################################
    meanv=load('mean_v.mat');
    lambda=getparm('lambda');
    mean_v=-meanv.m(2,:)'*365.25/4/pi*lambda*1000; % m(1,:) is master APS + mean deviation from model
    v_sort=sort(mean_v);
    min_v=v_sort(ceil(length(v_sort)*0.001))
    max_v=v_sort(floor(length(v_sort)*0.999))
    mean_v(mean_v<min_v)=min_v;
    mean_v(mean_v>max_v)=max_v;


    mean_v_name=['ps_mean_v.xy'];
    mean_v=[ps.lonlat,double(mean_v)];
    save(mean_v_name,'mean_v','-ASCII');

    ph_uw=[ph_uw(:,1:master_ix-1) zeros(n_ps,1) ph_uw(:,master_ix:end)];

    save(['viS_ph_' value_type '.mat'], 'ph_uw');

    viS_message(['INFO      : File ' ['viS_ph_' value_type '.mat'] ' created.']);

    load('ps2.mat')

    %==========================================================
    ij=load('ps_ij.txt');         % PS radar coord.
    ps_ll=load('ps_ll.txt');      % PS geographic coord
    ps_mean=load('ps_mean_v.xy'); % PS velocities
    load pm2

    % [rg az defo coh lat lon]
    ps_f=[ij ps_mean(:,3) coh_ps ps_ll(:,2) ps_ll(:,1)];

    save(['viS_' value_type '.mat'], 'ps_f');

    %Send message to viStaMPS output window 
    viS_message(['INFO      : File ' ['viS_' value_type '.mat'] ' created.']);

end




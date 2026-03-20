function varargout = viSDataDisplay(varargin)
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
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @viSDataDisplay_OpeningFcn, ...
                   'gui_OutputFcn',  @viSDataDisplay_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before viSDataDisplay is made visible.
function viSDataDisplay_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to viSDataDisplay (see VARARGIN)

% Choose default command line output for viSDataDisplay
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes viSDataDisplay wait for user response (see UIRESUME)
% uiwait(handles.figureDataDisplay);

addpath(fullfile(pwd));

% Re-Locate GUI window
movegui(hObject,'center');

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

vistamps.DataDisplay.Handles = handles;

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);

set(vistamps.DataDisplay.Handles.editProjectFolder, 'String', vistamps.Setup.ProjectFolder);

% Default Data Display 
hObject=vistamps.DataDisplay.Handles.popupmenuSource;
set(hObject, 'Value', 1);

% Default Background Type 
hObject=vistamps.DataDisplay.Handles.popupmenuBackgroundType;
set(hObject, 'Value', 3);

if isfield(vistamps.DataDisplay, 'NumberInterferograms')

    set(vistamps.DataDisplay.Handles.checkboxListInterferogramsPlot, 'Value', 1.0);
    
    set(vistamps.DataDisplay.Handles.checkboxNImagesPlot, 'Value', 1.0);

    set(vistamps.DataDisplay.Handles.checkboxSizeDateText, 'Value', 1.0);

    set(vistamps.DataDisplay.Handles.checkboxTextColor, 'Value', 1.0);

    set(vistamps.DataDisplay.Handles.checkboxLongitudeRange, 'Value', 1.0);

    set(vistamps.DataDisplay.Handles.checkboxLatitudeRange, 'Value', 1.0);
end

imshow(imread('viS_back.png'),'Parent',vistamps.DataDisplay.Handles.axesLogo);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% --- Outputs from this function are returned to the command line.
function varargout = viSDataDisplay_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function LoadBackgroundImage(type)

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end

    switch (type)
        case 'black'
            vistamps.DataDisplay.Background = imread('viS_black.jpg');
        case 'white'
            vistamps.DataDisplay.Background= imread('viS_white.jpg');
        case 'meanamplitude'
            vistamps.DataDisplay.Background = imread('viS_map.jpg');
    end

    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);

    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function LoadData()

    BackgroundType_UpdateFcn();

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end
        
    ps_f=[];
    load(['viS_' vistamps.DataDisplay.ValueType '.mat']);
    vistamps.DataDisplay.Data=ps_f;
    clear ps_f;
    
    vistamps.DataDisplay.DeformationMin	= round(min(vistamps.DataDisplay.Data(:, 3))-1);
    vistamps.DataDisplay.DeformationMax	= round(max(vistamps.DataDisplay.Data(:, 3))+1);
    
    ph_uw=[];
    load(['viS_ph_' vistamps.DataDisplay.ValueType '.mat']);
    vistamps.DataDisplay.Data_=ph_uw;
    clear ph_uw;

    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);

        

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function DisplayData()

    h = waitbar(0,'Processing! Please wait...','Interruptible','on');

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end

    waitbar(50/100);

    if (~isfield(vistamps.DataDisplay, 'Figure') || ~ishandle(vistamps.DataDisplay.Figure))
        vistamps.DataDisplay.Figure = figure;
        set(vistamps.DataDisplay.Figure,'CloseRequestFcn',@Figure_CloseRequestFcn);
        set(vistamps.Handles.pushbuttonReferenceArea,'Enable','on');
        set(vistamps.Handles.pushbuttonReferenceAreaCircle,'Enable','on');
        set(vistamps.Handles.pushbuttonTimeSeriesPlot,'Enable','on');
        set(vistamps.DataDisplay.Figure,'toolbar','figure');
    end

    figure(vistamps.DataDisplay.Figure);
    
    %painters | zbuffer | OpenGL
    %set(gcf, 'Renderer', 'zbuffer');
    subimage(vistamps.DataDisplay.Background, gray(256));
    set(gca,'YDir','normal');
    
    
    %# make sure the image doesn't disappear if we plot something else
    hold on
       
    % Reading colormap
    load viS_cmap_defo;
    colormap(viS_cmap_defo); 

    plot_pixel_size=getparm('plot_pixels_scatterer');
    
    switch vistamps.Setup.OrbitType
        case 'Descending'
            scatter((vistamps.DataDisplay.Columns-vistamps.DataDisplay.Data(:, 2)+1).*vistamps.DataDisplay.AspectRatioColumns, (vistamps.DataDisplay.Rows-vistamps.DataDisplay.Data(:, 1)+1).*vistamps.DataDisplay.AspectRatioRows, plot_pixel_size, vistamps.DataDisplay.Data(:,3), 'filled');
        otherwise
            scatter(vistamps.DataDisplay.Data(:, 2).*vistamps.DataDisplay.AspectRatioColumns, vistamps.DataDisplay.Data(:, 1).*vistamps.DataDisplay.AspectRatioRows, plot_pixel_size, vistamps.DataDisplay.Data(:,3), 'filled');
    end

    title('PS Deformation Map','FontSize',12);
    xlabel('range','FontSize',12);
    ylabel('azimuth','FontSize',12);
    cbar_label = '[mm/y]';
    chandle = colorbar;
    set(chandle,'FontSize',20);
    set(get(chandle,'title'),'string',cbar_label);
    
    
    %set(gca, 'CLim', [vistamps.viSDataDisplay.DeformationMin, vistamps.viSDataDisplay.DeformationMax]);
    %caxis([vistamps.DataDisplay.DeformationMin, vistamps.DataDisplay.DeformationMax]);
     deformationMin = str2double(get(vistamps.DataDisplay.Handles.editDeformationThresholdMin, 'String'));
     deformationMax = str2double(get(vistamps.DataDisplay.Handles.editDeformationThresholdMax, 'String'));
     caxis([deformationMin, deformationMax]);

    axis off;
    hold off;

    waitbar(100);
    
    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);

    close(h);


    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% --- Executes when user attempts to close a viSDataDisplay Figure.
function Figure_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to viSDataDisplay Figure (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: delete(hObject) closes the viSDataDisplay Figure
delete(hObject);

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end
    
set(vistamps.Handles.pushbuttonReferenceArea,'Enable','off');
set(vistamps.Handles.pushbuttonReferenceAreaCircle,'Enable','off');
set(vistamps.Handles.pushbuttonTimeSeriesPlot,'Enable','off');


    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function noError = FilterByCoherenceDefo()

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end

    coherence = str2double(get(vistamps.DataDisplay.Handles.textCoherenceThreshold, 'String'));
    if coherence < 0.0 || coherence >= 1.0
        errordlg('Coherence value must belong to [0, 1[','ERROR');
        noError = 0;
        return;
    else
        noError = 1;
    end
    
    
    
    %number of PS before filtering
    nPStotal=size(vistamps.DataDisplay.Data,1);
    %-------------------------------------------------------------------
    % Excluding PS outliers based on coherence
    %-------------------------------------------------------------------
    %number of PS before filtering
    nPStotal=size(vistamps.DataDisplay.Data,1);
    
    idx_ps_ch_remove=find(vistamps.DataDisplay.Data(:,4)<coherence);     
    vistamps.DataDisplay.Data(idx_ps_ch_remove,:)=[];
    vistamps.DataDisplay.Data_(idx_ps_ch_remove,:)=[];
    
    %number of PS removed based on coh
    nPScoh=size(idx_ps_ch_remove,1);
        
    %-------------------------------------------------------------------
    % Excluding PS outliers based on deformation
    %-------------------------------------------------------------------
    
     deformationMin = str2double(get(vistamps.DataDisplay.Handles.editDeformationThresholdMin, 'String'));
     deformationMax = str2double(get(vistamps.DataDisplay.Handles.editDeformationThresholdMax, 'String'));
   
    
    if deformationMin >= deformationMax
        errordlg('Min deformation must be less than Max deformation','ERROR');
        noError = 0;
        return;
    else
        noError = 1;
    end

    idx_ps_d_min_remove=find(vistamps.DataDisplay.Data(:,3)<deformationMin);
    vistamps.DataDisplay.Data(idx_ps_d_min_remove,:)=[];
    vistamps.DataDisplay.Data_(idx_ps_d_min_remove,:)=[];

    idx_ps_d_max_remove=find(vistamps.DataDisplay.Data(:,3)>deformationMax);
    vistamps.DataDisplay.Data(idx_ps_d_max_remove,:)=[];
    vistamps.DataDisplay.Data_(idx_ps_d_max_remove,:)=[];
    
    nPSdefo=nPStotal-nPScoh-size(vistamps.DataDisplay.Data_(:,1), 1);
      
    
    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);


    viS_message('************************************************************************************************');
    viS_message(sprintf('INFO      : initial no. of PS = %6.0f',nPStotal));
    viS_message(sprintf('INFO      : No. of PS with coh. bigger than %3.1f = %3.0f',coherence,nPStotal-nPScoh));
    viS_message(sprintf('INFO      : No. of PS with defo> %2.0f mm/yr and defo< %2.0f mm/yr = %5.0f',deformationMin,deformationMax,(nPStotal-nPScoh-nPSdefo)));
    viS_message(sprintf('INFO      : No. of PS rejected = %5.0f',nPSdefo+nPScoh));
    viS_message(sprintf('INFO      : No. of PS remaining after coh and defo filtering = %5.0f',nPStotal-(nPSdefo+nPScoh)));
    %viS_message('************************************************************************************************');
    
    
    
    

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% --- Executes during object creation, after setting all properties.
function popupmenuSource_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenuSource (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%    SOURCE
%     LOS velocity
%     Wrapped phase
%     Unwrapped phase

addlistener(hObject,'Value','PostSet',@Source_UpdateFcn);
addlistener(hObject,'Value','PostSet',@ValueTypeList_UpdateFcn);
set(hObject, 'String', {'LOS velocity' 'Wrapped phase' 'Unwrapped phase'});



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function Source_UpdateFcn(hObject, eventdata, handles)

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end

    hObject=vistamps.DataDisplay.Handles.popupmenuSource;

    contents = cellstr(get(hObject,'String'));
    vistamps.DataDisplay.Source = contents{get(hObject,'Value')};

    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);

    backgroundColorEnabled = get(vistamps.DataDisplay.Handles.uipanelDataToDisplay, 'BackgroundColor');
    backgroundColorDisabled = get(vistamps.DataDisplay.Handles.uipanelProjectFolder, 'BackgroundColor');
    
    switch vistamps.DataDisplay.Source
        case 'LOS velocity'
            set(get(vistamps.DataDisplay.Handles.uipanelCoherenceThreshold,'Children'), 'Enable', 'on');
            set(vistamps.DataDisplay.Handles.uipanelCoherenceThreshold, 'BackgroundColor', backgroundColorEnabled);
            set(get(vistamps.DataDisplay.Handles.uipanelDeformationThreshold,'Children'), 'Enable', 'on');
            set(vistamps.DataDisplay.Handles.uipanelDeformationThreshold, 'BackgroundColor', backgroundColorEnabled);
            
            set(get(vistamps.DataDisplay.Handles.uipanelNInterferogram,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelNInterferogram, 'BackgroundColor', backgroundColorDisabled);
            set(get(vistamps.DataDisplay.Handles.uipanelListInterferogramsPlot,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelListInterferogramsPlot, 'BackgroundColor', backgroundColorDisabled);
            set(get(vistamps.DataDisplay.Handles.uipanelNImagesPlot,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelNImagesPlot, 'BackgroundColor', backgroundColorDisabled);
            set(get(vistamps.DataDisplay.Handles.uipanelColorbar,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelColorbar, 'BackgroundColor', backgroundColorDisabled);
            set(get(vistamps.DataDisplay.Handles.uipanelSizeDateText,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelSizeDateText, 'BackgroundColor', backgroundColorDisabled);
            set(get(vistamps.DataDisplay.Handles.uipanelTextColor,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelTextColor, 'BackgroundColor', backgroundColorDisabled);
            set(get(vistamps.DataDisplay.Handles.uipanelLongitudeRange,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelLongitudeRange, 'BackgroundColor', backgroundColorDisabled);
            set(get(vistamps.DataDisplay.Handles.uipanelLatitudeRange,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelLatitudeRange, 'BackgroundColor', backgroundColorDisabled);
            
        case {'Wrapped phase', 'Unwrapped phase'}
            set(get(vistamps.DataDisplay.Handles.uipanelCoherenceThreshold,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelCoherenceThreshold, 'BackgroundColor', backgroundColorDisabled);
            set(get(vistamps.DataDisplay.Handles.uipanelDeformationThreshold,'Children'), 'Enable', 'off');
            set(vistamps.DataDisplay.Handles.uipanelDeformationThreshold, 'BackgroundColor', backgroundColorDisabled);
            
            set(get(vistamps.DataDisplay.Handles.uipanelNInterferogram,'Children'), 'Enable', 'on');
            set(vistamps.DataDisplay.Handles.uipanelNInterferogram, 'BackgroundColor', backgroundColorEnabled);
            set(get(vistamps.DataDisplay.Handles.uipanelListInterferogramsPlot,'Children'), 'Enable', 'on');
            if get(vistamps.DataDisplay.Handles.checkboxListInterferogramsPlot, 'Value') == 0.0
                set(vistamps.DataDisplay.Handles.editListInterferogramsPlot, 'Enable', 'on');
            else
                set(vistamps.DataDisplay.Handles.editListInterferogramsPlot, 'Enable', 'off');
            end
            set(vistamps.DataDisplay.Handles.uipanelListInterferogramsPlot, 'BackgroundColor', backgroundColorEnabled);
            set(get(vistamps.DataDisplay.Handles.uipanelNImagesPlot,'Children'), 'Enable', 'on');
            if get(vistamps.DataDisplay.Handles.checkboxNImagesPlot, 'Value') == 0.0
                set(vistamps.DataDisplay.Handles.editNImagesPlot, 'Enable', 'on');
            else
                set(vistamps.DataDisplay.Handles.editNImagesPlot, 'Enable', 'off');
            end            
            set(vistamps.DataDisplay.Handles.uipanelNImagesPlot, 'BackgroundColor', backgroundColorEnabled);
            set(get(vistamps.DataDisplay.Handles.uipanelColorbar,'Children'), 'Enable', 'on');
            set(vistamps.DataDisplay.Handles.uipanelColorbar, 'BackgroundColor', backgroundColorEnabled);
            set(get(vistamps.DataDisplay.Handles.uipanelSizeDateText,'Children'), 'Enable', 'on');
            if get(vistamps.DataDisplay.Handles.checkboxSizeDateText, 'Value') == 0.0
                set(vistamps.DataDisplay.Handles.editSizeDateText, 'Enable', 'on');
            else
                set(vistamps.DataDisplay.Handles.editSizeDateText, 'Enable', 'off');
            end 
            set(vistamps.DataDisplay.Handles.uipanelSizeDateText, 'BackgroundColor', backgroundColorEnabled);
            set(get(vistamps.DataDisplay.Handles.uipanelTextColor,'Children'), 'Enable', 'on');
            if get(vistamps.DataDisplay.Handles.checkboxTextColor, 'Value') == 0.0
                set(vistamps.DataDisplay.Handles.editTextColorRed, 'Enable', 'on');
                set(vistamps.DataDisplay.Handles.editTextColorGreen, 'Enable', 'on');
                set(vistamps.DataDisplay.Handles.editTextColorBlue, 'Enable', 'on');
            else
                set(vistamps.DataDisplay.Handles.editTextColorRed, 'Enable', 'off');
                set(vistamps.DataDisplay.Handles.editTextColorGreen, 'Enable', 'off');
                set(vistamps.DataDisplay.Handles.editTextColorBlue, 'Enable', 'off');
            end             
            set(vistamps.DataDisplay.Handles.uipanelTextColor, 'BackgroundColor', backgroundColorEnabled);
            set(get(vistamps.DataDisplay.Handles.uipanelLongitudeRange,'Children'), 'Enable', 'on');
            if get(vistamps.DataDisplay.Handles.checkboxLongitudeRange, 'Value') == 0.0
                set(vistamps.DataDisplay.Handles.editLongitudeRangeBottom, 'Enable', 'on');
                set(vistamps.DataDisplay.Handles.editLongitudeRangeTop, 'Enable', 'on');
            else
                set(vistamps.DataDisplay.Handles.editLongitudeRangeBottom, 'Enable', 'off');
                set(vistamps.DataDisplay.Handles.editLongitudeRangeTop, 'Enable', 'off');
            end             
            set(vistamps.DataDisplay.Handles.uipanelLongitudeRange, 'BackgroundColor', backgroundColorEnabled);
            set(get(vistamps.DataDisplay.Handles.uipanelLatitudeRange,'Children'), 'Enable', 'on');
            if get(vistamps.DataDisplay.Handles.checkboxLatitudeRange, 'Value') == 0.0
                set(vistamps.DataDisplay.Handles.editLatitudeRangeBottom, 'Enable', 'on');
                set(vistamps.DataDisplay.Handles.editLatitudeRangeTop, 'Enable', 'on');
            else
                set(vistamps.DataDisplay.Handles.editLatitudeRangeBottom, 'Enable', 'off');
                set(vistamps.DataDisplay.Handles.editLatitudeRangeTop, 'Enable', 'off');
            end              
            set(vistamps.DataDisplay.Handles.uipanelLatitudeRange, 'BackgroundColor', backgroundColorEnabled);
    end



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function ValueTypeList_UpdateFcn(hObject, eventdata, handles)

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end

    hObject=vistamps.DataDisplay.Handles.popupmenuValueType;

    switch vistamps.DataDisplay.Source
        case 'LOS velocity'
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

            load psver
            apsname=['aps',num2str(psver)];
            if exist(apsname, 'var')
                set(hObject, 'String', {'v' 'v-d' 'v-o' 'v-do' 'v-dos' 'v-da' 'v-a' 'v-ds' 'v-das'});
            else
                set(hObject, 'String', {'v' 'v-d' 'v-o' 'v-do' 'v-dos' 'v-ds'});
            end
            

        case 'Wrapped phase'
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %    VALUE_TYPE            
    %   'w' for wrapped phase
    %   'w-d' for wrapped phase minus smoothed dem error
    %   'w-o' for wrapped phase minus orbital ramps
    %   'w-dm' for wrapped phase minus dem error and master AOE
    %   'w-do' for wrapped phase minus dem error and orbital ramps
    %   'w-dmo' for wrapped phase minus dem error, master AOE and orbital ramps
            set(hObject, 'String', {'w' 'w-d' 'w-o' 'w-dm' 'w-do' 'w-dmo'});

        case 'Unwrapped phase'
    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
    %    VALUE_TYPE 
    %   'u' for unwrapped phase
    %   'u-d' for unwrapped phase minus dem error  
    %   'u-m' for unwrapped phase minus and master AOE  
    %   'u-o' for unwrapped phase minus orbital ramps 
    %   'u-dm' for unwrapped phase minus dem error and master AOE  
    %   'u-do' for unwrapped phase minus dem error and orbital ramps
    %   'u-dmo' for unwrapped phase minus dem error, master AOE and orbital ramps
    %   'u-dms' for unwrapped phase minus dem error and all AOE 
    %   'u-dmos' for unwrapped phase minus dem error, all AOE and orbital ramps
            set(hObject, 'String', {'u' 'u-d' 'u-m' 'u-o' 'u-dm' 'u-do' 'u-dmo' 'u-dms' 'u-dmos'});

    end

    % Default Value Type 
    set(hObject, 'Value', 1);
    ValueType_UpdateFcn;



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% --- Executes during object creation, after setting all properties.
function popupmenuValueType_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenuValueType (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

addlistener(hObject,'Value','PostSet',@ValueType_UpdateFcn);
addlistener(hObject,'Value','PostSet',@ValueTypeDescription_UpdateFcn);
addlistener(hObject,'Value','PostSet',@DeformationThreshold_UpdateFcn);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function ValueType_UpdateFcn(hObject, eventdata, handles)

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end

    hObject=vistamps.DataDisplay.Handles.popupmenuValueType;

    contents = cellstr(get(hObject,'String'));
    vistamps.DataDisplay.ValueType = contents{get(hObject,'Value')};
    
    hSlider=vistamps.DataDisplay.Handles.sliderCoherenceThreshold;
    set(hSlider, 'Value', 0);

    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function ValueTypeDescription_UpdateFcn(hObject, eventdata, handles)

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end

    hTextValueType = vistamps.DataDisplay.Handles.textValueType;

    switch vistamps.DataDisplay.ValueType
        case 'v'
            set(hTextValueType, 'String', 'Description: mean LOS velocity (MLV) in mm/yr');
        case 'v-d'
            set(hTextValueType, 'String', 'Description: MLV calculated after removal of dem error (mm/yr)');
        case 'v-o'
            set(hTextValueType, 'String', 'Description: MLV calculated after removal of orbital ramps (mm/yr)');
        case 'v-do'
            set(hTextValueType, 'String', 'Description: MLV calculated after removal of dem error and orbital ramps (mm/yr)');
        case 'v-dos'
            set(hTextValueType, 'String', 'Description: MLV calculated after removal of dem error, orbital ramps and aps (mm/yr)');
        case 'v-da'
            set(hTextValueType, 'String', 'Description: MLV calculated after removal dem error and aps(mm/yr)');
        case 'v-a'
            set(hTextValueType, 'String', 'Description: MLV calculated after removal aps(mm/yr)');
        case 'v-ds'
            set(hTextValueType, 'String', 'Description: MLV calculated after removal dem error and sc slave(mm/yr)');
        case 'v-das'
            set(hTextValueType, 'String', 'Description: MLV calculated after removal dem error, aps and sc slave(mm/yr)');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%            
        case 'w'
            set(hTextValueType, 'String', 'Description: Wrapped phase');
        case 'w-d'
            set(hTextValueType, 'String', 'Description: Wrapped phase minus smoothed dem error');
        case 'w-o'
            set(hTextValueType, 'String', 'Description: Wrapped phase minus orbital ramps'); 
        case 'w-dm'
            set(hTextValueType, 'String', 'Description: Wrapped phase minus dem error and master AOE'); 
        case 'w-do'
            set(hTextValueType, 'String', 'Description: Wrapped phase minus dem error and orbital ramps'); 
        case 'w-dmo'
            set(hTextValueType, 'String', 'Description: Wrapped phase minus dem error, master AOE and orbital ramps');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%            
        case 'u'
            set(hTextValueType, 'String', 'Description: Unwrapped phase');  
        case 'u-d'
            set(hTextValueType, 'String', 'Description: Unwrapped phase minus dem error');
        case 'u-m'
            set(hTextValueType, 'String', 'Description: Unwrapped phase minus and master AOE'); 
        case 'u-o'
            set(hTextValueType, 'String', 'Description: Unwrapped phase minus orbital ramps'); 
        case 'u-dm'
            set(hTextValueType, 'String', 'Description: Unwrapped phase minus dem error and master AOE');
        case 'u-do'
            set(hTextValueType, 'String', 'Description: Unwrapped phase minus dem error and orbital ramps'); 
        case 'u-dmo'
            set(hTextValueType, 'String', 'Description: Unwrapped phase minus dem error, master AOE and orbital ramps');  
        case 'u-dms'
            set(hTextValueType, 'String', 'Description: Unwrapped phase minus dem error and all AOE');  
        case 'u-dmos'
            set(hTextValueType, 'String', 'Description: Unwrapped phase minus dem error, all AOE and orbital ramps');           
        otherwise
            return;
    end
    
    switch vistamps.DataDisplay.Source
        case 'LOS velocity'
            LoadData();

            if (isfield(vistamps.DataDisplay, 'Figure') && ishandle(vistamps.DataDisplay.Figure))
                DisplayData();
            end
        otherwise
    end
        



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% --- Executes during object creation, after setting all properties.
function popupmenuBackgroundType_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenuBackgroundType (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

addlistener(hObject,'Value','PostSet',@BackgroundType_UpdateFcn);
set(hObject, 'String', {'Black' 'White' 'Mean Amplitude'});



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function BackgroundType_UpdateFcn(hObject, eventdata, handles)

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end

    hObject = vistamps.DataDisplay.Handles.popupmenuBackgroundType;
    
    contents = cellstr(get(hObject,'String'));
    vistamps.DataDisplay.BackgroundType = contents{get(hObject,'Value')};

    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);
    
    switch vistamps.DataDisplay.BackgroundType
        case 'Black'
            LoadBackgroundImage('black');
        case 'White'
            LoadBackgroundImage('white');
        case 'Mean Amplitude'
            LoadBackgroundImage('meanamplitude');
    end

    if (isfield(vistamps.DataDisplay, 'Figure') && ishandle(vistamps.DataDisplay.Figure))
        DisplayData();
    end
    
    

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
function DeformationThreshold_UpdateFcn(hObject, eventdata, handles)

    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end
    
    hObject=vistamps.DataDisplay.Handles.editDeformationThresholdMin;
    set(hObject, 'String', vistamps.DataDisplay.DeformationMin);
    
    hObject=vistamps.DataDisplay.Handles.editDeformationThresholdMax;
    set(hObject, 'String', vistamps.DataDisplay.DeformationMax);
    
    
    
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% --- Executes on slider movement.
function sliderCoherenceThreshold_Callback(hObject, eventdata, handles)
% hObject    handle to sliderCoherenceThreshold (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'Value') returns position of slider
%        get(hObject,'Min') and get(hObject,'Max') to determine range of slider

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

hSlider=vistamps.DataDisplay.Handles.sliderCoherenceThreshold;

vistamps.DataDisplay.CoherenceThreshold = get(hSlider, 'Value');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function sliderCoherenceThreshold_CreateFcn(hObject, eventdata, handles)
% hObject    handle to sliderCoherenceThreshold (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end

addlistener(hObject,'Value','PostSet',@textCoherenceThreshold_UpdateFcn);


function textCoherenceThreshold_UpdateFcn(hObject, eventdata, handles)
% hObject    handle to textCoherenceThreshold (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

hSlider=vistamps.DataDisplay.Handles.sliderCoherenceThreshold;
hText=vistamps.DataDisplay.Handles.textCoherenceThreshold;
textValue=round(get(hSlider, 'Value')*100)/100;
if (textValue == 1)
    textValue = 0.99;
end
set(hText, 'String', textValue);


function editDeformationThresholdMinMax_UpdateFcn(hObject, eventdata, handles)
% hObject    handle to textCoherenceThreshold (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

hMin = vistamps.DataDisplay.Handles.editDeformationThresholdMin;
set(hMin, 'String', min(vistamps.DataDisplay.Data(:, 3)));


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% --- Executes on selection change in popupmenuNInterferogram.
function popupmenuNInterferogram_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenuNInterferogram (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenuNInterferogram contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenuNInterferogram

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

contents = cellstr(get(hObject,'String'));
selectedOption = contents{get(hObject,'Value')};
switch selectedOption
    case 'Master'
        vistamps.DataDisplay.NumberInterferograms = 0;
    case 'Incremental Referencing'
        vistamps.DataDisplay.NumberInterferograms = -1;    
end

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function popupmenuNInterferogram_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenuNInterferogram (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% number of interferogram to reference to - defaults to 0 (master)
% -1 for incremental referencing
vistamps.DataDisplay.NumberInterferograms = 0;

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



function editListInterferogramsPlot_Callback(hObject, eventdata, handles)
% hObject    handle to editListInterferogramsPlot (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editListInterferogramsPlot as text
%        str2double(get(hObject,'String')) returns contents of editListInterferogramsPlot as a double

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxListInterferogramsPlot, 'Value') == 1
    return;
end

% list of interferograms to plot - defaults to [] (all)
vistamps.DataDisplay.ListInterferograms = get(hObject,'String');

% Write appdata structered variable
setappdata(0, 'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function editListInterferogramsPlot_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editListInterferogramsPlot (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% list of interferograms to plot - defaults to [] (all)
vistamps.DataDisplay.ListInterferograms = [];
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0, 'vistamps', vistamps);



% --- Executes on button press in checkboxListInterferogramsPlot.
function checkboxListInterferogramsPlot_Callback(hObject, eventdata, handles)
% hObject    handle to checkboxListInterferogramsPlot (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkboxListInterferogramsPlot

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(hObject,'Value') == 0
    set(vistamps.DataDisplay.Handles.editListInterferogramsPlot, 'Enable', 'on');
else
    set(vistamps.DataDisplay.Handles.editListInterferogramsPlot, 'Enable', 'off');
    % list of interferograms to plot - defaults to [] (all)
    vistamps.DataDisplay.ListInterferograms = [];
end

set(vistamps.DataDisplay.Handles.editListInterferogramsPlot, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);
    


function editNImagesPlot_Callback(hObject, eventdata, handles)
% hObject    handle to editNImagesPlot (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editNImagesPlot as text
%        str2double(get(hObject,'String')) returns contents of editNImagesPlot as a double

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxNImagesPlot,'Value') == 1
    return;
end

% maximum number of images to plot per row 
% defaults to 0 (find optimum based on image size)
vistamps.DataDisplay.MaxNumberImagesPlotRow = str2double(get(hObject,'String'));

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function editNImagesPlot_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editNImagesPlot (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% maximum number of images to plot per row 
% defaults to 0 (find optimum based on image size)
vistamps.DataDisplay.MaxNumberImagesPlotRow = 0;
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes on button press in checkboxNImagesPlot.
function checkboxNImagesPlot_Callback(hObject, eventdata, handles)
% hObject    handle to checkboxNImagesPlot (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkboxNImagesPlot

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(hObject,'Value') == 0
    set(vistamps.DataDisplay.Handles.editNImagesPlot, 'Enable', 'on');
else
    set(vistamps.DataDisplay.Handles.editNImagesPlot, 'Enable', 'off');
    % maximum number of images to plot per row 
    % defaults to 0 (find optimum based on image size)
    vistamps.DataDisplay.MaxNumberImagesPlotRow = 0;
end

set(vistamps.DataDisplay.Handles.editNImagesPlot, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);
    


% --- Executes on selection change in popupmenuColorbar.
function popupmenuColorbar_Callback(hObject, eventdata, handles)
% hObject    handle to popupmenuColorbar (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: contents = cellstr(get(hObject,'String')) returns popupmenuColorbar contents as cell array
%        contents{get(hObject,'Value')} returns selected item from popupmenuColorbar

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

contents = cellstr(get(hObject,'String'));
selectedOption = contents{get(hObject,'Value')};
switch selectedOption
    case 'Plot on master, if plotted'
        vistamps.DataDisplay.Colorbar = 0;  
    case 'Don''t plot a colorbar'
        vistamps.DataDisplay.Colorbar = 1;
    case 'Plot a colorbar underneath'
        vistamps.DataDisplay.Colorbar = 2;
end

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function popupmenuColorbar_CreateFcn(hObject, eventdata, handles)
% hObject    handle to popupmenuColorbar (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: popupmenu controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% colorbar flag - defaults to 0 (plot on master, if plotted)
% 1 = don't plot a colorbar
% 2 = plot a colorbar underneath
vistamps.DataDisplay.Colorbar = 0;

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



function editSizeDateText_Callback(hObject, eventdata, handles)
% hObject    handle to editSizeDateText (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editSizeDateText as text
%        str2double(get(hObject,'String')) returns contents of editSizeDateText as a double

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxSizeDateText,'Value') == 1
    return;
end

% size of date text in points - defaults to 0 (best)
% +ve size plots a top (default), -ve size plots at bottom
vistamps.DataDisplay.SizeDateTextPoints = str2double(get(hObject,'String'));

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);


% --- Executes during object creation, after setting all properties.
function editSizeDateText_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editSizeDateText (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% size of date text in points - defaults to 0 (best)
% +ve size plots a top (default), -ve size plots at bottom
vistamps.DataDisplay.SizeDateTextPoints = 0;
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes on button press in checkboxSizeDateText.
function checkboxSizeDateText_Callback(hObject, eventdata, handles)
% hObject    handle to checkboxSizeDateText (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkboxSizeDateText

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(hObject,'Value') == 0
    set(vistamps.DataDisplay.Handles.editSizeDateText, 'Enable', 'on');
else
    set(vistamps.DataDisplay.Handles.editSizeDateText, 'Enable', 'off');
    % size of date text in points - defaults to 0 (best)
    % +ve size plots a top (default), -ve size plots at bottom
    vistamps.DataDisplay.SizeDateTextPoints = 0;
end

set(vistamps.DataDisplay.Handles.editSizeDateText, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



function editTextColorRed_Callback(hObject, eventdata, handles)
% hObject    handle to editTextColorRed (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editTextColorRed as text
%        str2double(get(hObject,'String')) returns contents of editTextColorRed as a double

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxTextColor,'Value') == 1
    return;
end

% 1x3 color vector - default white or black depending on BACKGROUND
vistamps.DataDisplay.TextColor(1) = str2double(get(hObject,'String'));

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function editTextColorRed_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editTextColorRed (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% 1x3 color vector - default white or black depending on BACKGROUND
vistamps.DataDisplay.TextColor = [0 0 0];
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);




function editTextColorGreen_Callback(hObject, eventdata, handles)
% hObject    handle to editTextColorGreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editTextColorGreen as text
%        str2double(get(hObject,'String')) returns contents of editTextColorGreen as a double

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxTextColor,'Value') == 1
    return;
end

% 1x3 color vector - default white or black depending on BACKGROUND
vistamps.DataDisplay.TextColor(2) = str2double(get(hObject,'String'));

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function editTextColorGreen_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editTextColorGreen (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% 1x3 color vector - default white or black depending on BACKGROUND
vistamps.DataDisplay.TextColor = [0 0 0];
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);


function editTextColorBlue_Callback(hObject, eventdata, handles)
% hObject    handle to editTextColorBlue (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editTextColorBlue as text
%        str2double(get(hObject,'String')) returns contents of editTextColorBlue as a double

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxTextColor,'Value') == 1
    return;
end

% 1x3 color vector - default white or black depending on BACKGROUND
vistamps.DataDisplay.TextColor(2) = str2double(get(hObject,'String'));

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function editTextColorBlue_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editTextColorBlue (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% 1x3 color vector - default white or black depending on BACKGROUND
vistamps.DataDisplay.TextColor = [0 0 0];
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes on button press in checkboxTextColor.
function checkboxTextColor_Callback(hObject, eventdata, handles)
% hObject    handle to checkboxTextColor (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkboxTextColor

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(hObject,'Value') == 0
    set(vistamps.DataDisplay.Handles.editTextColorRed, 'Enable', 'on');
    set(vistamps.DataDisplay.Handles.editTextColorGreen, 'Enable', 'on');
    set(vistamps.DataDisplay.Handles.editTextColorBlue, 'Enable', 'on');
else
    set(vistamps.DataDisplay.Handles.editTextColorRed, 'Enable', 'off');
    set(vistamps.DataDisplay.Handles.editTextColorGreen, 'Enable', 'off');
    set(vistamps.DataDisplay.Handles.editTextColorBlue, 'Enable', 'off');
    % 1x3 color vector - default white or black depending on BACKGROUND
    vistamps.DataDisplay.TextColor = [];
end

set(vistamps.DataDisplay.Handles.editTextColorRed, 'String', '0');
set(vistamps.DataDisplay.Handles.editTextColorGreen, 'String', '0');
set(vistamps.DataDisplay.Handles.editTextColorBlue, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



function editLongitudeRangeBottom_Callback(hObject, eventdata, handles)
% hObject    handle to editLongitudeRangeBottom (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editLongitudeRangeBottom as text
%        str2double(get(hObject,'String')) returns contents of editLongitudeRangeBottom as a double


if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxLongitudeRange,'Value') == 1
    return;
end

% longitude range - defaults to [] (whole image)
vistamps.DataDisplay.LongitudeRange = [str2double(get(hObject,'String')) str2double(get(vistamps.DataDisplay.Handles.editLongitudeRangeTop,'String'))];

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function editLongitudeRangeBottom_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editLongitudeRangeBottom (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% longitude range - defaults to [] (whole image)
vistamps.DataDisplay.LongitudeRange = [];
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function editLongitudeRangeTop_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editLongitudeRangeTop (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% longitude range - defaults to [] (whole image)
vistamps.DataDisplay.LongitudeRange = [];
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



function editLongitudeRangeTop_Callback(hObject, eventdata, handles)
% hObject    handle to editLongitudeRangeTop (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editLongitudeRangeTop as text
%        str2double(get(hObject,'String')) returns contents of editLongitudeRangeTop as a double

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxLongitudeRange,'Value') == 1
    return;
end

% longitude range - defaults to [] (whole image)
vistamps.DataDisplay.LongitudeRange = [str2double(get(vistamps.DataDisplay.Handles.editLongitudeRangeBottom,'String')) str2double(get(hObject,'String'))];

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes on button press in checkboxLongitudeRange.
function checkboxLongitudeRange_Callback(hObject, eventdata, handles)
% hObject    handle to checkboxLongitudeRange (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkboxLongitudeRange

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(hObject,'Value') == 0
    set(vistamps.DataDisplay.Handles.editLongitudeRangeBottom, 'Enable', 'on');
    set(vistamps.DataDisplay.Handles.editLongitudeRangeTop, 'Enable', 'on');
    
    minimum = min(vistamps.DataDisplay.Data(:, 6));
    set(vistamps.DataDisplay.Handles.editLongitudeRangeBottom, 'String', num2str(minimum));
    vistamps.DataDisplay.LongitudeRange(1) = minimum;
    
    maximum = max(vistamps.DataDisplay.Data(:, 6));
    set(vistamps.DataDisplay.Handles.editLongitudeRangeTop, 'String', num2str(maximum));
    vistamps.DataDisplay.LongitudeRange(2) = maximum;
else
    set(vistamps.DataDisplay.Handles.editLongitudeRangeBottom, 'Enable', 'off');
    set(vistamps.DataDisplay.Handles.editLongitudeRangeTop, 'Enable', 'off');
    
    set(vistamps.DataDisplay.Handles.editLongitudeRangeBottom, 'String', '0');
    set(vistamps.DataDisplay.Handles.editLongitudeRangeTop, 'String', '0');
    
    % longitude range - defaults to [] (whole image)
    vistamps.DataDisplay.LongitudeRange = [];
end

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);




function editLatitudeRangeBottom_Callback(hObject, eventdata, handles)
% hObject    handle to editLatitudeRangeBottom (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editLatitudeRangeBottom as text
%        str2double(get(hObject,'String')) returns contents of editLatitudeRangeBottom as a double


if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxLatitudeRange,'Value') == 1
    return;
end

% longitude range - defaults to [] (whole image)
vistamps.DataDisplay.LatitudeRange = [str2double(get(hObject,'String')) str2double(get(vistamps.DataDisplay.Handles.editLatitudeRangeTop,'String'))];

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes during object creation, after setting all properties.
function editLatitudeRangeBottom_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editLatitudeRangeBottom (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% latitude range - defaults to [] (whole image)
vistamps.DataDisplay.LatitudeRange = [];
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



function editLatitudeRangeTop_Callback(hObject, eventdata, handles)
% hObject    handle to editLatitudeRangeTop (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hints: get(hObject,'String') returns contents of editLatitudeRangeTop as text
%        str2double(get(hObject,'String')) returns contents of editLatitudeRangeTop as a double

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(vistamps.DataDisplay.Handles.checkboxLatitudeRange,'Value') == 1
    return;
end

% longitude range - defaults to [] (whole image)
vistamps.DataDisplay.LatitudeRange = [str2double(get(vistamps.DataDisplay.Handles.editLatitudeRangeBottom,'String')) str2double(get(hObject,'String'))];

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);




% --- Executes during object creation, after setting all properties.
function editLatitudeRangeTop_CreateFcn(hObject, eventdata, handles)
% hObject    handle to editLatitudeRangeTop (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: edit controls usually have a white background on Windows.
%       See ISPC and COMPUTER.
if ispc && isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor','white');
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

% latitude range - defaults to [] (whole image)
vistamps.DataDisplay.LatitudeRange = [];
set(hObject, 'String', '0');

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes on button press in checkboxLatitudeRange.
function checkboxLatitudeRange_Callback(hObject, eventdata, handles)
% hObject    handle to checkboxLatitudeRange (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Hint: get(hObject,'Value') returns toggle state of checkboxLatitudeRange

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if get(hObject,'Value') == 0
    set(vistamps.DataDisplay.Handles.editLatitudeRangeBottom, 'Enable', 'on');
    set(vistamps.DataDisplay.Handles.editLatitudeRangeTop, 'Enable', 'on');
    
    minimum = min(vistamps.DataDisplay.Data(:, 5));
    set(vistamps.DataDisplay.Handles.editLatitudeRangeBottom, 'String', num2str(minimum));
    vistamps.DataDisplay.LatitudeRange(1) = minimum;
    
    maximum = max(vistamps.DataDisplay.Data(:, 5));
    set(vistamps.DataDisplay.Handles.editLatitudeRangeTop, 'String', num2str(maximum));
    vistamps.DataDisplay.LatitudeRange(2) = maximum;
else
    set(vistamps.DataDisplay.Handles.editLatitudeRangeBottom, 'Enable', 'off');
    set(vistamps.DataDisplay.Handles.editLatitudeRangeTop, 'Enable', 'off');
    
    set(vistamps.DataDisplay.Handles.editLatitudeRangeBottom, 'String', '0');
    set(vistamps.DataDisplay.Handles.editLatitudeRangeTop, 'String', '0');
    
    % longitude range - defaults to [] (whole image)
    vistamps.DataDisplay.LatitudeRange = [];
end


% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Executes on button press in pushbuttonDisplay.
function pushbuttonDisplay_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonDisplay (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

switch vistamps.DataDisplay.Source
    case 'LOS velocity'
        LoadData();

        %Coherence and Deformation Thresholds
        if ~FilterByCoherenceDefo()
            return;
        end

       
        DisplayData();
    case {'Wrapped phase', 'Unwrapped phase'}
        BackgroundType = 0;
        switch vistamps.DataDisplay.BackgroundType
            case 'Black'
                BackgroundType = 0; 
            case 'White'
                BackgroundType = 1;
            case 'Mean Amplitude'
                BackgroundType = 5;
        end
        
        %ps_plot(VALUE_TYPE,
        %BACKGROUND,
        %PHASE_LIMS,
        %REF_IFG,
        %IFG_LIST,
        %N_X,
        %CBAR_FLAG,
        %TEXTSIZE,
        %TEXTCOLOR,
        %LON_RG,
        %LAT_RG) 
        viS_ps_plot(vistamps.DataDisplay.ValueType,...
            BackgroundType,...
            0,...
            vistamps.DataDisplay.NumberInterferograms,...
            vistamps.DataDisplay.ListInterferograms,...
            vistamps.DataDisplay.MaxNumberImagesPlotRow,...
            vistamps.DataDisplay.Colorbar,...
            vistamps.DataDisplay.SizeDateTextPoints,...
            vistamps.DataDisplay.TextColor,...
            vistamps.DataDisplay.LongitudeRange,...
            vistamps.DataDisplay.LatitudeRange);
end

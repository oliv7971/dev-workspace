function varargout = viStaMPS(varargin)
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
                   'gui_OpeningFcn', @viStaMPS_OpeningFcn, ...
                   'gui_OutputFcn',  @viStaMPS_OutputFcn, ...
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



% --- Executes just before viStaMPS is made visible.
function viStaMPS_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to viStaMPS (see VARARGIN)

% Choose default command line output for viStaMPS
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes viStaMPS wait for user response (see UIRESUME)
% uiwait(handles.figureviStaMPS);

[pwd] = fileparts(mfilename('fullpath'));
addpath(fullfile(pwd));

vistamps.Handles = handles;

% Re-Locate GUI window
movegui(hObject,'northwest');

imshow(imread('viS_back.png'),'Parent', vistamps.Handles.axesLogo);

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Outputs from this function are returned to the command line.
function varargout = viStaMPS_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;




% --- Executes during object deletion, before destroying properties.
function figureviStaMPS_DeleteFcn(hObject, eventdata, handles)
% hObject    handle to figureviStaMPS (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Remove appdata structered variable
if (isappdata(0, 'vistamps'))
    rmappdata(0, 'vistamps');
end;

close all force;


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% --- Executes on button press in togglebutton.
function togglebuttonONOFF(hObject, window)
% hObject    handle to togglebutton (see GCBO)

% Hint: get(hObject,'Value') returns toggle state of togglebutton

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

window = window(4:size(window, 2));

if get(hObject,'Value')==1
    if (~isfield(vistamps, window))
        eval(window);
    else
        h=eval(['vistamps.' window '.Handles.figure' window]);
        set(h, 'visible', 'on');
    end
else
    h=eval(['vistamps.' window '.Handles.figure' window]);
    set(h, 'visible', 'off');
end



% --- Executes on button press in pushbuttonSetup.
function pushbuttonSetup_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonSetup (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');   
end

if ~isfield(vistamps, 'Setup')
    % Create Setup window
    eval('viSSetup');
else
    if isfield(vistamps, 'DataDisplay') &&...
            isfield(vistamps.Setup, 'ProjectFolder') &&...
                exist(fullfile(vistamps.Setup.ProjectFolder,'viS_Setup.mat'), 'file')
        load viS_Setup projectFolder orbitType scaleFactor Distance;
        vistamps.Setup.ProjectFolder = projectFolder;
        set(vistamps.Setup.Handles.editProjectFolder, 'String', vistamps.Setup.ProjectFolder);
        vistamps.Setup.OrbitType = orbitType;
        % Write appdata structered variable
        setappdata(0,'vistamps', vistamps);

        if strcmp(vistamps.Setup.OrbitType, 'Ascending')
            set(vistamps.Setup.Handles.radiobuttonAscending, 'Value', 1);
        elseif strcmp(vistamps.Setup.OrbitType, 'Descending')
            set(vistamps.Setup.Handles.radiobuttonDescending, 'Value', 1);    
        end

        set(vistamps.Setup.Handles.editScaleFactor, 'String', scaleFactor);
        set(vistamps.Setup.Handles.editDistance, 'String', Distance);
    end
end

togglebuttonONOFF(hObject, 'viSSetup');





% --- Executes on button press in pushbuttonDataDisplay.
function pushbuttonDataDisplay_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonDataDisplay (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');   
end

togglebuttonONOFF(hObject, 'viSDataDisplay');


% --- Executes on button press in pushbuttonReferenceArea.
function pushbuttonReferenceArea_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonReferenceArea (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

viS_getpoly;



% --- Executes on button press in pushbuttonReferenceAreaCircle.
function pushbuttonReferenceAreaCircle_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonReferenceAreaCircle (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

viS_getcircle;


% --- Executes on button press in pushbuttonTimeSeriesPlot.
function pushbuttonTimeSeriesPlot_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonTimeSeriesPlot (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

viS_getps_ts;


% --- Executes on button press in pushbuttonExportGISGE.
function pushbuttonExportGISGE_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonExportGISGE (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

eval('viSExport');


% --- Executes on button press in pushbutton3DVisualization.
function pushbutton3DVisualization_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton3DVisualization (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');   
end

viS_3DVisualization(str2double(get(vistamps.Setup.Handles.editDistance, 'String')));

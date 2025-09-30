function varargout = viSSetup(varargin)
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
                   'gui_OpeningFcn', @viSSetup_OpeningFcn, ...
                   'gui_OutputFcn',  @viSSetup_OutputFcn, ...
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


% --- Executes just before viSSetup is made visible.
function viSSetup_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to viSSetup (see VARARGIN)

% Choose default command line output for viSSetup
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes viSSetup wait for user response (see UIRESUME)
% uiwait(handles.figureSetup);

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

vistamps.Setup.Handles = handles;

imshow(imread('viS_back.png'),'Parent',vistamps.Setup.Handles.axesLogo);

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Outputs from this function are returned to the command line.
function varargout = viSSetup_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
varargout{1} = handles.output;



% --- Executes on button press in pushbuttonBrowse.
function pushbuttonBrowse_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonBrowse (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

folder = uigetdir;
if folder ~= 0
    set(vistamps.Setup.Handles.editProjectFolder, 'String', folder);
else
    return;
end


addpath(fullfile(pwd));

activeFolder = pwd;

if exist(fullfile(folder, 'viS_Setup.mat'), 'file')
    cd(folder);
    load viS_Setup orbitType scaleFactor Distance;
    if strcmp(orbitType, 'Descending')
        set(vistamps.Setup.Handles.radiobuttonDescending, 'Value', 1);
    else
        set(vistamps.Setup.Handles.radiobuttonAscending, 'Value', 1);
    end
	set(vistamps.Setup.Handles.editScaleFactor, 'String', scaleFactor);
    set(vistamps.Setup.Handles.editDistance, 'String', Distance);

    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);
    
    uipanelOrbitType_SelectionChangeFcn();
else
    set(vistamps.Setup.Handles.radiobuttonDescending, 'Value', 0);
    set(vistamps.Setup.Handles.radiobuttonAscending, 'Value', 0);
    
    set(vistamps.Setup.Handles.editScaleFactor, 'String', '1.0');
    set(vistamps.Setup.Handles.editDistance, 'String', '5.0');   
    
    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);
end

cd(activeFolder);



% --- Executes when selected object is changed in uipanelOrbitType.
function uipanelOrbitType_SelectionChangeFcn(hObject, eventdata, handles)
% hObject    handle to the selected object in uipanelOrbitType 
% eventdata  structure with the following fields (see UIBUTTONGROUP)
%	EventName: string 'SelectionChanged' (read only)
%	OldValue: handle of the previously selected object or empty if none was selected
%	NewValue: handle of the currently selected object
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if (get(vistamps.Setup.Handles.radiobuttonAscending, 'Value') == 1)
    vistamps.Setup.OrbitType = 'Ascending';
elseif (get(vistamps.Setup.Handles.radiobuttonDescending, 'Value') == 1)
    vistamps.Setup.OrbitType = 'Descending';
end
    
% Write appdata structered variable
setappdata(0,'vistamps', vistamps);


% --- Executes on button press in pushbuttonRunProject.
function pushbuttonRunProject_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonRunProject (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

if strcmp(get(vistamps.Setup.Handles.editProjectFolder, 'String'), '')
    errordlg('Please choose Project Folder!','ERROR');
    return;
end

if (~isfield(vistamps.Setup, 'OrbitType'))
    errordlg('Please choose Orbit Type!','ERROR');
    return;
end

if isempty(get(vistamps.Setup.Handles.editScaleFactor, 'String'))
    errordlg('Please define Scale Factor parameter!','ERROR');
    return;
end    

if isempty(get(vistamps.Setup.Handles.editDistance, 'String'))
    errordlg('Please define Distance parameter!','ERROR');
    return;
end 

set(vistamps.Handles.listboxOutput, 'String', []);
drawnow();

%Send message to viStaMPS output window
viS_message('--------------------------------------------------');
viS_message('INFO      : Creating new project...');

vistamps.Setup.ProjectFolder = get(vistamps.Setup.Handles.editProjectFolder, 'String');
cd(vistamps.Setup.ProjectFolder);


if ~exist('viS_Setup.mat', 'file')
    isNewProject = 1;
else
    load viS_Setup projectFolder orbitType scaleFactor Distance;
    if ~strcmp(projectFolder, vistamps.Setup.ProjectFolder) ||...
            ~strcmp(orbitType, vistamps.Setup.OrbitType) ||...
            ~strcmp(scaleFactor, get(vistamps.Setup.Handles.editScaleFactor, 'String')) ||...
            ~strcmp(Distance, get(vistamps.Setup.Handles.editDistance, 'String'))
        isNewProject = 1;
    else
        isNewProject = 0;
    end    
end


% Write appdata structered variable
setappdata(0,'vistamps', vistamps);


if isfield(vistamps, 'DataDisplay')
    if (isappdata(0, 'vistamps'))    
        % Read appdata structered variable
        vistamps=getappdata(0, 'vistamps');
    end
    if isfield(vistamps.DataDisplay, 'Handles')
        delete(vistamps.DataDisplay.Handles.figureDataDisplay);
    end
    vistamps = rmfield(vistamps, 'DataDisplay');
    % Write appdata structered variable
    setappdata(0,'vistamps', vistamps);
end

viS_Initialize(isNewProject,...
    str2double(get(vistamps.Setup.Handles.editScaleFactor, 'String')));

% Create Data Display window
eval('viSDataDisplay');

set(vistamps.Handles.pushbuttonDataDisplay, 'Enable', 'on');
set(vistamps.Handles.pushbutton3DVisualization, 'Enable', 'on');

if isNewProject == 1
    projectFolder = vistamps.Setup.ProjectFolder;
    orbitType   = vistamps.Setup.OrbitType;
    scaleFactor = get(vistamps.Setup.Handles.editScaleFactor, 'String');
    Distance    = get(vistamps.Setup.Handles.editDistance, 'String');
    save viS_Setup projectFolder orbitType scaleFactor Distance;
end

viS_message('INFO      : DONE!');


    
    

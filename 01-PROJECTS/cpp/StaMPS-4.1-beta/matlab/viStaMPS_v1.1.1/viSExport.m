function varargout = viSExport(varargin)
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
                   'gui_OpeningFcn', @viSExport_OpeningFcn, ...
                   'gui_OutputFcn',  @viSExport_OutputFcn, ...
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


% --- Executes just before viSExport is made visible.
function viSExport_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to viSExport (see VARARGIN)

% Choose default command line output for viSExport
handles.output = hObject;

% Update handles structure
guidata(hObject, handles);

% UIWAIT makes viSExport wait for user response (see UIRESUME)
% uiwait(handles.figureExport);


% Re-Locate GUI window
movegui(hObject,'center');

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

vistamps.Export.Handles = handles;

imshow(imread('viS_back.png'),'Parent',vistamps.Export.Handles.axesLogo);

% Write appdata structered variable
setappdata(0,'vistamps', vistamps);



% --- Outputs from this function are returned to the command line.
function varargout = viSExport_OutputFcn(hObject, eventdata, handles) 
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

[FileName, PathName] = uigetfile('*.txt','Select source file');

filename = fullfile(PathName, FileName);

if ~exist(filename, 'file')
    errordlg('Please choose a source file','ERROR');
    return;
else
    set(vistamps.Export.Handles.editSourceFile, 'String', filename);
end



% --- Executes during object creation, after setting all properties.
function sliderOpacity_CreateFcn(hObject, eventdata, handles)
% hObject    handle to sliderOpacity (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end

addlistener(hObject,'Value','PostSet',@textOpacity_UpdateFcn);



function textOpacity_UpdateFcn(hObject, eventdata, handles)
% hObject    handle to textStep (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

hSlider=vistamps.Export.Handles.sliderOpacity;
hText=vistamps.Export.Handles.textOpacity;
set(hText, 'String', round(get(hSlider, 'Value')));



% --- Executes during object creation, after setting all properties.
function sliderStep_CreateFcn(hObject, eventdata, handles)
% hObject    handle to sliderStep (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    empty - handles not created until after all CreateFcns called

% Hint: slider controls usually have a light gray background.
if isequal(get(hObject,'BackgroundColor'), get(0,'defaultUicontrolBackgroundColor'))
    set(hObject,'BackgroundColor',[.9 .9 .9]);
end

addlistener(hObject,'Value','PostSet',@textStep_UpdateFcn);



function textStep_UpdateFcn(hObject, eventdata, handles)
% hObject    handle to textStep (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

hSlider=vistamps.Export.Handles.sliderStep;
hText=vistamps.Export.Handles.textStep;
set(hText, 'String', round(get(hSlider, 'Value')));



% --- Executes on button press in pushbuttonExport.
function pushbuttonExport_Callback(hObject, eventdata, handles)
% hObject    handle to pushbuttonExport (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)


[FileName, PathName] = uiputfile('*.kml','Create export file');

if isequal(FileName,0)
   return;
end

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

filename = fullfile(PathName, FileName);
data    = get(vistamps.Export.Handles.editSourceFile, 'String');
if ~exist(data, 'file')
    errordlg('Please choose a source file','ERROR');
    return;
end

[FileName1, PathName1] = uigetfile('*.png','Select colorbar file');

filename1 = fullfile(PathName1, FileName1);


%Send message to viStaMPS output window
viS_message('--------------------------------------------------');
viS_message(['INFO      : Exporting data to ' filename]);

step    = round(str2double(get(vistamps.Export.Handles.textStep, 'String')));
opacity = str2double(get(vistamps.Export.Handles.textOpacity, 'String'))/100;

viS_ps_gescatter(filename, filename1, data, step, opacity);
viS_message('INFO      : DONE!');

close(vistamps.Export.Handles.figureExport);

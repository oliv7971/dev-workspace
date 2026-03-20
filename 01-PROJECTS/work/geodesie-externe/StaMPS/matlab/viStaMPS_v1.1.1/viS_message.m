function viS_message(msg)
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
%msg - Message to be displayed in output

if (isappdata(0, 'vistamps'))    
    % Read appdata structered variable
    vistamps=getappdata(0, 'vistamps');
end

old_content=cellstr(get(vistamps.Handles.listboxOutput,'String'));
new_content = [old_content;{msg}];
hListBox = vistamps.Handles.listboxOutput;
set(hListBox, 'String', new_content);
set(hListBox, 'ListboxTop', numel(get(hListBox,'string')));
drawnow();

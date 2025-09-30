// This file defines the dialog interface for user interactions in the application.
// It includes the layout and elements for batch presentation settings and parameters.

dialog BatchPresentationDialog
  :title "Batch Presentation Settings"
  :width 400
  :height 300
  :label "Configure your batch presentation settings"
  :items
  (
    (text "Select Presentation Files:")
    (file_dialog "presentationFiles" "Select Files" "All Files (*.*)|*.*" "C:\\")
    
    (text "Processing Options:")
    (checkbox "enableLogging" "Enable Logging" 1)
    (checkbox "overwriteExisting" "Overwrite Existing Presentations" 0)
    
    (text "Output Directory:")
    (edit_box "outputDirectory" "C:\\Output" 1)
    
    (button "startBatch" "Start Batch Processing")
    (button "cancel" "Cancel")
  )
end_dialog
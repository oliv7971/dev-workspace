;; Usage Examples for TCPOINT Placement Commands

;; Example 1: Automatic Placement of TCPOINT Blocks
;; This example demonstrates how to automatically place TCPOINT blocks
;; at the ends of all lines and polylines in the drawing.

(defun c:example-auto-placement ()
  (princ "\n=== Example: Automatic Placement of TCPOINT Blocks ===")
  (c:place-tcpoint)  ;; Call the main command for automatic placement
  (princ "\nTCPOINT blocks have been placed automatically."))

;; Example 2: Semi-Automatic Placement of TCPOINT Blocks
;; This example shows how to use the semi-automatic mode to select
;; specific lines and polylines for TCPOINT placement.

(defun c:example-semi-auto-placement ()
  (princ "\n=== Example: Semi-Automatic Placement of TCPOINT Blocks ===")
  (c:place-tcpoint)  ;; Call the main command for semi-automatic placement
  (princ "\nSelect the lines and polylines for TCPOINT placement."))

;; Example 3: Manual Placement of TCPOINT Blocks
;; This example illustrates how to manually place TCPOINT blocks
;; by specifying a reference center.

(defun c:example-manual-placement ()
  (princ "\n=== Example: Manual Placement of TCPOINT Blocks ===")
  (c:place-tcpoint)  ;; Call the main command for manual placement
  (princ "\nClick to define the reference center for TCPOINT placement."))

;; Example 4: Creating Intersection Centers and Placing TCPOINT Blocks
;; This example demonstrates how to create intersection centers from
;; axes and then place TCPOINT blocks at those centers.

(defun c:example-create-centers-and-place ()
  (princ "\n=== Example: Create Intersection Centers and Place TCPOINT Blocks ===")
  (c:create-centres)  ;; Create intersection centers
  (c:place-tcpoint)   ;; Call the main command to place TCPOINT blocks
  (princ "\nTCPOINT blocks have been placed at the intersection centers."))

(princ "\nUsage examples loaded. Use the commands to see the examples in action.")
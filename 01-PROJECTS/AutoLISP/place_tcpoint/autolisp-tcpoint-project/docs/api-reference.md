# API Reference for TCPOINT Placement Project

## Overview
This document serves as an API reference for the TCPOINT placement project. It outlines the functions and commands available in the project, providing details on their usage, parameters, and return values.

## Functions

### _num
```lisp
(defun _num (x)
```
**Description:** Converts various input types to a number, returning 0.0 for non-numeric inputs.

**Parameters:**
- `x`: The input value to convert.

**Returns:** A numeric value.

---

### _to-list
```lisp
(defun _to-list (v)
```
**Description:** Converts a VARIANT, SAFEARRAY, or LIST to a standard LIST.

**Parameters:**
- `v`: The input value to convert.

**Returns:** A LIST or nil if conversion fails.

---

### _is-pt2
```lisp
(defun _is-pt2 (p)
```
**Description:** Checks if the input is a 2D point (list of two numbers).

**Parameters:**
- `p`: The input to check.

**Returns:** T if valid, nil otherwise.

---

### _is-pt3
```lisp
(defun _is-pt3 (p)
```
**Description:** Checks if the input is a 3D point (list of three numbers).

**Parameters:**
- `p`: The input to check.

**Returns:** T if valid, nil otherwise.

---

### _safe-dist2d
```lisp
(defun _safe-dist2d (p q)
```
**Description:** Calculates the 2D distance between two points.

**Parameters:**
- `p`: The first point.
- `q`: The second point.

**Returns:** The distance as a float.

---

### _dist2d-pt-seg
```lisp
(defun _dist2d-pt-seg (c a b)
```
**Description:** Calculates the distance from a point to a line segment defined by two endpoints.

**Parameters:**
- `c`: The point.
- `a`: The first endpoint of the segment.
- `b`: The second endpoint of the segment.

**Returns:** The distance as a float.

---

### _ensure-layer
```lisp
(defun _ensure-layer (doc name)
```
**Description:** Ensures that a specified layer exists in the drawing.

**Parameters:**
- `doc`: The active document.
- `name`: The name of the layer to check/create.

**Returns:** The layer object.

---

### _add-blockref-dynamic
```lisp
(defun _add-blockref-dynamic (space name pt calque-ligne)
```
**Description:** Inserts a block reference into the drawing on a specified layer.

**Parameters:**
- `space`: The space where the block will be inserted.
- `name`: The name of the block.
- `pt`: The insertion point.
- `calque-ligne`: The layer name.

**Returns:** The block reference object.

---

## Commands

### c:place-tcpoint
```lisp
(defun c:place-tcpoint ()
```
**Description:** Main command for placing TCPOINT blocks at the ends of lines and polylines.

**Parameters:** None.

**Returns:** None.

---

### c:config-tcpoint
```lisp
(defun c:config-tcpoint ()
```
**Description:** Command to configure parameters for the TCPOINT placement.

**Parameters:** None.

**Returns:** None.

---

### c:test-centres
```lisp
(defun c:test-centres ()
```
**Description:** Command to test the detection of centers.

**Parameters:** None.

**Returns:** None.

---

### c:create-centres
```lisp
(defun c:create-centres ()
```
**Description:** Command to create intersection centers automatically.

**Parameters:** None.

**Returns:** None.

---

## Conclusion
This API reference provides a comprehensive overview of the functions and commands available in the TCPOINT placement project. For further details on usage, please refer to the user manual.
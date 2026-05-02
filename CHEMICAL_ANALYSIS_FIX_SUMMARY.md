# Chemical Analysis Fix - Zero Results Issue

## Problem
All chemical analysis results were showing **0.0000** for both Lignin and Pectin ratios.

## Root Cause Analysis

### Investigation
1. Ran diagnostic on background-removed images
2. Found that HSV Hue range was only 0-124 (no red in upper 160-180 range)
3. Discovered that:
   - **Pectin**: Detected 54,384 pixels at sensitivity 10, but ZERO at sensitivity 5
   - **Lignin**: No detection even at sensitivity 10 with original ranges

### The Issues
1. **Default sensitivity too low**: Sensitivity 5 was too strict
2. **Lignin color range too narrow**: Only checking pure red (0-20° and 160-180°)
3. **Actual staining colors**: 
   - Lignin appears as **pink/magenta (Hue 110-140°)** not pure red
   - Pectin burgundy only detected with wider ranges

## Solution Implemented

### 1. Increased Default Sensitivity
**Changed in `src/gradio_ui/config.py` and `app.py`:**
- Default lignin_sensitivity: 5 → **10**
- Default pectin_sensitivity: 5 → **10**

### 2. Expanded Lignin Color Detection
**Changed in `src/gradio_ui/backend/chemical_analysis.py`:**

**Before** (only pure red):
```python
# Red: 0-20 and 160-180
lower_red1 = [0, 30, 30]
upper_red1 = [10 + sensitivity * 2, 255, 255]
lower_red2 = [170 - sensitivity * 2, 30, 30]
upper_red2 = [180, 255, 255]
```

**After** (includes pink/magenta):
```python
# Red: 0-40 and 150-180
lower_red1 = [0, 20, 20]  # Lower thresholds
upper_red1 = [10 + sensitivity * 3, 255, 255]  # Wider range
lower_red2 = [170 - sensitivity * 2, 20, 20]
upper_red2 = [180, 255, 255]

# ADDED: Pink/Magenta: 110-150
lower_pink = [110, 20, 20]
upper_pink = [140 + sensitivity, 255, 255]

# Combine all three masks
lignin_mask = OR(mask_red1, mask_red2, mask_pink)
```

## Results After Fix

### Test on Sample Image: `20240630-20240644_STANDARDa_T24_20x_PG_EDF_nobg_*.png`

**Before:**
- Lignin: 0 pixels (0.0000 ratio)
- Pectin: 0 pixels (0.0000 ratio)

**After:**
- **Lignin: 193,033 pixels (25.9% ratio)** ✅
- **Pectin: 54,384 pixels (7.3% ratio)** ✅

## Technical Details

### HSV Color Ranges (at sensitivity 10)
**Lignin (PG Staining):**
- Pure Red (lower): Hue 0-40, Sat 20+, Val 20+
- Pure Red (upper): Hue 150-180, Sat 20+, Val 20+
- Pink/Magenta: Hue 110-150, Sat 20+, Val 20+

**Pectin (Ruthenium Red):**
- Burgundy/Purple: Hue 120-180, Sat 20+, Val 20+

### Why This Works
1. **PG staining** (lignin) often appears **pink or magenta** under microscopy, not pure red
2. **Lower S/V thresholds** (30→20) catch lighter/darker stains
3. **Higher default sensitivity** ensures detection out-of-the-box
4. **User can still adjust** sensitivity 1-10 in Settings tab

## Files Modified
1. `src/gradio_ui/config.py` - Changed default sensitivity 5→10
2. `app.py` - Changed UI default sensitivity 5→10
3. `src/gradio_ui/backend/chemical_analysis.py` - Added pink/magenta detection for lignin

## Impact
- ✅ Chemical analysis now produces real, measurable results
- ✅ Works out-of-the-box with default settings
- ✅ Still customizable for different staining protocols
- ✅ Matches actual microscopy stain colors

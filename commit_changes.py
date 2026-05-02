#!/usr/bin/env python3
"""Commit Phase 1 changes: Entry point rename and cleanup"""
import subprocess
import os

os.chdir('/Users/emmanuelkiprotich/USDA-Segmentation-S2')

print("="*70)
print("PHASE 1 - UI POLISH: ENTRY POINT RENAME")
print("="*70)

# Add all changes
print("\n📦 Staging all changes...")
result = subprocess.run(['git', 'add', '-A'], capture_output=True, text=True)
if result.returncode == 0:
    print("   ✅ Changes staged")
else:
    print(f"   ❌ Error: {result.stderr}")
    exit(1)

# Show what will be committed
print("\n" + "="*70)
print("📋 CHANGES TO BE COMMITTED:")
print("="*70)
result = subprocess.run(['git', 'status', '--short'], capture_output=True, text=True)
print(result.stdout)

# Show full status
print("\n" + "="*70)
print("📊 DETAILED STATUS:")
print("="*70)
result = subprocess.run(['git', 'status'], capture_output=True, text=True)
print(result.stdout)

# Commit
commit_message = """Phase 1 - UI Polish: Rename entry point and fix chemical analysis

Part 1: Entry Point Rename
- Renamed gradio_app.py → app.py for cleaner entry point
- Updated all documentation references (HANDOVER_GRADIO_UI_REPORT.md - 10 locations)
- Updated scripts: launch_ui.sh, check_setup.py, commit_ui_changes.sh, git_commit_ui.py
- Updated test files: test_gradio_imports.py, run_gradio_debug.py
- Cleaned up 18 temporary/redundant documentation files

Part 2: Chemical Analysis Fix (CRITICAL BUG FIX)
- Fixed zero-ratio bug in chemical analysis
- Increased default sensitivity from 5 to 10 (now detects staining properly)
- Expanded lignin detection to include pink/magenta colors (Hue 110-150)
- Lowered S/V thresholds from 30 to 20 for better detection
- Results: Lignin now detects 25.9%, Pectin 7.3% (was 0% for both)

Testing:
- Diagnostic tests confirm chemical analysis now works
- Sample image shows: Lignin 193k pixels (25.9%), Pectin 54k pixels (7.3%)
- All functionality preserved

Files modified:
- app.py (renamed + sensitivity defaults)
- src/gradio_ui/config.py (sensitivity defaults)
- src/gradio_ui/backend/chemical_analysis.py (expanded color ranges)

To run: python3 app.py"""

print("\n" + "="*70)
print("💾 COMMITTING TO ui-polish BRANCH:")
print("="*70)
result = subprocess.run(['git', 'commit', '-m', commit_message], capture_output=True, text=True)
print(result.stdout)
if result.stderr and 'nothing to commit' not in result.stderr.lower():
    print(f"STDERR: {result.stderr}")

if result.returncode == 0:
    print("\n" + "="*70)
    print("✅ PHASE 1 COMPLETE!")
    print("="*70)
    print("\n📝 Summary:")
    print("  - All changes committed to ui-polish branch")
    print("  - Entry point: app.py")
    print("  - Run command: python3 app.py")
    print("\n🧪 Next: Test the UI by running:")
    print("     python3 app.py")
else:
    print(f"\n❌ Commit failed with code {result.returncode}")

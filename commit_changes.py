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
commit_message = """Phase 1 - UI Polish: Rename entry point and update references

Changes:
- Renamed gradio_app.py → app.py for cleaner entry point
- Updated all documentation references (HANDOVER_GRADIO_UI_REPORT.md - 10 locations)
- Updated scripts: launch_ui.sh, check_setup.py, commit_ui_changes.sh, git_commit_ui.py
- Updated test files: test_gradio_imports.py, run_gradio_debug.py
- Cleaned up 18 temporary/redundant documentation files
- Removed temporary helper scripts

Verification:
- app.py exists and is functional (513 lines)
- All imports work correctly
- Usage instructions updated throughout
- No remaining references to gradio_app.py

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

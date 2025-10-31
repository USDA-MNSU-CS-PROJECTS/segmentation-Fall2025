from pathlib import Path

print(sum(1 for p in Path("src\data\yolo_train\images").glob("*") if p.is_file()))

import argparse
import os
import re
import glob

def get_args():
    parser = argparse.ArgumentParser(description="Audit and validate commands and paths in historical documentation.")
    parser.add_argument("--scan-only", action="store_true", help="Only scan and report without generating full diffs")
    parser.add_argument("--include", type=str, default="docs/plans/*.md,docs/reviews/*.md", help="Comma-separated glob patterns to include")
    parser.add_argument("--exclude", type=str, default="", help="Comma-separated glob patterns to exclude")
    parser.add_argument("--output-report", type=str, default="docs/reports/documentation_audit_report.md", help="Path to output the markdown report")
    return parser.parse_args()

def extract_paths_from_text(text):
    path_regex = r'((?:scripts|assets|configs|edge-vision-uav-landing|gimbal-video-stabilization-analyzer)/[a-zA-Z0-9_\-\./]+\.(?:py|yaml|csv|mp4|txt|json))'
    return re.findall(path_regex, text)

def check_path_exists(project_root, rel_path):
    return os.path.exists(os.path.join(project_root, rel_path))

def find_replacement(rel_path):
    if rel_path.startswith("scripts/"):
        return "edge-vision-uav-landing/" + rel_path
    if rel_path.startswith("tests/verify_video_assets.py"):
        return "edge-vision-uav-landing/tests/verify_video_assets.py"
    return None

def main():
    args = get_args()
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    
    includes = args.include.split(',')
    excludes = set(args.exclude.split(',')) if args.exclude else set()
    
    files_to_scan = set()
    for inc in includes:
        for f in glob.glob(os.path.join(project_root, inc.strip())):
            files_to_scan.add(f)
            
    for exc in excludes:
        for f in glob.glob(os.path.join(project_root, exc.strip())):
            if f in files_to_scan:
                files_to_scan.remove(f)

    broken_references = []
    
    for file_path in files_to_scan:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line_idx, line in enumerate(lines):
            paths = extract_paths_from_text(line)
            for p in paths:
                if not check_path_exists(project_root, p):
                    rep = find_replacement(p)
                    rep_exists = False
                    if rep:
                        rep_exists = check_path_exists(project_root, rep)
                    
                    broken_references.append({
                        'file': os.path.relpath(file_path, project_root),
                        'line': line_idx + 1,
                        'broken_path': p,
                        'suggested_replacement': rep if rep_exists else "N/A (Deleted or untracked)",
                        'context': line.strip()
                    })

    os.makedirs(os.path.dirname(os.path.join(project_root, args.output_report)), exist_ok=True)
    with open(os.path.join(project_root, args.output_report), 'w', encoding='utf-8') as rf:
        rf.write("# Documentation Command Audit Report\n\n")
        rf.write(f"Scanned {len(files_to_scan)} files.\n\n")
        rf.write("## Broken References & Migrations\n\n")
        
        if not broken_references:
            rf.write("No broken canonical paths found.\n")
        else:
            rf.write("| Document | Line | Broken Path | Suggested Migration |\n")
            rf.write("|---|---|---|---|\n")
            
            seen = set()
            for ref in broken_references:
                key = (ref['file'], ref['broken_path'])
                if key not in seen:
                    rf.write(f"| `{ref['file']}` | {ref['line']} | `{ref['broken_path']}` | `{ref['suggested_replacement']}` |\n")
                    seen.add(key)
                    
    print(f"[INFO] Audit complete. Found {len(broken_references)} broken references.")
    print(f"[INFO] Report written to {args.output_report}")

if __name__ == "__main__":
    main()

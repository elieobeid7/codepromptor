import os
import sys
import fnmatch
import argparse
from typing import Set


def load_gitignore_patterns(root: str) -> Set[str]:
    patterns = set()
    gitignore = os.path.join(root, ".gitignore")
    if os.path.isfile(gitignore):
        with open(gitignore, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    patterns.add(line)
    return patterns


def matches_pattern(path: str, patterns: Set[str]) -> bool:
    norm = path.replace(os.sep, "/")
    for pat in patterns:
        p = pat.replace(os.sep, "/")
        if p.endswith("/"):
            base = p[:-1]
            if norm == base or norm.startswith(base + "/"):
                return True
        if fnmatch.fnmatch(norm, p):
            return True
        for seg in norm.split("/"):
            if fnmatch.fnmatch(seg, p):
                return True
    return False


def print_tree(root: str, patterns: Set[str]) -> str:
    lines = ["/"]
    for cur_dir, dirs, files in os.walk(root):
        rel_dir = os.path.relpath(cur_dir, root)
        if rel_dir != "." and matches_pattern(rel_dir, patterns):
            dirs[:] = []
            continue
        entries = sorted(dirs + files, key=lambda x: (x in files, x.lower()))
        depth = 0 if rel_dir == "." else rel_dir.count(os.sep) + 1
        prefix = "    " * depth
        for name in entries:
            rel = os.path.join(rel_dir, name) if rel_dir != "." else name
            if matches_pattern(rel, patterns):
                continue
            suffix = "/" if os.path.isdir(os.path.join(cur_dir, name)) else ""
            lines.append(f"{prefix}{name}{suffix}")
    return "\n".join(lines)


def dump_contents(root: str, patterns: Set[str], out_file):
    for cur_dir, dirs, files in os.walk(root):
        rel_dir = os.path.relpath(cur_dir, root)
        if rel_dir != "." and matches_pattern(rel_dir, patterns):
            dirs[:] = []
            continue
        for fname in sorted(files):
            rel_path = os.path.join(rel_dir, fname)
            if matches_pattern(rel_path, patterns):
                continue
            out_file.write(f"File: {rel_path}\n")
            out_file.write("-" * 50 + "\n")
            try:
                with open(os.path.join(cur_dir, fname), "r", encoding="utf-8") as f:
                    content = f.read()
                    out_file.write(content)
                print(f"Added: {rel_path}")
            except Exception as e:
                out_file.write(f"[Error reading {rel_path}: {e}]\n")
            out_file.write("\n")


def main():
    parser = argparse.ArgumentParser(description="Dump directory structure and files.")
    parser.add_argument("root", help="Directory to scan.")
    parser.add_argument(
        "-e",
        "--exclude",
        help="Comma-separated glob patterns to exclude (e.g. readme.md,.gitignore,.css)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        help="Directory to write the resulting text file (defaults to prompts/<folder>)",
    )
    args = parser.parse_args()

    root = args.root
    if not os.path.isdir(root):
        print(f"Error: '{root}' is not a directory.")
        sys.exit(1)

    # Build exclusion patterns with defaults
    patterns: Set[str] = {
        ".git/",  # always skip git folder
        ".vscode/",  # skip VSCode settings
        "*.png",
        "*.jpg",
        "*.jpeg",
        "*.gif",
        "*.bmp",
        "*.svg",
        "*.mp4",
        "*.mp3",
        "*.wav",
        "*.avi",
        "*.mov",
        "*.mkv",
        "*.webp",
        "*.pdf",
        "*.ppt",
        "*.pptx",
        "*.doc",
        "*.docx",
        "*.xls",
        "*.xlsx",
        "*.csv",
    }
    patterns.update(load_gitignore_patterns(root))
    if args.exclude:
        extra = [p.strip() for p in args.exclude.split(",") if p.strip()]
        patterns.update(extra)

    # Determine output directory
    if args.output_dir:
        out_dir = args.output_dir
    else:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        out_dir = os.path.join(script_dir, "prompts")
    os.makedirs(out_dir, exist_ok=True)

    # Build output file path
    folder = os.path.basename(os.path.abspath(root))
    output_file = os.path.join(out_dir, f"{folder}.txt")

    with open(output_file, "w", encoding="utf-8") as out:
        out.write("Directory Structure:\n")
        out.write("====================\n")
        out.write(print_tree(root, patterns))
        out.write("\n\nFile Contents:\n")
        out.write("==============\n")
        dump_contents(root, patterns, out)

    print(f"Done! Output written to {output_file}")


if __name__ == "__main__":
    main()

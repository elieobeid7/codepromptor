import os
import sys
import fnmatch
import argparse
import re
from typing import Set, Optional


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


def count_matches(
    content: str, needle: str, ignore_case: bool, whole_word: bool
) -> int:
    if not needle:
        return 0
    flags = re.IGNORECASE if ignore_case else 0
    if whole_word:
        pattern = r"\b" + re.escape(needle) + r"\b"
    else:
        pattern = re.escape(needle)
    return len(re.findall(pattern, content, flags))


def dump_contents(
    root: str,
    patterns: Set[str],
    out_file,
    search: Optional[str] = None,
    ignore_case: bool = False,
    whole_word: bool = False,
    include_patterns: Optional[Set[str]] = None,
    exclude_files: Optional[Set[str]] = None,
):
    total_matches = 0
    files_with_matches = 0

    for cur_dir, dirs, files in os.walk(root):
        rel_dir = os.path.relpath(cur_dir, root)
        if rel_dir != "." and matches_pattern(rel_dir, patterns):
            dirs[:] = []
            continue
        for fname in sorted(files):
            rel_path = os.path.join(rel_dir, fname)
            if matches_pattern(rel_path, patterns):
                continue

            rel_norm = rel_path.replace(os.sep, "/")

            # Skip explicitly excluded files (relative paths)
            if exclude_files and rel_norm in exclude_files:
                continue

            # If include patterns are provided, only process files matching them
            if include_patterns:
                included = False
                for pat in include_patterns:
                    p = pat.replace(os.sep, "/")
                    if fnmatch.fnmatch(rel_norm, p) or fnmatch.fnmatch(fname, p):
                        included = True
                        break
                if not included:
                    continue

            file_path = os.path.join(cur_dir, fname)

            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except Exception as e:
                out_file.write(f"File: {rel_path}\n")
                out_file.write("-" * 50 + "\n")
                out_file.write(f"[Error reading {rel_path}: {e}]\n")
                out_file.write("\n")
                continue

            matches_in_file = 0
            if search:
                matches_in_file = count_matches(
                    content, search, ignore_case, whole_word
                )
                if matches_in_file == 0:
                    # Skip files that do not match the search criteria
                    continue
                total_matches += matches_in_file
                files_with_matches += 1

            out_file.write(f"File: {rel_path}\n")
            out_file.write("-" * 50 + "\n")
            out_file.write(content)
            out_file.write("\n")
            print(f"Added: {rel_path}")

    return total_matches, files_with_matches


def main():
    parser = argparse.ArgumentParser(description="Dump directory structure and files.")
    parser.add_argument("root", help="Directory to scan.")
    parser.add_argument(
        "-e",
        "--exclude",
        help="Comma-separated glob patterns to exclude (e.g. readme.md,.gitignore,.css)",
    )
    parser.add_argument(
        "--include",
        dest="include",
        help=(
            "Comma-separated glob patterns to include (e.g. *.ts,*.tsx). "
            "If provided, only files matching at least one of these patterns are processed."
        ),
    )
    parser.add_argument(
        "--exclude-files",
        dest="exclude_files",
        help=(
            "Comma-separated relative file paths to exclude (e.g. frontend/app/src/main.tsx)."
        ),
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        dest="output_dir",
        help="Directory to write the resulting text file (defaults to prompts/<folder>)",
    )
    parser.add_argument(
        "-s",
        "--search",
        dest="search",
        help=(
            "String to search for in file contents. If provided, only files containing "
            "matches are included in the output."
        ),
    )
    parser.add_argument(
        "--ignore-case",
        action="store_true",
        help="Ignore case when searching file contents.",
    )
    parser.add_argument(
        "--whole-word",
        action="store_true",
        help="Match whole words instead of substrings when searching.",
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

    # Include-only patterns (for file contents)
    include_patterns: Optional[Set[str]] = None
    if args.include:
        include_patterns = {p.strip() for p in args.include.split(",") if p.strip()}

    # Explicit file exclusions (relative to root)
    exclude_files_set: Optional[Set[str]] = None
    if args.exclude_files:
        exclude_files_set = set()
        for raw in args.exclude_files.split(","):
            path = raw.strip()
            if not path:
                continue
            if os.path.isabs(path):
                try:
                    rel = os.path.relpath(path, root)
                except ValueError:
                    # Different drive (on Windows) or unrelated path: skip
                    continue
            else:
                rel = path
            exclude_files_set.add(rel.replace(os.sep, "/"))

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
        total_matches, files_with_matches = dump_contents(
            root,
            patterns,
            out,
            search=args.search,
            ignore_case=args.ignore_case,
            whole_word=args.whole_word,
            include_patterns=include_patterns,
            exclude_files=exclude_files_set,
        )

    print(f"Done! Output written to {output_file}")
    if args.search:
        mode = "whole word" if args.whole_word else "substring"
        case = "ignore case" if args.ignore_case else "case sensitive"
        print(
            f"Search summary: '{args.search}' "
            f"({mode}, {case}) -> {total_matches} matches in {files_with_matches} files."
        )


if __name__ == "__main__":
    main()

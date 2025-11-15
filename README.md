# CodePromptor

A Python script inspired by [repo2file](https://github.com/artkulak/repo2file) to generate an LLM prompt text file from your code. Here's what it does:

- Recursively dump a directory tree.
- Collect and embed file contents into a single text file.
- Automatically skip `.git/`, `.vscode/`, and common media/document formats.
- Honor your `.gitignore` rules.
- Offer a single `--exclude` flag for any extra patterns.
- Optionally customize the output directory.

---

## Usage

```bash
python codepromptor.py <root> [options]
```

- (required): Path to the directory you want to scan.

### Flags and Options

| Flag                 | Alias | Description                                                                                                                                 |
| -------------------- | ----- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `-e`, `--exclude`    | —     | Comma‑separated glob patterns to exclude (e.g. `readme.md,.gitignore,.css`).                                                                |
| `-o`, `--output-dir` | —     | Directory where the resulting text file will be saved. Defaults to a `prompts/` folder next to script.                                      |
| `-s`, `--search`     | —     | String to search for inside file contents. If provided, ONLY files containing at least one match are included in the File Contents section. |
| `--ignore-case`      | —     | Make the search case‑insensitive (default is case‑sensitive).                                                                               |
| `--whole-word`       | —     | Match only whole words using Python's word boundary (`\b`) logic instead of plain substrings.                                               |
| `--include`          | —     | Comma‑separated glob patterns to include (e.g. `*.ts,*.tsx`). Only files matching at least one pattern are processed.                       |
| `--exclude-files`    | —     | Comma‑separated relative file paths to exclude (e.g. `frontend/app/src/main.tsx`).                                                          |

### Defaults

- **Always** skips the following:

  - `.git/` directory
  - `.vscode/` directory
  - File types: `png`, `jpg`, `jpeg`, `gif`, `bmp`, `svg`, `mp4`, `mp3`, `wav`, `avi`, `mov`, `mkv`, `webp`, `pdf`, `ppt`, `pptx`, `doc`, `docx`, `xls`, `xlsx`, `csv`

- Honors all patterns in `.gitignore` (if present).
- Prints each file as it’s added:

---

## Examples

1. **Basic scan** (uses defaults, output to `prompts/<folder>.txt`):

   ```bash
   python codepromptor.py /path/to/my-project
   ```

2. **Exclude specific files** (`README.md`, `.gitignore`, `package-lock.json`):

   ```bash
   python codepromptor.py ./my-app \
     -e readme.md,.gitignore,package-lock.json
   ```

3. **Custom output directory**:

   ```bash
   python codepromptor.py ./my-app \
     -o /tmp/dumps
   ```

4. **Combine exclude + custom output**:
5. **Search for a case‑sensitive substring** (`UserService`):

   ```bash
   python codepromptor.py ./my-app -s "UserService"
   ```

6. **Case‑insensitive substring search**:

   ```bash
   python codepromptor.py ./my-app -s "userservice" --ignore-case
   ```

7. **Case‑insensitive whole‑word search** (word boundary match):

   ```bash
   python codepromptor.py ./my-app -s "UserService" --ignore-case --whole-word
   ```

Example summary output for a search run:

```text
Done! Output written to .../prompts/my-app.txt
Search summary: 'UserService' (whole word, ignore case) -> 37 matches in 12 files.
```

If you omit `-s/--search`, the behavior is identical to the original version (all text files included that aren't excluded by patterns).

8. **Include only TypeScript sources**:

   ```bash
   python codepromptor.py ./my-app --include "*.ts,*.tsx"
   ```

9. **Exclude a specific file by relative path**:

   ```bash
   python codepromptor.py ./my-app --exclude-files "frontend/app/src/main.tsx"
   ```

10. **Combine include + search** (search only within TypeScript files):

```bash
python codepromptor.py ./my-app --include "*.ts,*.tsx" -s "UserService"
```

11. **Combine exclude-files + search** (ignore one noisy file):

```bash
python codepromptor.py ./my-app -s "UserService" --exclude-files "frontend/app/src/main.tsx"
```

---

## Search Mode Details

When you provide `-s/--search`:

1. The directory tree still lists all entries (except those excluded by patterns) so you retain full structural context.
2. The File Contents section ONLY includes files where the search string matched at least once.
3. Matching is performed after exclusion filtering (`--exclude`, `.gitignore`, built‑in skips).
4. If `--include` is supplied, only files matching at least one include pattern are considered for searching or dumping.
5. If `--exclude-files` is supplied, those specific relative paths are removed after pattern filtering but before searching.
6. `--ignore-case` toggles a case‑insensitive search; default is case‑sensitive.
7. `--whole-word` wraps the term with `\b` word boundaries. In Python, `\b` treats letters, digits, and underscore as word characters, so `UserService` won't match `UserServiceImpl` in whole‑word mode, but will match `UserService` followed by punctuation or whitespace.
8. The script reports two numbers at the end:
   - Total number of matches across all included files.
   - Number of distinct files containing at least one match.

These help you compare against IDE/editor search results.

Edge notes:

- Binary / media / large non‑text formats are already excluded by default patterns.
- If a file can't be read (e.g. encoding error), an error line is written for that file only when it would otherwise be included (for non‑search runs) or if it passes the search test (which effectively it can't, so unreadable files under search mode are skipped after logging the read error line).
- Whole‑word mode may treat underscores as part of words (`my_var` counts `my_var` as one word); plan searches accordingly.

  ```bash
  python codepromptor.py ../repo \
    -e '*.test.js',node_modules/ \
    -o /var/log/dir-dumps
  ```

---

## Output Structure

The script generates a single `.txt` file named after the scanned folder (e.g. **my-app.txt**), containing:

1. **Directory Structure**

   ```
   /
   ├── src/
   │   ├── index.js
   │   └── lib/
   └── README.md
   ```

2. **File Contents**

   ```
   File: src/index.js
   --------------------------------------------------
   // (file contents...)

   File: docs/overview.md
   --------------------------------------------------
   # Overview
   ...
   ```

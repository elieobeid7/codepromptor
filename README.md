# CodePromptor

A Python script inspired by [repo2file](https://github.com/artkulak/repo2file) to generate an LLM prompt text file from your code, here's what it does:

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

| Flag                 | Alias | Description                                                                                            |
| -------------------- | ----- | ------------------------------------------------------------------------------------------------------ |
| `-e`, `--exclude`    | —     | Comma‑separated glob patterns to exclude (e.g. `readme.md,.gitignore,.css`).                           |
| `-o`, `--output-dir` | —     | Directory where the resulting text file will be saved. Defaults to a `prompts/` folder next to script. |

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

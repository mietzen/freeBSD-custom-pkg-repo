import os
import datetime
from pathlib import Path
import argparse
import fnmatch

HEADER = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Directory Listing</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            padding: 10px;
            border: 1px solid #ddd;
            text-align: left;
        }
        th {
            background-color: #f4f4f4;
        }
        a {
            text-decoration: none;
            color: #007bff;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
"""

FOOTER = """</body>
</html>"""

initial_base_directory = None

def human_readable_size(size):
    # Convert size to human-readable format
    for unit in ['bytes', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024

def should_exclude(path, exclude_patterns, include_dot):
    # Exclude dot directories by default if include_dot is False
    if not include_dot and any(part.startswith('.') for part in Path(path).parts):
        return True

    for pattern in exclude_patterns:
        if fnmatch.fnmatch(path, pattern):
            return True
    return False

def generate_index(directory, exclude_patterns, include_dot):
    files = []
    dirs = []

    for entry in sorted(os.scandir(directory), key=lambda e: e.name):
        if should_exclude(entry.path, exclude_patterns, include_dot):
            continue
        if entry.is_dir():
            dirs.append(entry)
        elif entry.is_file():
            files.append(entry)

    index_path = Path(directory) / "index.html"
    with open(index_path, "w") as f:
        f.write(HEADER)
        f.write(f"<h1>Index of {directory}</h1>")

        f.write("<table>")
        f.write("<tr><th>Name</th><th>Size</th><th>Creation Date</th></tr>")

        if directory != initial_base_directory:
            f.write("<tr><td><a href='../index.html'>..</a></td><td>-</td><td>-</td></tr>")

        for d in dirs:
            f.write(f"<tr><td><a href='./{d.name}/index.html'>{d.name}/</a></td><td>-</td>")
            creation_time = datetime.datetime.fromtimestamp(d.stat().st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"<td>{creation_time}</td></tr>")

        for file in files:
            size = file.stat().st_size
            readable_size = human_readable_size(size)
            creation_time = datetime.datetime.fromtimestamp(file.stat().st_ctime).strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"<tr><td><a href='{file.name}'>{file.name}</a></td><td>{readable_size}</td><td>{creation_time}</td></tr>")

        f.write("</table>")
        f.write(FOOTER)

def traverse_and_generate(base_dir, exclude_patterns, include_dot):
    for root, dirs, files in os.walk(base_dir):
        if should_exclude(root, exclude_patterns, include_dot):
            continue
        generate_index(root, exclude_patterns, include_dot)

def main():
    global initial_base_directory

    parser = argparse.ArgumentParser(description="Generate index.html files for directories.")
    parser.add_argument("directory", type=str, help="The base directory to start from.")
    parser.add_argument("--exclude", action="append", default=[], help="Glob patterns to exclude (can be used multiple times).")
    parser.add_argument("--include-dot", action="store_true", help="Include directories starting with a dot (e.g., .git, .svn).")

    args = parser.parse_args()
    initial_base_directory = args.directory
    exclude_patterns = args.exclude
    include_dot = args.include_dot

    if not os.path.isdir(initial_base_directory):
        print(f"Error: {initial_base_directory} is not a valid directory.")
    else:
        traverse_and_generate(initial_base_directory, exclude_patterns, include_dot)
        print("Index files generated successfully.")

if __name__ == "__main__":
    main()

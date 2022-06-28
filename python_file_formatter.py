import argparse
import os
from glob import glob
from typing import Optional

import pyparsing
from yapf.yapflib.yapf_api import FormatCode


def format_file(in_file: str, out_file: Optional[str] = None, encoding: str = "utf-8",
                remove_comments: bool = False, style_config="facebook", out_file_suffix: str = "_formatted"):
    if not os.path.isfile(in_file) or not in_file.endswith(".py"):
        raise ValueError("'in_file' must be a Python file with extension '.py'")
    
    with open(in_file, encoding=encoding) as f:
        code = f.read()
    
    if remove_comments:
        comment_filter = pyparsing.python_style_comment.suppress()
        any_python_quoted_string = (
                pyparsing.QuotedString('"""', multiline=True)
                | pyparsing.QuotedString("'''", multiline=True)
                | pyparsing.QuotedString('"')
                | pyparsing.QuotedString("'")
        )
        comment_filter.ignore(any_python_quoted_string)
        code = comment_filter.transform_string(code)
    code, changed = FormatCode(code, style_config=style_config)
    
    if out_file is None:
        out_file = in_file[:-3] + out_file_suffix + ".py"  # -3 because of ".py"
    os.makedirs(os.path.dirname(out_file), exist_ok=True)
    with open(out_file, "w", encoding=encoding, newline="") as f:
        f.write(code)
    
    return changed


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in_file", type=str, required=True,
                        help="Input Python file to format. Can also be a directory in which case all Python files "
                             "('*.py') are collected recursively within this directory and all subdirectories")
    parser.add_argument("-o", "--out_file", type=str, default=None,
                        help="Formatted output Python file. If not specified, then the same filename as the input "
                             "file 'in_file' will be used but with provided suffix 'out_file_suffix'. The new file "
                             "will be stored in the same directory where 'in_file' is located. If 'in_file' is a "
                             "directory, this the same filename as every collected Python file is used. If 'in_file' "
                             "is a directory, 'out_file' can be specified but must also be a directory. The formatted "
                             "Python files will then be stores in this directory (keeping the subdirectory structure "
                             "of the collected input Python files). In any case, missing directories are created.")
    parser.add_argument("-e", "--encoding", type=str, default="utf-8",
                        help="Encoding to use for all input and output files. Default: 'utf-8'.")
    parser.add_argument("-s", "--out_file_suffix", type=str, default="_formatted",
                        help="The suffix to append to the 'in_file' filename in case 'out_file' was not specified. "
                             "If 'out_file' was specified, this argument is ignored. Default: '_formatted'.")
    parser.add_argument("-sc", "--style_config", type=str, default="facebook",
                        help="YAPF style config to use for the main Python formatting. Default: 'facebook'.")
    parser.add_argument("-r", "--remove_comments", default=False, action=argparse.BooleanOptionalAction,
                        help="If specified, comments are removed.")
    args = parser.parse_args()
    if os.path.isdir(args.in_file):
        files = glob(os.path.join(args.in_file, "**", "*.py"), recursive=True)
        common_path = os.path.commonpath(files) + os.sep
        for file in files:
            format_file(
                in_file=file,
                out_file=None if args.out_file is None else os.path.join(args.out_file, file[len(common_path):]),
                encoding=args.encoding,
                remove_comments=args.remove_comments,
                style_config=args.style_config,
                out_file_suffix=args.out_file_suffix
            )
    else:
        format_file(
            in_file=args.in_file,
            out_file=args.out_file,
            encoding=args.encoding,
            remove_comments=args.remove_comments,
            style_config=args.style_config,
            out_file_suffix=args.out_file_suffix
        )

# license-grep

Figures out and collates licenses for a Python/JavaScript/Dart/Rust environment.

# Requirements

Python 3.7+.

# Example usage

Dump JSON and two styles of Markdown describing a combined Python + JavaScript environment:

```
python3 -m license_grep \
  --py my_virtual_env/python3.7/site-packages \
  --js my_js_project_root \
  --write-json license-info.json \
  --write-table table.md \
  --write-grouped-markdown grouped.md \
  --dump-unknown-licenses
```

Also see `--help` :)

# Dart/Flutter support

Very beta, very ad-hoc.

Install the `PyYAML` package, then try

```
python3 -m license_grep \
  --dart ./my-app-root \ 
  --dart-pub-cache ./my-flutter-or-dart-root/.pub-cache/ \
  --dump-unknown-licenses
```

# Rust support

Very beta, very ad-hoc.

Install the `toml` package, then try

```
python3 -m license_grep \
  --rust ./my-rust-app \
  --dump-unknown-licenses
```

If things don't work out, ensure you can build your app in the first place and that ``CARGO_HOME`` is set.

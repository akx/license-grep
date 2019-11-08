.PHONY: license_grep/licenses.json

license_grep/licenses.json:
	curl -o $@ "https://raw.githubusercontent.com/spdx/license-list-data/master/json/licenses.json"

# run script
run:
    python bgg_ranks.py

# lint and format
lint:
    trunk check

# check code and deps for vulns
deps:
    snyk test

#!/usr/bin/env bash

# Requires having installed flypush w/ its setup script first, from:
# https://github.com/tom-f-oconnell/flypush
# TODO automatically install that + the multi_tracker dep

sudo -u flypush psql -f setup.sql

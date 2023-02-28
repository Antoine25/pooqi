#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import numpy as np
    import ConfigParser
except ImportError:
    import configparser as ConfigParser

BIT = 16
MAX_VAL = 2**BIT / 2


def read_config_file(config_file_path):
    """Return the dictionnary corresponding to the config_file_path."""
    dic = {}
    for section in list_config_file_sections(config_file_path):
        dic[section] = read_config_file_section(config_file_path, section)

    return dic


def read_config_file_section(config_file_path, section):
    """
        Use ConfigParser for reading a configuration file.
        Returns an dictionnary with keys/values of the section.
    """

    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.read(config_file_path)

    if config.has_section(section):
        configSection = config._sections[section]
        # configSection.pop("__name__")

        return {key: value.split() for key, value in configSection.items()}
    else:
        return {}


def list_config_file_sections(config_file_path):
    """List all the sections of the file <config_file_path>"""
    config = ConfigParser.ConfigParser()
    config.optionxform = str
    config.read(config_file_path)

    return config.sections()

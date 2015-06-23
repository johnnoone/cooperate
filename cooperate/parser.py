import argparse


class CLIParser(argparse.ArgumentParser):

    def convert_arg_line_to_args(self, arg_line):
        if arg_line.startswith('-'):
            return arg_line.split(' ', 1)

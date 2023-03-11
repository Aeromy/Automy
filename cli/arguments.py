import argparse


class Arguments:
    @staticmethod
    def debug():
        parser = argparse.ArgumentParser(description="Debug mode.")
        parser.add_argument(
            "-d", "--debug", action="store_true", help="enable debug mode"
        )
        args = parser.parse_args()
        return args.debug

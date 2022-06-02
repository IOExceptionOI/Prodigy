import logging

from prodigy.util.color import Style


def log_setup(name: str, level, file: str = 'test.log') -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    fhandler = logging.FileHandler(filename=file, mode='a')
    fhandler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(fhandler)
    return logger


# Print iterations progress
def print_progress_bar(iteration,
                       total,
                       prefix='Progress:',
                       suffix='completed',
                       decimals=1,
                       length=100,
                       fill='█',
                       print_end=""):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(
        100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(
        f'{Style.YELLOW if (iteration / float(total)) < 1 else Style.GREEN}\r{prefix} |{bar}| {percent}% {suffix}{Style.RESET}',
        end=print_end,
        flush=True)
    # Print New Line on Complete
    if iteration == total:
        print()

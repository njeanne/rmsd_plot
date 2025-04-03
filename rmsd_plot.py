#! /usr/bin/env python3

"""
Created on 03 Apr. 2025
"""

import argparse
import logging
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy
import pandas as pd
import seaborn as sns


__author__ = "Nicolas JEANNE"
__copyright__ = "GNU General Public License"
__email__ = "jeanne.n@chu-toulouse.fr"
__version__ = "1.0.0"


def create_log(path, level):
    """Create the log as a text file and as a stream.

    :param path: the path of the log.
    :type path: str
    :param level: the level og the log.
    :type level: str
    :return: the logging:
    :rtype: logging
    """

    log_level_dict = {"DEBUG": logging.DEBUG,
                      "INFO": logging.INFO,
                      "WARNING": logging.WARNING,
                      "ERROR": logging.ERROR,
                      "CRITICAL": logging.CRITICAL}

    if level is None:
        log_level = log_level_dict["INFO"]
    else:
        log_level = log_level_dict[args.log_level]

    if os.path.exists(path):
        os.remove(path)

    logging.basicConfig(format="%(asctime)s %(levelname)s:\t%(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S",
                        level=log_level,
                        handlers=[logging.FileHandler(path), logging.StreamHandler()])
    return logging


def restricted_extension(out_file):
    """Inspect if the outputfile has a correct extension.

    :param out_file: the output file path.
    :type out_file: str
    :raises ArgumentTypeError: no correct extension
    :return: the output file path.
    :rtype: str
    """
    valid_extensions = [".jpg", ".jpeg", ".pdf", ".pgf", ".png", ".ps", ".raw", ".rgba", ".svg", ".svgz", ".tif",
                        ".tiff"]
    extension = os.path.splitext(out_file)[1]
    if not extension in valid_extensions:
        raise argparse.ArgumentTypeError(f"{out_file} has not a valid extension. Valid extensions are: "
                                         f"{', '.join(valid_extensions)}.")
    return out_file


def extract_data(dat_file):
    """
    Extract the dat file data.

    :param dat_file: the dat file path.
    :type dat_file: str
    :return: the data frame of the dat.
    :rtype: pandas.DataFrame
    """
    # Read data from the file and handle missing values as NaN
    data = numpy.genfromtxt(dat_file, missing_values="NA", dtype=float, comments=None)
    # Filter out rows containing NaN (i.e., 'NA' values)
    data = data[~numpy.isnan(data).any(axis=1)]
    # Extracting columns from the data
    df = pd.DataFrame({"frames": list(data[:, 0].astype(int)), "RMSD": list(data[:, 1])})
    logging.info(f"{len(df)} frames RMSD values extracted for the RMSD plot.")
    return df


def plot_rmsd(src, out_path, title, color):
    """
    Create the RMSD line plot.

    :param src: the data source.
    :type src: pd.Dataframe
    :param out_path: the plot output path.
    :type out_path: str
    :param title: the plot title.
    :type title: str
    :param color: the line color.
    :type color: str
    """
    # set the seaborn plots theme and size
    sns.set_theme()
    rcParams["figure.figsize"] = 15, 12
    try:
        rms_line_ax = sns.lineplot(data=src, x="frames", y="RMSD", color=color)
    except ValueError as exc:
        colors = dict(matplotlib.colors.BASE_COLORS, **matplotlib.colors.CSS4_COLORS)
        # Sort colors by hue, saturation, value and name.
        by_hsv = sorted((tuple(matplotlib.colors.rgb_to_hsv(matplotlib.colors.to_rgba(color)[:3])), name)
                        for name, color in colors.items())
        available_colors = ""
        for available_color in [name for hsv, name in by_hsv]:
            available_colors = f"{available_colors}\n{available_color}"
        logging.error(f"\"{args.color}\" is not a valid color. Choose a color in:{available_colors}")
        sys.exit(1)
    plot = rms_line_ax.get_figure()
    plt.suptitle(title, fontsize="large", fontweight="bold")
    plt.xlabel("frames", fontweight="bold")
    plt.ylabel("RMSD (\u212B)", fontweight="bold")
    plot.savefig(out_path)
    logging.info(f"RMSD plot created: {os.path.abspath(out_path)}")


if __name__ == "__main__":
    descr = f"""
    {os.path.basename(__file__)} v. {__version__}

    Created by {__author__}.
    Contact: {__email__}
    {__copyright__}

    Distributed on an "AS IS" basis without warranties or conditions of any kind, either express or
    implied.

    Plot the Root Mean Square Deviation (RMSD) values from a '.dat' file for a molecule.
    """
    parser = argparse.ArgumentParser(description=descr, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("-o", "--out", required=True, type=restricted_extension,
                        help="path to the output file. The allowed extensions are:"
                             "'jpg': 'Joint Photographic Experts Group', 'jpeg': 'Joint Photographic Experts Group', "
                             "'pdf': 'Portable Document Format', 'pgf': 'PGF code for LaTeX', "
                             "'png': 'Portable Network Graphics', 'ps': 'Postscript', 'raw': 'Raw RGBA bitmap', "
                             "'rgba': 'Raw RGBA bitmap', 'svg': 'Scalable Vector Graphics', "
                             "'svgz': 'Scalable Vector Graphics', 'tif': 'Tagged Image File Format', "
                             "'tiff': 'Tagged Image File Format'.")
    parser.add_argument("-t", "--title", required=True, type=str, help="the plot title")
    parser.add_argument("-c", "--color", required=False, type=str, default="blue",
                        help="the line plot color")
    parser.add_argument("-l", "--log", required=False, type=str,
                        help="the path for the log file. If this option is  skipped, the log file is created in the "
                              "output directory.")
    parser.add_argument("--log-level", required=False, type=str,
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="set the log level. If this option is skipped, the log level is INFO.")
    parser.add_argument("-v", "--version", action="version", version=__version__)
    parser.add_argument("input", type=str, help="the .dat file.")
    args = parser.parse_args()

    out_dir = os.path.dirname(args.out)
    os.makedirs(out_dir, exist_ok=True)

    # create the logger
    if args.log:
        log_path = args.log
    else:
        log_path = os.path.join(out_dir, f"{os.path.splitext(os.path.basename(__file__))[0]}.log")
    create_log(log_path, args.log_level)

    logging.info(f"version: {__version__}")
    logging.info(f"CMD: {' '.join(sys.argv)}")

    df_from_dat_file = extract_data(args.input)
    plot_rmsd(df_from_dat_file, args.out, args.title, args.color)
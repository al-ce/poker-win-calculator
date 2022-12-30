from setuptools import setup

INSTALL_REQUIRES = ["getkey"]

setup(
    name="poker-win-calculator",
    description="CLI tool for calculating the winner of a Texas Holdem round",
    url="https://github.com/al-ce/poker-win-calculator",
    install_requires=INSTALL_REQUIRES,
    # packages=["poker_win_calculator"],
    python_requires=">=3.6",
    # setup.py is in the root directory of the project, but cli.py is in the
    # poker_win_calculator directory. So we need to specify the directory
    # containing cli.py
    entry_points={"console_scripts": ["poker-win-calculator=poker_win_calculator.cli:main"]},
    version="0.1.0",
)

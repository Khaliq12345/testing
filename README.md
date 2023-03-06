
# Project Description

This project is a Python script that uses Playwright, a Python library that automates web browsers, to interact with and place bets on an online betting website. The script prompts the user to input the required information for the bet they want to place, and then uses Playwright to navigate the website, find the appropriate betting category and outcome, and click the bet.

## Requirements

To use this script, you will need to have Python 3 installed on your machine, as well as the following Python libraries:
`playwright`
`time`

## Installation

1. Clone or download the project files to your local machine.

2. Install the required libraries by running the following command in your terminal:

```python
pip install playwright
```

## Usage

1. Open your terminal and navigate to the directory where the project files are located.

2. Run the following command to start the script:

```
python main.py
```

3. Follow the prompts in the terminal to input the required information for the bet you want to place.

Example of input:

INPUT: money line; 1

ODD: 1.53

4. Wait for the script to finish executing. The script will take a screenshot of the webpage once the bet is placed.

Note: Make sure that the input is in lower case expect those like (1X).

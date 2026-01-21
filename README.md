# Terminal Fireworks
A simple python script which displays fireworks in your terminal.

## Showcase
![Fireworks Terminal Gif](images/fireworks.gif)

![Fireworks Terminal Gif](images/kitty.gif)

## Features
- Fireworks follow real projectile motion
- Customisable physics parameters (see [Command Line Options](#command-line-options))
- Responsive to terminal resizing (sort of)
- Uses existing terminal color config

## Requirements
- Python 3.6 or higher
- A terminal which supports the curses module

## Installation
This is simplest to install using [pipx](https://github.com/pypa/pipx).

From remote:
`pipx install git+https://github.com/chloem3ow/terminal-fireworks.git`

Or clone and install from local:
`pipx install .`

## Usage
Run `fireworks` in your terminal.

### Controls
- `]` Increase fireworks per second
- `[` Decrease fireworks per second
- `🡑` Increase firework launch power
- `🡓` Decrease firework launch power
- `u`, `U` Toggle UI (mostly for development)
- `q`, `Q`, `ctrl-C` Quit

### Command Line Options
  - `-h`, `--help` show help message and exit
  - `--framerate` Frames per second (default: 30)
  - `--gravity` Gravity strength (default: 0.2)
  - `--decay-time` Particle decay time in seconds (default: 0.4)
  - `--explosion-height` Distance from top of screen where fireworks explode, as a fraction of the screen (default: 0.3)
  - `--gap` Gap between fireworks in seconds (default: 1.5)
  - `--fragments` Min and max explosion fragments (default: 8 20)
  - `--force` Min and max explosion speed (default: 2.5 3.5)
  - `--speed` Firework launch speed (default: 1.0)
  - `--delta-v` Sets how much the rocket can accelerate (default: 3.0)

  ## Licence
  Distributed under MIT licence. See [LISENCE](LISENCE) for more details.

  ## Acknowledgements
  Inspired largely by [terminal-rain](https://github.com/rmaake1/terminal-rain-lightning).

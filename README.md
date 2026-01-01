# Tritonide

Tritonide is a Python-driven research project focused on browser automation and the integration of chess engines with web interfaces. It functions by synchronizing the Stockfish engine with a live Chess.com session, allowing for real-time position analysis and automated move execution. This tool was developed solely for educational purposes to explore the intersection of Selenium-based web scraping and UCI (Universal Chess Interface) protocols.

### Engine Configuration

The application does not include the Stockfish binary due to its size and platform-specific requirements. You must provide the engine yourself for the system to function.

1.  Navigate to the official Stockfish download page: https://stockfishchess.org/download/
2.  Download the version compatible with your operating system (e.g., AVX2 or BMI2 for Windows).
3.  Extract the downloaded archive and locate the executable file.
4.  Rename this file to exactly `stockfish.exe`.
5.  Place `stockfish.exe` in the root directory of the Tritonide folder, alongside `main.py`.

Without this file, the EngineManager module will fail to initialize and the application will throw a terminal error.

### Technical Overview

The system operates through a modular architecture. The browser module utilizes Selenium to monitor the Chess.com DOM. It specifically watches for changes in the chess-board element, where it parses the CSS classes of individual pieces to reconstruct the board state into a FEN (Forsyth-Edwards Notation) string.

Once the state is captured, the engine module processes the FEN. Users can manipulate parameters such as calculation depth and skill levels through the interface. The interaction between the engine's suggested move and the browser is handled by simulated mouse events, which include randomized delay intervals to mimic human input latency.

### Installation and Setup

Ensure Python 3.10 or higher is installed on your system. You will also need an updated version of Google Chrome.

Install the necessary dependencies via pip:

`pip install selenium stockfish customtkinter`

Launch the application by running:

`python main.py`

### Important Considerations and Disclaimer

This software is a technical demonstration. Using automation tools on public chess servers is a violation of their terms of service and will likely result in a permanent account ban. The developers of Tritonide do not condone cheating in competitive environments. 

This project is intended for developers interested in automation and chess enthusiasts who wish to study engine evaluations in a controlled, private environment. Use this code responsibly and at your own risk. The author assumes no liability for any misuse of this software or for any actions taken by third-party platforms in response to its use.
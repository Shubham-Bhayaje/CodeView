# Python Code Visualizer

A visual tool for step-by-step Python code execution with real-time variable tracking and memory visualization.

![Python Code Visualizer](https://via.placeholder.com/800x450?text=Python+Code+Visualizer)

## Overview

Python Code Visualizer is an educational tool that helps users understand how Python code executes line by line. It provides a visual representation of code execution, variable states, output, and memory usage, making it ideal for beginners learning Python or for educators demonstrating programming concepts.

## Features

- **Interactive Code Editor**: Write or paste Python code directly in the application
- **Line-by-Line Execution**: Step through code execution one line at a time
- **Variable Tracking**: See all variables and their values as they change during execution
- **Output Display**: View print statements and other outputs in real-time
- **Memory Visualization**: Understand how variables are stored in memory
- **Execution Controls**: Play, pause, step forward, and reset execution
- **Adjustable Speed**: Control the pace of automatic execution

## Installation

### Prerequisites

- Python 3.7 or higher
- Flet package (`pip install flet`)

### Setup

1. Clone this repository or download the source code:
   ```
   git clone https://github.com/yourusername/python-code-visualizer.git
   cd python-code-visualizer
   ```

2. Install required dependencies:
   ```
   pip install flet
   ```

3. Run the application:
   ```
   python code_visualizer.py
   ```

## Usage

1. Enter or paste your Python code in the editor on the left side
2. Click "Start Visualization" to initialize the visualization
3. Use the control buttons to manipulate execution:
   - ▶️ Play: Run the code automatically at the set speed
   - ⏸️ Pause: Pause automatic execution
   - ⏭️ Step Forward: Execute one line at a time
   - 🔄 Reset: Reset the visualization to the beginning
4. Adjust the execution speed using the slider
5. Watch the real-time updates in the visualization panels:
   - Code Execution: Shows the current line being executed
   - Variables: Displays all variables and their current values
   - Output: Shows any printed output from your code
   - Memory Visualization: Provides details about memory usage

## Example

Try this sample code:

```python
# Sample code to visualize
x = 5
y = 10
total = x + y

for i in range(3):
    total += i
    print(f"Loop {i}: total = {total}")

print("Final total:", total)
```

## Limitations

- The current version supports basic Python syntax and features
- Complex operations like multi-threading, file I/O, or GUI operations may not visualize correctly
- Some advanced Python features might cause unexpected behavior

## Troubleshooting

If you encounter the error `AttributeError: 'Page' object has no attribute 'add_to_control_queue'`:

1. This is likely due to using a newer version of Flet that has changed its threading API
2. Update the code in `schedule_next_step` method to use `page.update()` instead:

```python
def schedule_next_step(self):
    # Use page.update() with a callback function instead of add_to_control_queue
    self.page.update(lambda: self.continue_execution())
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

- Built using [Flet](https://flet.dev/) - a framework for building interactive multi-platform applications in Python
- Inspired by Python Tutor and other educational programming tools

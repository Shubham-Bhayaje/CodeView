import flet as ft
from flet import Colors, Icons  # Updated to capital versions
import ast
import sys
import time
import io
import traceback
from threading import Timer
from contextlib import redirect_stdout
from typing import Dict, Any, List


class CodeVisualizer:
    def __init__(self, page: ft.Page):
        self.page = page
        self.setup_app()
        self.variables: Dict[str, Any] = {}
        self.current_line = 0
        self.code_lines = []
        self.execution_speed = 1.0
        self.is_playing = False
        self.output_buffer = io.StringIO()
        self.execution_namespace = {}
        self.line_mapping = []  # Maps AST node line numbers to code line indices
        self.execution_timer = None

    def setup_app(self):
        self.page.title = "Python Code Visualizer"
        self.page.window_width = 1200
        self.page.window_height = 800
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20

        # Code input area
        self.code_input = ft.TextField(
            multiline=True,
            min_lines=10,
            max_lines=10,
            expand=True,
            value="""# Sample code to visualize
x = 5
y = 10
total = x + y
i=0
for i in range(3):
    total += i
    print(f"Loop {i}: total = {total}")

print("Final total:", total)""",
            border_color=Colors.BLUE_400,
            text_style=ft.TextStyle(font_family="Consolas")
        )

        # Visualization displays
        self.code_display = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.variable_display = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.output_display = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
        self.memory_display = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)

        # Control buttons
        self.controls = ft.Row(
            controls=[
                ft.IconButton(Icons.PLAY_ARROW, on_click=self.play_execution,
                            tooltip="Play", icon_color=Colors.GREEN),
                ft.IconButton(Icons.PAUSE, on_click=self.pause_execution,
                            tooltip="Pause", icon_color=Colors.BLUE),
                ft.IconButton(Icons.SKIP_NEXT, on_click=self.step_forward,
                            tooltip="Step Forward", icon_color=Colors.PURPLE),
                ft.IconButton(Icons.REPLAY, on_click=self.reset_visualization,
                            tooltip="Reset", icon_color=Colors.RED),
                ft.Slider(min=0.1, max=3, divisions=29, value=1.0,
                         label="{value}x", on_change=self.change_speed,
                         width=200, tooltip="Execution Speed")
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )

        # Create the layout with all components visible at once
        self.visualization_panel = ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Container(
                            content=self.code_display,
                            expand=2,
                            padding=10,
                            border=ft.border.all(1, Colors.GREY_300)),
                        ft.Container(
                            content=self.variable_display,
                            expand=1,
                            padding=10,
                            border=ft.border.all(1, Colors.GREY_300))
                    ],
                    expand=True
                ),
                ft.Row(
                    controls=[
                        ft.Container(
                            content=self.output_display,
                            expand=1,
                            padding=10,
                            border=ft.border.all(1, Colors.GREY_300)),
                        ft.Container(
                            content=self.memory_display,
                            expand=1,
                            padding=10,
                            border=ft.border.all(1, Colors.GREY_300))
                    ],
                    expand=True
                )
            ],
            expand=True
        )

        # Main layout
        self.page.add(
            ft.Column(
                controls=[
                    ft.Text("Python Code Visualizer", 
                           size=24, weight=ft.FontWeight.BOLD),
                    ft.Row(
                        controls=[
                            ft.Column(
                                controls=[
                                    ft.Text("Enter Python Code:", 
                                           weight=ft.FontWeight.BOLD),
                                    self.code_input,
                                    ft.ElevatedButton(
                                        "Start Visualization",
                                        on_click=self.start_visualization,
                                        icon=Icons.PLAY_CIRCLE_FILL_OUTLINED,
                                        style=ft.ButtonStyle(
                                            bgcolor=Colors.BLUE_400,
                                            color=Colors.WHITE
                                        )
                                    )
                                ],
                                expand=2,
                                spacing=10
                            ),
                            ft.Column(
                                controls=[
                                    self.controls,
                                    self.visualization_panel
                                ],
                                expand=3,
                                spacing=10
                            )
                        ],
                        expand=True,
                        spacing=20
                    )
                ],
                expand=True,
                spacing=20
            )
        )

    def start_visualization(self, e):
        try:
            self.code_lines = self.code_input.value.split('\n')
            self.execution_namespace = {}
            self.current_line = 0
            self.clear_displays()
            
            # Parse the code
            self.ast_tree = ast.parse(self.code_input.value)
            
            # Create instrumented code for execution
            self.instrumented_code = self.instrument_code()
            
            # Reset state
            self.variables = {}
            self.update_displays()
            self.page.update()
        except Exception as ex:
            self.show_error(f"Syntax Error: {str(ex)}")

    def instrument_code(self):
        """Prepare the code for line-by-line execution by adding instrumentation"""
        # For simplicity in this example, we'll use a basic line-by-line approach
        # A more robust solution would use AST transformation
        instrumented_lines = []
        for i, line in enumerate(self.code_lines):
            # Skip empty lines and comments
            if not line.strip() or line.strip().startswith('#'):
                instrumented_lines.append(line)
            else:
                # Add proper indentation
                indent = len(line) - len(line.lstrip())
                indent_str = ' ' * indent
                instrumented_lines.append(line)
        
        return '\n'.join(instrumented_lines)

    def play_execution(self, e):
        if self.execution_timer:
            self.execution_timer.cancel()
            self.execution_timer = None
            
        self.is_playing = True
        self.continue_execution()

    def continue_execution(self):
        if not self.is_playing or self.current_line >= len(self.code_lines):
            self.is_playing = False
            return
            
        self.step_forward(None)
        
        if self.is_playing and self.current_line < len(self.code_lines):
            # Schedule the next execution step
            delay = 1.0 / self.execution_speed
            self.execution_timer = Timer(delay, self.schedule_next_step)
            self.execution_timer.daemon = True
            self.execution_timer.start()
    
    def schedule_next_step(self):
        # This function will be called by the Timer thread
        # We need to use Flet's current threading approach
        self.page.add(ft.Text("", visible=False))  # Add a dummy control to force update
        self.page.update()
        self.continue_execution()

    def pause_execution(self, e):
        self.is_playing = False
        if self.execution_timer:
            self.execution_timer.cancel()
            self.execution_timer = None
        self.page.update()

    def step_forward(self, e):
        if self.current_line >= len(self.code_lines):
            return

        try:
            # Get the current line
            line = self.code_lines[self.current_line].strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                self.current_line += 1
                self.update_displays()
                self.page.update()
                return
            
            # Execute the current line
            output_capture = io.StringIO()
            with redirect_stdout(output_capture):
                try:
                    # First try to execute as an expression to get a result
                    try:
                        expr_ast = ast.parse(line, mode='eval')
                        result = eval(compile(expr_ast, '<string>', 'eval'), globals(), self.execution_namespace)
                        # Store result if it's an assignment
                        if '=' in line and not line.strip().startswith('if') and not line.strip().startswith('for'):
                            var_name = line.split('=')[0].strip()
                            self.execution_namespace[var_name] = result
                    except SyntaxError:
                        # If it's not an expression, execute as a statement
                        stmt_ast = ast.parse(line, mode='exec')
                        exec(compile(stmt_ast, '<string>', 'exec'), globals(), self.execution_namespace)
                except Exception as exec_error:
                    # For control statements like if/for, try to execute the whole block
                    # This is a simplified approach - a real solution would need proper AST parsing
                    if line.rstrip().endswith(':'):
                        # Find the indented block
                        block_lines = [line]
                        indent_level = len(self.code_lines[self.current_line]) - len(line.lstrip())
                        i = self.current_line + 1
                        while i < len(self.code_lines):
                            next_line = self.code_lines[i]
                            if not next_line.strip():  # Skip empty lines
                                block_lines.append(next_line)
                                i += 1
                                continue
                            next_indent = len(next_line) - len(next_line.lstrip())
                            if next_indent <= indent_level:
                                break
                            block_lines.append(next_line)
                            i += 1
                        
                        # Execute the block
                        block_code = '\n'.join(block_lines)
                        block_ast = ast.parse(block_code, mode='exec')
                        exec(compile(block_ast, '<string>', 'exec'), globals(), self.execution_namespace)
                        
                        # Move to the end of the block
                        self.current_line = i - 1
                    else:
                        # Re-raise if it's not a control structure
                        raise exec_error
            
            # Capture output if any
            output = output_capture.getvalue()
            if output:
                self.output_display.controls.append(
                    ft.Text(output.rstrip(), 
                          selectable=True, 
                          font_family="Consolas")
                )
            
            # Update variables
            self.variables = dict(self.execution_namespace)
            
            # Move to next line
            self.current_line += 1
            self.update_displays()
            self.page.update()
            
        except Exception as e:
            trace = traceback.format_exc()
            self.show_error(f"Runtime Error: {str(e)}\n\n{trace}")
            self.is_playing = False
            if self.execution_timer:
                self.execution_timer.cancel()
                self.execution_timer = None

    def reset_visualization(self, e):
        self.is_playing = False
        if self.execution_timer:
            self.execution_timer.cancel()
            self.execution_timer = None
        self.start_visualization(None)

    def change_speed(self, e):
        self.execution_speed = e.control.value
        self.page.update()

    def clear_displays(self):
        self.code_display.controls.clear()
        self.variable_display.controls.clear()
        self.output_display.controls.clear()
        self.memory_display.controls.clear()

    def update_displays(self):
        self.update_code_display()
        self.update_variable_display()
        self.update_memory_display()

    def update_code_display(self):
        self.code_display.controls.clear()
        self.code_display.controls.append(
            ft.Text("Code Execution", 
                  weight=ft.FontWeight.BOLD, 
                  size=16)
        )
        
        for i, line in enumerate(self.code_lines):
            self.code_display.controls.append(
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text(f"{i+1}:", width=40, 
                                  color=Colors.GREY_600,
                                  text_align=ft.TextAlign.RIGHT),
                            ft.Text(
                                line,
                                color=Colors.RED if i == self.current_line else Colors.BLACK,
                                selectable=True,
                                bgcolor=Colors.YELLOW_100 if i == self.current_line else None,
                                font_family="Consolas"
                            )
                        ]
                    ),
                    padding=5,
                    border_radius=4
                )
            )

    def update_variable_display(self):
        self.variable_display.controls.clear()
        self.variable_display.controls.append(
            ft.Text("Variables", 
                  weight=ft.FontWeight.BOLD,
                  size=16)
        )
        
        if not self.variables:
            self.variable_display.controls.append(
                ft.Text("No variables defined yet", italic=True))
            return

        # Filter out built-ins and modules
        filtered_vars = {k: v for k, v in self.variables.items() 
                       if not k.startswith('__') and not isinstance(v, type(sys))}
        
        for name, value in filtered_vars.items():
            try:
                value_type = type(value).__name__
                # Limit length of repr for large objects
                value_repr = repr(value)
                if len(value_repr) > 100:
                    value_repr = value_repr[:97] + "..."
                
                self.variable_display.controls.append(
                    ft.Container(
                        content=ft.Row(
                            controls=[
                                ft.Text(f"{name}:", 
                                      weight=ft.FontWeight.BOLD, 
                                      width=100),
                                ft.Text(value_repr, 
                                      color=Colors.BLUE_700,
                                      selectable=True,
                                      expand=True),
                                ft.Text(f"({value_type})", 
                                      color=Colors.GREY_600)
                            ],
                            spacing=10
                        ),
                        padding=5,
                        bgcolor=Colors.GREY_100,
                        border_radius=4,
                        margin=ft.margin.only(bottom=5)
                    )
                )
            except Exception as e:
                # Handle any errors displaying variable values
                self.variable_display.controls.append(
                    ft.Text(f"Error displaying {name}: {str(e)}", 
                          color=Colors.RED)
                )

    def update_memory_display(self):
        self.memory_display.controls.clear()
        self.memory_display.controls.append(
            ft.Text("Memory Visualization", 
                  weight=ft.FontWeight.BOLD,
                  size=16)
        )
        
        if not self.variables:
            self.memory_display.controls.append(
                ft.Text("No variables in memory yet", italic=True))
            return
            
        # Filter out built-ins and modules
        filtered_vars = {k: v for k, v in self.variables.items() 
                       if not k.startswith('__') and not isinstance(v, type(sys))}
        
        # Simple memory visualization
        for name, value in filtered_vars.items():
            try:
                size = sys.getsizeof(value)
                value_repr = repr(value)
                if len(value_repr) > 100:
                    value_repr = value_repr[:97] + "..."
                    
                self.memory_display.controls.append(
                    ft.Container(
                        content=ft.Column(
                            controls=[
                                ft.Text(f"Variable: {name}", 
                                      weight=ft.FontWeight.BOLD),
                                ft.Text(f"Type: {type(value).__name__}"),
                                ft.Text(f"Value: {value_repr}", 
                                      color=Colors.BLUE_700),
                                ft.Text(f"Size: {size} bytes",
                                      color=Colors.GREY_600)
                            ],
                            spacing=5
                        ),
                        padding=10,
                        bgcolor=Colors.GREY_50,
                        border_radius=6,
                        margin=ft.margin.only(bottom=10)
                    )
                )
            except Exception as e:
                # Handle any errors displaying memory info
                self.memory_display.controls.append(
                    ft.Text(f"Error displaying memory for {name}: {str(e)}", 
                          color=Colors.RED)
                )

    def show_error(self, message):
        dlg = ft.AlertDialog(
            title=ft.Text("Error", color=Colors.RED),
            content=ft.Text(message),
            actions=[
                ft.TextButton("OK", on_click=self.close_dialog)
            ]
        )
        self.page.dialog = dlg
        dlg.open = True
        self.page.update()

    def close_dialog(self, e):
        self.page.dialog.open = False
        self.page.update()

def main(page: ft.Page):
    visualizer = CodeVisualizer(page)

ft.app(target=main)
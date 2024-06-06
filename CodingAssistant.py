from tkinter import *
from tkinter import ttk
from tkinter import scrolledtext  # Import scrolledtext for scrollable text area
import google.generativeai as genai
from dotenv import load_dotenv
import os

def run_code(chat):
    try:
        user_input = input_label.get()  # Get the user input from the Entry widget
        user_line = f"User: {user_input}"
    
        # Generate content using the Gemini model
        response = chat.send_message(user_input)
        
        # Extract text content from the response object
        model_response = ''.join(part.text for part in response.parts)
        
        print(model_response)
        
        # Update chat history
        conversation_history.append(
            {
                'role': "user",
                "parts": [{ 'text': user_line}]
            }
        )
        conversation_history.append(
            {
                'role': "model",
                "parts": [{ 'text': model_response}]
            }
        )
        
        # Display only the assistant's latest response
        response_text.config(state='normal')
        response_text.delete('1.0', END)

        # Insert any remaining text after the last code snippet
        response_text.insert(END, model_response, 'normal')
        
        response_text.config(state='disabled')
        response_text.tag_config('code', foreground='green', font=('Courier New', 8), background='lightgray')
        
    except Exception as e:
        response_text.config(state='normal')
        response_text.delete('1.0', END)
        response_text.insert(END, f"Error: {e}")
        response_text.config(state='disabled')

def main():
    global input_label
    global response_text
    # Construct the prompt with the user input
    prompt = (
        f"You will be given either some code or a question on how to code something. "
        f"Respond with the following rules:\n"
        f"Rules when given code with question(s):\n"
        f"1) In your response, provide changes to the code that assist the user in solving their problem.\n"
        f"2) In your response, whenever you generate specifically a new line of code that is not part of "
        f"the original code, surround the line with ```.\n"
        f"Rules when given just a question:\n"
        f"1) In your response, provide assistance and code to help the user with their question.\n"
        f"2) Surround generated code with ```.\n\n"
        f"No matter what, provide an explanation of your response. \n"
        f"The following is the user input:\n"
    )
    global conversation_history
    
    conversation_history = [{
        'role': "user",
        'parts': [{ 'text': prompt }]
    }]
    
    load_dotenv()
    gemini_api_key = os.environ.get('GEMINI_API_KEY')
    
    if not gemini_api_key:
        response_text.config(state='normal')
        response_text.delete('1.0', END)
        response_text.insert(END, "Error: Gemini API key not found.")
        response_text.config(state='disabled')
        return
    
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    chat = model.start_chat(history=conversation_history)
    
    root = Tk()
    root.title("Code Assistant")
    root.attributes('-topmost', True)
    
    # Calculate screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    # Desired padding around the mainframe
    padding = 20
    
    # Calculate the actual usable height of the window
    title_bar_height = root.winfo_height() - root.winfo_toplevel().winfo_height()
    window_height = screen_height - title_bar_height - padding
    
    # Set the size of the window and position it in the bottom right corner
    window_width = 300
    x_position = screen_width - window_width
    y_position = screen_height - window_height - title_bar_height - padding
    root.geometry(f'{window_width}x{window_height}+{x_position}+{y_position}')
    
    style = ttk.Style()
    
    # Define styles
    style.configure('TFrame', background='#7ba4b0')
    style.configure('TLabel', background='#7ba4b0', font=('Helvetica', 12))
    style.configure('TButton', background='#007bff', foreground='#0a0a0a', font=('Helvetica', 12, 'bold'))
    style.configure('TEntry', font=('Helvetica', 12))
    
    # Configure button hover style
    style.map('TButton', background=[('active', '#0056b3')])
    
    # Configure 'code' tag for green text
    style.configure('code', foreground='green')

    mainframe = ttk.Frame(root, padding=f"{padding} {padding} {padding} {padding}", style="TFrame")
    mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
    
    # Configure resizing behavior
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    mainframe.columnconfigure(2, weight=1)  # Column 2 (where widgets are placed) expands with the window
    mainframe.rowconfigure(4, weight=1)     # Row 4 (where response_text is) expands with the window
    
    # Add minsize to prevent excessive shrinking
    root.minsize(window_width, window_height)
    
    ttk.Label(mainframe, text="Enter code or question:", style="TLabel").grid(column=2, row=1, sticky=W)
    input_label = ttk.Entry(mainframe, style="TEntry")
    input_label.grid(column=2, row=2, sticky=(W, E))
    ttk.Button(mainframe, text="Generate assistance", command=lambda: run_code(chat), style="TButton").grid(column=2, row=3, sticky=(W, E))
    
    # Add the response scrolledtext
    response_text = scrolledtext.ScrolledText(mainframe, wrap=WORD, width=50, height=10, font=('Helvetica', 8))
    response_text.grid(column=2, row=4, sticky=(N, S, E, W))
    response_text.insert(END, "Response will appear here.")
    response_text.config(state='disabled')  # Make the text widget read-only
    
    for child in mainframe.winfo_children(): 
        child.grid_configure(padx=10, pady=5)
        
    root.mainloop()

    
if __name__ == "__main__":
    main()
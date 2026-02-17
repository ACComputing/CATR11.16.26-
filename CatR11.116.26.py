#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  CATSEEK R1 (Distill V3.2 14B) — Catseek-Style GUI Simulator         ║
║  Recreates the chat.deepseek.com experience in Tkinter.              ║
║  Features: DeepThink (Chain of Thought), Dark Mode, Streaming Text   ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import tkinter as tk
from tkinter import ttk, font
import threading
import time
import random
import sys

# ════════════════════ THEME CONFIGURATION ════════════════════
class Theme:
    # CatseekR1 Web Colors
    BG_MAIN     = "#2b2d31"       # Main chat background
    BG_SIDEBAR  = "#1e1f22"       # Sidebar background
    BG_INPUT    = "#383a40"       # Input field background
    BG_THINK    = "#1e1f22"       # Thinking block background (slightly darker)
    
    FG_PRIMARY  = "#dbdee1"       # Main text
    FG_SEC      = "#949ba4"       # Secondary text / metadata
    FG_DIM      = "#6d6f78"       # Placeholder / faint text
    
    ACCENT      = "#4d6bfe"       # CatseekR1 Blue
    ACCENT_HOVR = "#5d7bff"       # Lighter Blue
    
    BORDER      = "#383a40"       # Border lines
    SCROLLBAR   = "#1e1f22"       # Scrollbar track
    
    FONT_CODE   = ("Consolas", 10) if sys.platform == "win32" else ("Menlo", 10)
    FONT_UI     = ("Segoe UI", 10) if sys.platform == "win32" else ("SF Pro Text", 11)
    FONT_BOLD   = ("Segoe UI", 10, "bold") if sys.platform == "win32" else ("SF Pro Text", 11, "bold")
    FONT_HEADER = ("Segoe UI", 14, "bold") if sys.platform == "win32" else ("SF Pro Display", 14, "bold")

# ════════════════════ MOCK LOGIC (THE BRAIN) ════════════════════
class CatBrain:
    """Simulates the R1 reasoning process with Realistic Logic."""
    
    def generate_response(self, prompt, use_deepthink=True):
        """
        Generator that yields:
        - ('think', text) : Updates to the thinking process
        - ('think_done', time) : Thinking finished
        - ('text', char) : Streaming response characters
        """
        # Dynamic Thoughts based on context
        short_prompt = (prompt[:25] + '...') if len(prompt) > 25 else prompt
        thoughts = [
            f"Ingesting user query: '{short_prompt}'",
            "Tokenizing input stream...",
            "Analyzing semantic intent...",
            "Retrieving relevant context from vector database...",
            "Cross-referencing with V3.2 knowledge graph...",
            "Identifying potential ambiguities...",
            "Formulating chain-of-thought path...",
            "Refining output for readability...",
            "Final safety check complete."
        ]
        
        # 1. DeepThink Phase
        if use_deepthink:
            start = time.time()
            
            yield ('think', "Thinking Process:\n")
            
            # Simulate variable thinking steps
            steps_to_show = random.randint(4, len(thoughts))
            selected_thoughts = thoughts[:steps_to_show]
            
            for i, thought in enumerate(selected_thoughts):
                time.sleep(random.uniform(0.3, 0.7))
                yield ('think', f"{i+1}. {thought}\n")
            
            total_time = f"{time.time() - start:.1f}s"
            yield ('think_done', total_time)
        
        # 2. Response Generation Phase
        # Generate a "Real Context" simulated response
        response = (
            f"### Response to Query\n"
            f"**Input Analysis:**\n"
            f"The system has received the input \"{prompt}\". Based on the Distill V3.2 architecture (14B), "
            f"this query implies a request for information retrieval or generation.\n\n"
            f"**Simulated Output:**\n"
            f"As this is a GUI simulator for the Catseek R1 interface, I do not have live access to the 14B parameter weights. "
            f"However, a real inference pass would likely structure the response as follows:\n\n"
            f"1.  **Deconstruction**: Breaking down '{short_prompt}' into key components.\n"
            f"2.  **Synthesis**: Combining knowledge vectors to address the specific intent.\n"
            f"3.  **Refinement**: Formatting the data for optimal readability.\n\n"
            f"**Technical Metadata:**\n"
            f"- **Tokens Processed**: {len(prompt.split()) + 42}\n"
            f"- **Latency**: Low (Local Simulation)\n"
            f"- **Model State**: Ready"
        )
        
        # Special handling for code requests to look like real code generation
        if "code" in prompt.lower() or "python" in prompt.lower() or "function" in prompt.lower():
            clean_func_name = "".join(x for x in prompt.split()[0] if x.isalnum()) or "example"
            response = (
                f"Here is a Python implementation based on your request regarding '{short_prompt}':\n\n"
                f"```python\n"
                f"def {clean_func_name.lower()}_logic(data):\n"
                f"    \"\"\"\n"
                f"    Implements logic for: {prompt}\n"
                f"    \"\"\"\n"
                f"    # Initialize V3.2 Context\n"
                f"    result = []\n"
                f"    \n"
                f"    # Process data stream\n"
                f"    for item in data:\n"
                f"        if validate(item):\n"
                f"            result.append(process_core(item))\n"
                f"            \n"
                f"    return result\n"
                f"```\n\n"
                f"This code utilizes an optimized loop structure consistent with best practices."
            )

        for char in response:
            time.sleep(0.01) # Fast typing speed
            yield ('text', char)

# ════════════════════ GUI APPLICATION ════════════════════
class CatseekR1App:
    def __init__(self, root):
        self.root = root
        self.root.title("Catseek R1 (Distill V3.2 14B)")
        self.root.geometry("1100x800")
        self.root.configure(bg=Theme.BG_MAIN)
        self.brain = CatBrain()
        self.is_generating = False
        self.deepthink_active = tk.BooleanVar(value=True)

        self.setup_styles()
        self.build_layout()
        self.show_welcome_screen()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Scrollbar styling
        self.style.configure("Vertical.TScrollbar", 
                           background=Theme.BG_MAIN, 
                           troughcolor=Theme.BG_MAIN,
                           bordercolor=Theme.BG_MAIN, 
                           arrowcolor=Theme.FG_SEC)
        
        # Invisible frame styling
        self.style.configure("TFrame", background=Theme.BG_MAIN)

    def build_layout(self):
        # --- Sidebar ---
        self.sidebar = tk.Frame(self.root, bg=Theme.BG_SIDEBAR, width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # New Chat Button
        btn_new = tk.Label(self.sidebar, text="+ New Chat", bg=Theme.BG_MAIN, fg=Theme.FG_PRIMARY, 
                         font=Theme.FONT_UI, cursor="hand2", pady=10)
        btn_new.pack(fill="x", padx=15, pady=20)
        btn_new.bind("<Button-1>", lambda e: self.reset_chat())
        
        # History List
        lbl_today = tk.Label(self.sidebar, text="Today", bg=Theme.BG_SIDEBAR, fg=Theme.FG_DIM, 
                           font=("Segoe UI", 9), anchor="w")
        lbl_today.pack(fill="x", padx=15, pady=(10,5))
        
        for item in ["Python Optimization", "Tuna Price Analysis", "World Domination Plans"]:
            l = tk.Label(self.sidebar, text=item, bg=Theme.BG_SIDEBAR, fg=Theme.FG_SEC, 
                       font=Theme.FONT_UI, anchor="w", cursor="hand2", padx=15, pady=5)
            l.pack(fill="x")
            l.bind("<Enter>", lambda e, w=l: w.configure(bg="#2b2d31"))
            l.bind("<Leave>", lambda e, w=l: w.configure(bg=Theme.BG_SIDEBAR))

        # User Profile (Bottom)
        profile = tk.Frame(self.sidebar, bg=Theme.BG_SIDEBAR, height=60)
        profile.pack(side="bottom", fill="x", padx=15, pady=15)
        tk.Label(profile, text="🐱", font=("Arial", 16), bg=Theme.BG_SIDEBAR).pack(side="left")
        tk.Label(profile, text=" User", font=Theme.FONT_BOLD, bg=Theme.BG_SIDEBAR, fg=Theme.FG_PRIMARY).pack(side="left", padx=5)

        # --- Main Chat Area ---
        self.main_area = tk.Frame(self.root, bg=Theme.BG_MAIN)
        self.main_area.pack(side="right", fill="both", expand=True)

        # Header (Model Selector)
        header = tk.Frame(self.main_area, bg=Theme.BG_MAIN, height=50)
        header.pack(fill="x", pady=10)
        tk.Label(header, text="Catseek R1 (Distill V3.2 14B)", bg=Theme.BG_MAIN, fg=Theme.FG_PRIMARY, 
               font=Theme.FONT_BOLD).pack()

        # Chat Canvas (Scrollable)
        self.canvas = tk.Canvas(self.main_area, bg=Theme.BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_area, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Theme.BG_MAIN)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Responsive width
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        self.canvas.pack(side="top", fill="both", expand=True, padx=0)
        self.scrollbar.pack(side="right", fill="y")
        
        # --- Input Area (Floating) ---
        input_container = tk.Frame(self.main_area, bg=Theme.BG_MAIN, pady=20)
        input_container.pack(side="bottom", fill="x")
        
        # Input Box Style
        self.input_frame = tk.Frame(input_container, bg=Theme.BG_INPUT, padx=1, pady=1)
        self.input_frame.pack(fill="x", padx=100) # Centered with margins
        
        # Text Entry
        self.txt_input = tk.Text(self.input_frame, height=3, bg=Theme.BG_INPUT, fg=Theme.FG_PRIMARY, 
                               font=Theme.FONT_UI, relief="flat", insertbackground="white", wrap="word")
        self.txt_input.pack(fill="x", padx=10, pady=(10, 0))
        self.txt_input.bind("<Return>", self.handle_enter)
        self.txt_input.focus_set()

        # Toolbar (DeepThink, Search, Send)
        toolbar = tk.Frame(self.input_frame, bg=Theme.BG_INPUT, height=40)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        # DeepThink Toggle
        self.btn_deepthink = tk.Label(toolbar, text="🧠 DeepThink (R1)", fg=Theme.ACCENT, bg=Theme.BG_INPUT, 
                                    font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.btn_deepthink.pack(side="left", padx=10)
        self.btn_deepthink.bind("<Button-1>", self.toggle_deepthink)
        
        # Search (Visual only)
        tk.Label(toolbar, text="🌐 Search", fg=Theme.FG_DIM, bg=Theme.BG_INPUT, 
               font=("Segoe UI", 9, "bold")).pack(side="left", padx=10)

        # Send Button
        self.btn_send = tk.Label(toolbar, text="➤", bg=Theme.FG_DIM, fg="white", font=("Arial", 12),
                               width=4, height=1, cursor="hand2")
        self.btn_send.pack(side="right", padx=5)
        self.btn_send.bind("<Button-1>", lambda e: self.submit_query())

        tk.Label(input_container, text="Catseek R1 can make mistakes. Please verify important info.", 
               bg=Theme.BG_MAIN, fg=Theme.FG_DIM, font=("Segoe UI", 8)).pack(pady=(5,0))

    def on_canvas_configure(self, event):
        self.canvas.itemconfig(self.window_id, width=event.width)

    def toggle_deepthink(self, event):
        curr = self.deepthink_active.get()
        self.deepthink_active.set(not curr)
        color = Theme.ACCENT if not curr else Theme.FG_DIM
        self.btn_deepthink.configure(fg=color)

    def show_welcome_screen(self):
        self.clear_chat()
        
        wel_frame = tk.Frame(self.scrollable_frame, bg=Theme.BG_MAIN, pady=50)
        wel_frame.pack(fill="x", expand=True)
        
        tk.Label(wel_frame, text="🐱", font=("Arial", 64), bg=Theme.BG_MAIN).pack()
        tk.Label(wel_frame, text="Hi, I'm Catseek R1", font=Theme.FONT_HEADER, bg=Theme.BG_MAIN, fg=Theme.FG_PRIMARY).pack(pady=10)
        tk.Label(wel_frame, text="What can I help you with today?", font=Theme.FONT_UI, bg=Theme.BG_MAIN, fg=Theme.FG_SEC).pack()

        # Prompt Suggestions
        grid = tk.Frame(wel_frame, bg=Theme.BG_MAIN)
        grid.pack(pady=30)
        
        prompts = ["Explain Quantum Mechanics", "Write a Snake Game", "Analyze financial data"]
        for p in prompts:
            btn = tk.Label(grid, text=p, bg=Theme.BG_SIDEBAR, fg=Theme.FG_SEC, width=25, height=2, cursor="hand2")
            btn.pack(pady=5)
            btn.bind("<Button-1>", lambda e, t=p: self.prefill_input(t))
            
        self.is_welcome = True

    def prefill_input(self, text):
        self.txt_input.delete("1.0", tk.END)
        self.txt_input.insert("1.0", text)

    def clear_chat(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

    def reset_chat(self):
        self.clear_chat()
        self.show_welcome_screen()

    def handle_enter(self, event):
        if not event.state & 0x0001: # Shift key check
            self.submit_query()
            return "break" # Prevent newline

    def submit_query(self):
        if self.is_generating: return
        
        prompt = self.txt_input.get("1.0", tk.END).strip()
        if not prompt: return
        
        if getattr(self, 'is_welcome', False):
            self.clear_chat()
            self.is_welcome = False

        self.txt_input.delete("1.0", tk.END)
        self.btn_send.config(bg=Theme.ACCENT)
        
        # 1. Add User Message
        self.add_message("User", prompt)
        
        # 2. Add Bot Placeholder
        self.is_generating = True
        threading.Thread(target=self.generate_response_thread, args=(prompt,), daemon=True).start()

    def add_message(self, role, text):
        container = tk.Frame(self.scrollable_frame, bg=Theme.BG_MAIN, padx=100, pady=10)
        container.pack(fill="x")
        
        icon = "👤" if role == "User" else "🐱"
        tk.Label(container, text=icon, font=("Arial", 18), bg=Theme.BG_MAIN, fg=Theme.FG_PRIMARY).pack(side="left", anchor="n")
        
        content = tk.Frame(container, bg=Theme.BG_MAIN)
        content.pack(side="left", fill="x", expand=True, padx=15)
        
        tk.Label(content, text=role, font=("Segoe UI", 10, "bold"), bg=Theme.BG_MAIN, fg=Theme.FG_PRIMARY).pack(anchor="w")
        
        msg_lbl = tk.Label(content, text=text, font=Theme.FONT_UI, bg=Theme.BG_MAIN, fg=Theme.FG_PRIMARY, 
                         justify="left", anchor="w", wraplength=650)
        msg_lbl.pack(anchor="w", pady=(2,0))
        
        return content # Return content frame to add thinking/streaming later

    def generate_response_thread(self, prompt):
        # Create empty bot message structure
        time.sleep(0.2)
        
        # Use root.after to safely manipulate GUI from thread
        msg_container = []
        def create_container():
            c = self.add_message("Catseek R1", "")
            msg_container.append(c)
        self.root.after(0, create_container)
        
        # Wait for container creation
        while not msg_container: time.sleep(0.01)
        parent_frame = msg_container[0]
        
        # --- Thinking UI Block ---
        think_vars = {'label': None, 'content': None, 'text': ""}
        
        if self.deepthink_active.get():
            def setup_think_ui():
                # Grey box container
                box = tk.Frame(parent_frame, bg=Theme.BG_THINK, padx=10, pady=5)
                box.pack(fill="x", anchor="w", pady=(5, 10))
                
                # Header
                header = tk.Frame(box, bg=Theme.BG_THINK)
                header.pack(fill="x")
                tk.Label(header, text="Thought Process", font=("Segoe UI", 9, "bold"), 
                       bg=Theme.BG_THINK, fg=Theme.FG_SEC).pack(side="left")
                
                # Content (Initially visible)
                content_lbl = tk.Label(box, text="", font=Theme.FONT_CODE, bg=Theme.BG_THINK, 
                                     fg=Theme.FG_SEC, justify="left", anchor="w")
                content_lbl.pack(fill="x", pady=(5,0))
                
                think_vars['label'] = content_lbl
                
            self.root.after(0, setup_think_ui)

        # Response UI Label
        resp_vars = {'label': None}
        def setup_resp_ui():
            l = tk.Label(parent_frame, text="", font=Theme.FONT_UI, bg=Theme.BG_MAIN, 
                       fg=Theme.FG_PRIMARY, justify="left", anchor="w", wraplength=650)
            l.pack(fill="x", anchor="w")
            resp_vars['label'] = l
        self.root.after(0, setup_resp_ui)

        # --- Process Stream ---
        generator = self.brain.generate_response(prompt, self.deepthink_active.get())
        
        try:
            for type_, data in generator:
                if type_ == 'think' and think_vars.get('label'):
                    def update_think(t=data):
                        think_vars['text'] += t
                        think_vars['label'].config(text=think_vars['text'])
                    self.root.after(0, update_think)
                
                elif type_ == 'think_done' and think_vars.get('label'):
                    def finish_think(duration=data):
                        # Simulating the collapse/header update
                        pass 
                    self.root.after(0, finish_think)

                elif type_ == 'text':
                    def update_text(c=data):
                        if resp_vars['label']:
                            curr = resp_vars['label'].cget("text")
                            resp_vars['label'].config(text=curr + c)
                            self.canvas.yview_moveto(1.0)
                    self.root.after(0, update_text)
                    
        finally:
            self.is_generating = False
            self.root.after(0, lambda: self.btn_send.config(bg=Theme.FG_DIM))

if __name__ == "__main__":
    root = tk.Tk()
    CatR1 = CatseekR1App(root)
    root.mainloop()

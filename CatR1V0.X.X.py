#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║  CATSEEK R1 (1-Bit 14B Local Client)                                 ║
║  Real Inference GUI for GGUF/BitNet Models.                          ║
║  Features: Auto-Dependency & Model Wizard, <think> Parsing.          ║
╚══════════════════════════════════════════════════════════════════════╝
"""
import tkinter as tk
from tkinter import ttk, font, filedialog, messagebox
import threading
import time
import sys
import os
import subprocess
import urllib.request

# ════════════════════ CONFIGURATION ════════════════════
# Default model to download if missing (DeepSeek R1 14B - Efficient Q2_K Quant)
# Using direct resolve URL to bypass Hugging Face login/account requirements
MODEL_URL = "https://huggingface.co/unsloth/DeepSeek-R1-Distill-Qwen-14B-GGUF/resolve/main/DeepSeek-R1-Distill-Qwen-14B-Q2_K.gguf"
MODEL_FILENAME = "DeepSeek-R1-Distill-Qwen-14B-Q2_K.gguf"

# ════════════════════ WIZARDS ════════════════════
def check_setup(root_window):
    """Checks dependencies and model presence at boot."""
    
    # 1. Check Library
    try:
        import llama_cpp
    except ImportError:
        if messagebox.askyesno("Missing Driver", "Engine 'llama-cpp-python' is missing.\nInstall now? (Requires C++ compiler)"):
            install_library(root_window)
        else:
            return False

    # 2. Check Model
    if not os.path.exists(MODEL_FILENAME):
        if messagebox.askyesno("Missing Model", f"DeepSeek 14B model not found.\nDownload automatically? (~5 GB)\n\nTarget: {MODEL_FILENAME}"):
            download_model(root_window)
        # Note: We continue even if they say no, allowing manual load later
        
    return True

def install_library(root_window):
    """Installs pip packages via subprocess."""
    win = tk.Toplevel(root_window)
    win.title("Installing Engine...")
    win.geometry("300x100")
    tk.Label(win, text="Running pip install llama-cpp-python...", font=("Segoe UI", 10)).pack(pady=20)
    win.update()
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "llama-cpp-python"])
        messagebox.showinfo("Success", "Engine installed. The app will now check for the model.")
        win.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"Install failed: {e}")
        sys.exit(1)

def download_model(root_window):
    """Downloads the GGUF model with a progress bar."""
    win = tk.Toplevel(root_window)
    win.title("Downloading 14B Model")
    win.geometry("400x150")
    
    lbl = tk.Label(win, text="Connecting to Hugging Face...", font=("Segoe UI", 10))
    lbl.pack(pady=10)
    
    progress = ttk.Progressbar(win, orient="horizontal", length=300, mode="determinate")
    progress.pack(pady=10)
    
    lbl_status = tk.Label(win, text="0%", font=("Segoe UI", 8))
    lbl_status.pack()

    def _reporthook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = (downloaded / total_size) * 100
            progress["value"] = percent
            lbl_status.config(text=f"{int(percent)}% ({int(downloaded/1024/1024)} MB / {int(total_size/1024/1024)} MB)")
            win.update_idletasks()

    def _worker():
        try:
            # Direct download using urllib - bypasses huggingface_hub auth
            urllib.request.urlretrieve(MODEL_URL, MODEL_FILENAME, _reporthook)
            messagebox.showinfo("Complete", "Model downloaded successfully!")
            win.destroy()
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to download model.\n{e}")
            win.destroy()

    threading.Thread(target=_worker, daemon=True).start()

# Try import globally
HAS_LLM = False
try:
    from llama_cpp import Llama
    HAS_LLM = True
except ImportError:
    pass

# ════════════════════ THEME CONFIGURATION ════════════════════
class Theme:
    BG_MAIN     = "#2b2d31"       # Main chat background
    BG_SIDEBAR  = "#1e1f22"       # Sidebar background
    BG_INPUT    = "#383a40"       # Input field background
    BG_THINK    = "#1e1f22"       # Thinking block background
    FG_PRIMARY  = "#dbdee1"       # Main text
    FG_SEC      = "#949ba4"       # Secondary text
    FG_DIM      = "#6d6f78"       # Placeholder
    ACCENT      = "#4d6bfe"       # Blue
    BORDER      = "#383a40"       # Border lines
    
    FONT_CODE   = ("Consolas", 10) if sys.platform == "win32" else ("Menlo", 10)
    FONT_UI     = ("Segoe UI", 10) if sys.platform == "win32" else ("SF Pro Text", 11)
    FONT_BOLD   = ("Segoe UI", 10, "bold") if sys.platform == "win32" else ("SF Pro Text", 11, "bold")
    FONT_HEADER = ("Segoe UI", 14, "bold") if sys.platform == "win32" else ("SF Pro Display", 14, "bold")

# ════════════════════ REAL LOGIC (LOCAL LLM) ════════════════════
class RealBrain:
    """
    Connects to local GGUF models.
    Specialized for DeepSeek R1 <think> tag parsing.
    """
    def __init__(self):
        self.llm = None
        self.model_path = MODEL_FILENAME
        self.n_ctx = 4096
        self.n_gpu_layers = -1 # Auto-offload to GPU
        
    def load_model(self):
        if not HAS_LLM:
            return "Library missing. Please restart to run Auto-Installer."
        
        if not os.path.exists(self.model_path):
            return f"Model not found: {self.model_path}\nPlease use 'Load Model' or restart to download."

        if self.llm: return None # Already loaded

        try:
            self.llm = Llama(
                model_path=self.model_path,
                n_ctx=self.n_ctx,
                n_gpu_layers=self.n_gpu_layers,
                verbose=False
            )
            return None
        except Exception as e:
            return f"Failed to load model: {str(e)}"

    def generate_response(self, prompt, use_deepthink=True):
        """
        Generator yielding: ('think', text) or ('text', text)
        """
        error = self.load_model()
        if error:
            yield ('text', f"⚠️ [SYSTEM ERROR]\n{error}")
            return

        # Prepare Chat Format
        full_prompt = f"<|User|>{prompt}<|Assistant|>"

        stream = self.llm(
            full_prompt,
            max_tokens=self.n_ctx,
            stop=["<|User|>", "<|end|>"],
            stream=True,
            temperature=0.6
        )

        # <think> Parsing State Machine
        buffer = ""
        is_thinking = False
        start_time = time.time()
        
        yield ('think', "Initializing Matrix...\n")

        for output in stream:
            token = output['choices'][0]['text']
            buffer += token
            
            # Check for opening tag
            if "<think>" in buffer:
                is_thinking = True
                parts = buffer.split("<think>")
                if parts[0]: yield ('text', parts[0])
                buffer = parts[1] 
                
            # Check for closing tag
            if "</think>" in buffer:
                is_thinking = False
                parts = buffer.split("</think>")
                if parts[0]: yield ('think', parts[0])
                yield ('think_done', f"{time.time() - start_time:.1f}s")
                buffer = parts[1] 
                
            # Yield content
            if buffer:
                if is_thinking:
                    yield ('think', buffer)
                elif "<" in buffer and len(buffer) < 9: 
                    continue # Hold potential tag
                else:
                    yield ('text', buffer)
                buffer = ""

# ════════════════════ GUI APPLICATION ════════════════════
class CatseekR1App:
    def __init__(self, root):
        self.root = root
        self.root.title("Catseek R1 (1-Bit 14B Local)")
        self.root.geometry("1100x800")
        self.root.configure(bg=Theme.BG_MAIN)
        
        self.brain = RealBrain()
        self.is_generating = False
        self.deepthink_active = tk.BooleanVar(value=True)

        # 🚀 AUTO-SETUP ON LAUNCH
        self.root.after(100, lambda: check_setup(self.root))

        self.setup_styles()
        self.build_layout()
        self.show_welcome_screen()

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("Vertical.TScrollbar", background=Theme.BG_MAIN, 
                           troughcolor=Theme.BG_MAIN, bordercolor=Theme.BG_MAIN, arrowcolor=Theme.FG_SEC)
        self.style.configure("TFrame", background=Theme.BG_MAIN)

    def build_layout(self):
        # Sidebar
        self.sidebar = tk.Frame(self.root, bg=Theme.BG_SIDEBAR, width=260)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # New Chat
        btn_new = tk.Label(self.sidebar, text="+ New Chat", bg=Theme.BG_MAIN, fg=Theme.FG_PRIMARY, 
                         font=Theme.FONT_UI, cursor="hand2", pady=10)
        btn_new.pack(fill="x", padx=15, pady=20)
        btn_new.bind("<Button-1>", lambda e: self.reset_chat())

        # Load Model Button
        btn_load = tk.Label(self.sidebar, text="📂 Load GGUF Model", bg=Theme.BG_SIDEBAR, fg=Theme.FG_DIM,
                          font=("Segoe UI", 9, "bold"), cursor="hand2", pady=10)
        btn_load.pack(side="bottom", fill="x", pady=20)
        btn_load.bind("<Button-1>", self.select_model)

        # Main Area
        self.main_area = tk.Frame(self.root, bg=Theme.BG_MAIN)
        self.main_area.pack(side="right", fill="both", expand=True)

        # Header
        header = tk.Frame(self.main_area, bg=Theme.BG_MAIN, height=50)
        header.pack(fill="x", pady=10)
        self.lbl_header = tk.Label(header, text="Catseek R1 (1-Bit 14B Local)", bg=Theme.BG_MAIN, fg=Theme.FG_PRIMARY, 
               font=Theme.FONT_BOLD)
        self.lbl_header.pack()

        # Canvas
        self.canvas = tk.Canvas(self.main_area, bg=Theme.BG_MAIN, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.main_area, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=Theme.BG_MAIN)

        self.scrollable_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.canvas.pack(side="top", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Input Area
        input_container = tk.Frame(self.main_area, bg=Theme.BG_MAIN, pady=20)
        input_container.pack(side="bottom", fill="x")
        
        self.input_frame = tk.Frame(input_container, bg=Theme.BG_INPUT, padx=1, pady=1)
        self.input_frame.pack(fill="x", padx=100)
        
        self.txt_input = tk.Text(self.input_frame, height=3, bg=Theme.BG_INPUT, fg=Theme.FG_PRIMARY, 
                               font=Theme.FONT_UI, relief="flat", insertbackground="white", wrap="word")
        self.txt_input.pack(fill="x", padx=10, pady=(10, 0))
        self.txt_input.bind("<Return>", self.handle_enter)
        self.txt_input.focus_set()

        # Toolbar
        toolbar = tk.Frame(self.input_frame, bg=Theme.BG_INPUT, height=40)
        toolbar.pack(fill="x", padx=5, pady=5)
        
        self.btn_deepthink = tk.Label(toolbar, text="🧠 DeepThink", fg=Theme.ACCENT, bg=Theme.BG_INPUT, 
                                    font=("Segoe UI", 9, "bold"), cursor="hand2")
        self.btn_deepthink.pack(side="left", padx=10)
        self.btn_deepthink.bind("<Button-1>", self.toggle_deepthink)
        
        self.btn_send = tk.Label(toolbar, text="➤", bg=Theme.FG_DIM, fg="white", font=("Arial", 12), width=4, cursor="hand2")
        self.btn_send.pack(side="right", padx=5)
        self.btn_send.bind("<Button-1>", lambda e: self.submit_query())

    def select_model(self, event=None):
        path = filedialog.askopenfilename(filetypes=[("GGUF Models", "*.gguf")])
        if path:
            self.brain.model_path = path
            self.brain.llm = None # Force reload
            self.lbl_header.config(text=f"Model: {os.path.basename(path)}")
            messagebox.showinfo("Model Selected", f"Loaded: {os.path.basename(path)}")

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
        tk.Label(wel_frame, text="Catseek R1", font=Theme.FONT_HEADER, bg=Theme.BG_MAIN, fg=Theme.FG_PRIMARY).pack(pady=10)
        tk.Label(wel_frame, text="1-Bit 14B Local Inference", font=Theme.FONT_UI, bg=Theme.BG_MAIN, fg=Theme.FG_SEC).pack()
        self.is_welcome = True

    def clear_chat(self):
        for widget in self.scrollable_frame.winfo_children(): widget.destroy()

    def reset_chat(self):
        self.clear_chat()
        self.show_welcome_screen()

    def handle_enter(self, event):
        if not event.state & 0x0001: 
            self.submit_query()
            return "break"

    def submit_query(self):
        if self.is_generating: return
        prompt = self.txt_input.get("1.0", tk.END).strip()
        if not prompt: return
        
        if getattr(self, 'is_welcome', False):
            self.clear_chat()
            self.is_welcome = False

        self.txt_input.delete("1.0", tk.END)
        self.btn_send.config(bg=Theme.ACCENT)
        self.add_message("User", prompt)
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
        
        return content

    def generate_response_thread(self, prompt):
        time.sleep(0.2)
        msg_container = []
        def create_container():
            c = self.add_message("Catseek R1", "")
            msg_container.append(c)
        self.root.after(0, create_container)
        
        while not msg_container: time.sleep(0.01)
        parent_frame = msg_container[0]
        
        # UI References
        think_vars = {'label': None, 'text': ""}
        resp_vars = {'label': None}

        # Setup DeepThink Box
        if self.deepthink_active.get():
            def setup_think():
                box = tk.Frame(parent_frame, bg=Theme.BG_THINK, padx=10, pady=5)
                box.pack(fill="x", anchor="w", pady=(5, 10))
                header = tk.Frame(box, bg=Theme.BG_THINK)
                header.pack(fill="x")
                tk.Label(header, text="Thought Process", font=("Segoe UI", 9, "bold"), 
                       bg=Theme.BG_THINK, fg=Theme.FG_SEC).pack(side="left")
                content_lbl = tk.Label(box, text="", font=Theme.FONT_CODE, bg=Theme.BG_THINK, 
                                     fg=Theme.FG_SEC, justify="left", anchor="w")
                content_lbl.pack(fill="x", pady=(5,0))
                think_vars['label'] = content_lbl
            self.root.after(0, setup_think)

        # Setup Response Box
        def setup_resp():
            l = tk.Label(parent_frame, text="", font=Theme.FONT_UI, bg=Theme.BG_MAIN, 
                       fg=Theme.FG_PRIMARY, justify="left", anchor="w", wraplength=650)
            l.pack(fill="x", anchor="w")
            resp_vars['label'] = l
        self.root.after(0, setup_resp)

        generator = self.brain.generate_response(prompt)
        
        try:
            for type_, data in generator:
                if type_ == 'think' and think_vars.get('label'):
                    def update_think(t=data):
                        think_vars['text'] += t
                        think_vars['label'].config(text=think_vars['text'])
                    self.root.after(0, update_think)
                elif type_ == 'text':
                    def update_text(c=data):
                        if resp_vars['label']:
                            curr = resp_vars['label'].cget("text")
                            resp_vars['label'].config(text=curr + c)
                            self.canvas.yview_moveto(1.0)
                    self.root.after(0, update_text)
        except Exception as e:
            def show_err(err=str(e)):
                if resp_vars['label']:
                    resp_vars['label'].config(text=f"Error: {err}", fg="red")
            self.root.after(0, show_err)
        finally:
            self.is_generating = False
            self.root.after(0, lambda: self.btn_send.config(bg=Theme.FG_DIM))

if __name__ == "__main__":
    root = tk.Tk()
    app = CatseekR1App(root)
    root.mainloop()

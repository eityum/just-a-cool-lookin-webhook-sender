import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import os

ANSI_FG = {
    "Default":  "39",
    "Gray":     "30",
    "Red":      "31",
    "Green":    "32",
    "Yellow":   "33",
    "Blue":     "34",
    "Magenta":  "35",
    "Cyan":     "36",
    "White":    "37",
}

ANSI_BG = {
    "None":        "0",
    "Dark Blue":   "40",
    "Orange":      "41",
    "Marble Blue": "42",
    "Gray-Turq":   "43",
    "Gray":        "44",
    "Indigo":      "45",
    "Light Gray":  "46",
    "White":       "47",
}

ANSI_STYLE = {
    "Normal":    "0",
    "Bold":      "1",
    "Dim/Line":  "2",
}

PREVIEW_FG = {
    "Default":  "#ffffff",
    "Gray":     "#4f545c",
    "Red":      "#dc322f",
    "Green":    "#859900",
    "Yellow":   "#b58900",
    "Blue":     "#268bd2",
    "Magenta":  "#d33682",
    "Cyan":     "#2aa198",
    "White":    "#ffffff",
}

PREVIEW_BG = {
    "None":        "#2b2d31",
    "Dark Blue":   "#002b36",
    "Orange":      "#cb4b16",
    "Marble Blue": "#586e75",
    "Gray-Turq":   "#657b83",
    "Gray":        "#839496",
    "Indigo":      "#6c71c4",
    "Light Gray":  "#93a1a1",
    "White":       "#fdf6e3",
}


class WebhookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Webhook Sender")
        self.root.geometry("600x580")
        self.root.configure(bg="#2b2d31")
        self.selected_file = None

        tk.Label(root, text="Webhook URL:", bg="#2b2d31", fg="white", font=("Arial", 10)).pack(pady=(10, 0))
        self.webhook_entry = tk.Entry(root, width=70, bg="#1e1f22", fg="white", insertbackground="white")
        self.webhook_entry.pack(pady=5)

        style = ttk.Style()
        style.configure("TNotebook", background="#2b2d31", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1e1f22", foreground="white", padding=[10, 5])
        style.map("TNotebook.Tab", background=[("selected", "#5865f2")])

        self.tabs = ttk.Notebook(root)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)

        # Text tab
        self.text_frame = tk.Frame(self.tabs, bg="#2b2d31")
        self.tabs.add(self.text_frame, text="Text")
        tk.Label(self.text_frame, text="Message:", bg="#2b2d31", fg="white").pack(pady=(10, 0))
        self.text_box = tk.Text(self.text_frame, height=8, bg="#1e1f22", fg="white", insertbackground="white")
        self.text_box.pack(padx=10, pady=5, fill="both", expand=True)
        tk.Button(self.text_frame, text="Send Text", command=self.send_text, bg="#5865f2", fg="white", relief="flat", padx=10).pack(pady=5)

        # Image tab
        self.image_frame = tk.Frame(self.tabs, bg="#2b2d31")
        self.tabs.add(self.image_frame, text="Image URL")
        tk.Label(self.image_frame, text="Image URL:", bg="#2b2d31", fg="white").pack(pady=(10, 0))
        self.image_entry = tk.Entry(self.image_frame, width=70, bg="#1e1f22", fg="white", insertbackground="white")
        self.image_entry.pack(pady=5)
        tk.Label(self.image_frame, text="Caption (optional):", bg="#2b2d31", fg="white").pack()
        self.caption_entry = tk.Entry(self.image_frame, width=70, bg="#1e1f22", fg="white", insertbackground="white")
        self.caption_entry.pack(pady=5)
        tk.Button(self.image_frame, text="Send Image", command=self.send_image, bg="#5865f2", fg="white", relief="flat", padx=10).pack(pady=5)

        # File tab
        self.file_frame = tk.Frame(self.tabs, bg="#2b2d31")
        self.tabs.add(self.file_frame, text="File")
        tk.Label(self.file_frame, text="Select a file to send (max 10MB):", bg="#2b2d31", fg="white").pack(pady=(10, 0))
        self.file_label = tk.Label(self.file_frame, text="No file selected", bg="#2b2d31", fg="gray")
        self.file_label.pack()
        tk.Button(self.file_frame, text="Browse File", command=self.browse_file, bg="#4e5058", fg="white", relief="flat", padx=10).pack(pady=5)
        tk.Button(self.file_frame, text="Send File", command=self.send_file, bg="#5865f2", fg="white", relief="flat", padx=10).pack(pady=5)

        # Embed tab
        self.embed_frame = tk.Frame(self.tabs, bg="#2b2d31")
        self.tabs.add(self.embed_frame, text="Embed")
        tk.Label(self.embed_frame, text="Title:", bg="#2b2d31", fg="white").pack(pady=(10, 0))
        self.embed_title = tk.Entry(self.embed_frame, width=70, bg="#1e1f22", fg="white", insertbackground="white")
        self.embed_title.pack(pady=3)
        tk.Label(self.embed_frame, text="Description:", bg="#2b2d31", fg="white").pack()
        self.embed_desc = tk.Text(self.embed_frame, height=4, bg="#1e1f22", fg="white", insertbackground="white")
        self.embed_desc.pack(padx=10, pady=3, fill="x")
        tk.Label(self.embed_frame, text="Color (hex, e.g. ff0000):", bg="#2b2d31", fg="white").pack()
        self.embed_color = tk.Entry(self.embed_frame, width=20, bg="#1e1f22", fg="white", insertbackground="white")
        self.embed_color.insert(0, "5865f2")
        self.embed_color.pack(pady=3)
        tk.Button(self.embed_frame, text="Send Embed", command=self.send_embed, bg="#5865f2", fg="white", relief="flat", padx=10).pack(pady=5)

        # ANSI tab
        self.ansi_frame = tk.Frame(self.tabs, bg="#2b2d31")
        self.tabs.add(self.ansi_frame, text="ANSI Color")
        self._build_ansi_tab()

        self.status = tk.Label(root, text="", bg="#2b2d31", fg="green", font=("Arial", 10))
        self.status.pack(pady=5)

    def _build_ansi_tab(self):
        f = self.ansi_frame

        # Segments list
        self.ansi_segments = []  # list of dicts: {text, fg, bg, style}

        # Controls row
        ctrl = tk.Frame(f, bg="#2b2d31")
        ctrl.pack(fill="x", padx=8, pady=(8, 2))

        tk.Label(ctrl, text="Text:", bg="#2b2d31", fg="white").grid(row=0, column=0, sticky="w")
        self.ansi_text_entry = tk.Entry(ctrl, width=22, bg="#1e1f22", fg="white", insertbackground="white")
        self.ansi_text_entry.grid(row=0, column=1, padx=4)

        tk.Label(ctrl, text="FG:", bg="#2b2d31", fg="white").grid(row=0, column=2)
        self.ansi_fg_var = tk.StringVar(value="Default")
        fg_menu = ttk.Combobox(ctrl, textvariable=self.ansi_fg_var, values=list(ANSI_FG.keys()), width=9, state="readonly")
        fg_menu.grid(row=0, column=3, padx=4)

        tk.Label(ctrl, text="BG:", bg="#2b2d31", fg="white").grid(row=0, column=4)
        self.ansi_bg_var = tk.StringVar(value="None")
        bg_menu = ttk.Combobox(ctrl, textvariable=self.ansi_bg_var, values=list(ANSI_BG.keys()), width=9, state="readonly")
        bg_menu.grid(row=0, column=5, padx=4)

        tk.Label(ctrl, text="Style:", bg="#2b2d31", fg="white").grid(row=0, column=6)
        self.ansi_style_var = tk.StringVar(value="Normal")
        style_menu = ttk.Combobox(ctrl, textvariable=self.ansi_style_var, values=list(ANSI_STYLE.keys()), width=8, state="readonly")
        style_menu.grid(row=0, column=7, padx=4)

        tk.Button(ctrl, text="Add", command=self.ansi_add_segment,
                  bg="#5865f2", fg="white", relief="flat", padx=6).grid(row=0, column=8, padx=(6, 0))

        # Segment list box
        list_frame = tk.Frame(f, bg="#2b2d31")
        list_frame.pack(fill="x", padx=8, pady=2)

        tk.Label(list_frame, text="Segments:", bg="#2b2d31", fg="white").pack(anchor="w")
        seg_row = tk.Frame(list_frame, bg="#2b2d31")
        seg_row.pack(fill="x")

        self.seg_listbox = tk.Listbox(seg_row, bg="#1e1f22", fg="white", selectbackground="#5865f2",
                                      height=4, width=52, relief="flat")
        self.seg_listbox.pack(side="left", fill="x", expand=True)

        sb = tk.Scrollbar(seg_row, orient="vertical", command=self.seg_listbox.yview)
        sb.pack(side="left", fill="y")
        self.seg_listbox.config(yscrollcommand=sb.set)

        btn_col = tk.Frame(list_frame, bg="#2b2d31")
        btn_col.pack(anchor="e", pady=2)
        tk.Button(btn_col, text="Remove Selected", command=self.ansi_remove_segment,
                  bg="#ed4245", fg="white", relief="flat", padx=6).pack(side="left", padx=2)
        tk.Button(btn_col, text="Clear All", command=self.ansi_clear_segments,
                  bg="#4e5058", fg="white", relief="flat", padx=6).pack(side="left", padx=2)

        # Preview
        tk.Label(f, text="Preview:", bg="#2b2d31", fg="white").pack(anchor="w", padx=8)
        self.ansi_preview = tk.Text(f, height=3, bg="#111214", fg="white",
                                    insertbackground="white", relief="flat",
                                    font=("Consolas", 11), state="disabled", padx=6, pady=4)
        self.ansi_preview.pack(fill="x", padx=8, pady=2)

        # Raw output (read only)
        tk.Label(f, text="Raw (auto-built):", bg="#2b2d31", fg="white").pack(anchor="w", padx=8)
        self.ansi_raw = tk.Text(f, height=3, bg="#1e1f22", fg="#72767d",
                                insertbackground="white", relief="flat",
                                font=("Consolas", 9), state="disabled", padx=4, pady=4)
        self.ansi_raw.pack(fill="x", padx=8, pady=2)

        tk.Button(f, text="Send ANSI Message", command=self.send_ansi,
                  bg="#5865f2", fg="white", relief="flat", padx=10).pack(pady=6)

    def ansi_add_segment(self):
        text = self.ansi_text_entry.get()
        if not text:
            return
        seg = {
            "text":  text,
            "fg":    self.ansi_fg_var.get(),
            "bg":    self.ansi_bg_var.get(),
            "style": self.ansi_style_var.get(),
        }
        self.ansi_segments.append(seg)
        label = f'[{seg["style"]} | FG:{seg["fg"]} | BG:{seg["bg"]}] {seg["text"]}'
        self.seg_listbox.insert(tk.END, label)
        self.ansi_text_entry.delete(0, tk.END)
        self._ansi_refresh()

    def ansi_remove_segment(self):
        sel = self.seg_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        self.seg_listbox.delete(idx)
        self.ansi_segments.pop(idx)
        self._ansi_refresh()

    def ansi_clear_segments(self):
        self.seg_listbox.delete(0, tk.END)
        self.ansi_segments.clear()
        self._ansi_refresh()

    def _build_ansi_string(self):
        """Build the raw ANSI escape string (no code block wrapper)."""
        parts = []
        for seg in self.ansi_segments:
            style_code = ANSI_STYLE[seg["style"]]
            fg_code    = ANSI_FG[seg["fg"]]
            bg_code    = ANSI_BG[seg["bg"]]

            if bg_code == "0":
                # no background
                code = f"\x1b[{style_code};{fg_code}m"
            else:
                code = f"\x1b[{style_code};{fg_code};{bg_code}m"

            parts.append(f"{code}{seg['text']}\x1b[0m")
        return "".join(parts)

    def _ansi_refresh(self):
        raw = self._build_ansi_string()
        # update raw box (show printable escape repr)
        raw_display = raw.replace("\x1b", "\\e")
        self.ansi_raw.config(state="normal")
        self.ansi_raw.delete("1.0", tk.END)
        self.ansi_raw.insert(tk.END, f"```ansi\n{raw_display}\n```")
        self.ansi_raw.config(state="disabled")

        # update preview using tkinter tags for color
        self.ansi_preview.config(state="normal")
        self.ansi_preview.delete("1.0", tk.END)
        for i, seg in enumerate(self.ansi_segments):
            tag = f"seg_{i}"
            fg_color = PREVIEW_FG[seg["fg"]]
            bg_color = PREVIEW_BG[seg["bg"]]
            font_weight = "bold" if seg["style"] == "Bold" else "normal"
            self.ansi_preview.tag_configure(tag, foreground=fg_color, background=bg_color, font=("Consolas", 11, font_weight))
            self.ansi_preview.insert(tk.END, seg["text"], tag)
        self.ansi_preview.config(state="disabled")

    def send_ansi(self):
        url = self.get_webhook()
        if not url:
            return
        if not self.ansi_segments:
            messagebox.showerror("Error", "No segments added!")
            return
        raw = self._build_ansi_string()
        content = f"```ansi\n{raw}\n```"
        r = requests.post(url, json={"content": content})
        self.set_status(r.status_code)

    # ── original methods ──────────────────────────────────────────────────────

    def get_webhook(self):
        url = self.webhook_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a webhook URL!")
            return None
        return url

    def set_status(self, code):
        if code in (200, 204):
            self.status.config(text="Sent successfully!", fg="green")
        else:
            self.status.config(text=f"Error: {code}", fg="red")

    def send_text(self):
        url = self.get_webhook()
        if not url:
            return
        message = self.text_box.get("1.0", tk.END).strip()
        if not message:
            messagebox.showerror("Error", "Message is empty!")
            return
        r = requests.post(url, json={"content": message})
        self.set_status(r.status_code)

    def send_image(self):
        url = self.get_webhook()
        if not url:
            return
        image_url = self.image_entry.get().strip()
        caption = self.caption_entry.get().strip()
        if not image_url:
            messagebox.showerror("Error", "Please enter an image URL!")
            return
        payload = {"embeds": [{"title": caption, "image": {"url": image_url}}]}
        r = requests.post(url, json=payload)
        self.set_status(r.status_code)

    def browse_file(self):
        file = filedialog.askopenfilename(filetypes=[
            ("All supported", "*.txt *.png *.jpg *.jpeg *.gif *.pdf *.zip *.lua *.py"),
            ("Text files", "*.txt"),
            ("Images", "*.png *.jpg *.jpeg *.gif"),
            ("All files", "*.*")
        ])
        if file:
            self.selected_file = file
            self.file_label.config(text=os.path.basename(file), fg="white")

    def send_file(self):
        url = self.get_webhook()
        if not url:
            return
        if not self.selected_file:
            messagebox.showerror("Error", "No file selected!")
            return
        if os.path.getsize(self.selected_file) > 10 * 1024 * 1024:
            messagebox.showerror("Error", "File exceeds 10MB limit!")
            return
        with open(self.selected_file, "rb") as f:
            r = requests.post(url, files={"file": f})
        self.set_status(r.status_code)

    def send_embed(self):
        url = self.get_webhook()
        if not url:
            return
        title = self.embed_title.get().strip()
        desc = self.embed_desc.get("1.0", tk.END).strip()
        color_hex = self.embed_color.get().strip().lstrip("#")
        try:
            color_int = int(color_hex, 16)
        except ValueError:
            color_int = 5793266
        payload = {"embeds": [{"title": title, "description": desc, "color": color_int}]}
        r = requests.post(url, json=payload)
        self.set_status(r.status_code)


root = tk.Tk()
app = WebhookApp(root)
root.mainloop()
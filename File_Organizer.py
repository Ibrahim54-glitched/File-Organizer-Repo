import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import shutil
import json
import os
import threading

try:
    from tkinterdnd2 import DND_FILES
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False

SETTINGS_FILE = "settings.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_settings(source_paths, destination_path, selected_categories, folder_lists, duplicate_mode):
    data = {
        "source_paths": [str(p) for p in source_paths],
        "destination_path": str(destination_path),
        "selected_categories": list(selected_categories),
        "folder_lists": folder_lists,
        "duplicate_mode": duplicate_mode
    }
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def default_folder_lists():
    return {
        "Installation Files": ["exe", "msi", "apk", "dmg", "pkg", "deb", "rpm", "bat", "sh", "appimage"],
        "Documents": ["doc", "docx", "pdf", "txt", "rtf", "odt", "xls", "xlsx", "csv",
                      "ppt", "pptx", "html", "htm", "md", "log", "json", "xml", "yml", "yaml"],
        "Images": ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "svg", "webp", "heic",
                   "ico", "jfif", "psd", "ai", "eps"],
        "Videos": ["mp4", "avi", "mov", "wmv", "flv", "mkv", "webm", "mpeg", "3gp",
                   "mts", "m2ts", "ts"],
        "Audio": ["mp3", "wav", "aac", "flac", "ogg", "m4a", "wma", "aiff", "opus"],
        "Compressed Files": ["zip", "rar", "7z", "tar", "gz", "bz2", "xz", "iso", "cab", "zst"],
        "Programming": ["py", "java", "c", "cpp", "cs", "js", "ts", "html", "css", "php",
                        "swift", "kt", "go", "rs", "rb"],
        "Design": ["fig", "sketch", "xd", "indd", "idml"]
    }

def create_folders(target_path: Path, folder_list: dict):
    for folder_name in folder_list:
        (target_path / folder_name).mkdir(parents=True, exist_ok=True)

def move_file_one(src: Path, dst_folder: Path, mode: str):
    dst = dst_folder / src.name
    if dst.exists():
        if mode == "Skip":
            return None
        elif mode == "Overwrite":
            try:
                if dst.is_file():
                    os.remove(dst)
                else:
                    shutil.rmtree(dst)
            except Exception:
                pass
        elif mode == "Rename":
            counter = 1
            while dst.exists():
                dst = dst_folder / f"{src.stem}_{counter}{src.suffix}"
                counter += 1
    shutil.move(str(src), str(dst))
    return dst

def build_preview(sources, target_dir: Path, folder_lists: dict, selected_categories):
    preview = []
    selected = {k: set(v) for k, v in folder_lists.items() if k in selected_categories}
    for src_dir in sources:
        if not src_dir.exists():
            continue
        for file_path in src_dir.rglob("*"):
            if file_path.is_file():
                ext = file_path.suffix.lower().lstrip(".")
                for cat, exts in selected.items():
                    if ext in exts:
                        preview.append((file_path, cat, target_dir / cat / file_path.name))
                        break
    return preview

class FileSorterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("File Sorter")
        self.geometry("600x750")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        s = load_settings()
        self.folder_lists = s.get("folder_lists", default_folder_lists())
        self.source_paths = [Path(p) for p in s.get("source_paths", [])]
        self.destination_path = Path(s.get("destination_path", "D:/Downloads"))
        self.selected_categories = set(s.get("selected_categories", list(self.folder_lists.keys())))
        self.duplicate_mode = s.get("duplicate_mode", "Rename")
        self.last_moves = []

        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=6, pady=6)

        self.main_tab = self.tabview.add("Main")
        self.preview_tab = self.tabview.add("Preview")
        self.log_tab = self.tabview.add("Log")

        self.build_main_tab()
        self.build_preview_tab()
        self.build_log_tab()
        self.refresh_sources_listbox()
        self.refresh_category_checks()
        self.refresh_preview_table()

        if DND_AVAILABLE:
            try:
                self.sources_listbox.drop_target_register(DND_FILES)
                self.sources_listbox.dnd_bind("<<Drop>>", self.on_drop_sources)
            except Exception:
                pass

    def build_main_tab(self):
        src_frame = ctk.CTkFrame(self.main_tab)
        src_frame.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(src_frame, text="Source Paths:").pack(anchor="w", padx=6, pady=4)

        lb_frame = ctk.CTkFrame(src_frame)
        lb_frame.pack(fill="x", padx=6, pady=4)
        self.sources_listbox = tk.Listbox(lb_frame, selectmode=tk.EXTENDED, height=6, activestyle="none")
        self.sources_listbox.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=4)
        src_scroll = ttk.Scrollbar(lb_frame, orient="vertical", command=self.sources_listbox.yview)
        src_scroll.pack(side="right", fill="y", padx=(0, 6), pady=4)
        self.sources_listbox.config(yscrollcommand=src_scroll.set)

        hint = "Drag & drop folders here" if DND_AVAILABLE else "Add folders using the button"
        ctk.CTkLabel(src_frame, text=hint, fg_color="transparent", text_color=("gray70", "gray70")).pack(anchor="w", padx=6)

        btns = ctk.CTkFrame(self.main_tab)
        btns.pack(fill="x", padx=6, pady=4)
        ctk.CTkButton(btns, text="Add Folder", width=100, command=self.add_source_path).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Remove Selected", width=130, command=self.delete_selected_sources).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Clear", width=70, command=self.clear_sources).pack(side="left", padx=4)

        dest = ctk.CTkFrame(self.main_tab)
        dest.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(dest, text="Destination Path:").pack(anchor="w", padx=6)
        self.dest_entry = ctk.CTkEntry(dest, width=360)
        self.dest_entry.insert(0, str(self.destination_path))
        self.dest_entry.pack(side="left", padx=6, pady=6)
        ctk.CTkButton(dest, text="Browse", width=90, command=self.browse_destination).pack(side="left", padx=6)

        dup_frame = ctk.CTkFrame(self.main_tab)
        dup_frame.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(dup_frame, text="On duplicate:").pack(side="left", padx=6)
        self.dup_option = ctk.CTkOptionMenu(dup_frame, values=["Skip", "Overwrite", "Rename"], width=140,
                                            command=lambda _: self.save_all_settings())
        self.dup_option.set(self.duplicate_mode)
        self.dup_option.pack(side="left", padx=6)

        cat_frame = ctk.CTkFrame(self.main_tab)
        cat_frame.pack(fill="both", expand=False, padx=6, pady=6)
        head = ctk.CTkFrame(cat_frame)
        head.pack(fill="x")
        ctk.CTkLabel(head, text="Select Categories:").pack(side="left", padx=6, pady=6)
        ctk.CTkButton(head, text="Manage Categories", width=160, command=self.open_category_manager).pack(side="right", padx=6)

        self.cat_scroll = ctk.CTkScrollableFrame(cat_frame, width=560, height=230)
        self.cat_scroll.pack(fill="both", expand=True, padx=6, pady=6)
        self.category_vars = {}

        actions = ctk.CTkFrame(self.main_tab)
        actions.pack(fill="x", padx=6, pady=8)
        ctk.CTkButton(actions, text="Preview", width=100, command=self.refresh_preview_table).pack(side="left", padx=6)
        ctk.CTkButton(actions, text="Sort Files", width=110, command=self.start_sorting_thread).pack(side="left", padx=6)
        ctk.CTkButton(actions, text="Undo Last Run", width=140, command=self.undo_last_run).pack(side="left", padx=6)

    def build_preview_tab(self):
        top = ctk.CTkFrame(self.preview_tab)
        top.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(top, text="Preview of files to be moved").pack(side="left", padx=6)
        ctk.CTkButton(top, text="Refresh", width=90, command=self.refresh_preview_table).pack(side="right", padx=6)

        tree_frame = ctk.CTkFrame(self.preview_tab)
        tree_frame.pack(fill="both", expand=True, padx=6, pady=6)

        cols = ("name", "category", "from", "to")
        self.preview_tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
        self.preview_tree.heading("name", text="Name")
        self.preview_tree.heading("category", text="Category")
        self.preview_tree.heading("from", text="From")
        self.preview_tree.heading("to", text="To")
        self.preview_tree.column("name", width=150, anchor="w")
        self.preview_tree.column("category", width=110, anchor="w")
        self.preview_tree.column("from", width=200, anchor="w")
        self.preview_tree.column("to", width=200, anchor="w")
        self.preview_tree.pack(side="left", fill="both", expand=True, padx=(6, 0), pady=6)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.preview_tree.yview)
        self.preview_tree.configure(yscrollcommand=tree_scroll.set)
        tree_scroll.pack(side="right", fill="y", padx=(0, 6), pady=6)

    def build_log_tab(self):
        tools = ctk.CTkFrame(self.log_tab)
        tools.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(tools, text="Search:").pack(side="left", padx=6)
        self.log_search = ctk.CTkEntry(tools, width=220)
        self.log_search.pack(side="left", padx=6)
        ctk.CTkButton(tools, text="Find Next", width=100, command=self.find_in_log).pack(side="left", padx=6)
        ctk.CTkButton(tools, text="Clear Log", width=90, command=lambda: self.log_box.delete("1.0", "end")).pack(side="left", padx=6)

        self.log_box = ctk.CTkTextbox(self.log_tab, wrap="none")
        self.log_box.pack(fill="both", expand=True, padx=6, pady=6)
        scroll = ctk.CTkScrollbar(self.log_tab, command=self.log_box.yview)
        scroll.place(relx=1, rely=0.16, relheight=0.82, anchor="ne")
        self.log_box.configure(yscrollcommand=scroll.set)

    def on_drop_sources(self, event):
        data = event.data
        if not data:
            return
        paths = []
        buf = ""
        in_quote = False
        for ch in data:
            if ch == "{":
                in_quote = True
                buf = ""
            elif ch == "}":
                in_quote = False
                paths.append(buf)
                buf = ""
            elif ch == " " and not in_quote:
                if buf:
                    paths.append(buf)
                    buf = ""
            else:
                buf += ch
        if buf:
            paths.append(buf)
        added = 0
        for p in paths:
            pth = Path(p)
            if pth.exists() and pth.is_dir() and pth not in self.source_paths:
                self.source_paths.append(pth)
                added += 1
        if added:
            self.refresh_sources_listbox()
            self.save_all_settings()

    def refresh_sources_listbox(self):
        self.sources_listbox.delete(0, "end")
        for p in self.source_paths:
            self.sources_listbox.insert("end", str(p))

    def add_source_path(self):
        folder = filedialog.askdirectory()
        if folder:
            p = Path(folder)
            if p not in self.source_paths:
                self.source_paths.append(p)
                self.refresh_sources_listbox()
                self.save_all_settings()

    def delete_selected_sources(self):
        sel = list(self.sources_listbox.curselection())
        if not sel:
            return
        for idx in reversed(sel):
            del self.source_paths[idx]
        self.refresh_sources_listbox()
        self.save_all_settings()

    def clear_sources(self):
        if self.source_paths and messagebox.askyesno("Confirm", "Remove all source folders?"):
            self.source_paths.clear()
            self.refresh_sources_listbox()
            self.save_all_settings()

    def browse_destination(self):
        folder = filedialog.askdirectory()
        if folder:
            self.destination_path = Path(folder)
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, str(folder))
            self.save_all_settings()

    def refresh_category_checks(self):
        for w in self.cat_scroll.winfo_children():
            w.destroy()
        self.category_vars.clear()
        for cat in self.folder_lists.keys():
            var = ctk.BooleanVar(value=(cat in self.selected_categories))
            chk = ctk.CTkCheckBox(self.cat_scroll, text=cat, variable=var,
                                  command=self.save_all_settings)
            chk.pack(anchor="w", padx=8, pady=2)
            self.category_vars[cat] = var

    def open_category_manager(self):
        win = ctk.CTkToplevel(self)
        win.title("Manage Categories")
        win.geometry("560x420")
        win.resizable(False, False)

        left = ctk.CTkFrame(win)
        left.pack(side="left", fill="y", padx=8, pady=8)
        right = ctk.CTkFrame(win)
        right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

        lb = tk.Listbox(left, height=16)
        lb.pack(side="left", fill="y", padx=(6, 0), pady=6)
        sbar = ttk.Scrollbar(left, orient="vertical", command=lb.yview)
        sbar.pack(side="right", fill="y", padx=(0, 6), pady=6)
        lb.config(yscrollcommand=sbar.set)

        for name in self.folder_lists.keys():
            lb.insert("end", name)

        form = ctk.CTkFrame(right)
        form.pack(fill="x", padx=6, pady=6)
        ctk.CTkLabel(form, text="Category Name").grid(row=0, column=0, sticky="w", padx=6, pady=6)
        name_entry = ctk.CTkEntry(form, width=260)
        name_entry.grid(row=0, column=1, padx=6, pady=6, sticky="w")

        ctk.CTkLabel(form, text="Extensions (comma-separated)").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        ext_entry = ctk.CTkEntry(form, width=260)
        ext_entry.grid(row=1, column=1, padx=6, pady=6, sticky="w")

        btns = ctk.CTkFrame(right)
        btns.pack(fill="x", padx=6, pady=6)
        def refresh_lb():
            lb.delete(0, "end")
            for n in self.folder_lists.keys():
                lb.insert("end", n)

        def on_select(evt=None):
            sel = lb.curselection()
            if not sel:
                name_entry.delete(0, "end")
                ext_entry.delete(0, "end")
                return
            name = lb.get(sel[0])
            exts = ", ".join(self.folder_lists.get(name, []))
            name_entry.delete(0, "end")
            name_entry.insert(0, name)
            ext_entry.delete(0, "end")
            ext_entry.insert(0, exts)

        lb.bind("<<ListboxSelect>>", on_select)

        def add_update():
            name = name_entry.get().strip()
            exts = [e.strip().lstrip(".").lower() for e in ext_entry.get().split(",") if e.strip()]
            if not name or not exts:
                return
            self.folder_lists[name] = sorted(set(exts))
            self.selected_categories.add(name)
            refresh_lb()
            self.refresh_category_checks()
            self.save_all_settings()

        def delete_cat():
            sel = lb.curselection()
            if not sel:
                return
            name = lb.get(sel[0])
            if messagebox.askyesno("Delete", f"Delete category '{name}'?"):
                self.folder_lists.pop(name, None)
                self.selected_categories.discard(name)
                refresh_lb()
                name_entry.delete(0, "end")
                ext_entry.delete(0, "end")
                self.refresh_category_checks()
                self.save_all_settings()

        ctk.CTkButton(btns, text="Add / Update", command=add_update).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Delete", fg_color="red", command=delete_cat).pack(side="left", padx=6)
        ctk.CTkButton(btns, text="Close", command=win.destroy).pack(side="right", padx=6)

    def refresh_preview_table(self):
        for i in self.preview_tree.get_children():
            self.preview_tree.delete(i)
        selected = [c for c, v in self.category_vars.items() if v.get()]
        self.selected_categories = set(selected)
        target = Path(self.dest_entry.get()) if hasattr(self, "dest_entry") else self.destination_path
        preview = build_preview(self.source_paths, target, self.folder_lists, self.selected_categories)
        for src, cat, dst in preview:
            self.preview_tree.insert("", "end", values=(src.name, cat, str(src), str(dst)))

    def append_log(self, text):
        self.log_box.insert("end", text + "\n")
        self.log_box.see("end")

    def find_in_log(self):
        needle = self.log_search.get()
        if not needle:
            return
        start = self.log_box.index(tk.INSERT)
        idx = self.log_box.search(needle, start, nocase=True, stopindex="end")
        if not idx:
            idx = self.log_box.search(needle, "1.0", nocase=True, stopindex="end")
            if not idx:
                return
        end_idx = f"{idx}+{len(needle)}c"
        self.log_box.tag_remove("highlight", "1.0", "end")
        self.log_box.tag_add("highlight", idx, end_idx)
        self.log_box.tag_config("highlight", background="#444466")
        self.log_box.mark_set(tk.INSERT, end_idx)
        self.log_box.see(idx)

    def start_sorting_thread(self):
        t = threading.Thread(target=self.run_sorting, daemon=True)
        t.start()

    def run_sorting(self):
        self.last_moves = []
        self.append_log("Starting sort...")
        target = Path(self.dest_entry.get())
        create_folders(target, self.folder_lists)
        preview_now = []
        for iid in self.preview_tree.get_children():
            vals = self.preview_tree.item(iid, "values")
            if not vals:
                continue
            src = Path(vals[2])
            cat = vals[1]
            preview_now.append((src, cat))
        if not preview_now:
            selected = [c for c, v in self.category_vars.items() if v.get()]
            preview = build_preview(self.source_paths, target, self.folder_lists, set(selected))
            for src, cat, _ in preview:
                preview_now.append((src, cat))

        mode = self.dup_option.get()
        moved_count = 0
        missing = 0
        for src, cat in preview_now:
            if not src.exists():
                missing += 1
                continue
            try:
                dst = move_file_one(src, target / cat, mode)
                if dst:
                    self.last_moves.append((dst, src))
                    moved_count += 1
                    self.append_log(f"Moved: {src} → {dst}")
                else:
                    self.append_log(f"Skipped (duplicate): {src}")
            except Exception as e:
                self.append_log(f"Error moving {src}: {e}")
        self.append_log(f"Done. Moved {moved_count} file(s)." + (f" Missing: {missing}." if missing else ""))
        self.save_all_settings()
        self.after(50, lambda: messagebox.showinfo("Completed", "File sorting completed!"))

    def undo_last_run(self):
        if not self.last_moves:
            messagebox.showinfo("Undo", "Nothing to undo.")
            return
        undone = 0
        for new_path, old_path in reversed(self.last_moves):
            try:
                old_dir = old_path.parent
                old_dir.mkdir(parents=True, exist_ok=True)
                if new_path.exists():
                    shutil.move(str(new_path), str(old_path))
                    undone += 1
                    self.append_log(f"Restored: {new_path} → {old_path}")
            except Exception as e:
                self.append_log(f"Error restoring {new_path}: {e}")
        self.last_moves.clear()
        messagebox.showinfo("Undo", f"Undo complete. Restored {undone} file(s).")

    def save_all_settings(self):
        self.selected_categories = {c for c, v in self.category_vars.items() if v.get()}
        self.duplicate_mode = self.dup_option.get()
        save_settings(self.source_paths, Path(self.dest_entry.get()), self.selected_categories, self.folder_lists, self.duplicate_mode)

if __name__ == "__main__":
    app = FileSorterApp()
    app.protocol("WM_DELETE_WINDOW", lambda: (app.save_all_settings(), app.destroy()))
    app.mainloop()

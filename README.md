# File Sorter App

A simple but surprisingly handy desktop tool to keep your folders organized.  
Built with **Python** and **CustomTkinter**, this app automatically sorts files from multiple source folders into a single destination, neatly organized into categories like **Documents**, **Images**, **Videos**, and more.

---

## ✨ Features

- **Multiple Source Folders** – Add as many locations as you like.
- **Persistent Settings** – Your chosen folders and categories are saved automatically.
- **Category Selection** – Choose which file types to sort (e.g., only Images or Documents).
- **Log Tab** – See exactly what got moved and where.
- **Undo (Last Run)** – Move files back if you change your mind.
- **Preview Tab** – Check what will be moved before running.
- **Modern Interface** – Built with CustomTkinter for a clean, dark-themed look.

---

## 🖼 Screenshot
<img width="582" height="766" alt="image" src="https://github.com/user-attachments/assets/52537bd2-59c9-4d9e-b440-dde94b89f27b" />


---

## 📦 Installation

1. Make sure you have **Python 3.8+** installed.
2. Install the required packages:
   ```bash
   pip install customtkinter
   ```
3. Download or clone this repository:
   ```bash
   git clone https://github.com/Ibrahim54-glitched/filesorter.git
   cd filesorter
   ```
4. Run the app:
   ```bash
   python main.py
   ```

---

## ⚙ How to Use

1. **Add Source Paths** – Click *Add* and choose the folders you want to scan.
2. **Set Destination** – Choose where the sorted files will be placed.
3. **Pick Categories** – Tick only the categories you want to sort.
4. **Click "Sort Files"** – The app will organize your files into subfolders.
5. **Check the Log** – Switch to the *Log* tab to see what happened.

---

## 🔙 Undo Feature

If you regret your last run, you can undo it and restore the files to their original location *(works only for the most recent sorting)*.

---

## 📂 Supported File Categories

- **Installation Files** – `.exe`, `.msi`, `.apk`, `.dmg`, etc.
- **Documents** – `.pdf`, `.docx`, `.xlsx`, `.txt`, etc.
- **Images** – `.jpg`, `.png`, `.svg`, `.webp`, etc.
- **Videos** – `.mp4`, `.avi`, `.mkv`, etc.
- **Audio** – `.mp3`, `.wav`, `.flac`, etc.
- **Archives** – `.zip`, `.rar`, `.tar`, etc.
- **Programming** – `.py`, `.java`, `.cpp`, `.html`, etc.
- **Design Files** – `.fig`, `.xd`, `.psd`, etc.

---

## 🛠 Built With

- **Python** – Core programming language
- **CustomTkinter** – Modern-looking UI framework for Tkinter
- **Pathlib & Shutil** – For file and folder operations

---

## 💡 Future Ideas

- Option to run in the background and auto-sort every few minutes
- More advanced undo/redo history
- Custom category creation
- Drag-and-drop file adding

---

## 📜 License

This project is licensed under the **MIT License** – feel free to use and modify it.

---

Made with ☕ and Python by **Ibrahim54-glitched**

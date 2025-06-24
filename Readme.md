# 🌟 QuickFavs – Effortless Access to Your Essentials

**QuickFavs** is a modern and lightweight PyQt6 desktop application that empowers users to manage and launch their most-used files, folders, URLs, and applications with speed and simplicity. Whether you're a productivity enthusiast or just want quick access to your tools, QuickFavs is designed to help you stay focused and organized.

---

## 🎯 Features at a Glance

- ✅ **System Tray Integration** – Runs discreetly in the background and is accessible anytime via the tray icon.
- 🖱️ **Drag-and-Drop Support** – Simply drag in files, folders, or links to add them as favorites.
- 🏷️ **Tagging System** – Assign custom tags to categorize and find favorites quickly.
- 🔎 **Smart Search** – Filter by name, type, tag, or description in real time.
- ✏️ **Edit Support** – Update any favorite's details like name, path, type, tags, or notes.
- 🗑️ **Delete Confirmation** – Prevent mistakes with a built-in deletion prompt.
- 📢 **Status Bar Feedback** – Get instant updates and feedback on your actions.
- 🖱️ **Context Menu** – Right-click items for quick actions like Open, Edit, or Delete.
- 🧠 **Dynamic Button States** – UI adapts intelligently based on your selection.

### ⌨️ Keyboard Shortcuts

| Shortcut | Action                   |
| -------- | ------------------------ |
| `Ctrl+A` | Add or update favorite   |
| `Ctrl+E` | Edit selected favorite   |
| `Delete` | Remove selected favorite |
| `Esc`    | Cancel edit              |

---

## ⚙️ Startup Options

- **Launch on system startup** *(Windows only)* – Enable auto-launch using `pywin32`.
- **Start minimized to tray** – Keep your desktop clean; QuickFavs will run silently in the background.

---

## 🛠️ Installation Guide

### 1. Clone the Repository

```bash
git clone https://github.com/Chipsy99/QuickFavs.git
cd QuickFavs
```

### 2. Install Requirements

```bash
pip install PyQt6
pip install pyinstaller      # For building .exe
pip install pywin32          # Optional: For Windows startup feature
```

### 3. Run the App

```bash
python your_app_file_name.py
```

Replace `your_app_file_name.py` with your actual script, such as `main.py` or `quickfavs.py`.

---

## 🧩 Build a Standalone Executable (.exe)

You can turn QuickFavs into a single-file executable using PyInstaller:

```bash
pyinstaller --noconsole --onefile --windowed --icon="C:/Users/User/Desktop/icon.ico" your_app_file_name.py
```

**Flags explained:**

- `--noconsole`: No command prompt window
- `--onefile`: Bundle everything into one file
- `--windowed`: Mark as a GUI app
- `--icon`: Custom app icon (adjust path as needed)

Output will be found in the `dist/` directory.

---

## 📌 Pin to Windows Taskbar

1. Launch `QuickFavs.exe` from the `dist/` folder.
2. Right-click its icon in the taskbar.
3. Select **Pin to taskbar** for easy access.

---

## 🗂️ File Structure

| File             | Description                          |
| ---------------- | ------------------------------------ |
| `favorites.json` | Stores saved favorites.              |
| `settings.json`  | Stores app preferences and settings. |

---

## 🚀 How to Use QuickFavs

### ➕ Add a Favorite

1. Fill in the **Name** and **Path or URL** fields.
2. Choose a type: **File**, **Folder**, **URL**, or **App**.
3. Optionally, add **Tags** and a **Description**.
4. Click **Add**.

💡 You can also drag and drop an item into the app to auto-fill its info.

### 🟢 Open a Favorite

- Double-click the item in the list.
- Or right-click and select **Open**.

### 📝 Edit a Favorite

- Select the favorite and click **Edit** or press `Ctrl+E`.
- Make changes, then click **Update**.
- Press `Esc` to cancel editing.

### ❌ Delete a Favorite

- Select the favorite and click **Delete Selected** or press `Delete`.
- Confirm in the prompt to complete deletion.

### 🔍 Search Your Favorites

- Use the search field to filter favorites by any attribute (name, type, tag, description).

### 🧭 Using the System Tray

- Click **Exit** to minimize the app to tray.
- Click the tray icon to restore it.
- Right-click the tray icon to quickly open a favorite or close the app.

---

## 📥 Pre-built Releases

Visit the [Releases Page](https://github.com/Chipsy99/QuickFavs/releases) to download pre-built executables (if available).

---

## 🤝 Contributing

We welcome contributions of all kinds!

- Found a bug or have a suggestion? Open an **Issue**.
- Want to improve or add features? Submit a **Pull Request**.

---

## 📄 License

> **MIT License** – Simple and permissive.

You’re free to use, modify, and distribute this project. Don’t forget to add a `LICENSE` file to your repository.

---

✨ This document has been carefully refined to ensure smooth readability, proper grammar, and consistency across all sections. Let QuickFavs boost your daily workflow with elegance and speed!


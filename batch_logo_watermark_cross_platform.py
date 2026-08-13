import os
import sys
import json
import shutil
import threading
import tempfile
import re
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image, ImageTk

try:
    import gdown
except ImportError:
    gdown = None

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
except ImportError:
    arabic_reshaper = None
    get_display = None


EXTS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff")

SETTINGS_FILE = os.path.join(
    os.path.expanduser("~"),
    ".batch_logo_watermark_settings.json"
)

DRIVE_CACHE = os.path.join(
    tempfile.gettempdir(),
    "BatchLogoWatermark_GDrive"
)

POSITIONS = [
    "Top Left", "Top Center", "Top Right",
    "Middle Left", "Center", "Middle Right",
    "Bottom Left", "Bottom Center", "Bottom Right"
]

TEXT = {
    "ar": {
        "title": "Batch Logo Watermark",
        "subtitle": "إضافة لوجو وتغيير مقاس عدد كبير من الصور بسهولة",
        "system": "النظام",
        "light": "فاتح",
        "dark": "داكن",
        "files": "الملفات",
        "local_folder": "مجلد الصور",
        "logo": "اللوجو PNG",
        "output": "مجلد الحفظ",
        "choose": "اختيار",
        "drive": "Google Drive",
        "drive_hint": "ضع رابط مجلد Google Drive المشترك",
        "drive_url": "رابط Google Drive",
        "download": "تحميل الصور وعرضها",
        "drive_note": "يجب أن يكون المجلد متاحًا: أي شخص لديه الرابط",
        "use_drive_source": "استخدم Google Drive كمصدر وتخطَّ مجلد الصور",
        "logo_settings": "إعدادات اللوجو",
        "default_position": "المكان الافتراضي",
        "logo_size": "حجم اللوجو",
        "opacity": "الشفافية",
        "margin": "الهامش",
        "output_size": "مقاس الصور الناتجة",
        "resize": "تغيير المقاس قبل إضافة اللوجو",
        "width": "العرض",
        "height": "الارتفاع",
        "update_size": "تحديث المقاس",
        "cover": "قص لملء المقاس",
        "contain": "بدون قص",
        "preview": "المعاينة",
        "count": "عدد الصور",
        "columns": "عدد الأعمدة",
        "update_preview": "تحديث المعاينة",
        "gallery": "معرض الصور",
        "select_all": "تحديد الكل",
        "clear": "إلغاء التحديد",
        "apply_selected": "تطبيق على المحدد",
        "selected": "محدد",
        "ready": "جاهز",
        "start": "ابدأ المعالجة",
        "processing": "جاري المعالجة...",
        "found": "تم العثور على {} صورة",
        "choose_source": "اختر مجلد الصور لعرض المعاينة",
        "no_logo": "اختر اللوجو أولًا",
        "download_started": "جاري تحميل الصور من Google Drive...",
        "download_done": "تم تحميل {} صورة من Google Drive",
        "download_error": "تعذر تحميل Google Drive",
        "drive_folder_only": "استخدم رابط مجلد Google Drive، وليس رابط ملف منفرد.",
        "drive_permission": "تأكد أن المجلد مضبوط على: أي شخص لديه الرابط يمكنه العرض.",
        "error": "خطأ",
        "success": "اكتملت المعالجة",
        "done": "تمت معالجة {} صورة.",
        "save_to": "مكان الحفظ:",
        "errors": "فشل في {} صورة.",
        "close_processing": "المعالجة ما زالت تعمل. هل تريد الإغلاق؟",
        "theme": "المظهر",
        "language": "اللغة",
        "arabic": "العربية",
        "english": "English",
        "position": {
            "Top Left": "أعلى يسار",
            "Top Center": "أعلى وسط",
            "Top Right": "أعلى يمين",
            "Middle Left": "وسط يسار",
            "Center": "منتصف",
            "Middle Right": "وسط يمين",
            "Bottom Left": "أسفل يسار",
            "Bottom Center": "أسفل وسط",
            "Bottom Right": "أسفل يمين"
        }
    },
    "en": {
        "title": "Batch Logo Watermark",
        "subtitle": "Brand and resize large batches of images with ease",
        "system": "System",
        "light": "Light",
        "dark": "Dark",
        "files": "FILES",
        "local_folder": "Image Folder",
        "logo": "Logo PNG",
        "output": "Output Folder",
        "choose": "Browse",
        "drive": "Google Drive",
        "drive_hint": "Paste a shared Google Drive folder link",
        "drive_url": "Google Drive URL",
        "download": "Download & Preview",
        "drive_note": "The folder must be shared as: Anyone with the link",
        "use_drive_source": "Use Google Drive as source (skip image folder)",
        "logo_settings": "LOGO SETTINGS",
        "default_position": "Default position",
        "logo_size": "Logo size",
        "opacity": "Opacity",
        "margin": "Margin",
        "output_size": "OUTPUT SIZE",
        "resize": "Resize before adding logo",
        "width": "Width",
        "height": "Height",
        "update_size": "Update size",
        "cover": "Cover",
        "contain": "Contain",
        "preview": "PREVIEW",
        "count": "Images",
        "columns": "Columns",
        "update_preview": "Refresh preview",
        "gallery": "Preview Gallery",
        "select_all": "Select all",
        "clear": "Clear",
        "apply_selected": "Apply to selected",
        "selected": "Selected",
        "ready": "Ready",
        "start": "Start Processing",
        "processing": "Processing...",
        "found": "{} images found",
        "choose_source": "Choose an image folder to preview",
        "no_logo": "Choose a logo first",
        "download_started": "Downloading images from Google Drive...",
        "download_done": "{} images downloaded from Google Drive",
        "download_error": "Google Drive download failed",
        "drive_folder_only": "Use a Google Drive folder link, not a single-file link.",
        "drive_permission": "Make sure the folder is shared as: Anyone with the link can view.",
        "error": "Error",
        "success": "Processing complete",
        "done": "{} images processed.",
        "save_to": "Saved to:",
        "errors": "{} images failed.",
        "close_processing": "Processing is still running. Close anyway?",
        "theme": "Theme",
        "language": "Language",
        "arabic": "العربية",
        "english": "English",
        "position": {
            "Top Left": "Top Left",
            "Top Center": "Top Center",
            "Top Right": "Top Right",
            "Middle Left": "Middle Left",
            "Center": "Center",
            "Middle Right": "Middle Right",
            "Bottom Left": "Bottom Left",
            "Bottom Center": "Bottom Center",
            "Bottom Right": "Bottom Right"
        }
    }
}


class ModernWatermarkApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.lang = "en"
        self.processing = False
        self.files = []
        self.logo_image = None
        self.cards = {}
        self.position_overrides = {}
        self.selected = set()
        self.preview_images = {}
        self.drive_source = False
        self.use_drive_source = tk.BooleanVar(value=False)

        self.input_dir = tk.StringVar()
        self.logo_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.drive_url = tk.StringVar()

        self.position = tk.StringVar(value="Bottom Right")
        self.size_pct = tk.IntVar(value=20)
        self.opacity = tk.IntVar(value=100)
        self.resize_enabled = tk.BooleanVar(value=True)

        self.set_window_icon()
        self.load_settings()
        self.configure_tk_fonts()
        self.build_ui()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(150, self.refresh_grid)

    def font_family(self):
        if self.lang != "ar":
            return "Segoe UI"

        try:
            families = set(tkfont.families())
            if "Cairo" in families:
                return "Cairo"
        except Exception:
            pass

        return "Segoe UI"

    def app_font(self, size=13, weight="normal"):
        return ctk.CTkFont(
            family=self.font_family(),
            size=size,
            weight=weight
        )

    def configure_tk_fonts(self):
        family = self.font_family()
        for name in (
            "TkDefaultFont", "TkTextFont", "TkMenuFont",
            "TkHeadingFont", "TkCaptionFont",
            "TkSmallCaptionFont", "TkIconFont", "TkTooltipFont"
        ):
            try:
                tkfont.nametofont(name).configure(family=family)
            except Exception:
                pass

    # ============================================================
    # Arabic rendering
    # ============================================================

    def tr(self, key):
        value = TEXT[self.lang][key]
        return self.shape_ar(value) if self.lang == "ar" else value

    def shape_ar(self, text):
        if not isinstance(text, str):
            return text

        if arabic_reshaper is None or get_display is None:
            return text

        try:
            return get_display(arabic_reshaper.reshape(text))
        except Exception:
            return text

    def position_label(self, position):
        return self.shape_ar(TEXT["ar"]["position"][position]) if self.lang == "ar" else TEXT["en"]["position"][position]

    def position_values(self):
        return [self.position_label(p) for p in POSITIONS]

    def position_from_label(self, label):
        for p in POSITIONS:
            if self.position_label(p) == label:
                return p
        return "Bottom Right"

    # ============================================================
    # UI
    # ============================================================

    def build_ui(self):
        for child in self.winfo_children():
            child.destroy()

        self.title(self.tr("title"))
        self.geometry("1320x880")
        self.minsize(1080, 740)

        rtl = self.lang == "ar"

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        title = ctk.CTkLabel(
            header,
            text=self.tr("title"),
            font=self.app_font(size=23, weight="bold")
        )
        title.grid(row=0, column=0, padx=22, pady=(14, 0), sticky="e" if rtl else "w")

        subtitle = ctk.CTkLabel(
            header,
            text=self.tr("subtitle"),
            font=self.app_font(size=12),
            text_color=("gray45", "gray65")
        )
        subtitle.grid(row=1, column=0, padx=22, pady=(0, 12), sticky="e" if rtl else "w")

        language = ctk.CTkSegmentedButton(
            header,
            values=[self.tr("arabic"), self.tr("english")],
            command=self.switch_language,
            width=170
        )
        language.grid(row=0, column=1, rowspan=2, padx=10, pady=15)
        language.set(self.tr("arabic") if rtl else self.tr("english"))

        theme = ctk.CTkSegmentedButton(
            header,
            values=[self.tr("system"), self.tr("light"), self.tr("dark")],
            command=self.change_theme,
            width=230
        )
        theme.grid(row=0, column=2, rowspan=2, padx=18, pady=15)
        theme.set(self.tr("light"))
        ctk.set_appearance_mode("Light")

        # Sidebar
        sidebar_col = 1 if rtl else 0
        main_col = 0 if rtl else 1

        sidebar = ctk.CTkScrollableFrame(
            self, width=330, corner_radius=0
        )
        sidebar.grid(
            row=1,
            column=sidebar_col,
            sticky="nsew",
            padx=(10, 5) if not rtl else (5, 10),
            pady=10
        )

        self.card_title(sidebar, self.tr("files"))

        self.file_row(sidebar, self.tr("local_folder"), self.input_dir, self.pick_input)
        self.file_row(sidebar, self.tr("logo"), self.logo_path, self.pick_logo)
        self.file_row(sidebar, self.tr("output"), self.output_dir, self.pick_output)

        # Google Drive
        self.card_title(sidebar, self.tr("drive"))

        self.drive_hint_label = ctk.CTkLabel(
            sidebar,
            text=self.tr("drive_hint"),
            text_color=("gray40", "gray70"),
            wraplength=280,
            justify="right" if rtl else "left"
        )
        self.drive_hint_label.pack(fill="x", padx=10, pady=(0, 5))

        self.drive_entry = ctk.CTkEntry(
            sidebar,
            textvariable=self.drive_url,
            justify="right" if rtl else "left",
            placeholder_text=self.tr("drive_url")
        )
        self.bind_paste(self.drive_entry)
        self.drive_entry.pack(fill="x", padx=10, pady=5)

        self.drive_button = ctk.CTkButton(
            sidebar,
            text=self.tr("download"),
            height=38,
            command=self.download_drive
        )
        self.drive_button.pack(fill="x", padx=10, pady=(2, 5))

        ctk.CTkLabel(
            sidebar,
            text=self.tr("drive_note"),
            text_color=("gray50", "gray65"),
            wraplength=280,
            justify="right" if rtl else "left"
        ).pack(fill="x", padx=10, pady=(0, 10))

        self.drive_source_check = ctk.CTkCheckBox(
            sidebar,
            text=self.tr("use_drive_source"),
            variable=self.use_drive_source,
            command=self.drive_source_toggle
        )
        self.drive_source_check.pack(
            anchor="e" if rtl else "w",
            padx=10,
            pady=(0, 10)
        )

        # Logo settings
        self.card_title(sidebar, self.tr("logo_settings"))

        self.add_label(sidebar, self.tr("default_position"))
        self.position_combo = ctk.CTkComboBox(
            sidebar,
            values=self.position_values(),
            command=self.position_changed
        )
        self.position_combo.pack(fill="x", padx=10, pady=(0, 9))
        self.position_combo.set(self.position_label(self.position.get()))

        self.slider_block(sidebar, self.tr("logo_size"), self.size_pct, 5, 50, "%")
        self.slider_block(sidebar, self.tr("opacity"), self.opacity, 10, 100, "%")

        self.add_label(sidebar, self.tr("margin"))
        self.margin_entry = ctk.CTkEntry(sidebar)
        self.bind_paste(self.margin_entry)
        self.margin_entry.insert(0, "30")
        self.margin_entry.pack(fill="x", padx=10, pady=(0, 9))

        # Output
        self.card_title(sidebar, self.tr("output_size"))

        ctk.CTkCheckBox(
            sidebar,
            text=self.tr("resize"),
            variable=self.resize_enabled,
            command=self.refresh_grid
        ).pack(anchor="e" if rtl else "w", padx=10, pady=5)

        size_row = ctk.CTkFrame(sidebar, fg_color="transparent")
        size_row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(size_row, text=self.tr("width")).pack(side="right" if rtl else "left")
        self.width_entry = ctk.CTkEntry(size_row, width=80)
        self.bind_paste(self.width_entry)
        self.width_entry.insert(0, "1024")
        self.width_entry.pack(side="right" if rtl else "left", padx=5)

        ctk.CTkLabel(size_row, text="×").pack(side="right" if rtl else "left", padx=4)

        ctk.CTkLabel(size_row, text=self.tr("height")).pack(side="right" if rtl else "left")
        self.height_entry = ctk.CTkEntry(size_row, width=80)
        self.bind_paste(self.height_entry)
        self.height_entry.insert(0, "1024")
        self.height_entry.pack(side="right" if rtl else "left", padx=5)

        ctk.CTkButton(
            sidebar,
            text=self.tr("update_size"),
            height=34,
            command=self.refresh_grid
        ).pack(fill="x", padx=10, pady=(4, 8))

        self.resize_mode_combo = ctk.CTkSegmentedButton(
            sidebar,
            values=[self.tr("cover"), self.tr("contain")],
            command=lambda _: self.refresh_grid()
        )
        self.resize_mode_combo.pack(fill="x", padx=10, pady=(0, 12))
        self.resize_mode_combo.set(self.tr("cover"))

        # Preview
        self.card_title(sidebar, self.tr("preview"))

        row = ctk.CTkFrame(sidebar, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row, text=self.tr("count")).pack(side="right" if rtl else "left")
        self.count_entry = ctk.CTkEntry(row, width=65)
        self.bind_paste(self.count_entry)
        self.count_entry.insert(0, "12")
        self.count_entry.pack(side="left" if rtl else "right")

        row2 = ctk.CTkFrame(sidebar, fg_color="transparent")
        row2.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(row2, text=self.tr("columns")).pack(side="right" if rtl else "left")
        self.columns_entry = ctk.CTkEntry(row2, width=65)
        self.bind_paste(self.columns_entry)
        self.columns_entry.insert(0, "3")
        self.columns_entry.pack(side="left" if rtl else "right")

        ctk.CTkButton(
            sidebar,
            text=self.tr("update_preview"),
            command=self.refresh_grid
        ).pack(fill="x", padx=10, pady=(8, 12))

        # Main gallery
        main = ctk.CTkFrame(self, corner_radius=14)
        main.grid(
            row=1, column=main_col,
            sticky="nsew",
            padx=(5, 10) if not rtl else (10, 5),
            pady=10
        )
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        toolbar = ctk.CTkFrame(main, fg_color="transparent")
        toolbar.grid(row=0, column=0, sticky="ew", padx=12, pady=10)
        toolbar.grid_columnconfigure(5, weight=1)

        ctk.CTkLabel(
            toolbar,
            text=self.tr("gallery"),
            font=self.app_font(size=18, weight="bold")
        ).grid(row=0, column=0, padx=8)

        ctk.CTkButton(
            toolbar, text=self.tr("select_all"),
            width=105, command=self.select_all_visible
        ).grid(row=0, column=1, padx=4)

        ctk.CTkButton(
            toolbar, text=self.tr("clear"),
            width=80, command=self.clear_selection
        ).grid(row=0, column=2, padx=4)

        self.batch_position_combo = ctk.CTkComboBox(
            toolbar,
            values=self.position_values(),
            width=155
        )
        self.batch_position_combo.grid(row=0, column=3, padx=(12, 4))
        self.batch_position_combo.set(self.position_label(self.position.get()))

        ctk.CTkButton(
            toolbar,
            text=self.tr("apply_selected"),
            width=135,
            command=self.apply_position_to_selected
        ).grid(row=0, column=4, padx=4)

        self.selection_label = ctk.CTkLabel(
            toolbar,
            text=f"{self.tr('selected')}: 0"
        )
        self.selection_label.grid(row=0, column=5, sticky="e" if not rtl else "w", padx=8)

        self.gallery = ctk.CTkScrollableFrame(main, corner_radius=10)
        self.gallery.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Footer
        footer = ctk.CTkFrame(self, corner_radius=0)
        footer.grid(row=2, column=0, columnspan=2, sticky="ew")
        footer.grid_columnconfigure(0, weight=1)

        self.status_label = ctk.CTkLabel(
            footer, text=self.tr("ready"), anchor="e" if rtl else "w"
        )
        self.status_label.grid(row=0, column=0, padx=18, pady=(7, 0), sticky="ew")

        self.progress = ctk.CTkProgressBar(footer, height=8)
        self.progress.grid(row=1, column=0, padx=18, pady=(3, 9), sticky="ew")
        self.progress.set(0)

        self.process_btn = ctk.CTkButton(
            footer,
            text=self.tr("start"),
            height=42,
            font=self.app_font(size=14, weight="bold"),
            command=self.start_processing
        )
        self.process_btn.grid(row=0, column=1, rowspan=2, padx=18, pady=8)

        ctk.CTkLabel(
            footer,
            text="Powered by Hossam Ibrahim © 2026",
            text_color=("gray45", "gray65")
        ).grid(row=0, column=2, rowspan=2, padx=(0, 18))

    def card_title(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            font=self.app_font(size=12, weight="bold"),
            text_color=("#1f6aa5", "#5fa8dc")
        ).pack(anchor="e" if self.lang == "ar" else "w", padx=12, pady=(13, 7))

    def add_label(self, parent, text):
        ctk.CTkLabel(
            parent,
            text=text,
            anchor="e" if self.lang == "ar" else "w"
        ).pack(fill="x", padx=10, pady=(0, 4))


    def bind_paste(self, entry):
        def paste(event=None):
            try:
                text = self.clipboard_get()
                if text:
                    entry.delete(0, "end")
                    entry.insert("insert", text)
                return "break"
            except Exception:
                return "break"

        entry.bind("<Control-v>", paste)
        entry.bind("<Control-V>", paste)
        entry.bind("<Shift-Insert>", paste)
        entry.bind("<Button-3>", lambda event: self.show_paste_menu(event, entry))

    def show_paste_menu(self, event, entry):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(
            label="Paste" if self.lang == "en" else "لصق",
            command=lambda: self._paste_into_entry(entry)
        )
        menu.add_command(
            label="Select All" if self.lang == "en" else "تحديد الكل",
            command=lambda: entry.select_range(0, "end")
        )
        menu.tk_popup(event.x_root, event.y_root)

    def _paste_into_entry(self, entry):
        try:
            text = self.clipboard_get()
            if text:
                entry.delete(0, "end")
                entry.insert(0, text)
                entry.focus_set()
        except Exception:
            pass

    def file_row(self, parent, label, variable, command):
        rtl = self.lang == "ar"

        ctk.CTkLabel(
            parent, text=label,
            anchor="e" if rtl else "w"
        ).pack(fill="x", padx=10, pady=(2, 3))

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 8))

        entry = ctk.CTkEntry(
            row,
            textvariable=variable,
            justify="right" if rtl else "left"
        )
        self.bind_paste(entry)
        entry.pack(side="right" if rtl else "left", fill="x", expand=True)

        ctk.CTkButton(
            row, text=self.tr("choose"), width=62,
            command=command
        ).pack(side="left" if rtl else "right", padx=(6, 0))

    def slider_block(self, parent, label, variable, start, end, suffix):
        rtl = self.lang == "ar"

        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(row, text=label, width=75).pack(
            side="right" if rtl else "left"
        )

        slider = ctk.CTkSlider(
            row, from_=start, to=end,
            variable=variable,
            command=lambda _: self.refresh_grid()
        )
        slider.pack(side="right" if rtl else "left", fill="x", expand=True, padx=7)

        value = ctk.CTkLabel(row, text=f"{variable.get()} {suffix}", width=48)
        value.pack(side="left" if rtl else "right")

        def update_value(*_):
            value.configure(text=f"{int(variable.get())} {suffix}")

        variable.trace_add("write", update_value)

    # ============================================================
    # Language / theme
    # ============================================================

    def switch_language(self, value):
        if value == self.tr("arabic"):
            self.lang = "ar"
        else:
            self.lang = "en"

        self.configure_tk_fonts()
        self.build_ui()
        self.refresh_grid()

    def change_theme(self, value):
        if value == self.tr("dark"):
            ctk.set_appearance_mode("Dark")
        elif value == self.tr("light"):
            ctk.set_appearance_mode("Light")
        else:
            ctk.set_appearance_mode("System")

    # ============================================================
    # Google Drive
    # ============================================================

    def extract_drive_folder_id(self, url):
        patterns = [
            r"drive\.google\.com/drive/(?:u/\d+/)?folders/([a-zA-Z0-9_-]+)",
            r"drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    def drive_source_toggle(self):
        if self.use_drive_source.get() and self.files:
            self.output_dir.set(
                os.path.join(DRIVE_CACHE, "watermarked")
            )

    def download_drive(self):
        if self.processing:
            return

        url = self.drive_url.get().strip()

        if not url:
            messagebox.showerror(
                self.tr("error"),
                self.tr("drive_url")
            )
            return

        folder_id = self.extract_drive_folder_id(url)

        if not folder_id:
            messagebox.showerror(
                self.tr("error"),
                self.tr("drive_folder_only")
            )
            return

        if gdown is None:
            messagebox.showerror(
                self.tr("error"),
                "gdown is not installed.\nInstall it with: pip install gdown"
            )
            return

        self.drive_button.configure(
            state="disabled",
            text=self.tr("download_started")
        )
        self.status_label.configure(text=self.tr("download_started"))
        self.progress.set(0)

        threading.Thread(
            target=self.drive_worker,
            args=(url,),
            daemon=True
        ).start()

    def drive_worker(self, url):
        try:
            if os.path.isdir(DRIVE_CACHE):
                shutil.rmtree(DRIVE_CACHE, ignore_errors=True)
            os.makedirs(DRIVE_CACHE, exist_ok=True)

            # gdown 6.x supports public folders with more than 50 files.
            # Pass the folder ID directly and disable cookie usage so a stale
            # local Google Drive cookie cannot break a public-folder download.
            gdown.download_folder(
                id=self.extract_drive_folder_id(url),
                output=DRIVE_CACHE,
                quiet=True,
                use_cookies=False
            )

            image_files = []
            for root, _, names in os.walk(DRIVE_CACHE):
                for name in names:
                    if name.lower().endswith(EXTS):
                        image_files.append(
                            os.path.join(root, name)
                        )

            image_files.sort()

            if not image_files:
                raise RuntimeError("No supported image files found.")

            self.after(
                0,
                self.drive_finished,
                image_files
            )

        except Exception as e:
            self.after(
                0,
                self.drive_failed,
                str(e)
            )

    def drive_finished(self, image_files):
        self.drive_source = True
        self.use_drive_source.set(True)
        self.files = image_files
        self.selected.clear()
        self.position_overrides.clear()

        self.input_dir.set(DRIVE_CACHE)
        self.output_dir.set(
            os.path.join(DRIVE_CACHE, "watermarked")
        )

        self.drive_button.configure(
            state="normal",
            text=self.tr("download")
        )

        self.status_label.configure(
            text=self.tr("download_done").format(len(image_files))
        )

        self.progress.set(1)
        self.refresh_grid()

    def drive_failed(self, error):
        self.drive_button.configure(
            state="normal",
            text=self.tr("download")
        )
        self.progress.set(0)
        self.status_label.configure(
            text=self.tr("download_error")
        )

        messagebox.showerror(
            self.tr("download_error"),
            self.tr("drive_permission") + "\n\n" + error
        )

    # ============================================================
    # Local files
    # ============================================================

    def pick_input(self):
        p = filedialog.askdirectory(
            title="Choose image folder" if self.lang == "en" else "اختر مجلد الصور"
        )
        if p:
            self.drive_source = False
            self.use_drive_source.set(False)
            self.input_dir.set(p)
            self.load_files()
            self.refresh_grid()

    def pick_logo(self):
        p = filedialog.askopenfilename(
            title="Choose logo" if self.lang == "en" else "اختر اللوجو",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        if p:
            self.logo_path.set(p)
            try:
                self.logo_image = Image.open(p).convert("RGBA")
            except Exception:
                self.logo_image = None
                messagebox.showerror(
                    self.tr("error"),
                    "Could not open the logo." if self.lang == "en" else "تعذر فتح ملف اللوجو."
                )
                return

            self.refresh_grid()

    def pick_output(self):
        p = filedialog.askdirectory(
            title="Choose output folder" if self.lang == "en" else "اختر مجلد الحفظ"
        )
        if p:
            self.output_dir.set(p)

    def load_files(self):
        src = self.input_dir.get().strip()

        if not os.path.isdir(src):
            self.files = []
            return

        self.files = sorted([
            os.path.join(src, f)
            for f in os.listdir(src)
            if f.lower().endswith(EXTS)
        ])

        self.selected.intersection_update(self.files)
        self.position_overrides = {
            p: v for p, v in self.position_overrides.items()
            if p in self.files
        }

        self.status_label.configure(
            text=self.tr("found").format(len(self.files))
        )

    # ============================================================
    # Image engine
    # ============================================================

    def get_margin(self):
        try:
            return max(0, int(self.margin_entry.get()))
        except Exception:
            return 30

    def get_size(self):
        if not self.resize_enabled.get():
            return None

        try:
            w = int(self.width_entry.get())
            h = int(self.height_entry.get())
            if w <= 0 or h <= 0:
                raise ValueError
            return w, h
        except Exception:
            return 1024, 1024

    def resize_image(self, img):
        size = self.get_size()

        if size is None:
            return img.copy()

        tw, th = size

        if img.size == (tw, th):
            return img.copy()

        cover_label = self.tr("cover")
        if self.resize_mode_combo.get() == cover_label:
            scale = max(tw / img.width, th / img.height)
            nw = max(1, int(img.width * scale))
            nh = max(1, int(img.height * scale))

            resized = img.resize(
                (nw, nh),
                Image.Resampling.LANCZOS
            )

            left = max(0, (nw - tw) // 2)
            top = max(0, (nh - th) // 2)

            return resized.crop(
                (left, top, left + tw, top + th)
            )

        scale = min(tw / img.width, th / img.height)
        nw = max(1, int(img.width * scale))
        nh = max(1, int(img.height * scale))

        resized = img.resize(
            (nw, nh),
            Image.Resampling.LANCZOS
        )

        canvas = Image.new(
            "RGBA",
            (tw, th),
            (255, 255, 255, 255)
        )
        canvas.alpha_composite(
            resized,
            ((tw - nw) // 2, (th - nh) // 2)
        )

        return canvas

    def position_for(self, path):
        return self.position_overrides.get(
            path,
            self.position.get()
        )

    def apply_logo(self, img, logo, position):
        if logo is None:
            return img

        target_w = max(
            1,
            int(img.width * int(self.size_pct.get()) / 100)
        )

        ratio = target_w / logo.width
        target_h = max(
            1,
            int(logo.height * ratio)
        )

        wm = logo.resize(
            (target_w, target_h),
            Image.Resampling.LANCZOS
        )

        alpha = wm.getchannel("A")
        opacity = max(
            10,
            min(100, int(self.opacity.get()))
        )
        alpha = alpha.point(
            lambda a: int(a * opacity / 100)
        )
        wm.putalpha(alpha)

        margin = self.get_margin()

        if "Left" in position:
            x = margin
        elif "Right" in position:
            x = img.width - target_w - margin
        else:
            x = (img.width - target_w) // 2

        if "Top" in position:
            y = margin
        elif "Bottom" in position:
            y = img.height - target_h - margin
        else:
            y = (img.height - target_h) // 2

        img.alpha_composite(
            wm,
            (max(0, x), max(0, y))
        )

        return img

    def build_image(self, path):
        img = Image.open(path).convert("RGBA")
        img = self.resize_image(img)

        if self.logo_image is not None:
            img = self.apply_logo(
                img,
                self.logo_image,
                self.position_for(path)
            )

        return img

    # ============================================================
    # Gallery
    # ============================================================

    def refresh_grid(self):
        if self.processing or not hasattr(self, "gallery"):
            return

        for child in self.gallery.winfo_children():
            child.destroy()

        self.cards.clear()
        self.preview_images.clear()

        if not self.files:
            ctk.CTkLabel(
                self.gallery,
                text=self.tr("choose_source"),
                font=self.app_font(size=16),
                text_color=("gray45", "gray65")
            ).pack(pady=80)
            return

        try:
            count = max(1, min(500, int(self.count_entry.get())))
        except Exception:
            count = 12

        try:
            columns = max(1, min(8, int(self.columns_entry.get())))
        except Exception:
            columns = 4

        shown = self.files[:count]

        for i, path in enumerate(shown):
            self.create_card(
                path,
                i // columns,
                i % columns
            )

        for c in range(columns):
            self.gallery.grid_columnconfigure(c, weight=1)

        self.update_selection_label()

    def create_card(self, path, row, col):
        rtl = self.lang == "ar"
        selected = path in self.selected

        card = ctk.CTkFrame(
            self.gallery,
            corner_radius=12,
            border_width=2 if selected else 1,
            border_color="#2f80ed" if selected else ("#d8d8d8", "#333333")
        )
        card.grid(
            row=row, column=col,
            padx=6, pady=6,
            sticky="nsew"
        )

        self.cards[path] = {
            "card": card,
            "selected": tk.BooleanVar(value=selected)
        }

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=7, pady=(7, 4))

        ctk.CTkCheckBox(
            top,
            text=self.tr("select_all") if False else (
                "تحديد" if rtl else "Select"
            ),
            variable=self.cards[path]["selected"],
            width=70,
            command=lambda p=path: self.toggle_selected(p)
        ).pack(side="right" if rtl else "left")

        name = os.path.basename(path)
        ctk.CTkLabel(
            top,
            text=name,
            anchor="e" if rtl else "w",
            font=self.app_font(size=10)
        ).pack(
            side="left" if rtl else "right",
            fill="x",
            expand=True,
            padx=5
        )

        canvas = tk.Canvas(
            card,
            width=215,
            height=215,
            bg="#eeeeee",
            highlightthickness=0
        )
        canvas.pack(padx=7, pady=5)

        pos_combo = ctk.CTkComboBox(
            card,
            values=self.position_values(),
            width=205,
            height=30,
            command=lambda value, p=path:
                self.change_position(p, value)
        )
        pos_combo.pack(padx=7, pady=(2, 7))
        pos_combo.set(self.position_label(self.position_for(path)))

        self.cards[path]["canvas"] = canvas
        self.cards[path]["combo"] = pos_combo

        self.render_card(path)

    def render_card(self, path):
        if path not in self.cards:
            return

        try:
            img = self.build_image(path)
            preview = img.copy()
            preview.thumbnail((207, 207), Image.Resampling.LANCZOS)

            bg = Image.new("RGB", preview.size, "white")

            if "A" in preview.getbands():
                bg.paste(
                    preview,
                    mask=preview.getchannel("A")
                )
            else:
                bg.paste(preview)

            photo = ImageTk.PhotoImage(bg)
            self.preview_images[path] = photo

            canvas = self.cards[path]["canvas"]
            canvas.delete("all")
            canvas.create_image(
                107,
                107,
                image=photo,
                anchor="center"
            )

        except Exception:
            pass

    def change_position(self, path, value):
        self.position_overrides[path] = self.position_from_label(value)
        self.render_card(path)

    def position_changed(self, value):
        self.position.set(
            self.position_from_label(value)
        )
        self.batch_position_combo.set(value)
        self.refresh_grid()

    def toggle_selected(self, path):
        if self.cards[path]["selected"].get():
            self.selected.add(path)
        else:
            self.selected.discard(path)

        selected = path in self.selected

        self.cards[path]["card"].configure(
            border_width=2 if selected else 1,
            border_color="#2f80ed" if selected else ("#d8d8d8", "#333333")
        )

        self.update_selection_label()

    def select_all_visible(self):
        try:
            count = max(1, int(self.count_entry.get()))
        except Exception:
            count = 12

        self.selected.update(self.files[:count])
        self.refresh_grid()

    def clear_selection(self):
        self.selected.clear()
        self.refresh_grid()

    def update_selection_label(self):
        if hasattr(self, "selection_label"):
            self.selection_label.configure(
                text=f"{self.tr('selected')}: {len(self.selected)}"
            )

    def apply_position_to_selected(self):
        position = self.position_from_label(
            self.batch_position_combo.get()
        )

        for path in self.selected:
            self.position_overrides[path] = position

        self.refresh_grid()

    # ============================================================
    # Processing
    # ============================================================

    def start_processing(self):
        if self.processing:
            return

        src = self.input_dir.get().strip()
        logo_file = self.logo_path.get().strip()

        # When Google Drive is selected as the source, the local image-folder
        # picker is intentionally skipped.
        if self.use_drive_source.get():
            if not self.files or not self.drive_source:
                messagebox.showerror(
                    self.tr("error"),
                    self.tr("download_started")
                )
                return

            src = DRIVE_CACHE
        else:
            if not os.path.isdir(src):
                messagebox.showerror(
                    self.tr("error"),
                    self.tr("local_folder")
                )
                return

        if not os.path.isfile(logo_file):
            messagebox.showerror(
                self.tr("error"),
                self.tr("no_logo")
            )
            return

        out = self.output_dir.get().strip()
        if not out:
            out = os.path.join(src, "watermarked")
            self.output_dir.set(out)

        os.makedirs(out, exist_ok=True)

        size = self.get_size()

        settings = {
            "src": src,
            "out": out,
            "logo_file": logo_file,
            "files": list(self.files),
            "resize": self.resize_enabled.get(),
            "size": size,
            "mode": "cover" if self.resize_mode_combo.get() == self.tr("cover") else "contain",
            "size_pct": int(self.size_pct.get()),
            "opacity": int(self.opacity.get()),
            "margin": self.get_margin(),
            "default_position": self.position.get(),
            "overrides": dict(self.position_overrides)
        }

        self.processing = True
        self.process_btn.configure(
            state="disabled",
            text=self.tr("processing")
        )
        self.progress.set(0)

        threading.Thread(
            target=self.worker_process,
            args=(settings,),
            daemon=True
        ).start()

    def worker_process(self, settings):
        done = 0
        errors = []
        files = settings["files"]

        try:
            logo = Image.open(
                settings["logo_file"]
            ).convert("RGBA")

            total = len(files)

            for i, name in enumerate(files, 1):
                try:
                    path = os.path.join(
                        settings["src"],
                        name
                    )
                    img = Image.open(path).convert("RGBA")

                    if settings["resize"] and settings["size"]:
                        tw, th = settings["size"]

                        if settings["mode"] == "cover":
                            scale = max(
                                tw / img.width,
                                th / img.height
                            )
                            nw = max(1, int(img.width * scale))
                            nh = max(1, int(img.height * scale))

                            img = img.resize(
                                (nw, nh),
                                Image.Resampling.LANCZOS
                            )

                            left = max(0, (nw - tw) // 2)
                            top = max(0, (nh - th) // 2)

                            img = img.crop(
                                (
                                    left,
                                    top,
                                    left + tw,
                                    top + th
                                )
                            )
                        else:
                            scale = min(
                                tw / img.width,
                                th / img.height
                            )
                            nw = max(1, int(img.width * scale))
                            nh = max(1, int(img.height * scale))

                            resized = img.resize(
                                (nw, nh),
                                Image.Resampling.LANCZOS
                            )

                            canvas = Image.new(
                                "RGBA",
                                (tw, th),
                                (255, 255, 255, 255)
                            )

                            canvas.alpha_composite(
                                resized,
                                (
                                    (tw - nw) // 2,
                                    (th - nh) // 2
                                )
                            )
                            img = canvas

                    target_w = max(
                        1,
                        int(img.width * settings["size_pct"] / 100)
                    )

                    ratio = target_w / logo.width
                    target_h = max(
                        1,
                        int(logo.height * ratio)
                    )

                    wm = logo.resize(
                        (target_w, target_h),
                        Image.Resampling.LANCZOS
                    )

                    alpha = wm.getchannel("A")
                    alpha = alpha.point(
                        lambda a: int(
                            a * settings["opacity"] / 100
                        )
                    )
                    wm.putalpha(alpha)

                    position = settings["overrides"].get(
                        path,
                        settings["default_position"]
                    )

                    margin = settings["margin"]

                    if "Left" in position:
                        x = margin
                    elif "Right" in position:
                        x = img.width - target_w - margin
                    else:
                        x = (img.width - target_w) // 2

                    if "Top" in position:
                        y = margin
                    elif "Bottom" in position:
                        y = img.height - target_h - margin
                    else:
                        y = (img.height - target_h) // 2

                    img.alpha_composite(
                        wm,
                        (max(0, x), max(0, y))
                    )

                    ext = os.path.splitext(name)[1].lower()

                    # Google Drive downloads can include nested folders.
                    # Flatten output names while preserving the original filename.
                    base_name = os.path.basename(name)
                    out_path = os.path.join(
                        settings["out"],
                        os.path.splitext(base_name)[0] + ext
                    )

                    if ext in (".jpg", ".jpeg"):
                        img.convert("RGB").save(
                            out_path,
                            quality=95,
                            optimize=True
                        )
                    elif ext == ".webp":
                        img.save(
                            out_path,
                            quality=95,
                            method=6
                        )
                    else:
                        img.save(out_path)

                    done += 1

                except Exception as e:
                    errors.append(f"{name}: {e}")

                pct = i / total if total else 0

                self.after(
                    0,
                    self.update_progress,
                    pct,
                    i,
                    total,
                    name
                )

        except Exception as e:
            errors.append(str(e))

        self.after(
            0,
            self.processing_finished,
            done,
            errors,
            settings["out"]
        )

    def update_progress(self, pct, current, total, name):
        self.progress.set(pct)
        self.status_label.configure(
            text=f"{current}/{total} • {int(pct * 100)}% • {name}"
        )

    def processing_finished(self, done, errors, out):
        self.processing = False

        self.process_btn.configure(
            state="normal",
            text=self.tr("start")
        )

        self.progress.set(1 if done else 0)

        self.status_label.configure(
            text=self.tr("done").format(done)
        )

        msg = (
            self.tr("done").format(done)
            + "\n\n"
            + self.tr("save_to")
            + "\n"
            + out
        )

        if errors:
            msg += "\n\n" + self.tr("errors").format(len(errors))

        messagebox.showinfo(
            self.tr("success"),
            msg
        )

    # ============================================================
    # Settings
    # ============================================================

    def load_settings(self):
        if not os.path.isfile(SETTINGS_FILE):
            return

        try:
            with open(
                SETTINGS_FILE,
                "r",
                encoding="utf-8"
            ) as f:
                data = json.load(f)

            self.size_pct.set(
                int(data.get("size_pct", 20))
            )
            self.opacity.set(
                int(data.get("opacity", 100))
            )

        except Exception:
            pass

    def save_settings(self):
        try:
            data = {
                "size_pct": int(self.size_pct.get()),
                "opacity": int(self.opacity.get())
            }

            with open(
                SETTINGS_FILE,
                "w",
                encoding="utf-8"
            ) as f:
                json.dump(
                    data,
                    f,
                    ensure_ascii=False,
                    indent=2
                )

        except Exception:
            pass

    # ============================================================
    # Window
    # ============================================================

    def resource_path(self, filename):
        """Return a path that works both from Python and a PyInstaller bundle."""
        if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
            base = sys._MEIPASS
        else:
            base = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base, filename)

    def set_window_icon(self):
        # Windows supports iconbitmap(.ico). macOS uses the .icns app icon
        # at the bundle level, so do not call iconbitmap there.
        if sys.platform.startswith("win"):
            try:
                icon_path = self.resource_path("app.ico")
                if os.path.isfile(icon_path):
                    self.iconbitmap(icon_path)
            except Exception:
                pass

    def on_close(self):
        if self.processing:
            if not messagebox.askyesno(
                self.tr("error"),
                self.tr("close_processing")
            ):
                return

        self.save_settings()
        self.destroy()


if __name__ == "__main__":
    app = ModernWatermarkApp()
    app.mainloop()

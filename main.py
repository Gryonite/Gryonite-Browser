import json
import sys
from pathlib import Path
from urllib.parse import quote

from PySide6.QtCore import QUrl, QTimer
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QTabWidget,
    QToolBar,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWebEngineCore import QWebEngineProfile, QWebEnginePage
from PySide6.QtWebEngineWidgets import QWebEngineView

from adblock import YinAdBlocker


APP_NAME = "Yin Browser"

APP_DIR = Path.home() / "YinBrowser"
SETTINGS_FILE = APP_DIR / "settings.json"

SEARCH_ENGINES = {
    "Google": "https://www.google.com/search?q=",
    "Bing": "https://www.bing.com/search?q=",
    "DuckDuckGo": "https://duckduckgo.com/?q=",
}

DEFAULT_SETTINGS = {
    "search_engine": "Google",
    "theme": "Dark",
    "accent": "#8b7cff",
    "startup": "Yin Home",
    "zoom": "100%",
    "adblock_enabled": True,
}

ACCENT_COLORS = {
    "Yin Purple": "#8b7cff",
    "Ocean Blue": "#4d9dff",
    "Mint": "#49c6a8",
    "Rose": "#ee719b",
    "Amber": "#e6a23c",
}


def load_settings():
    APP_DIR.mkdir(parents=True, exist_ok=True)
    settings = DEFAULT_SETTINGS.copy()

    try:
        with SETTINGS_FILE.open("r", encoding="utf-8") as file:
            saved = json.load(file)

        for key in settings:
            if key in saved:
                settings[key] = saved[key]

    except (OSError, json.JSONDecodeError):
        pass

    if settings["search_engine"] not in SEARCH_ENGINES:
        settings["search_engine"] = "Google"

    if settings["theme"] not in ("Dark", "Light", "System"):
        settings["theme"] = "Dark"

    if settings["startup"] not in ("Yin Home", "Blank Page"):
        settings["startup"] = "Yin Home"

    if settings["zoom"] not in (
        "80%", "90%", "100%", "110%", "125%", "150%"
    ):
        settings["zoom"] = "100%"

    if settings["accent"] not in ACCENT_COLORS.values():
        settings["accent"] = "#8b7cff"

    if not isinstance(settings["adblock_enabled"], bool):
        settings["adblock_enabled"] = True

    return settings


def save_settings(settings):
    APP_DIR.mkdir(parents=True, exist_ok=True)

    with SETTINGS_FILE.open("w", encoding="utf-8") as file:
        json.dump(settings, file, indent=4)


def make_home_html(accent, search_engine):
    search_url = SEARCH_ENGINES[search_engine]

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Yin Home</title>

<style>
* {{ box-sizing: border-box; }}

body {{
    margin: 0;
    min-height: 100vh;
    display: grid;
    place-items: center;
    background: radial-gradient(
        ellipse at top, #292d42 0%, #17191f 55%, #101116 100%
    );
    color: #f2f3f8;
    font-family: "Segoe UI", Arial, sans-serif;
}}

main {{
    width: min(720px, calc(100% - 36px));
    text-align: center;
    margin-top: -5vh;
}}

.logo {{
    width: 76px;
    height: 76px;
    margin: 0 auto 22px;
    display: grid;
    place-items: center;
    border-radius: 24px;
    background: linear-gradient(145deg, {accent}, #4b4d9e);
    box-shadow: 0 12px 40px #0006;
    font-size: 42px;
    font-weight: 700;
}}

h1 {{
    font-size: clamp(38px, 7vw, 58px);
    margin: 0;
    letter-spacing: -2px;
}}

.subtitle {{
    color: #aeb3c7;
    margin: 12px 0 34px;
    font-size: 15px;
}}

form {{
    display: flex;
    gap: 10px;
    padding: 8px;
    border-radius: 15px;
    background: #222530;
    border: 1px solid #3b4053;
    box-shadow: 0 14px 45px #0004;
}}

input {{
    flex: 1;
    min-width: 0;
    background: transparent;
    border: 0;
    outline: 0;
    color: white;
    font-size: 16px;
    padding: 12px 14px;
}}

input::placeholder {{ color: #9298ad; }}

button {{
    border: 0;
    border-radius: 10px;
    padding: 0 20px;
    color: white;
    background: {accent};
    font-size: 15px;
    cursor: pointer;
}}

button:hover {{ filter: brightness(1.12); }}

.section-title {{
    text-align: left;
    color: #9ea4b9;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin: 34px 0 12px 4px;
}}

.links {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
}}

.link {{
    display: block;
    padding: 17px 10px;
    text-decoration: none;
    color: #e7e9f3;
    border: 1px solid #343847;
    border-radius: 13px;
    background: #20232c;
}}

.link:hover {{ background: #2b2f3b; }}

.link span {{
    display: block;
    color: #aeb3c7;
    font-size: 12px;
    margin-top: 6px;
}}

footer {{
    color: #777e94;
    font-size: 12px;
    margin-top: 34px;
}}

@media (max-width: 480px) {{
    .links {{ grid-template-columns: 1fr; }}
    .link {{ padding: 13px; }}
    form {{ gap: 4px; }}
    button {{ padding: 0 13px; }}
}}
</style>
</head>

<body>
<main>
    <div class="logo">Y</div>
    <h1>Yin Browser</h1>
    <p class="subtitle">A quieter place to browse.</p>

    <form id="searchForm">
        <input id="searchInput" type="text"
               placeholder="Search or enter a website"
               autocomplete="off" autofocus>
        <button type="submit">Search</button>
    </form>

    <div class="section-title">Quick links</div>

    <div class="links">
        <a class="link" href="https://www.youtube.com">
            ▶ YouTube <span>Videos and music</span>
        </a>
        <a class="link" href="https://www.wikipedia.org">
            ◈ Wikipedia <span>Explore knowledge</span>
        </a>
        <a class="link" href="https://github.com">
            ⌘ GitHub <span>Projects and code</span>
        </a>
    </div>

    <footer>Yin Browser · Your browsing starts here</footer>
</main>

<script>
document.getElementById("searchForm").addEventListener(
    "submit", function(event) {{
        event.preventDefault();

        const text = document.getElementById("searchInput")
            .value.trim();

        if (!text) return;

        let destination;

        if (/^[a-zA-Z][a-zA-Z0-9+.-]*:\\/\\//.test(text)) {{
            destination = text;
        }} else if (
            /^[\\w-]+(\\.[\\w-]+)+(\\/.*)?$/.test(text)
            && !text.includes(" ")
        ) {{
            destination = "https://" + text;
        }} else {{
            destination = "{search_url}" + encodeURIComponent(text);
        }}

        window.location.href = destination;
    }}
);
</script>
</body>
</html>
"""


def build_stylesheet(theme, accent):
    if theme == "Light":
        background = "#f2f3f8"
        toolbar = "#ffffff"
        text = "#202331"
        field = "#ffffff"
        border = "#d5d8e3"
        tab = "#e7e9f1"
        selected = "#ffffff"
    else:
        background = "#17191f"
        toolbar = "#20232b"
        text = "#eeeeee"
        field = "#111319"
        border = "#414858"
        tab = "#242832"
        selected = "#343a48"

    return f"""
        QMainWindow, QWidget {{
            background: {background};
            color: {text};
        }}

        QToolBar {{
            background: {toolbar};
            border: none;
            spacing: 6px;
            padding: 7px;
        }}

        QPushButton {{
            background: {tab};
            color: {text};
            border: 1px solid {border};
            border-radius: 7px;
            padding: 7px 11px;
        }}

        QPushButton:hover {{ border-color: {accent}; }}

        QPushButton:checked {{
            background: {accent};
            color: white;
        }}

        QLineEdit, QComboBox {{
            background: {field};
            color: {text};
            border: 1px solid {border};
            border-radius: 7px;
            padding: 8px 10px;
        }}

        QComboBox QAbstractItemView {{
            background: {field};
            color: {text};
            selection-background-color: {accent};
        }}

        QTabWidget::pane {{ border: none; }}

        QTabBar::tab {{
            background: {tab};
            color: {text};
            padding: 9px 15px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
        }}

        QTabBar::tab:selected {{
            background: {selected};
            border-bottom: 2px solid {accent};
        }}
    """


class SettingsPage(QWidget):
    def __init__(self, browser_window):
        super().__init__()

        self.browser_window = browser_window

        outer = QHBoxLayout(self)
        outer.setContentsMargins(30, 28, 30, 28)
        outer.setSpacing(24)

        sidebar = QVBoxLayout()

        brand = QLabel("Y I N")
        brand.setStyleSheet(
            "font-size: 20px; font-weight: 800; letter-spacing: 5px;"
        )
        sidebar.addWidget(brand)

        description = QLabel("BROWSER SETTINGS")
        description.setStyleSheet(
            "color: #969db2; font-size: 10px; letter-spacing: 2px;"
        )
        sidebar.addWidget(description)

        self.nav_buttons = []

        for label in ("General", "Appearance", "About"):
            button = QPushButton(label)
            button.setCheckable(True)
            button.setMinimumHeight(40)
            button.clicked.connect(
                lambda checked=False, name=label: self.show_section(name)
            )
            sidebar.addWidget(button)
            self.nav_buttons.append(button)

        sidebar.addStretch()

        save_button = QPushButton("Save settings")
        save_button.setMinimumHeight(42)
        save_button.clicked.connect(self.save)
        sidebar.addWidget(save_button)

        outer.addLayout(sidebar, 1)

        self.sections = QStackedWidget()
        outer.addWidget(self.sections, 4)

        # GENERAL
        general_page = self.make_section(
            "General", "Your browsing, your rules."
        )
        general_form = QFormLayout()
        general_form.setVerticalSpacing(18)

        self.search_combo = QComboBox()
        self.search_combo.addItems(list(SEARCH_ENGINES))
        self.search_combo.setCurrentText(
            browser_window.settings["search_engine"]
        )
        general_form.addRow("Default search engine", self.search_combo)

        self.startup_combo = QComboBox()
        self.startup_combo.addItems(["Yin Home", "Blank Page"])
        self.startup_combo.setCurrentText(
            browser_window.settings["startup"]
        )
        general_form.addRow("When Yin opens", self.startup_combo)

        self.zoom_combo = QComboBox()
        self.zoom_combo.addItems(
            ["80%", "90%", "100%", "110%", "125%", "150%"]
        )
        self.zoom_combo.setCurrentText(
            browser_window.settings["zoom"]
        )
        general_form.addRow("Default webpage zoom", self.zoom_combo)

        self.adblock_combo = QComboBox()
        self.adblock_combo.addItems(["Enabled", "Disabled"])
        self.adblock_combo.setCurrentText(
            "Enabled"
            if browser_window.settings["adblock_enabled"]
            else "Disabled"
        )
        general_form.addRow("Ad blocker", self.adblock_combo)

        self.blocked_label = QLabel("Blocked requests: 0")
        general_form.addRow("AdBlock statistics", self.blocked_label)

        self.blocked_timer = QTimer(self)
        self.blocked_timer.timeout.connect(self.update_blocked_count)
        self.blocked_timer.start(1000)

        general_page.layout().addLayout(general_form)
        general_page.layout().addStretch()
        self.sections.addWidget(general_page)

        # APPEARANCE
        appearance_page = self.make_section(
            "Appearance", "A little personality goes a long way."
        )
        appearance_form = QFormLayout()
        appearance_form.setVerticalSpacing(18)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light", "System"])
        self.theme_combo.setCurrentText(
            browser_window.settings["theme"]
        )
        appearance_form.addRow("Theme", self.theme_combo)

        self.accent_combo = QComboBox()
        for name, color in ACCENT_COLORS.items():
            self.accent_combo.addItem(name, color)

        accent_index = self.accent_combo.findData(
            browser_window.settings["accent"]
        )
        self.accent_combo.setCurrentIndex(max(0, accent_index))
        appearance_form.addRow("Accent color", self.accent_combo)

        appearance_page.layout().addLayout(appearance_form)
        appearance_page.layout().addStretch()
        self.sections.addWidget(appearance_page)

        # ABOUT
        about_page = self.make_section(
            "About Yin", "A custom browser built one feature at a time."
        )

        about_text = QLabel(
            "Yin Browser\n\n"
            "A personal browser with a custom start page and adjustable settings.\n\n"
            "Rendering engine: Qt WebEngine (Chromium-based)\n\n"
            "Your settings are saved locally on this computer.\n\n"
            "AdBlock uses a basic domain blocklist. It may not block every ad."
        )
        about_text.setWordWrap(True)
        about_page.layout().addWidget(about_text)
        about_page.layout().addStretch()
        self.sections.addWidget(about_page)

        self.show_section("General")

    def make_section(self, heading, subtitle):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(18)

        heading_label = QLabel(heading)
        heading_label.setStyleSheet(
            "font-size: 30px; font-weight: 700;"
        )

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(
            "color: #969db2; font-size: 13px;"
        )

        layout.addWidget(heading_label)
        layout.addWidget(subtitle_label)

        return page

    def show_section(self, name):
        indexes = {"General": 0, "Appearance": 1, "About": 2}
        self.sections.setCurrentIndex(indexes[name])

        for button in self.nav_buttons:
            button.setChecked(button.text() == name)

    def update_blocked_count(self):
        count = self.browser_window.adblocker.blocked_count
        self.blocked_label.setText(f"Blocked requests: {count}")

    def save(self):
        settings = self.browser_window.settings

        settings["search_engine"] = self.search_combo.currentText()
        settings["startup"] = self.startup_combo.currentText()
        settings["zoom"] = self.zoom_combo.currentText()
        settings["theme"] = self.theme_combo.currentText()
        settings["accent"] = self.accent_combo.currentData()
        settings["adblock_enabled"] = (
            self.adblock_combo.currentText() == "Enabled"
        )

        self.browser_window.save_current_settings()
        self.browser_window.apply_theme()
        self.browser_window.apply_zoom()

        self.browser_window.adblocker.enabled = (
            settings["adblock_enabled"]
        )

        self.browser_window.refresh_home_tabs()

        self.browser_window.statusBar().showMessage(
            "Yin settings saved successfully.", 3000
        )


class YinBrowser(QMainWindow):
    def __init__(self):
        super().__init__()

        self.settings = load_settings()

        # Create a shared WebEngine profile and attach the blocker
        # before creating any browser tabs.
        self.profile = QWebEngineProfile("YinBrowserProfile", self)
        self.adblocker = YinAdBlocker(self.profile)
        self.adblocker.enabled = self.settings["adblock_enabled"]
        self.profile.setUrlRequestInterceptor(self.adblocker)

        self.setWindowTitle(APP_NAME)
        self.resize(1240, 820)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.currentChanged.connect(self.update_address_bar)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.setCentralWidget(self.tabs)

        toolbar = QToolBar("Navigation")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        buttons = [
            ("←", "Back", self.go_back),
            ("→", "Forward", self.go_forward),
            ("⟳", "Reload", self.reload_page),
            ("⌂", "Yin Home", self.go_home),
        ]

        for label, tooltip, callback in buttons:
            button = QPushButton(label)
            button.setToolTip(tooltip)
            button.clicked.connect(callback)
            toolbar.addWidget(button)

        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText(
            "Search or enter a website"
        )
        self.address_bar.returnPressed.connect(self.navigate_to_address)
        toolbar.addWidget(self.address_bar)

        settings_button = QPushButton("⚙ Settings")
        settings_button.clicked.connect(self.open_settings)
        toolbar.addWidget(settings_button)

        new_tab_button = QPushButton("+")
        new_tab_button.setToolTip("New tab")
        new_tab_button.clicked.connect(self.add_tab)
        toolbar.addWidget(new_tab_button)

        new_tab_action = QAction(self)
        new_tab_action.setShortcut(QKeySequence("Ctrl+T"))
        new_tab_action.triggered.connect(self.add_tab)
        self.addAction(new_tab_action)

        close_tab_action = QAction(self)
        close_tab_action.setShortcut(QKeySequence("Ctrl+W"))
        close_tab_action.triggered.connect(
            lambda: self.close_tab(self.tabs.currentIndex())
        )
        self.addAction(close_tab_action)

        self.apply_theme()
        self.add_tab()

    def current_browser(self):
        widget = self.tabs.currentWidget()
        return widget if isinstance(widget, QWebEngineView) else None

    def add_tab(self):
        browser = QWebEngineView()

        page = QWebEnginePage(self.profile, browser)
        browser.setPage(page)
        browser.setZoomFactor(self.zoom_factor())

        index = self.tabs.addTab(browser, "Yin Home")
        self.tabs.setCurrentIndex(index)

        browser.titleChanged.connect(
            lambda title, view=browser: self.update_tab_title(view, title)
        )
        browser.urlChanged.connect(
            lambda url, view=browser: self.update_address_for_view(view, url)
        )

        if self.settings["startup"] == "Blank Page":
            browser.setHtml(
                "<html><body style='background:#17191f'></body></html>"
            )
            self.tabs.setTabText(index, "Blank")
        else:
            self.show_home(browser)

        return browser

    def show_home(self, browser):
        browser.setHtml(
            make_home_html(
                self.settings["accent"],
                self.settings["search_engine"]
            ),
            QUrl("https://yin.local/")
        )

        index = self.tabs.indexOf(browser)
        if index != -1:
            self.tabs.setTabText(index, "Yin Home")

        if browser is self.current_browser():
            self.address_bar.clear()

    def open_settings(self):
        for index in range(self.tabs.count()):
            if isinstance(self.tabs.widget(index), SettingsPage):
                self.tabs.setCurrentIndex(index)
                return

        page = SettingsPage(self)
        index = self.tabs.addTab(page, "Settings")
        self.tabs.setCurrentIndex(index)
        self.address_bar.setText("yin://settings")

    def update_tab_title(self, browser, title):
        index = self.tabs.indexOf(browser)
        if index != -1 and title:
            self.tabs.setTabText(index, title[:28])

    def update_address_for_view(self, browser, url):
        if browser is self.current_browser():
            if url.host() == "yin.local":
                self.address_bar.clear()
            else:
                self.address_bar.setText(url.toString())

    def update_address_bar(self, _index=None):
        widget = self.tabs.currentWidget()

        if isinstance(widget, SettingsPage):
            self.address_bar.setText("yin://settings")
        elif isinstance(widget, QWebEngineView):
            url = widget.url()
            if url.host() == "yin.local":
                self.address_bar.clear()
            else:
                self.address_bar.setText(url.toString())
        else:
            self.address_bar.clear()

    def navigate_to_address(self):
        text = self.address_bar.text().strip()
        if not text:
            return

        if text == "yin://settings":
            self.open_settings()
            return

        browser = self.current_browser()
        if browser is None:
            browser = self.add_tab()

        if "://" in text:
            destination = text
        elif " " not in text and "." in text:
            destination = "https://" + text
        else:
            engine = SEARCH_ENGINES[self.settings["search_engine"]]
            destination = engine + quote(text)

        browser.setUrl(QUrl(destination))

    def go_home(self):
        browser = self.current_browser()
        if browser is not None:
            self.show_home(browser)
        else:
            self.add_tab()

    def go_back(self):
        browser = self.current_browser()
        if browser is not None:
            browser.back()

    def go_forward(self):
        browser = self.current_browser()
        if browser is not None:
            browser.forward()

    def reload_page(self):
        browser = self.current_browser()
        if browser is None:
            return

        if browser.url().host() == "yin.local":
            self.show_home(browser)
        else:
            browser.reload()

    def zoom_factor(self):
        return int(self.settings["zoom"].rstrip("%")) / 100.0

    def apply_zoom(self):
        for index in range(self.tabs.count()):
            widget = self.tabs.widget(index)
            if isinstance(widget, QWebEngineView):
                widget.setZoomFactor(self.zoom_factor())

    def apply_theme(self):
        theme = self.settings["theme"]
        if theme == "System":
            theme = "Dark"

        self.setStyleSheet(
            build_stylesheet(theme, self.settings["accent"])
        )

    def save_current_settings(self):
        save_settings(self.settings)

    def refresh_home_tabs(self):
        for index in range(self.tabs.count()):
            widget = self.tabs.widget(index)

            if (
                isinstance(widget, QWebEngineView)
                and widget.url().host() == "yin.local"
            ):
                self.show_home(widget)

    def close_tab(self, index):
        if index < 0:
            return

        widget = self.tabs.widget(index)

        if self.tabs.count() == 1:
            if isinstance(widget, SettingsPage):
                self.tabs.removeTab(index)
                widget.deleteLater()
                self.add_tab()
            elif isinstance(widget, QWebEngineView):
                self.show_home(widget)
            return

        self.tabs.removeTab(index)

        if widget is not None:
            widget.deleteLater()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)

    window = YinBrowser()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
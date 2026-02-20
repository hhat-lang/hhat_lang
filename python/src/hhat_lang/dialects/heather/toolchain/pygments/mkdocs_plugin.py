from __future__ import annotations

from pathlib import Path

from mkdocs.plugins import BasePlugin
from mkdocs.config import config_options as c
from pygments.formatters.html import HtmlFormatter


class HhatCssPlugin(BasePlugin):
    config_scheme = (
        ("light_style", c.Type(str, default="hhat_heather_light")),
        ("dark_style", c.Type(str, default="hhat_heather_dark")),
        ("light_scheme", c.Type(str, default="default")),  # Material light scheme name
        ("dark_scheme", c.Type(str, default="slate")),     # Material dark scheme name
        ("css_path", c.Type(str, default="stylesheets/hhat-heather-pygments.css")),
        ("selector", c.Type(str, default=".highlight")),
    )

    def on_config(self, config):
        docs_dir = Path(config["docs_dir"])
        out_path = docs_dir / self.config["css_path"]
        out_path.parent.mkdir(parents=True, exist_ok=True)

        # Scope each generated stylesheet to Material's scheme attribute selector:
        light_sel = f'[data-md-color-scheme="{self.config["light_scheme"]}"] {self.config["selector"]}'
        dark_sel  = f'[data-md-color-scheme="{self.config["dark_scheme"]}"] {self.config["selector"]}'

        light_css = HtmlFormatter(style=self.config["light_style"]).get_style_defs(light_sel)
        dark_css  = HtmlFormatter(style=self.config["dark_style"]).get_style_defs(dark_sel)

        out_path.write_text(light_css + "\n\n" + dark_css + "\n", encoding="utf-8")

        extra_css = config.setdefault("extra_css", [])
        if self.config["css_path"] not in extra_css:
            extra_css.append(self.config["css_path"])

        return config
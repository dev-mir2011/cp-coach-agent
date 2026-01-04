from fpdf import FPDF
import webbrowser
import json
import sys
import os


def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works in dev and PyInstaller exe"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)


def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))


font_path = resource_path("../data/fonts")


class BasePDFGPT(FPDF):
    """
    Docstring for BasePDFGPT
    """

    def __init__(self, THEMES, theme="light", global_line_height=1.6):
        super().__init__()
        self.theme = THEMES[theme]
        self.set_auto_page_break(auto=True, margin=15)

        # Fonts (FPDF safe)
        lbm_path = os.path.join(font_path, "LM/LibertinusMono-Regular.ttf")
        roboto_regular_path = os.path.join(font_path, "R/Roboto-Regular.ttf")
        roboto_bold_path = os.path.join(font_path, "R/Roboto-Bold.ttf")
        roboto_medium_path = os.path.join(font_path, "R/Roboto-Medium.ttf")
        fira_code_path = os.path.join(font_path, "FC/FiraCode-Medium.ttf")

        self.add_font("LibertinusMono", "", lbm_path)
        self.add_font("Roboto", "", roboto_regular_path)
        self.add_font("Roboto", "B", roboto_bold_path)
        self.add_font("RobotoMedium", "", roboto_medium_path)
        self.add_font("FiraCode", "", fira_code_path)

        self.bold_capable_fonts = {"Roboto"}
        self.global_line_height = global_line_height

    def lh(self, font_size):
        return font_size / self.global_line_height

    def apply_style(self, key):
        font, style, size, color = self.theme[key]
        if style == "B" and font not in self.bold_capable_fonts:
            style = ""
        self.set_font(font, style, size)
        self.set_text_color(*hex_to_rgb(color))
        return size

    def apply_code_style(self):
        font, style, size, text_color, bg_color = self.theme["code"]
        self.set_font(font, style, size)
        self.set_text_color(*hex_to_rgb(text_color))
        self.set_fill_color(*hex_to_rgb(bg_color))
        return size

    def add_page(self, *args, **kwargs):
        super().add_page(*args, **kwargs)
        self.set_fill_color(*hex_to_rgb(self.theme["bg"]))
        self.rect(0, 0, self.w, self.h, "F")

    def main_header(self, text):
        size = self.apply_style("main_header")
        self.cell(0, self.lh(size), text, align="C", new_y="NEXT")
        self.ln(6)

    def report_name(self, text):
        size = self.apply_style("report_name")
        self.multi_cell(0, self.lh(size), text, align="C")
        self.ln(10)

    def h3(self, text):
        size = self.apply_style("h3")
        self.cell(0, self.lh(size), text, new_y="NEXT")
        self.ln(4)

    def h4(self, text):
        size = self.apply_style("h4")
        self.cell(0, self.lh(size), text, new_y="NEXT")
        self.ln(3)

    def pdf_header(self, title, subtitle):
        self.main_header(title)
        self.report_name(subtitle)
        self.hr()

    def body(self, text):
        size = self.apply_style("body")
        self.multi_cell(0, self.lh(size), text)
        self.ln(4)

    def secondary_text(self, text):
        size = self.apply_style("secondary")
        self.multi_cell(0, self.lh(size), text)
        self.ln(3)

    def blockquote(self, text):
        size = self.apply_style("secondary")
        x = self.get_x()
        self.set_x(x + 8)
        self.multi_cell(0, self.lh(size), text)
        self.set_x(x)
        self.ln(4)

    def code(self, text, padding=2):

        size = self.apply_code_style()
        lines = text.split("\n")
        line_height = self.lh(size)
        block_width = self.w - self.l_margin - self.r_margin

        for line in lines:
            if self.get_y() + line_height + padding > self.h - self.b_margin:
                self.add_page()

            x, y = self.get_x(), self.get_y()
            self.set_fill_color(*hex_to_rgb(self.theme["code"][4]))
            self.rect(x, y, block_width, line_height + padding, "F")

            self.set_xy(x + padding, y + padding / 2)
            self.cell(0, line_height, line, ln=1)

        self.ln(6)

    def _list_item(self, prefix, text, size, indent=8, gap=3):
        x, y = self.get_x(), self.get_y()
        self.cell(indent, self.lh(size), prefix, align="R")
        self.set_xy(x + indent + gap, y)
        self.multi_cell(0, self.lh(size), text)
        self.set_x(x)

    def ul(self, items):
        size = self.apply_style("body")
        for item in items:
            self._list_item("•", item, size)
        self.ln(4)

    def ol(self, items, start=1):
        size = self.apply_style("body")
        for i, item in enumerate(items, start=start):
            self._list_item(f"{i}.", item, size)
        self.ln(4)

    def table(self, headers, rows, col_widths):
        size = self.apply_style("body")
        for h, w in zip(headers, col_widths):
            self.cell(w, self.lh(size), h, border=1)
        self.ln()
        for row in rows:
            for cell, w in zip(row, col_widths):
                self.cell(w, self.lh(size), str(cell), border=1)
            self.ln()
        self.ln(6)

    def link_text(self, text, url):
        size = self.apply_style("body")
        self.set_text_color(0, 102, 204)
        self.cell(0, self.lh(size), text, link=url, new_y="NEXT")
        self.ln(2)

    def hr(self, thickness=0.4, gap=8):
        self.set_draw_color(*hex_to_rgb(self.theme["divider"][3]))
        self.set_line_width(thickness)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(gap)

    def footer(self):
        self.set_y(-15)
        size = self.apply_style("secondary")
        self.cell(0, self.lh(size), f"Page {self.page_no()}", align="C")

    def output_pdf(self, name="report.pdf", auto_open=True):
        self.output(name)
        if auto_open:
            webbrowser.open(name)


data_path = resource_path("../data")
THEME_FILE = os.path.join(data_path, "themes.json")


with open(THEME_FILE) as t:
    THEMES = json.load(t)

#! PDF() id the function to create a pdf with formatting.


def PDF(content, theme="dark", global_line_height=1.6):
    pdf = BasePDFGPT(THEMES, theme=theme, global_line_height=global_line_height)
    pdf.add_page()

    pdf.pdf_header(
        "CPCoach Analysis",
        f"— Summary and analysis of problem {content['problem_name']} —",
    )

    pdf.h3("Problem Snapshot")
    pdf.body(content["problem_snapshot"])
    pdf.link_text(
        content["problem_link"]["name"],
        content["problem_link"]["url"],
    )

    pdf.h3("Problem Summary")
    pdf.body(content["problem_summary"])

    pdf.h3("Key Insight")
    pdf.ol(content["key_insights"])

    if content.get("why_this_works"):
        pdf.h3("Why This Approach Works")
        pdf.body(content["why_this_works"])

    pdf.h3("High Level Strategy")
    pdf.body(content["high_level_strategy"])

    pdf.h3("Input Format")
    pdf.blockquote(content["input_format"])

    pdf.h3("Output Format")
    pdf.blockquote(content["output_format"])

    pdf.h3("Constraints & Implications")
    pdf.body(content["constraints_and_implications"])

    pdf.h3("Common Mistakes & Edge Cases")
    pdf.body(content["common_mistakes_and_edge_cases"])

    pdf.h3("Worked Examples")
    pdf.body(content["example"])

    pdf.h3("Final Complexity Analysis")
    pdf.body(content["final_complexity_analysis"])

    pdf.h3("Takeaway")
    pdf.body(content["takeaway"])

    pdf.h3("Reference Implementation")
    pdf.code("cpcoach solve <problem_id> --lang <lang>")

    return pdf


def content_from_json(cache_data, scraped_data):
    problem_code = f"{scraped_data['contest_id']}{scraped_data['index']}"

    analysis = cache_data["analysis"]
    summary = analysis["summary"]
    deep_analysis = analysis["analysis"]
    solution = analysis["solution"]

    # ---- Constraints (robust handling) ----
    constraints = summary.get("constraints", {})
    bounds = constraints.get("bounds", [])

    bounds_lines = []
    for b in bounds:
        if isinstance(b, dict):
            bounds_lines.append(
                f"- {b.get('variable', '')}: {b.get('range', b.get('condition', ''))}"
            )
        else:
            bounds_lines.append(f"- {b}")

    constraints_text = (
        f"Time Limit: {constraints.get('time_limit', 'N/A')}\n"
        f"Memory Limit: {constraints.get('memory_limit', 'N/A')}\n"
        "Bounds:\n" + ("\n".join(bounds_lines) if bounds_lines else "N/A")
    )

    # ---- Sample cases formatting ----
    examples = []
    for i, sc in enumerate(summary.get("sample_cases", []), 1):
        examples.append(
            f"Example {i}\n"
            f"Input:\n{sc.get('input', '')}\n\n"
            f"Output:\n{sc.get('output', '')}"
        )

    # ---- Snapshot ----
    snapshot = (
        f"Problem Code: {problem_code}\n"
        f"Title: {scraped_data.get('title', 'N/A')}\n"
        f"Rating: {scraped_data.get('rating', 'N/A')}\n"
        f"Platform: Codeforces"
    )

    return {
        "problem_name": problem_code,
        "problem_snapshot": snapshot,
        "problem_link": {
            "name": f"CodeForces Problem {problem_code}",
            "url": scraped_data.get("url", ""),
        },
        "problem_summary": summary.get("problem_statement", ""),
        "key_insights": solution.get("key_insights", []),
        "why_this_works": deep_analysis.get("key_observation", ""),
        "input_format": summary.get("input_format", {}).get("description", ""),
        "output_format": summary.get("output_format", {}).get("description", ""),
        "constraints_and_implications": constraints_text,
        "high_level_strategy": solution.get("approach", ""),
        "common_mistakes_and_edge_cases": "\n".join(
            f"- {e}" for e in deep_analysis.get("edge_cases", [])
        ),
        "example": "\n\n".join(examples),
        "final_complexity_analysis": (
            f"Time Complexity: {solution.get('time_complexity', 'N/A')}\n"
            f"Space Complexity: {solution.get('space_complexity', 'N/A')}"
        ),
        "takeaway": deep_analysis.get("key_observation", ""),
    }


# content = content_from_json(cache, scraped)

# pdf = PDF(content, theme="dark", global_line_height=1.6)

# pdf.output_pdf(f"cpcoach_analysis_{content['problem_name']}.pdf")

from cf_lookup import lookup_or_scrape


def generate_pdf_report(problem_name: str, theme="dark", auto_open=True):
    problem_name = problem_name.strip().upper()
    scraped_data = lookup_or_scrape(problem_name)

    cache_path = resource_path("../data/cache")
    cache_file_path = os.path.join(cache_path, f"{problem_name.strip().lower()}.txt")
    with open(cache_file_path, encoding="utf-8") as file:
        cache_data = json.load(file)

    content = content_from_json(cache_data, scraped_data)

    pdf = PDF(content, theme=theme, global_line_height=1.6)

    filename = f"CPCoach_analysis_{content['problem_name']}.pdf"
    output_path = os.path.join(os.getcwd(), filename)

    pdf.output_pdf(output_path, auto_open=auto_open)
    # return output_path

from pathlib import Path


def create_readme():
    textstring = """# RSS straumar\n\n

RSS straumar nokkurra vefsvæða sem vantar slíkt.\n\n


Hægri smelltu á tengilinn á .rss skrána, afritaðu tengilinn og notaðu í þeim rss-lesara sem hentar þér.\n\n

[Inoreader](https://inoreader.com/) er ágætur rss-lesari í vafra.\n\n"""

    for rss_file in Path("rss").rglob("*.rss"):
        textstring += f"- [{rss_file.stem}](https://raw.githubusercontent.com/pallih/rss/refs/heads/main/{rss_file})\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(textstring)


if __name__ == "__main__":
    create_readme()

#!/usr/bin/env python3

import os
import sys
import yaml  
import calendar
import itertools
from datetime import datetime
from dateutil.parser import (
    parse as parse_date,
)  


def escape_markdown(text: str) -> str:
    """Escapa colchetes para o markdown."""
    return str(text).replace("[", "\\[").replace("]", "\\]")


def main():
    entries = []
    # Caminhos a serem ignorados, normalizados com /
    skip_paths = {"content/index.md", "content/_index.md"}

    start_dir = "content/"

    for root, dirs, files in os.walk(start_dir):
        for file in files:
            if not file.endswith("index.md"):
                continue

            # Normaliza o caminho para usar / e ser relativo
            full_path = os.path.join(root, file).replace(os.path.sep, "/")

            if full_path in skip_paths:
                continue

            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                if lines and lines[0].strip() == "---":
                    fm_lines = []
                    i = 1
                    while i < len(lines) and lines[i].strip() != "---":
                        fm_lines.append(lines[i])
                        i += 1

                    if i < len(lines) and lines[i].strip() == "---":
                        front = yaml.safe_load("".join(fm_lines))

                        if front and "title" in front and "date" in front:
                            try:
                                date_obj = parse_date(str(front["date"]))

                                url = full_path.replace(start_dir, "", 1).replace(
                                    "index.md", ""
                                )
                                if not url.startswith("/"):
                                    url = "/" + url

                                entries.append(
                                    {
                                        "title": front["title"],
                                        "url": url,
                                        "date": date_obj,
                                    }
                                )

                            except Exception as e:
                                print(
                                    f"Erro ao analisar data em {full_path}: {e}",
                                    file=sys.stderr,
                                )

            except (yaml.YAMLError, UnicodeDecodeError) as e:
                print(f"Erro de YAML/Leitura em {full_path}: {e}", file=sys.stderr)
            except Exception as e:
                print(f"Erro genérico ao processar {full_path}: {e}", file=sys.stderr)

    entries.sort(key=lambda e: e["date"], reverse=True)

    grouped = {}
    for (year, month), group in itertools.groupby(
        entries, key=lambda e: (e["date"].year, e["date"].month)
    ):
        grouped[(year, month)] = list(group)  # Salva o grupo como uma lista

    try:
        with open("content/_index.md", "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write("title: JorgeLeandro's Blog\n")
            f.write("---\n\n")

            # As chaves já estarão em ordem (mais novas primeiro)
            # porque agrupamos uma lista já ordenada.
            for year, month in grouped.keys():
                month_name = calendar.month_name[month]  # Ex: "May", "June"
                f.write(f"## {year} - {month_name}\n\n")

                # Os posts dentro do 'grouped[(year, month)]' já estão
                # ordenados do mais novo para o mais antigo.
                for post in grouped[(year, month)]:
                    f.write(f"- [{escape_markdown(post['title'])}]({post['url']})\n")

                f.write("\n")  # Adiciona uma linha em branco após cada grupo de mês

        print("Gerado _index.md com posts agrupados por ano & mês.")

    except IOError as e:
        print(f"Erro ao escrever em content/_index.md: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()

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


def write_index_file(
    filepath: str,
    title: str,
    comments_enabled: bool,
    entries_list: list,
    all_tags_list: set,
    months_pt: list,
    active_tag: str = None,
):
    """
    Escreve um arquivo de índice (seja o principal ou de uma tag)
    agrupando os posts por data.
    """

    grouped = {}
    for (year, month), group in itertools.groupby(
        entries_list, key=lambda e: (e["date"].year, e["date"].month)
    ):
        grouped[(year, month)] = list(group)


    output_dir = os.path.dirname(filepath)
    if output_dir:  # Evita erro se o caminho for "" ou "."
        os.makedirs(output_dir, exist_ok=True)


    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("---\n")
            f.write(f'title: "{title}"\n')
            f.write(f'comments: {comments_enabled}\n')
            f.write("layout: single\n")
            f.write("---\n\n")


            if all_tags_list:
                sorted_tags = sorted(list(all_tags_list))
                tag_links = []
                

                if active_tag is None:

                    tag_links.append("`Todas`")
                else:

                    tag_links.append("[`Todas`](/)")


                for t in sorted_tags:
                    if t == active_tag:

                        tag_links.append(f"`{t}`")
                    else:

                        tag_links.append(f"[`{t}`](/tags/{t})")


                tag_line = " ".join(tag_links)
                f.write(f"**Tags:** {tag_line}\n\n")


            if not grouped:
                f.write("Nenhum post encontrado.\n\n")


            for year, month in grouped.keys():
                month_name = months_pt[month]  # Usa o calendar.month_name
                f.write(f"## {year} - {month_name}\n\n")

                for post in grouped[(year, month)]:
                    f.write(f"- [{escape_markdown(post['title'])}]({post['url']})\n")

                f.write("\n")

        print(f"Gerado: {filepath}")

    except IOError as e:
        print(f"Erro ao escrever em {filepath}: {e}", file=sys.stderr)


def main():
    entries = []
    all_tags = set()
    skip_paths = {"content/index.md", "content/_index.md"}

    start_dir = "content/"

    for root, dirs, files in os.walk(start_dir):
        dirs[:] = [d for d in dirs if d != "tags"]

        for file in files:
            if not file.endswith("index.md"):
                continue

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

                        if front:

                            tags = front.get("tags", [])
                            if isinstance(tags, list):
                                all_tags.update(tags)


                            if "title" in front and "date" in front:
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
                                            "tags": tags, 
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

    # Ordena todos os posts por data, UMA VEZ
    entries.sort(key=lambda e: e["date"], reverse=True)

    # Configuração dos meses em Português
    months_pt = [
        "",
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro",
    ]



    print("Gerando página principal...")
    write_index_file(
        filepath="content/_index.md",
        title="Blog do Jorge Leandro",
        comments_enabled=False,
        entries_list=entries,
        all_tags_list=all_tags,
        months_pt=months_pt,
        active_tag=None,
    )


    print("Gerando páginas de tags...")
    for tag in all_tags:
        tag_entries = [entry for entry in entries if tag in entry["tags"]]

        tag_filepath = f"content/tags/{tag}/index.md"

        write_index_file(
            filepath=tag_filepath,
            title="Blog do Jorge Leandro",
            comments_enabled=False,
            entries_list=tag_entries,
            all_tags_list=all_tags,
            months_pt=months_pt,
            active_tag=tag,
        )
    
    print("\nProcesso concluído.")


if __name__ == "__main__":
    main()


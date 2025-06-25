import re
import sys
from pathlib import Path

def get_citations_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return set(re.findall(r'@([a-zA-Z0-9-]+)', content))
    except FileNotFoundError:
        print(f"错误: 找不到文件 {file_path}", file=sys.stderr)
        return set()
    except Exception as e:
        print(f"读取文件 {file_path} 时发生错误: {e}", file=sys.stderr)
        return set()

def get_bib_keys(bib_path):
    try:
        with open(bib_path, 'r', encoding='utf-8') as f:
            bib_content = f.read()
        return set(re.findall(r'@\w+{([^,]+),', bib_content))
    except FileNotFoundError:
        print(f"错误: 找不到文件 {bib_path}", file=sys.stderr)
        return set()
    except Exception as e:
        print(f"读取文件 {bib_path} 时发生错误: {e}", file=sys.stderr)
        return set()

def compare_references(manuscript_paths, bib_path):
    all_manuscript_citations = set()
    manuscript_citations_map = {}

    for path in manuscript_paths:
        citations = get_citations_from_file(path)
        manuscript_citations_map[Path(path).name] = citations
        all_manuscript_citations.update(citations)

    bib_keys = get_bib_keys(bib_path)

    if not bib_keys:
        return

    missing_in_bib = all_manuscript_citations - bib_keys
    uncited_keys = bib_keys - all_manuscript_citations

    print('--- 引用与文献库比对报告 ---')
    print(f'共检查 {len(manuscript_paths)} 份手稿.')
    for name, citations in manuscript_citations_map.items():
        print(f'  - 手稿 "{name}" 中总引用条目数: {len(citations)}')
    print(f'.bib 文件中总文献条目数: {len(bib_keys)}')
    print(f'所有手稿中去重后总引用条目数: {len(all_manuscript_citations)}')
    print('\n--- 检查结果 ---')

    if not missing_in_bib and not uncited_keys:
        print('状态: 完美！所有引用均匹配，无冗余文献。')
    else:
        if missing_in_bib:
            print(f'【警告】手稿中引用但 .bib 文件缺失的条目 ({len(missing_in_bib)}):')
            for item in sorted(list(missing_in_bib)):
                sources = [name for name, cits in manuscript_citations_map.items() if item in cits]
                print(f'  - {item} (存在于: {", ".join(sources)})')
        else:
            print('所有手稿中的引用都在 .bib 文件中找到了。')

        if uncited_keys:
            print(f'\n【注意】存在于 .bib 文件但所有手稿中均未引用的条目 ({len(uncited_keys)}):')
            for item in sorted(list(uncited_keys)):
                print(f'  - {item}')
        else:
            print('\n.bib 文件中的所有文献都在手稿中被引用了。')


if __name__ == '__main__':
    manuscript_files = ['src-typ/manuscript_cn.typ', 'src-typ/manuscript_en.typ']
    bib_file = 'src-typ/references.bib'
    compare_references(manuscript_files, bib_file)
